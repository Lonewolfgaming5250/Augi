def detect_personality_from_message(message: str):
    """Smarter mood/tone detection: score personalities by keyword matches."""
    msg = message.lower()
    personality_keywords = {
        PersonalityType.HELPFUL: ["help", "stuck", "confused", "frustrated", "issue", "problem", "assist", "support"],
        PersonalityType.WITTY: ["lol", "funny", "joke", "haha", "pun", "witty", "entertain", "laugh", "humor"],
        PersonalityType.TECH_SAVVY: ["tech", "code", "program", "python", "ai", "machine learning", "computer", "software", "hardware"],
        PersonalityType.FRIENDLY: ["hi", "hello", "hey", "what's up", "how are you", "buddy", "friend", "greetings", "nice to meet"],
        PersonalityType.PROFESSIONAL: ["please", "thank you", "regards", "sincerely", "formal", "business", "report", "efficient", "professional"],
        PersonalityType.CASUAL: ["chill", "relax", "casual", "easygoing", "no worries", "laid back", "hang out", "just talking"],
        PersonalityType.SASSY: ["sassy", "attitude", "sardonic", "sneer", "smirk", "sarcastic", "mock", "tease"],
    }
    scores = {ptype: 0 for ptype in personality_keywords}
    for ptype, keywords in personality_keywords.items():
        for word in keywords:
            if word in msg:
                scores[ptype] += 1
    # Pick the highest scoring personality, break ties by priority order
    best_personality = None
    best_score = 0
    for ptype in [PersonalityType.WITTY, PersonalityType.HELPFUL, PersonalityType.TECH_SAVVY, PersonalityType.FRIENDLY, PersonalityType.PROFESSIONAL, PersonalityType.CASUAL, PersonalityType.SASSY]:
        if scores[ptype] > best_score:
            best_score = scores[ptype]
            best_personality = ptype
    return best_personality
"""
Augi - Personal AI Assistant Web App
Built with Streamlit for cross-platform access (Web, Android, iPhone, Desktop)
"""


import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic
from src.personality import PersonalityType, PersonalityManager
from src.memory_manager import MemoryManager
from src.user_profile import UserProfileManager
from src.permission_manager import PermissionManager, OperationType
from src.web_searcher import WebSearcher
import collections.abc
import streamlit_authenticator as stauth

def convert_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, collections.abc.Mapping):
        return {k: convert_sets(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets(i) for i in obj]
    else:
        return obj

    # Google login user name
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
    if "use_custom_name" not in st.session_state:
        st.session_state.use_custom_name = False
    if "custom_name" not in st.session_state:
        st.session_state.custom_name = ""
# Page configuration
st.set_page_config(
    page_title="Augi - AI Assistant",
    page_icon="[AI]",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Google Login Setup ---
import yaml
from yaml import SafeLoader

# Example config for Google login (replace with your client_id, etc.)
config = yaml.safe_load('''
credentials:
  usernames:
    user1:
      email: user1@gmail.com
      name: User One
cookie:
  expiry_days: 30
  key: some_signature_key
  name: augi_login_cookie
preauthorized:
  emails:
    - user1@gmail.com
''')

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status is False:
    st.error('Login failed. Please check your credentials.')
    st.stop()
elif authentication_status is None:
    st.warning('Please log in to use Augi.')
    st.stop()
else:
    st.session_state.user_name = name

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stChatMessage { margin-bottom: 1rem; }
    .personality-selector { margin: 1rem 0; }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if "client" not in st.session_state:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            st.error("Anthropic API key not found. Please set ANTHROPIC_API_KEY in your environment.")
            st.stop()
        st.session_state.client = Anthropic(api_key=api_key)
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    if "personality" not in st.session_state:
        st.session_state.personality = PersonalityType.FRIENDLY
    
    if "personality_manager" not in st.session_state:
        st.session_state.personality_manager = PersonalityManager()
    
    if "memory_manager" not in st.session_state:
        st.session_state.memory_manager = MemoryManager()
    
    if "user_profile_manager" not in st.session_state:
        st.session_state.user_profile_manager = UserProfileManager()
    
    if "permission_manager" not in st.session_state:
        st.session_state.permission_manager = PermissionManager()
    
    if "web_searcher" not in st.session_state:
        st.session_state.web_searcher = WebSearcher()
    
    if "enable_learning" not in st.session_state:
        st.session_state.enable_learning = True
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

init_session_state()

# Sidebar configuration
with st.sidebar:
    st.title(f"[SETTINGS] Settings - Logged in as: {st.session_state.user_name}")

    st.subheader("User Name")
    st.session_state.use_custom_name = st.checkbox("Use a different name", value=st.session_state.use_custom_name)
    if st.session_state.use_custom_name:
        st.session_state.custom_name = st.text_input("Enter your preferred name:", value=st.session_state.custom_name)
        display_name = st.session_state.custom_name if st.session_state.custom_name else st.session_state.user_name
    else:
        display_name = st.session_state.user_name
    st.info(f"Current name: {display_name}")
    
    # Personality selection
    st.subheader("Personality")
    personality_options = {
        "Professional": PersonalityType.PROFESSIONAL,
        "Friendly": PersonalityType.FRIENDLY,
        "Witty": PersonalityType.WITTY,
        "Helpful": PersonalityType.HELPFUL,
        "Tech Savvy": PersonalityType.TECH_SAVVY,
        "Casual": PersonalityType.CASUAL,
        "Sassy": PersonalityType.SASSY,
    }
    
    selected_personality = st.selectbox(
        "Choose personality:",
        list(personality_options.keys()),
        index=list(personality_options.values()).index(st.session_state.personality)
    )
    st.session_state.personality = personality_options[selected_personality]
    
    st.divider()
    
    # Learning settings
    st.subheader("Learning")
    st.session_state.enable_learning = st.checkbox("Enable learning", value=st.session_state.enable_learning)
    
    if st.button("View learned profile"):
        profile = st.session_state.user_profile_manager.get_profile()
        st.json(profile)
    
    if st.button("Clear learning"):
        st.session_state.user_profile_manager.clear_profile()
        st.success("Learning cleared!")
    
    st.divider()
    
    # Conversation management
    st.subheader("Conversations")
    if st.button("Save conversation"):
        st.session_state.memory_manager.save_conversation(
            st.session_state.conversation_history,
            st.session_state.session_id
        )
        st.success("Conversation saved!")
    
    if st.button("Start new conversation"):
        st.session_state.conversation_history = []
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.success("New conversation started!")
    
    st.divider()
    
    # Memory Recall Section
    st.subheader("[MEMORY] Memory & Recall")
    
    recall_tab1, recall_tab2, recall_tab3 = st.tabs(["Browse", "Search", "Stats"])
    
    with recall_tab1:
        st.write("**Your conversation history:**")
        all_convs = st.session_state.memory_manager.list_conversations(limit=20)
        if all_convs:
            for conv in all_convs:
                conv_label = f"{conv['session_id']} ({conv['message_count']} messages)"
                if st.button(conv_label, key=f"load_{conv['session_id']}"):
                    loaded_conv = st.session_state.memory_manager.load_conversation(conv["session_id"])
                    if loaded_conv:
                        st.session_state.conversation_history = loaded_conv
                        st.session_state.session_id = conv["session_id"]
                        st.success("Conversation loaded! Refresh to see messages.")
                        st.rerun()
        else:
            st.info("No conversations saved yet.")
    
    with recall_tab2:
        search_query = st.text_input("Search past conversations:")
        if search_query:
            search_results = st.session_state.memory_manager.search_conversations(search_query, limit=5)
            if search_results:
                st.write(f"Found {len(search_results)} matching conversation(s):")
                for result in search_results:
                    with st.expander(f"📄 {result.get('session_id', 'Unknown')}"):
                        st.write(f"**Timestamp:** {result.get('timestamp', 'N/A')}")
                        st.write(f"**Messages:** {result.get('message_count', 0)}")
                        st.write(f"**Matched content:** {result.get('matched_content', 'N/A')[:150]}")
                        if st.button("Load this conversation", key=f"search_load_{result['session_id']}"):
                            loaded_conv = st.session_state.memory_manager.load_conversation(result["session_id"])
                            if loaded_conv:
                                st.session_state.conversation_history = loaded_conv
                                st.session_state.session_id = result["session_id"]
                                st.success("Conversation loaded!")
                                st.rerun()
            else:
                st.info(f"No conversations found matching '{search_query}'")
    
    with recall_tab3:
        st.write("**Your memory statistics:**")
        all_conversations = st.session_state.memory_manager.list_conversations(limit=1000)
        total_messages = sum(c.get("message_count", 0) for c in all_conversations)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Conversations", len(all_conversations))
        with col2:
            st.metric("Total Messages", total_messages)
        with col3:
            if all_conversations:
                avg_messages = total_messages / len(all_conversations)
                st.metric("Avg Messages/Conv", f"{avg_messages:.1f}")
        
        if st.button("[DELETE] Clear ALL memory"):
            if st.session_state.memory_manager.clear_memory(confirm=True):
                st.success("All memory cleared!")
                st.session_state.conversation_history = []
                st.rerun()
    
    st.divider()
    

# Main chat interface
st.title(f"[AI] Augi - Your Personal AI Assistant ({display_name})")
st.markdown("*Cross-platform AI companion built with Streamlit*")

# Display conversation history
chat_container = st.container()
with chat_container:
    for message in st.session_state.conversation_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...", key="user_input")


if user_input:
    # Detect and adapt personality based on user message
    detected_personality = detect_personality_from_message(user_input)
    if detected_personality and detected_personality != st.session_state.personality:
        st.session_state.personality = detected_personality
        st.toast(f"Personality adapted to: {detected_personality.name.title()}")

    # Add user message to history
    st.session_state.conversation_history.append({
        "role": "user",
        "content": user_input
    })

    # Display user message
    with st.chat_message("user"):
        st.write(user_input)

    # Get AI response
    with st.spinner("Augi is thinking..."):
        try:
            # Check if internet search is needed
            search_keywords = ["search", "find", "look up", "weather", "news", "what's"]
            should_search = any(keyword in user_input.lower() for keyword in search_keywords)

            search_results = None
            if should_search:
                # Ask for permission
                if st.session_state.permission_manager.check_permission(OperationType.INTERNET_ACCESS, "web_search"):
                    search_results = st.session_state.web_searcher.search(user_input)
            
            # Get relevant past conversations for context
            relevant_convs = st.session_state.memory_manager.get_relevant_conversations(user_input, limit=2)
            past_context = ""
            if relevant_convs:
                past_context = "\n\nRELEVANT PAST CONVERSATIONS:\n"
                for conv in relevant_convs:
                    context = st.session_state.memory_manager.get_conversation_context(conv["session_id"], max_messages=3)
                    past_context += f"{context}\n---\n"
            
            # Build system prompt
            system_prompt = f"""You are Augi, a helpful personal AI assistant. Your personality is: {st.session_state.personality_manager.PERSONALITIES[st.session_state.personality].response_style}

{st.session_state.personality_manager.PERSONALITIES[st.session_state.personality].system_prompt_addition}

Current date and time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


You have access to the user's profile information:
{json.dumps(convert_sets(st.session_state.user_profile_manager.get_profile()), indent=2) if st.session_state.enable_learning else "No profile information available yet."}

IMPORTANT: You have complete memory of all past conversations with this user. Use this information to:
- Provide continuity and context
- Reference previous discussions
- Build on what you've learned about the user
- Give personalized and informed responses
{past_context}

When the user asks questions, be conversational and helpful. Reference past conversations when relevant. If you performed an internet search, incorporate the results naturally into your response.
"""
            
            # Add search context if available
            if search_results:
                system_prompt += f"\n\nInternet Search Results:\n{json.dumps(convert_sets(search_results), indent=2)}"
            
            # Call Claude API
            response = st.session_state.client.messages.create(
                model="claude-opus-4-1",
                max_tokens=1000,
                system=system_prompt,
                messages=st.session_state.conversation_history
            )
            if not response or not hasattr(response, "content") or not response.content or not hasattr(response.content[0], "text") or not response.content[0].text:
                st.error("No response from Claude. Please try again.")
            else:
                assistant_message = response.content[0].text
                # Add assistant message to history
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                # Display assistant message
                with st.chat_message("assistant"):
                    st.write(assistant_message)
                # Update user profile if learning is enabled
                if st.session_state.enable_learning:
                    st.session_state.user_profile_manager.extract_from_conversation(
                        st.session_state.conversation_history
                    )
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Footer
st.divider()
st.markdown("""
    <div style="text-align: center; color: gray; font-size: 0.8rem;">
    Augi v2.0 | Cross-platform AI Assistant | Powered by Streamlit & Claude
    </div>
    """, unsafe_allow_html=True)
