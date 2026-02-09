#!/usr/bin/env python3
"""
Enhanced Instagram Scraper with Account Support
Allows using Instagram account credentials for better performance
"""

import instaloader
import time
import os
import json
from pathlib import Path
from datetime import datetime

class InstagramScraperWithAccount:
    """Instagram scraper with optional account login"""
    
    def __init__(self):
        self.session_dir = Path("./sessions")
        self.session_dir.mkdir(exist_ok=True)
        self.output_dir = Path("./output")
        self.output_dir.mkdir(exist_ok=True)
        self.search_history_file = self.output_dir / "search_history.json"
        self.loader = None
        self.search_history = self.load_search_history()
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour
    
    def load_search_history(self):
        """Load search history"""
        if self.search_history_file.exists():
            try:
                with open(self.search_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_search_history(self):
        """Save search history"""
        try:
            with open(self.search_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.search_history, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def setup_account(self, username, password):
        """Setup Instagram account for better rate limiting"""
        try:
            self.loader = instaloader.Instaloader(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                quiet=True,
                sleep=True
            )
            
            session_file = self.session_dir / f"{username}_session"
            
            # Try loading existing session
            if session_file.exists():
                try:
                    self.loader.load_session_from_file(username, filename=str(session_file))
                    return {"status": "✅ Session loaded successfully"}
                except:
                    pass
            
            # Login and save session
            self.loader.login(username, password)
            self.loader.save_session_to_file(filename=str(session_file))
            
            return {"status": "✅ Account authenticated and session saved"}
        
        except instaloader.exceptions.InvalidCredentialsException:
            return {"error": "❌ Invalid Instagram credentials"}
        except Exception as e:
            return {"error": f"❌ Login failed: {str(e)[:100]}"}
    
    def get_user_info(self, username, timeout=10):
        """Get Instagram user info with timeout"""
        try:
            username = username.lstrip('@')
            
            # Check cache
            cached = self._cache_get(f"instagram:{username}")
            if cached:
                return cached
            
            # Create loader if not exists
            if self.loader is None:
                self.loader = instaloader.Instaloader(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    quiet=True,
                    sleep=False
                )
            
            # Get profile
            profile = self.loader.context.username_to_profile(username)
            
            info = {
                "platform": "Instagram",
                "username": profile.username,
                "full_name": profile.full_name,
                "followers": profile.follower_count,
                "following": profile.followee_count,
                "bio": profile.biography,
                "full_location": getattr(profile, 'city', '') or 'N/A',
                "posts_count": profile.mediacount,
                "is_verified": profile.is_verified,
                "is_public": not profile.is_private,
                "is_business_account": profile.is_business_account,
                "external_url": profile.external_url or "N/A",
                "search_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add account ID if available
            if hasattr(profile, 'userid'):
                info["account_id"] = profile.userid
            
            # Safe attribute access
            if hasattr(profile, 'business_address_json') and profile.business_address_json:
                info["business_address"] = profile.business_address_json.get('address', 'N/A')
            else:
                info["business_address"] = "N/A"
            
            # Auto-save
            self.search_history[username] = info
            self.save_search_history()
            self._cache_set(f"instagram:{username}", info)
            
            return info
        
        except instaloader.exceptions.ProfileNotExistsException:
            return {"error": "❌ Instagram user not found"}
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            return {"error": "❌ This account is private"}
        except instaloader.exceptions.InstaloaderException as e:
            return {"error": f"❌ Instagram error: {str(e)[:80]}"}
        except Exception as e:
            return {"error": f"❌ Error: {str(e)[:80]}"}
    
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
