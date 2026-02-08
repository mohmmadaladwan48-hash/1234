# Instagram Scraper Telegram Bot

A powerful Telegram bot that lets you search Instagram user information and export data to Excel - all from your phone or computer!

## 🚀 Features

✅ **Search Single Users** - Get instant info on any Instagram account  
✅ **Batch Search** - Search multiple users at once  
✅ **Auto-Save** - All searches automatically saved  
✅ **Export to Excel** - Generate professional Excel files with formatting  
✅ **View History** - See all your previous searches  
✅ **Arabic Support** - Perfect display of Arabic names and bios  
✅ **No Login Required** - Works with public accounts  
✅ **Interactive Buttons** - Easy menu navigation  

## 📊 What You Get

For each user:
- Username
- Full Name (with Arabic support)
- Follower Count
- Following Count
- Bio / About
- Location (City & Country)
- Post Count
- Verification Status
- Business Account Status
- Account Privacy Status
- External URL
- Search Timestamp

## 📱 How to Use

### Find Your Bot

1. Open Telegram
2. Search for: **@IGScraper_bot** (or find the bot link in the Telegram group)
3. Click "Start"

### Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see main menu |
| `/lookup` | Search for a single user |
| `/batch` | Search multiple users (comma-separated) |
| `/history` | View all your searches |
| `/export` | Export search history to Excel file |
| `/clear` | Clear your search history |
| `/help` | Show help menu |

### Quick Start

1. **Type a username** - Just send any Instagram username
   ```
   cristiano
   ```

2. **Get instant results** - Bot displays all user info
   ```
   ✅ @cristiano
   👤 Full Name: Cristiano Ronaldo
   👥 Followers: 632,000,000
   ...
   ```

3. **Export anytime** - Click "📥 Export" button or use `/export`

## 💾 File Storage

All files are saved to `/instagram-scraper/output/`:

```
output/
├── search_history.json              (Auto-saved after each search)
├── instagram_search_results.xlsx    (Generated when you export)
└── all_searches.csv                 (Optional CSV export)
```

## 🔧 Running the Bot Locally

### Requirements
- Python 3.9+
- Telegram account

### Installation

```bash
cd /instagram-scraper

# Install dependencies
pip install -r requirements.txt
pip install python-telegram-bot openpyxl instaloader

# Run the bot
python telegram_bot.py
```

### Running 24/7 on Your Server

For continuous operation, use `nohup`:

```bash
nohup python telegram_bot.py > bot.log &
```

Or use `screen`:

```bash
screen -S igbot python telegram_bot.py
```

## 📝 Example Usage

### Single Lookup
```
User: kevin
Bot: 
✅ @kevin
👤 Full Name: Kevin Systrom
👥 Followers: 5,234,567
📝 Bio: Co-founder of Instagram
📊 Posts: 1,234
✓ Verified: ✅ Yes
🌐 Public: 🌐 Yes
```

### Batch Search
```
User: kevin, cristiano, beyonce

Bot:
✅ Batch Search Complete

📊 Results: 3/3 users found

Users fetched:
• @kevin (Kevin Systrom) - 5,234,567 followers
• @cristiano (Cristiano Ronaldo) - 632,000,000 followers
• @beyonce (Beyoncé) - 302,000,000 followers
```

## 🎯 Button Menu

Quick actions available:
- 🔍 **Lookup User** - Search single account
- 📊 **Batch Search** - Search multiple accounts
- 📋 **View History** - See saved searches
- 📥 **Export Excel** - Download data

## ⚠️ Important Notes

- **No Login Required** - Works with public accounts
- **Arabic Support** - Full UTF-8 support for Arabic names
- **Rate Limiting** - Instagram may rate-limit after many requests
- **Privacy** - Respects user privacy and Instagram ToS
- **Data Storage** - Searches stored locally on your server

## 🆘 Troubleshooting

### Bot not responding
- Check if bot is running: `python telegram_bot.py`
- Verify token is correct
- Check internet connection

### "User not found" error
- Check username spelling
- Account may be deleted or suspended
- Try a different account

### Excel file not generated
- Make sure you have searches saved
- Check `/output` folder permissions
- Try `/clear` and search again

## 📞 Bot Details

- **Bot Username**: @IGScraper_bot
- **Token**: `8326472243:AAE-umWaL_3V6Tl6MBcNMifxGwQgfgTHFz4`
- **Type**: Polling-based bot

## 📚 API Information

Uses:
- **Telegram Bot API** - For bot communication
- **instaloader** - For Instagram data
- **openpyxl** - For Excel generation

## 🔐 Security

- Your credentials are **never** saved
- Data only stored locally
- All communication encrypted
- No third-party services

## 📈 Performance

- Fast response time (< 5 seconds per user)
- Handles batch requests efficiently
- Optimized Excel generation
- Low resource usage

## 🎓 Created With

- Python 3.9+
- python-telegram-bot
- instaloader
- openpyxl

---

**Enjoy using Instagram Scraper Bot!** 🚀

For issues or feature requests, please create an issue in the repository.
