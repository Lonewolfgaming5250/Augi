"""Web search functionality without opening a browser."""
import requests
from typing import Dict, List, Optional
from urllib.parse import quote
import json


class WebSearcher:
    """Performs web searches without opening a browser."""
    
    def __init__(self):
        """Initialize web searcher."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.search_results_cache = {}
    
    def search(self, query: str, num_results: int = 5, timeout: int = 10) -> List[Dict]:
        """Search the internet using multiple methods.
        
        Args:
            query: Search query
            num_results: Number of results to return
            timeout: Request timeout in seconds
            
        Returns:
            List of search results with title, url, and snippet
        """
        if not query or not query.strip():
            return []
        
        # Check cache
        cache_key = query.lower()
        if cache_key in self.search_results_cache:
            return self.search_results_cache[cache_key][:num_results]
        
        results = []
        
        # Try bing first
        results = self._search_bing(query, timeout)
        if not results:
            # Try alternative search
            results = self._search_alternative(query, timeout)
        
        # Cache results
        self.search_results_cache[cache_key] = results
        
        return results[:num_results]
    
    def _search_bing(self, query: str, timeout: int) -> List[Dict]:
        """Search using Bing search page."""
        try:
            url = f"https://www.bing.com/search?q={quote(query)}"
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for item in soup.find_all('li', class_='b_algo')[:5]:
                try:
                    title_elem = item.find('h2')
                    if title_elem:
                        title_link = title_elem.find('a')
                        if title_link:
                            title = title_link.get_text(strip=True)
                            url = title_link.get('href', '')
                            
                            snippet_elem = item.find('p')
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                            
                            if url and title:
                                results.append({
                                    'title': title,
                                    'url': url,
                                    'snippet': snippet
                                })
                except:
                    continue
            
            return results
        except:
            return []
    
    def _search_alternative(self, query: str, timeout: int) -> List[Dict]:
        """Alternative search method."""
        try:
            # Try fetching from a simple API endpoint
            url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1"
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Parse DuckDuckGo API response
            if 'RelatedTopics' in data:
                for item in data['RelatedTopics'][:5]:
                    if 'Text' in item and 'FirstURL' in item:
                        results.append({
                            'title': item.get('Text', 'Result')[:100],
                            'url': item.get('FirstURL', ''),
                            'snippet': item.get('Text', '')[:200]
                        })
            
            return results
        except:
            return []
    
    def search_with_summary(self, query: str, num_results: int = 3) -> str:
        """Search and return formatted results.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Formatted string of search results
        """
        results = self.search(query, num_results=num_results)
        
        if not results:
            return f"No results found for '{query}'"
        
        summary = f"Search Results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            summary += f"{i}. {result['title']}\n"
            summary += f"   URL: {result['url']}\n"
            if result['snippet']:
                # Truncate long snippets
                snippet = result['snippet'][:150] + "..." if len(result['snippet']) > 150 else result['snippet']
                summary += f"   {snippet}\n"
            summary += "\n"
        
        return summary
    
    def get_definition(self, term: str) -> Optional[str]:
        """Get a quick definition of a term.
        
        Args:
            term: Term to define
            
        Returns:
            Definition if found, None otherwise
        """
        query = f"definition of {term}"
        results = self.search(query, num_results=1)
        
        if results:
            return results[0].get('snippet', '')
        return None
    
    def search_weather(self, location: str) -> str:
        """Search for weather information.
        
        Args:
            location: Location to get weather for
            
        Returns:
            Weather information
        """
        query = f"weather in {location} today"
        return self.search_with_summary(query, num_results=2)
    
    def search_news(self, topic: str, num_results: int = 5) -> str:
        """Search for news about a topic.
        
        Args:
            topic: Topic to search for
            num_results: Number of results to return
            
        Returns:
            News results
        """
        query = f"{topic} news"
        return self.search_with_summary(query, num_results=num_results)
    
    def search_person(self, name: str) -> str:
        """Search for information about a person.
        
        Args:
            name: Person's name
            
        Returns:
            Information about the person
        """
        return self.search_with_summary(name, num_results=3)
    
    def clear_cache(self):
        """Clear search results cache."""
        self.search_results_cache.clear()
