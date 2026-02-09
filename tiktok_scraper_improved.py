#!/usr/bin/env python3
"""
Improved TikTok Scraper with Better API Support
"""

import requests
import json
import re
import os
import time
from bs4 import BeautifulSoup
from datetime import datetime

class TikTokScraperImproved:
    def __init__(self):
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY", "")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self._cache = {}
        self._cache_ttl = 86400
    
    def get_user_info(self, username):
        """Get TikTok user info with account ID"""
        try:
            username = username.lstrip('@')
            
            cached = self._cache_get(f"tiktok:{username}")
            if cached:
                return cached
            
            # Try RapidAPI first (most reliable)
            if self.rapidapi_key:
                info = self._api_scrape_rapidapi(username)
                if info and "error" not in info:
                    self._cache_set(f"tiktok:{username}", info)
                    return info
            
            # Fallback to web scrape
            info = self._web_scrape(username)
            if info and "error" not in info:
                self._cache_set(f"tiktok:{username}", info)
                return info
            
            return {"error": "❌ TikTok user not found or private account"}
        
        except Exception as e:
            return {"error": f"❌ TikTok error: {str(e)[:100]}"}
    
    def _cache_get(self, key):
        if key in self._cache:
            cached_data, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_data
            else:
                del self._cache[key]
        return None
    
    def _cache_set(self, key, data):
        self._cache[key] = (data, time.time())
    
    def _api_scrape_rapidapi(self, username):
        """Use RapidAPI TikTok endpoint"""
        try:
            # Best endpoint for user info
            url = "https://tiktok-api23.p.rapidapi.com/api/user/info"
            headers = {
                "x-rapidapi-host": "tiktok-api23.p.rapidapi.com",
                "x-rapidapi-key": self.rapidapi_key,
                "accept": "application/json"
            }
            params = {"uniqueId": username}
            
            r = requests.get(url, headers=headers, params=params, timeout=12)
            
            if r.status_code == 200:
                data = r.json()
                if data.get("data") or data.get("user"):
                    return self._parse_api_response(data)
            
            return None
        except:
            return None
    
    def _parse_api_response(self, data):
        """Parse RapidAPI response"""
        try:
            # Handle different response formats
            user_data = data.get("data", {}) or data.get("user", {})
            stats_data = data.get("stats", {}) or {}
            
            if not user_data:
                return None
            
            # Extract account ID
            account_id = (
                user_data.get("id") or 
                user_data.get("uid") or 
                user_data.get("userId") or
                "N/A"
            )
            
            result = {
                "platform": "TikTok",
                "account_id": str(account_id),  # ✅ NEW: Account ID
                "username": user_data.get("uniqueId") or user_data.get("name"),
                "full_name": user_data.get("nickname") or user_data.get("displayName") or "N/A",
                "followers": user_data.get("followerCount") or stats_data.get("followerCount") or 0,
                "following": user_data.get("followingCount") or stats_data.get("followingCount") or 0,
                "bio": user_data.get("signature") or user_data.get("description") or "",
                "full_location": user_data.get("region") or user_data.get("country") or "N/A",
                "posts_count": user_data.get("videoCount") or stats_data.get("videoCount") or 0,
                "likes": user_data.get("heartCount") or stats_data.get("heartCount") or 0,
                "is_verified": user_data.get("verified") or False,
                "is_public": not user_data.get("privateAccount", False),
                "is_business_account": user_data.get("businessAccountStatus") or False,
                "external_url": user_data.get("bioLink", {}).get("link") or "N/A" if user_data.get("bioLink") else "N/A",
                "search_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return result if result.get("username") else None
        except:
            return None
    
    def _web_scrape(self, username):
        """Fallback web scraping"""
        try:
            url = f"https://www.tiktok.com/@{username}"
            r = requests.get(url, headers=self.headers, timeout=15)
            
            if r.status_code == 404:
                return {"error": "❌ TikTok user not found"}
            if r.status_code != 200:
                return None
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Extract SIGI_STATE
            script = soup.find("script", id="SIGI_STATE")
            if script:
                try:
                    data = json.loads(script.string)
                    users = data.get("UserModule", {}).get("users", {})
                    stats = data.get("UserModule", {}).get("stats", {})
                    
                    if users:
                        user = list(users.values())[0]
                        stat = list(stats.values())[0] if stats else {}
                        
                        return {
                            "platform": "TikTok",
                            "account_id": user.get("id", "N/A"),  # ✅ NEW: Account ID from web scrape
                            "username": user.get("uniqueId"),
                            "full_name": user.get("nickname", "N/A"),
                            "followers": stat.get("followerCount", 0),
                            "following": stat.get("followingCount", 0),
                            "bio": user.get("signature", ""),
                            "full_location": user.get("region", "N/A"),
                            "posts_count": stat.get("videoCount", 0),
                            "likes": stat.get("heartCount", 0),
                            "is_verified": user.get("verified", False),
                            "is_public": not user.get("privateAccount", False),
                            "is_business_account": user.get("businessAccountStatus", False),
                            "external_url": user.get("bioLink", {}).get("link", "N/A") if user.get("bioLink") else "N/A",
                            "search_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                except:
                    pass
            
            return None
        except:
            return None
