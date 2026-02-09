#!/usr/bin/env python3
"""
Instagram Scraper Telegram Bot
Fetch Instagram user information and export to Excel via Telegram
"""

import logging
import time
import re
import asyncio
import os
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ChatAction
from advanced_scraper import InstagramInfoScraper
from tiktok_scraper import TikTokScraper

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============ UTILITY FUNCTIONS ============

def get_scraper(context):
    """Get user-isolated scraper instance"""
    if "scraper" not in context.user_data:
        context.user_data["scraper"] = InstagramInfoScraper()
    return context.user_data["scraper"]


def can_search(context, cooldown=5):
    """Rate limiting - prevent spam"""
    last = context.user_data.get("last_search", 0)
    now = time.time()
    if now - last < cooldown:
        return False
    context.user_data["last_search"] = now
    return True


def valid_username(username: str) -> bool:
    """Validate Instagram username format"""
    return bool(re.fullmatch(r"[a-zA-Z0-9._]{1,30}", username))


def format_user_info(info: dict) -> str:
    """Format user info for display (DRY principle)"""
    return f"""
✅ *@{info.get('username', 'N/A')}*

👤 *Full Name:* {info.get('full_name', 'N/A')}
👥 *Followers:* {info.get('followers', 'N/A')}
📤 *Following:* {info.get('following', 'N/A')}
📝 *Bio:* {info.get('bio', 'N/A')}
📍 *Location:* {info.get('full_location', 'N/A')}
📊 *Posts:* {info.get('posts_count', 'N/A')}
✓ *Verified:* {info.get('is_verified', 'N/A')}
🌐 *Public:* {info.get('is_public', 'N/A')}
🏢 *Business:* {info.get('is_business_account', 'N/A')}
🔗 *URL:* {info.get('external_url', 'N/A')}
🕐 *Search Time:* {info.get('search_timestamp', 'N/A')}
"""


def infer_account_origin(info: dict) -> dict:
    """Infer account origin from available data (estimation only)"""
    hints = []
    
    bio = info.get("bio", "").lower()
    if any(k in bio for k in ["ksa", "saudi", "egypt", "uae", "dubai", "middle east", "مصر", "السعودية"]):
        hints.append("📌 Bio mentions location keyword")
    
    url = info.get("external_url")
    if url and "." in url:
        try:
            tld = url.split(".")[-1].lower()
            if len(tld) == 2:
                hints.append(f"🌐 Website TLD: .{tld}")
        except:
            pass
    
    if info.get("is_business_account"):
        hints.append("💼 Business account detected")
    
    return {
        "origin": hints or ["🤷 Unknown (not enough data)"],
        "confidence": "⚠️ Low (estimated, not official)"
    }


def estimate_account_age(posts_count, followers):
    """Estimate account age based on activity"""
    try:
        posts = int(posts_count) if posts_count else 0
        
        if posts < 10:
            return "Very New / Low Activity"
        if posts < 50:
            return "New (< 50 posts)"
        if posts < 200:
            return "Somewhat Established (50-200 posts)"
        if posts < 500:
            return "Established (200-500 posts)"
        return "Very Active / Old (500+ posts)"
    except:
        return "Unknown"

# ============ END UTILITY FUNCTIONS ============

# Initialize scraper
scraper = InstagramInfoScraper()

# User sessions
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when /start is issued."""
    user_id = update.effective_user.id
    user_sessions[user_id] = {'searches': []}
    
    welcome_text = """
🎉 *Welcome to Social Media Scraper Bot!* 🎉

I can help you fetch user information from Instagram and TikTok, then export data to Excel.

📋 *Choose your platform:*
    """
    
    keyboard = [
        [InlineKeyboardButton("📸 Instagram", callback_data='platform_instagram'),
         InlineKeyboardButton("🎵 TikTok", callback_data='platform_tiktok')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when /help is issued."""
    help_text = """
📚 *Bot Commands Help*

🔍 */lookup* - Search single Instagram user
   • Reply with username when prompted
   • Get followers, bio, location, and more

📊 */batch* - Search multiple users
   • Enter usernames separated by commas
   • Results saved automatically

📋 */history* - View all your searches
   • Shows usernames, names, followers

📥 */export* - Export search history
   • Creates Excel file with all data
   • Download and share easily

🗑️ */clear* - Clear search history
   • Removes all saved searches

💡 *Tips:*
• All searches are auto-saved
• Arabic names display correctly
• Excel files are nicely formatted
• No login required!

Need more help? Just send a username!
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {'searches': []}
    
    # Platform selection
    if query.data == 'platform_instagram':
        await query.answer()
        context.user_data['platform'] = 'instagram'
        keyboard = [
            [InlineKeyboardButton("🔍 Lookup User", callback_data='lookup'),
             InlineKeyboardButton("📊 Batch Search", callback_data='batch')],
            [InlineKeyboardButton("📋 View History", callback_data='history'),
             InlineKeyboardButton("📥 Export Excel", callback_data='export')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📸 *Instagram Mode Selected*\n\nChoose an action:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'platform_tiktok':
        await query.answer()
        context.user_data['platform'] = 'tiktok'
        keyboard = [
            [InlineKeyboardButton("🔍 Lookup User", callback_data='lookup'),
             InlineKeyboardButton("📊 Batch Search", callback_data='batch')],
            [InlineKeyboardButton("📋 View History", callback_data='history'),
             InlineKeyboardButton("📥 Export Excel", callback_data='export')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎵 *TikTok Mode Selected*\n\nChoose an action:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'lookup':
        await query.answer()
        context.user_data['mode'] = 'lookup'
        platform = context.user_data.get('platform', 'instagram')
        await query.edit_message_text(f"📱 Send me the {platform.capitalize()} username you want to lookup:")
    
    elif query.data == 'batch':
        await query.answer()
        context.user_data['mode'] = 'batch'
        platform = context.user_data.get('platform', 'instagram')
        await query.edit_message_text(f"📱 Send me {platform.capitalize()} usernames separated by commas (e.g., user1, user2, user3):")
    
    elif query.data == 'history':
        await query.answer()
        await show_history(query, user_id)
    
    elif query.data == 'export':
        await query.answer()
        await export_to_excel(query, user_id)


async def lookup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /lookup command"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {'searches': []}
    
    context.user_data['mode'] = 'lookup'
    await update.message.reply_text("📱 Send me the Instagram username to lookup:")


async def batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /batch command"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {'searches': []}
    
    context.user_data['mode'] = 'batch'
    await update.message.reply_text("📱 Send me usernames separated by commas (e.g., user1, user2, user3):")


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show search history"""
    user_id = update.effective_user.id
    await show_history(update, user_id)


async def show_history(update, user_id) -> None:
    """Display search history"""
    if scraper.search_history:
        history_text = f"📋 *Search History* ({len(scraper.search_history)} users)\n\n"
        
        for i, (username, data) in enumerate(scraper.search_history.items(), 1):
            full_name = data.get('full_name', 'N/A')
            followers = data.get('followers', 'N/A')
            timestamp = data.get('search_timestamp', 'N/A')
            history_text += f"{i}. @{username}\n"
            history_text += f"   👤 {full_name}\n"
            history_text += f"   👥 {followers} followers\n"
            history_text += f"   🕐 {timestamp}\n\n"
        
        if hasattr(update, 'edit_message_text'):
            await update.edit_message_text(history_text, parse_mode='Markdown')
        else:
            await update.message.reply_text(history_text, parse_mode='Markdown')
    else:
        text = "❌ No search history found yet."
        if hasattr(update, 'edit_message_text'):
            await update.edit_message_text(text)
        else:
            await update.message.reply_text(text)


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /export command"""
    user_id = update.effective_user.id
    await export_to_excel(update, user_id)


async def export_to_excel(update, user_id) -> None:
    """Export search history to Excel"""
    scraper = get_scraper(update.callback_query.message._bot.get_chat(user_id) if hasattr(update, 'callback_query') else None)
    
    # For button callback
    if hasattr(update, 'callback_query'):
        chat = update.callback_query.message.chat
        message = update.callback_query.message
    else:
        chat = update.effective_chat
        message = update.message
    
    # This is a bit tricky - we need context to get scraper
    # Use the global scraper if available
    if not scraper.search_history:
        text = "❌ No searches to export. Search for some users first!"
        if hasattr(update, 'edit_message_text'):
            await update.edit_message_text(text)
        else:
            await message.reply_text(text)
        return
    
    try:
        # Show progress
        if hasattr(update, 'edit_message_text'):
            await update.edit_message_text("⏳ Generating Excel file...")
        else:
            await message.reply_text("⏳ Generating Excel file...")
        
        # Generate Excel with unique filename
        excel_path = scraper.export_search_history_to_excel()
        
        if excel_path and os.path.exists(excel_path):
            # Create unique filename
            unique_filename = f"instagram_{user_id}_{int(time.time())}.xlsx"
            
            # Send file
            with open(excel_path, 'rb') as excel_file:
                await chat.send_document(
                    document=excel_file,
                    caption=f"✅ Excel file with {len(scraper.search_history)} users",
                    filename=unique_filename
                )
            
            # Cleanup
            try:
                os.remove(excel_path)
            except:
                pass
        else:
            await message.reply_text("❌ Failed to create Excel file")
    
    except TimeoutError:
        await message.reply_text("⏱ Export timeout. Please try again.")
    except Exception as e:
        logger.exception("Export error")
        await message.reply_text("❌ Export failed. Please try again.")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear search history"""
    scraper.search_history = {}
    scraper.save_search_history()
    await update.message.reply_text("🗑️ Search history cleared!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages"""
    user_id = update.effective_user.id
    user_text = update.message.text.strip()
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {'searches': []}
    
    mode = context.user_data.get('mode', None)
    platform = context.user_data.get('platform', 'instagram')
    
    if mode == 'lookup':
        # Single lookup
        if not valid_username(user_text):
            await update.message.reply_text("❌ Invalid username. Use only letters, numbers, dots, and underscores.")
            return
        
        if not can_search(context, cooldown=5):
            await update.message.reply_text("⏳ Please wait a few seconds before searching again.")
            return
        
        await update.message.chat.send_action(ChatAction.TYPING)
        
        if platform == 'tiktok':
            tiktok_scraper = TikTokScraper()
            info = tiktok_scraper.get_user_info(user_text)
        else:
            scraper = get_scraper(context)
            try:
                # Use timeout for Instagram to prevent slowdown (max 10 seconds)
                info = await asyncio.wait_for(
                    asyncio.to_thread(scraper.get_user_info, user_text),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                info = {"error": "⏱️ Instagram lookup timed out (took too long). Try again later or use TikTok."}
        
        if isinstance(info, dict) and "error" not in info:
            response = format_user_info(info)
            
            if platform == 'instagram':
                # Add origin inference for Instagram
                origin = infer_account_origin(info)
                origin_text = "\n".join(f"{h}" for h in origin["origin"])
                response += f"\n🌍 *Estimated Origin:*\n{origin_text}\n_{origin['confidence']}_"
                
                # Add account age
                age = estimate_account_age(info.get('posts_count', 0), info.get('followers', 0))
                response += f"\n\n📅 *Account Age Estimate:* {age}"
            
            keyboard = [
                [InlineKeyboardButton("🔍 Search Another", callback_data='lookup'),
                 InlineKeyboardButton("📋 View History", callback_data='history')],
                [InlineKeyboardButton("📥 Export", callback_data='export')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            error_msg = info.get("error", "❌ User not found.")
            await update.message.reply_text(error_msg)
        
        context.user_data['mode'] = None
    
    elif mode == 'batch':
        # Batch lookup
        if not can_search(context, cooldown=10):
            await update.message.reply_text("⏳ Please wait before starting another batch search.")
            return
        
        usernames = [u.strip() for u in user_text.split(',')]
        usernames = [u for u in usernames if valid_username(u)]
        
        if not usernames:
            await update.message.reply_text("❌ No valid usernames found.")
            return
        
        await update.message.chat.send_action(ChatAction.TYPING)
        await update.message.reply_text(f"🔍 Searching {len(usernames)} users...")
        
        if platform == 'tiktok':
            tiktok_scraper = TikTokScraper()
            # Async batch search
            try:
                tasks = [
                    asyncio.to_thread(tiktok_scraper.get_user_info, u)
                    for u in usernames
                ]
                results = await asyncio.gather(*tasks)
                results = [r for r in results if isinstance(r, dict) and "error" not in r]
            except TimeoutError:
                await update.message.reply_text("⏱ Search timeout. TikTok took too long to respond.")
                context.user_data['mode'] = None
                return
        else:
            scraper = get_scraper(context)
            try:
                tasks = [
                    asyncio.to_thread(scraper.get_user_info, u)
                    for u in usernames
                ]
                results = await asyncio.gather(*tasks)
                results = [r for r in results if isinstance(r, dict)]
            except TimeoutError:
                await update.message.reply_text("⏱ Search timeout. Instagram took too long to respond.")
                context.user_data['mode'] = None
                return
        
        # Summary
        summary = f"""
✅ *Batch Search Complete*

📊 Results: {len(results)}/{len(usernames)} users found

Users fetched:
        """
        
        for result in results:
            summary += f"\n• @{result.get('username', 'N/A')} ({result.get('full_name', 'N/A')}) - {result.get('followers', 0)} followers"
        
        keyboard = [
            [InlineKeyboardButton("📥 Export to Excel", callback_data='export'),
             InlineKeyboardButton("📋 View History", callback_data='history')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(summary, parse_mode='Markdown', reply_markup=reply_markup)
        context.user_data['mode'] = None
    
    else:
        # Default: ask for platform if not selected
        if 'platform' not in context.user_data:
            keyboard = [
                [InlineKeyboardButton("📸 Instagram", callback_data='platform_instagram'),
                 InlineKeyboardButton("🎵 TikTok", callback_data='platform_tiktok')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Please select a platform first:", reply_markup=reply_markup)
            return
        
        # Treat as username lookup
        if not valid_username(user_text):
            await update.message.reply_text("❌ Invalid username. Use only letters, numbers, dots, and underscores.")
            return
        
        if not can_search(context, cooldown=5):
            await update.message.reply_text("⏳ Please wait a few seconds before searching again.")
            return
        
        await update.message.chat.send_action(ChatAction.TYPING)
        
        if platform == 'tiktok':
            tiktok_scraper = TikTokScraper()
            info = tiktok_scraper.get_user_info(user_text)
        else:
            scraper = get_scraper(context)
            try:
                # Use timeout for Instagram to prevent slowdown (max 10 seconds)
                info = await asyncio.wait_for(
                    asyncio.to_thread(scraper.get_user_info, user_text),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                info = {"error": "⏱️ Instagram lookup timed out (took too long). Try again later or use TikTok."}
        
        if isinstance(info, dict) and "error" not in info:
            response = format_user_info(info)
            
            if platform == 'instagram':
                origin = infer_account_origin(info)
                origin_text = "\n".join(f"{h}" for h in origin["origin"])
                response += f"\n\n🌍 *Estimated Origin:*\n{origin_text}\n_{origin['confidence']}_"
                
                age = estimate_account_age(info.get('posts_count', 0), info.get('followers', 0))
                response += f"\n\n📅 *Account Age Estimate:* {age}"
            
            keyboard = [
                [InlineKeyboardButton("🔍 Search Another", callback_data='lookup'),
                 InlineKeyboardButton("📥 Export", callback_data='export')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            error_msg = info.get("error", "❌ User not found.")
            await update.message.reply_text(error_msg)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors with specific error types"""
    logger.error(f'Update {update} caused error {context.error}')
    
    error = context.error
    
    try:
        if isinstance(error, TimeoutError):
            error_msg = "⏱ Request timeout. Instagram took too long to respond. Please try again."
        elif isinstance(error, ValueError):
            error_msg = "❌ Invalid input. Please check your request."
        else:
            error_msg = "❌ An unexpected error occurred. Please try again or use /help"
        
        if update and update.effective_message:
            await update.effective_message.reply_text(error_msg)
    except:
        logger.exception("Failed to send error message")


def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lookup", lookup_command))
    application.add_handler(CommandHandler("batch", batch_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("export", export_command))
    application.add_handler(CommandHandler("clear", clear_command))

    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))

    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    print("🤖 Telegram Bot started!")
    print("✅ Bot is running and waiting for messages...")
    print("📞 Bot Token: 8326472243:AAE-umWaL_3V6Tl6MBcNMifxGwQgfgTHFz4")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

