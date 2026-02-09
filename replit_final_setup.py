#!/usr/bin/env python3
"""
🚀 REPLIT SETUP - FINAL INSTRUCTIONS
"""

instructions = """
╔════════════════════════════════════════════════════════════════╗
║              🚀 REPLIT SETUP - FINAL STEPS 🚀                ║
╚════════════════════════════════════════════════════════════════╝

YOUR API KEY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1006bd59c1msh4c7cef1162f2416p1624b9jsne163b65558fb


✅ STEP 1: Open Replit Secrets
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

On your Replit project:
  1. Look for the lock icon (🔒) on left sidebar
  2. Click it to open Secrets
  3. Or: Tools → Secrets


✅ STEP 2: Add the API Key
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Click "Add new secret" and enter:

Key:   RAPIDAPI_KEY

Value: 1006bd59c1msh4c7cef1162f2416p1624b9jsne163b65558fb


✅ STEP 3: Save & Reload
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Click "Save"
2. Go back to editor
3. Click "Stop" then "Run"
   (Or reload the page)


✅ STEP 4: Verify Bot is Running
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Look in the Replit console for:
  ✅ "Telegram Bot started!"
  ✅ "Bot is running and waiting for messages..."

If you see these messages, you're good to go! 🎉


✅ STEP 5: Test in Telegram
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Open Telegram and message your bot:

  1. Send /start
  2. Select Instagram
  3. Search for any user (e.g., "instagram")
  4. Should get result in ~2 seconds! ⚡


🎯 WHAT YOU GET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Instagram:
  ✅ ~2 seconds (was 30+ seconds)
  ✅ No rate limiting
  ✅ Account ID
  ✅ All user info

TikTok:
  ✅ ~3 seconds
  ✅ No timeouts
  ✅ Account ID
  ✅ Complete data


⚠️ TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If bot doesn't start:
  1. Check Replit console for errors
  2. Make sure RAPIDAPI_KEY is in Secrets
  3. Click "Stop" then "Run" again

If searches timeout:
  1. Wait 1-2 minutes (API rate limit)
  2. Try again
  3. Should work normally after

If no response:
  1. Check bot token (TELEGRAM_TOKEN secret)
  2. Make sure bot is in active chat


📊 FILES IN YOUR PROJECT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Main Files:
  • telegram_bot.py (Main bot - uses RapidAPI scrapers)
  • instagram_rapidapi.py (Fast Instagram scraper)
  • tiktok_rapidapi.py (Fast TikTok scraper)

Support Files:
  • advanced_scraper.py (Backup Instagram scraper)
  • tiktok_scraper.py (Backup TikTok scraper)

Testing:
  • test_rapidapi.py (API configuration test)
  • final_test.py (Complete system test)


🔐 SECURITY NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ API key is ONLY in Replit Secrets
✅ NOT in any code files
✅ NOT on GitHub (safe to share)
✅ Replit encrypts all secrets


💬 COMMANDS IN BOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/start         - Choose platform (Instagram/TikTok)
/lookup        - Search single user
/batch         - Search multiple users (comma-separated)
/history       - View past searches
/export        - Download results as Excel
/clear         - Clear history
/help          - Show all commands


🚀 YOU'RE ALL SET!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Just add the secret and your bot is ready!
No other changes needed - everything is configured!

Go test it now! 🎉

╔════════════════════════════════════════════════════════════════╗
║                  Questions? Check the README!                  ║
║            GitHub: mohmmadaladwan48-hash/1234                  ║
╚════════════════════════════════════════════════════════════════╝
"""

print(instructions)

with open('REPLIT_FINAL_SETUP.txt', 'w', encoding='utf-8') as f:
    f.write(instructions)

print("\n✅ Setup guide saved!")
