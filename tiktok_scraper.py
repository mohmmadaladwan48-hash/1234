#!/usr/bin/env python3
"""
TikTok OSINT Scraper Module
Comprehensive TikTok user analysis with advanced features
"""

import requests
import json
import re
import os
import time
from bs4 import BeautifulSoup
from datetime import datetime

class TikTokScraper:
    def __init__(self):
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY", "")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.tiktok.com/"
        }
        self._cache = {}
        self._cache_ttl = 86400  # 24 hours
    
    def get_user_info(self, username):
        """Get TikTok user info with comprehensive analysis"""
        try:
            username = username.lstrip('@')
            
            # Check cache first
            cached = self._cache_get(f"tiktok:{username}")
            if cached:
                return cached
            
            # Try web scrape first
            info = self._web_scrape(username)
            if info and "error" not in info:
                # Add analysis
                info = self._enhance_info(info, username)
                self._cache_set(f"tiktok:{username}", info)
                return info
            
            # Fallback to API
            if self.rapidapi_key:
                info = self._api_scrape(username)
                if info and "error" not in info:
                    info = self._enhance_info(info, username)
                    self._cache_set(f"tiktok:{username}", info)
                    return info
            
            return {"error": "❌ Could not fetch TikTok user info. User may not exist."}
        
        except Exception as e:
            return {"error": f"❌ TikTok error: {str(e)[:100]}"}
    
    def _cache_get(self, key):
        """Retrieve from cache if fresh"""
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
            
            # Try SIGI_STATE script
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
                            "is_public": not user.get("privateAccount", False),
                            "is_business_account": user.get("businessAccountStatus", False),
                            "external_url": user.get("bioLink", {}).get("link", "N/A") if user.get("bioLink") else "N/A",
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
        except:
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
        """Scrape via RapidAPI"""
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
    
    def _enhance_info(self, info, username):
        """Enhance info with advanced analysis"""
        if "error" in info:
            return info
        
        bio = info.get("bio", "")
        
        # Extract socials from bio
        socials = self._extract_socials(bio)
        info["linked_accounts"] = socials
        
        # Extract contacts
        contacts = self._extract_contacts(bio)
        info["contacts"] = contacts
        
        # Extract hashtags
        hashtags = self._extract_hashtags(bio, username)
        info["hashtags"] = hashtags
        
        # Extract location from bio
        location = self._extract_location(bio)
        if location:
            info["bio_location"] = location
        
        # Calculate engagement
        followers = info.get("followers", 0)
        following = info.get("following", 0)
        likes = info.get("likes", 0)
        posts = info.get("posts_count", 0)
        
        if posts > 0:
            info["avg_likes_per_post"] = round(likes / posts, 2)
        if followers > 0 and posts > 0:
            info["engagement_rate"] = round((likes / (followers * posts) * 100), 2)
        
        return info
    
    def _extract_socials(self, bio):
        """Extract social media links from bio"""
        socials = {}
        if not bio:
            return socials
        
        patterns = {
            'instagram': r'@([a-zA-Z0-9._]{1,30})|instagram\.com/([a-zA-Z0-9._]{1,30})',
            'youtube': r'youtube\.com/@?([a-zA-Z0-9_-]+)',
            'twitter': r'twitter\.com/([a-zA-Z0-9_]+)|x\.com/([a-zA-Z0-9_]+)',
            'snapchat': r'snapchat[\s:]*([a-zA-Z0-9._-]+)',
            'discord': r'discord(?:\.gg|\.com)?[/\s]*([a-zA-Z0-9]+)',
            'telegram': r't\.me/([a-zA-Z0-9_]+)|telegram[/\s]*([a-zA-Z0-9_]+)'
        }
        
        for platform, pattern in patterns.items():
            match = re.search(pattern, bio, re.IGNORECASE)
            if match:
                handle = match.group(1) or (match.group(2) if match.lastindex >= 2 else None)
                if handle:
                    socials[platform] = handle
        
        return socials
    
    def _extract_contacts(self, bio):
        """Extract email and phone from bio"""
        contacts = {}
        if not bio:
            return contacts
        
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', bio)
        if email_match:
            contacts['email'] = email_match.group(1)
        
        phone_match = re.search(r'(\+?1?\s*[-.\(]?\d{3}[-.\)]?\s*\d{3}[-.]?\d{4}|\+\d{1,3}\s?\d{6,14})', bio)
        if phone_match:
            contacts['phone'] = phone_match.group(1)
        
        return contacts
    
    def _extract_hashtags(self, bio, username=""):
        """Extract hashtags from bio and username"""
        text = (bio or "") + " " + (username or "")
        tags = re.findall(r'#([a-zA-Z0-9_]+)', text)
        return list(set(tags))
    
    def _extract_location(self, bio):
        """Extract location from bio"""
        if not bio:
            return None
        
        patterns = [
            r'📍\s*([^\n]+)',
            r'🌍\s*([^\n]+)',
            r'📌\s*([^\n]+)',
            r'Location:\s*([^\n,]+)',
            r'From:\s*([^\n,]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, bio)
            if match:
                location = match.group(1).strip()
                if location and len(location) > 1:
                    return location
        
        return None
