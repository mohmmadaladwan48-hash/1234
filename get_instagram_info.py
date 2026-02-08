import instaloader
import time
import os
import json
from pathlib import Path

def get_instagram_info(username, retries=5, delay=10, login_user=None, login_pass=None):
    """
    Get Instagram user information including followers, following, bio, region, and account changes.
    Uses session management to avoid rate limiting.
    
    Args:
        username (str): Instagram username to fetch info for
        retries (int): Number of retries on rate limit (default: 5)
        delay (int): Delay in seconds between retries (default: 10)
        login_user (str): Instagram username for login (recommended)
        login_pass (str): Instagram password for login (recommended)
        
    Returns:
        dict: Dictionary containing user info or error message
    """
    # Create loader with optimized settings to avoid rate limiting
    session_dir = Path("./sessions")
    session_dir.mkdir(exist_ok=True)
    
    L = instaloader.Instaloader(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        quiet=False,
        sleep=True
    )
    
    # Try to load saved session or login
    try:
        if login_user:
            session_file = session_dir / login_user
            
            if session_file.exists():
                print(f"🔄 Loading saved session for {login_user}...")
                try:
                    L.load_session_from_file(login_user, filename=str(session_file))
                    print("✅ Session restored!")
                except Exception as e:
                    print(f"⚠️ Session restore failed, logging in again...")
                    L.login(login_user, login_pass)
                    print("✅ Login successful!")
            else:
                print(f"🔐 Logging in as {login_user}...")
                L.login(login_user, login_pass)
                print("✅ Login successful!")
                L.save_session_to_file(filename=str(session_file))
        else:
            print("⚠️ No login provided. This may result in rate limiting.")
            print("Continuing without authentication...\n")
    except Exception as e:
        print(f"⚠️ Authentication failed: {e}")
        print("Attempting to continue without login...\n")

    attempt = 0
    while attempt < retries:
        try:
            profile = instaloader.Profile.from_username(L.context, username)

            # Extract country from business address (if available)
            country = "Not available"
            city = "Not available"
            full_location = "Not available"
            
            try:
                if hasattr(profile, 'business_address_json') and profile.business_address_json:
                    country = profile.business_address_json.get("country") or "Not available"
                    city = profile.business_address_json.get("city") or "Not available"
                    
                    # Build full location string
                    location_parts = []
                    if city != "Not available":
                        location_parts.append(city)
                    if country != "Not available":
                        location_parts.append(country)
                    if location_parts:
                        full_location = ", ".join(location_parts)
            except (AttributeError, TypeError):
                pass  # Location data not available

            # Count name changes
            name_changes = "Not available"
            if hasattr(profile, 'name_changes') and profile.name_changes:
                name_changes = len(profile.name_changes)
            
            data = {
                "username": profile.username,
                "full_name": profile.full_name,
                "followers": f"{profile.followers:,}",
                "following": f"{profile.followees:,}",
                "bio": profile.biography if profile.biography else "No bio set",
                "city": city,
                "country": country,
                "full_location": full_location,
                "posts_count": profile.mediacount,
                "name_changes": name_changes,
                "is_business_account": "✅ Yes" if profile.is_business_account else "❌ No",
                "is_verified": "✅ Yes" if profile.is_verified else "❌ No",
                "is_public": "🌐 Yes" if not profile.is_private else "🔒 No",
                "external_url": profile.external_url if profile.external_url else "Not set",
                "igtv_count": profile.igtvcount if hasattr(profile, 'igtvcount') else "N/A"
            }

            return data

        except Exception as e:
            error_msg = str(e)
            if any(x in error_msg for x in ["401", "Unauthorized", "Please wait", "429", "Too Many Requests"]):
                attempt += 1
                if attempt < retries:
                    wait_time = delay * attempt
                    print(f"⏳ Rate limited. Waiting {wait_time} seconds before retry {attempt}/{retries-1}...")
                    time.sleep(wait_time)
                else:
                    return f"❌ Rate limited by Instagram. Please wait 30-60 minutes, or login with your Instagram account (Instagram credentials are kept private)."
            elif "does not exist" in error_msg.lower() or "not found" in error_msg.lower():
                return f"❌ User '@{username}' not found on Instagram. Check the spelling and try again."
            else:
                return f"❌ Error: {e}"
    
    return f"❌ Failed after {retries} attempts. Please try again later or login with your account."


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("📸 INSTAGRAM ACCOUNT INFO SCRAPER")
    print("=" * 60)
    print("\n💡 TIP: Login with your Instagram account for better results!")
    print("   This avoids rate limiting and gives access to more data.\n")
    
    # Ask if user wants to login
    login_choice = input("Do you want to login with your Instagram account? (yes/no): ").strip().lower()
    
    login_user = None
    login_pass = None
    
    if login_choice in ['yes', 'y']:
        login_user = input("Enter your Instagram username: ").strip()
        login_pass = input("Enter your Instagram password: ").strip()
    
    # Get target username
    username = input("\nEnter the Instagram username to fetch info for: ").strip()
    
    if not username:
        print("❌ Username cannot be empty!")
    else:
        print(f"\nFetching info for: @{username}")
        print("-" * 60)
        
        info = get_instagram_info(username, login_user=login_user, login_pass=login_pass)
        
        if isinstance(info, dict):
            print("\n✅ SUCCESS! Here's the account information:\n")
            for key, value in info.items():
                # Format output nicely
                key_display = key.replace("_", " ").title()
                print(f"  {key_display:<20}: {value}")
        else:
            print(f"\n{info}")
