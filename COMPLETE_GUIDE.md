# Instagram Scraper - Complete Guide

You now have **3 different versions** of an Instagram scraper:

## 📁 Folder Structure

```
instagram-scraper/              (Python - Recommended)
├── get_instagram_info.py       (Simple single-user lookup)
├── advanced_scraper.py         (Advanced: batch, export, sessions)
├── requirements.txt
└── README.md

instagram-scraper-php/          (PHP - Web-based scraping)
├── index.php
├── composer.json
└── README.md

instagram-scraper-nodejs/       (Node.js - Private API)
├── index.js
├── package.json
└── node_modules/
```

---

## 🚀 Quick Start (Python - Recommended)

### Option 1: Simple Single Lookup

```bash
cd /instagram-scraper
python get_instagram_info.py
```

**What it does:**
- Login with your Instagram account (optional)
- Fetch info for one user
- Display followers, following, bio, region, etc.

### Option 2: Advanced Features

```bash
cd /instagram-scraper
python advanced_scraper.py
```

**Features:**
✅ Single account lookup
✅ Batch lookup (multiple users at once)
✅ Export to JSON
✅ Export to CSV
✅ Session caching (save login)

---

## 📊 What You Can Get

### Basic Info
- Username
- Full Name
- Follower Count
- Following Count
- Bio / About
- Post Count
- Website URL

### Advanced Info
- City
- Country
- Full Location
- Verification Status (✅ Verified)
- Business Account Status
- Account Privacy (🔒 Private / 🌐 Public)
- Profile Picture URL
- Name Change Count
- IGTV Count

---

## 🔐 Authentication

### Why Login?
- ✅ Avoid rate limiting
- ✅ Access private account info (if you follow them)
- ✅ Get full location data
- ✅ Better reliability

### How It Works
1. First time: You enter credentials, they're saved
2. Subsequent runs: Automatically uses saved session
3. Sessions stored in `./sessions/` folder
4. Your credentials are **never** saved, only the session

---

## 📈 Batch Lookup Example

Fetch info for 100+ accounts:

```python
usernames = [
    "kevin",
    "cristiano",
    "beyonce",
    "instagram"
]

for user in usernames:
    info = scraper.get_user_info(user)
    results.append(info)

# Export all to CSV
scraper.export_to_csv(results, "accounts.csv")
```

---

## 💾 Export Formats

### JSON Export
```json
{
  "username": "kevin",
  "full_name": "Kevin Systrom",
  "followers": "5,234,567",
  "following": "234",
  "bio": "Co-founder of Instagram",
  "country": "United States",
  "city": "San Francisco",
  "is_verified": "✅ Yes"
}
```

### CSV Export
```csv
username,full_name,followers,following,bio,country,city
kevin,Kevin Systrom,5234567,234,Co-founder of Instagram,United States,San Francisco
```

---

## ⚠️ Important Notes

### Rate Limiting
- If you hit rate limits, **wait 30-60 minutes**
- Login helps avoid this
- Use delays between requests for batch operations

### Terms of Service
- Use responsibly
- Don't overload Instagram servers
- Respect user privacy
- Follow Instagram's ToS

### Limitations
- Private accounts need login + being a follower
- Some data only available with login
- Instagram may block aggressive scraping

---

## 🆘 Troubleshooting

### "Rate limited" Error
**Solution:** Wait 30 minutes, then try again with login

### "User not found"
**Solution:** Check the username spelling

### "Login failed"
**Solution:** 
- Verify username/password
- Check for 2FA enabled (may block scraping)
- Instagram may have temporarily blocked your IP

### "Permission denied for regions"
**Solution:** Login with your account to get region data

---

## 📚 Python API Reference

### Simple Usage

```python
from get_instagram_info import get_instagram_info

# Without login (public accounts only)
info = get_instagram_info("kevin")
print(info)

# With login
info = get_instagram_info("kevin", login_user="your_username", login_pass="your_password")
```

### Advanced Usage

```python
from advanced_scraper import InstagramInfoScraper

scraper = InstagramInfoScraper()

# Login
scraper.login("your_username", "your_password")

# Fetch single user
info = scraper.get_user_info("kevin")

# Export to JSON
scraper.export_to_json(info, "kevin")

# Batch fetch
users = ["kevin", "cristiano", "beyonce"]
results = [scraper.get_user_info(user) for user in users]

# Export to CSV
scraper.export_to_csv(results, "accounts.csv")
```

---

## 🔗 Comparison

| Feature | Simple | Advanced |
|---------|--------|----------|
| Single lookup | ✅ | ✅ |
| Batch lookup | ❌ | ✅ |
| Export JSON | ❌ | ✅ |
| Export CSV | ❌ | ✅ |
| Session save | ✅ | ✅ |
| Interactive menu | ✅ | ✅ |

---

## 🎯 Use Cases

1. **Marketing Research** - Analyze competitor accounts
2. **Data Collection** - Gather stats on multiple accounts
3. **Personal Archive** - Back up your favorite accounts' info
4. **Analytics** - Track account growth over time
5. **Verification** - Check if an account exists

---

## 📞 Support

Need help? The library documentation:
- **Python (instaloader)**: https://instaloader.github.io
- **Node.js**: https://docs.igpapi.com

---

**Last Updated:** February 8, 2026
**Version:** 1.0
**Status:** ✅ Ready to Use
