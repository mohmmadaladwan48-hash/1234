#!/usr/bin/env python3
"""
Instagram RapidAPI Scraper
Fast, reliable Instagram user data extraction using RapidAPI
"""

import requests
import json
import os
import time
from datetime import datetime
from pathlib import Path

class InstagramRapidAPIScraper:
    """Instagram scraper using RapidAPI endpoint"""
    
    def __init__(self):
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY", "")
        self.rapidapi_host = "instagram-scraper-api2.p.rapidapi.com"
        self.output_dir = Path("./output")
        self.output_dir.mkdir(exist_ok=True)
        self.search_history_file = self.output_dir / "search_history.json"
        self.search_history = self.load_search_history()
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour
    
    def load_search_history(self):
        """Load search history from JSON"""
        if self.search_history_file.exists():
            try:
                with open(self.search_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_search_history(self):
        """Save search history to JSON"""
        try:
            with open(self.search_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.search_history, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_user_info(self, username, timeout=10):
        """
        Get Instagram user info via RapidAPI
        Much faster and more reliable than web scraping
        """
        try:
            username = username.lstrip('@')
            
            # Check cache first
            cached = self._cache_get(f"instagram:{username}")
            if cached:
                return cached
            
            if not self.rapidapi_key:
                return {"error": "❌ RAPIDAPI_KEY not configured. Contact admin."}
            
            # Call RapidAPI endpoint
            url = "https://instagram-scraper-api2.p.rapidapi.com/v1/info"
            headers = {
                "x-rapidapi-host": self.rapidapi_host,
                "x-rapidapi-key": self.rapidapi_key,
                "accept": "application/json"
            }
            params = {"username_or_id_or_url": username}
            
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                info = self._parse_response(data, username)
                
                if info and "error" not in info:
                    # Save to history and cache
                    self.search_history[username] = info
                    self.save_search_history()
                    self._cache_set(f"instagram:{username}", info)
                    return info
            
            if response.status_code == 404:
                return {"error": "❌ Instagram user not found"}
            
            if response.status_code == 429:
                return {"error": "⏱️ RapidAPI rate limit. Try again in 1 minute."}
            
            return {"error": f"❌ API error: HTTP {response.status_code}"}
        
        except requests.Timeout:
            return {"error": "⏱️ Request timeout (10s). Try again later."}
        except Exception as e:
            return {"error": f"❌ Error: {str(e)[:100]}"}
    
    def _parse_response(self, data, username):
        """Parse RapidAPI response"""
        try:
            if not data or not data.get("data"):
                return None
            
            user = data["data"]
            
            return {
                "platform": "Instagram",
                "account_id": user.get("pk") or user.get("id", "N/A"),
                "username": user.get("username") or username,
                "full_name": user.get("full_name") or user.get("name", "N/A"),
                "followers": user.get("follower_count") or user.get("followers", 0),
                "following": user.get("following_count") or user.get("following", 0),
                "bio": user.get("biography") or user.get("bio", ""),
                "full_location": user.get("city") or user.get("location", "N/A"),
                "posts_count": user.get("media_count") or user.get("posts", 0),
                "is_verified": user.get("is_verified") or False,
                "is_public": not user.get("is_private", False),
                "is_business_account": user.get("is_business_account") or False,
                "external_url": user.get("external_url") or user.get("website", "N/A"),
                "profile_pic": user.get("profile_pic_url", "N/A"),
                "search_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except:
            return None
    
    def _cache_get(self, key):
        """Get from cache if fresh"""
        if key in self._cache:
            cached_data, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_data
            else:
                del self._cache[key]
        return None
    
    def _cache_set(self, key, data):
        """Store in cache with timestamp"""
        self._cache[key] = (data, time.time())
