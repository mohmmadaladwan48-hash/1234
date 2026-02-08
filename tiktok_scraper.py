#!/usr/bin/env python3
"""
TikTok Scraper Module
Fetch TikTok user information
"""

import requests
import json
import re
import os
from bs4 import BeautifulSoup
from datetime import datetime

class TikTokScraper:
    def __init__(self):
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY", "")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def get_user_info(self, username):
        """Get TikTok user info"""
        try:
            # Remove @ if present
            username = username.lstrip('@')
            
            # Web scrape first (no API key needed)
            info = self._web_scrape(username)
            if info:
                return info
            
            # Fallback to API if available
            if self.rapidapi_key and self.rapidapi_key != "":
                info = self._api_scrape(username)
                if info:
                    return info
            
            return {"error": "❌ Could not fetch TikTok user info. User may not exist."}
        
        except Exception as e:
            return {"error": f"❌ TikTok error: {str(e)[:100]}"}
    
    def _web_scrape(self, username):
        """Scrape TikTok profile via web"""
        try:
            url = f"https://www.tiktok.com/@{username}"
            
            r = requests.get(url, headers=self.headers, timeout=15)
            
            if r.status_code == 404:
                return {"error": "❌ TikTok user not found"}
            
            if r.status_code != 200:
                return None
            
            soup = BeautifulSoup(r.text, "html.parser")
            
            # Look for SIGI_STATE script
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
                            "username": user.get("uniqueId"),
                            "full_name": user.get("nickname", "N/A"),
                            "followers": stat.get("followerCount", 0),
                            "following": stat.get("followingCount", 0),
                            "bio": user.get("signature", ""),
                            "full_location": user.get("region", "N/A"),
                            "posts_count": stat.get("videoCount", 0),
                            "likes": stat.get("heartCount", 0),
                            "is_verified": user.get("verified", False),
                            "is_public": True,
                            "is_business_account": user.get("businessAccountStatus", False),
                            "external_url": user.get("bioLink", {}).get("link", "N/A"),
                            "search_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                except:
                    pass
            
            # Fallback: parse from meta tags
            meta_data = self._parse_meta_tags(soup)
            if meta_data.get('username'):
                return {
                    "platform": "TikTok",
                    "username": meta_data.get('username'),
                    "full_name": meta_data.get('full_name', 'N/A'),
                    "followers": meta_data.get('followers', 0),
                    "following": meta_data.get('following', 0),
                    "bio": meta_data.get('bio', ''),
                    "full_location": meta_data.get('location', 'N/A'),
                    "posts_count": meta_data.get('posts', 0),
                    "likes": meta_data.get('likes', 0),
                    "is_verified": meta_data.get('verified', False),
                    "is_public": True,
                    "is_business_account": False,
                    "external_url": "N/A",
                    "search_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            return None
        
        except Exception as e:
            return None
    
    def _parse_meta_tags(self, soup):
        """Extract data from meta tags"""
        meta_data = {}
        scripts = soup.find_all("script")
        
        for script in scripts:
            if script.string and '"uniqueId"' in script.string:
                try:
                    match = re.search(r'"uniqueId":"([^"]+)"', script.string)
                    if match:
                        meta_data['username'] = match.group(1)
                    
                    match = re.search(r'"nickname":"([^"]+)"', script.string)
                    if match:
                        meta_data['full_name'] = match.group(1)
                    
                    match = re.search(r'"followerCount":(\d+)', script.string)
                    if match:
                        meta_data['followers'] = int(match.group(1))
                    
                    match = re.search(r'"followingCount":(\d+)', script.string)
                    if match:
                        meta_data['following'] = int(match.group(1))
                    
                    match = re.search(r'"heartCount":(\d+)', script.string)
                    if match:
                        meta_data['likes'] = int(match.group(1))
                    
                    match = re.search(r'"videoCount":(\d+)', script.string)
                    if match:
                        meta_data['posts'] = int(match.group(1))
                    
                    match = re.search(r'"verified":([^,}]+)', script.string)
                    if match:
                        meta_data['verified'] = match.group(1).lower() == 'true'
                
                except:
                    pass
        
        return meta_data
    
    def _api_scrape(self, username):
        """Scrape via RapidAPI (optional, requires API key)"""
        try:
            url = "https://tiktok-api23.p.rapidapi.com/api/user/info"
            headers = {
                "x-rapidapi-host": "tiktok-api23.p.rapidapi.com",
                "x-rapidapi-key": self.rapidapi_key,
                "accept": "application/json"
            }
            params = {"uniqueId": username}
            
            r = requests.get(url, headers=headers, params=params, timeout=10)
            
            if r.status_code != 200:
                return None
            
            data = r.json()
            user = data.get("user", {})
            stats = data.get("stats", {})
            
            return {
                "platform": "TikTok",
                "username": user.get("uniqueId"),
                "full_name": user.get("nickname", "N/A"),
                "followers": stats.get("followerCount", 0),
                "following": stats.get("followingCount", 0),
                "bio": user.get("signature", ""),
                "full_location": user.get("region", "N/A"),
                "posts_count": stats.get("videoCount", 0),
                "likes": stats.get("heartCount", 0),
                "is_verified": user.get("verified", False),
                "is_public": True,
                "is_business_account": False,
                "external_url": "N/A",
                "search_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        except:
            return None
