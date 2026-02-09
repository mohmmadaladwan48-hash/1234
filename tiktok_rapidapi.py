#!/usr/bin/env python3
"""
TikTok RapidAPI Scraper - Optimized Version
Fast and reliable TikTok user data extraction
"""

import requests
import json
import os
import time
from datetime import datetime

class TikTokRapidAPIScraper:
    """TikTok scraper using RapidAPI"""
    
    def __init__(self):
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY", "")
        self.rapidapi_host = "tiktok-api23.p.rapidapi.com"
        self._cache = {}
        self._cache_ttl = 86400  # 24 hours
    
    def get_user_info(self, username, timeout=12):
        """Get TikTok user info via RapidAPI"""
        try:
            username = username.lstrip('@')
            
            # Check cache
            cached = self._cache_get(f"tiktok:{username}")
            if cached:
                return cached
            
            if not self.rapidapi_key:
                return {"error": "❌ RAPIDAPI_KEY not configured"}
            
            # RapidAPI TikTok endpoint
            url = "https://tiktok-api23.p.rapidapi.com/api/user/info"
            headers = {
                "x-rapidapi-host": self.rapidapi_host,
                "x-rapidapi-key": self.rapidapi_key,
                "accept": "application/json"
            }
            params = {"uniqueId": username}
            
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                info = self._parse_response(data)
                
                if info and "error" not in info:
                    self._cache_set(f"tiktok:{username}", info)
                    return info
            
            if response.status_code == 404:
                return {"error": "❌ TikTok user not found"}
            
            if response.status_code == 429:
                return {"error": "⏱️ RapidAPI rate limit. Try again later."}
            
            return None  # Fallback to web scrape
        
        except requests.Timeout:
            return None  # Fallback
        except:
            return None  # Fallback
    
    def _parse_response(self, data):
        """Parse RapidAPI TikTok response"""
        try:
            if not data:
                return None
            
            # Handle different response structures
            user_data = data.get("data") or data.get("user") or data
            stats = data.get("stats") or {}
            
            if not user_data.get("uniqueId"):
                return None
            
            return {
                "platform": "TikTok",
                "account_id": user_data.get("id") or user_data.get("uid", "N/A"),
                "username": user_data.get("uniqueId"),
                "full_name": user_data.get("nickname") or "N/A",
                "followers": user_data.get("followerCount") or stats.get("followerCount", 0),
                "following": user_data.get("followingCount") or stats.get("followingCount", 0),
                "bio": user_data.get("signature", ""),
                "full_location": user_data.get("region", "N/A"),
                "posts_count": user_data.get("videoCount") or stats.get("videoCount", 0),
                "likes": user_data.get("heartCount") or stats.get("heartCount", 0),
                "is_verified": user_data.get("verified", False),
                "is_public": not user_data.get("privateAccount", False),
                "is_business_account": user_data.get("businessAccountStatus", False),
                "external_url": user_data.get("bioLink", {}).get("link", "N/A") if user_data.get("bioLink") else "N/A",
                "profile_pic": user_data.get("avatarLarger", "N/A"),
                "search_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except:
            return None
    
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
