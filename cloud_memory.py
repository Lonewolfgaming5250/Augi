"""
MongoDB Atlas cloud memory integration for Augi AI Assistant
"""
from pymongo import MongoClient
import os


# Use environment variable for MongoDB Atlas URI, fallback to a correct default
MONGODB_URI = os.getenv(
    "MONGODB_ATLAS_URI",
    "mongodb+srv://killerzd1996_db_user:h6z5y1YwAoUgHFqy@cluster0.pzh0azx.mongodb.net/augi?retryWrites=true&w=majority"
)
DB_NAME = "augi"

class CloudMemory:
    def __init__(self, uri=MONGODB_URI, db_name=DB_NAME):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.conversations = self.db["conversations"]
        self.user_profiles = self.db["user_profiles"]

    def save_conversation(self, session_id, conversation_data):
        """Save or update a conversation by session_id."""
        self.conversations.update_one(
            {"session_id": session_id},
            {"$set": conversation_data},
            upsert=True
        )

    def load_conversation(self, session_id):
        """Load a conversation by session_id."""
        return self.conversations.find_one({"session_id": session_id})

    def list_conversations(self, limit=10):
        """List recent conversations (most recent first)."""
        return list(self.conversations.find().sort("timestamp", -1).limit(limit))

    def save_user_profile(self, user_id, profile_data):
        """Save or update a user profile."""
        self.user_profiles.update_one(
            {"user_id": user_id},
            {"$set": profile_data},
            upsert=True
        )

    def load_user_profile(self, user_id):
        """Load a user profile by user_id."""
        return self.user_profiles.find_one({"user_id": user_id})

    def search_conversations(self, keyword, limit=5):
        """Search conversations for a keyword in any message content."""
        return list(self.conversations.find({"messages.content": {"$regex": keyword, "$options": "i"}}).limit(limit))

    def clear_memory(self):
        """Delete all conversations and user profiles (dangerous!)."""
        self.conversations.delete_many({})
        self.user_profiles.delete_many({})
