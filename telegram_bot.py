#!/usr/bin/env python3
"""
Instagram Scraper Telegram Bot
Fetch Instagram user information and export to Excel via Telegram
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ChatAction
import os
from pathlib import Path
from advanced_scraper import InstagramInfoScraper

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize scraper
scraper = InstagramInfoScraper()

# User sessions
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when /start is issued."""
    user_id = update.effective_user.id
    user_sessions[user_id] = {'searches': []}
    
    welcome_text = """
🎉 *Welcome to Instagram Scraper Bot!* 🎉

I can help you fetch Instagram user information and export data to Excel.

📋 *Available Commands:*
• /lookup - Search for a single user
• /batch - Search multiple users at once
• /history - View your search history
• /export - Export search history to Excel
• /clear - Clear your search history
• /help - Show help menu

🚀 Let's get started!
    """
    
    keyboard = [
        [InlineKeyboardButton("🔍 Lookup User", callback_data='lookup'),
         InlineKeyboardButton("📊 Batch Search", callback_data='batch')],
        [InlineKeyboardButton("📋 View History", callback_data='history'),
         InlineKeyboardButton("📥 Export Excel", callback_data='export')]
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
    
    if query.data == 'lookup':
        await query.answer()
        context.user_data['mode'] = 'lookup'
        await query.edit_message_text("📱 Send me the Instagram username you want to lookup:")
    
    elif query.data == 'batch':
        await query.answer()
        context.user_data['mode'] = 'batch'
        await query.edit_message_text("📱 Send me usernames separated by commas (e.g., user1, user2, user3):")
    
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
    if not scraper.search_history:
        text = "❌ No searches to export. Search for some users first!"
        if hasattr(update, 'edit_message_text'):
            await update.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return
    
    try:
        # Show progress
        if hasattr(update, 'edit_message_text'):
            await update.edit_message_text("⏳ Generating Excel file...")
        else:
            await update.message.reply_text("⏳ Generating Excel file...")
        
        # Generate Excel
        excel_path = scraper.export_search_history_to_excel()
        
        if excel_path and os.path.exists(excel_path):
            # Send file
            with open(excel_path, 'rb') as excel_file:
                await update.effective_chat.send_document(
                    document=excel_file,
                    caption=f"✅ Excel file with {len(scraper.search_history)} users",
                    filename="instagram_search_results.xlsx"
                )
        else:
            await update.effective_message.reply_text("❌ Failed to create Excel file")
    
    except Exception as e:
        logger.error(f"Export error: {e}")
        await update.effective_message.reply_text(f"❌ Error: {str(e)}")


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
    
    if mode == 'lookup':
        # Single lookup
        await update.message.chat.send_action(ChatAction.TYPING)
        
        info = scraper.get_user_info(user_text)
        
        if isinstance(info, dict):
            # Format response
            response = f"""
✅ *@{info['username']}*

👤 *Full Name:* {info['full_name']}
👥 *Followers:* {info['followers']}
📤 *Following:* {info['following']}
📝 *Bio:* {info['bio']}
📍 *Location:* {info['full_location']}
📊 *Posts:* {info['posts_count']}
✓ *Verified:* {info['is_verified']}
🌐 *Public:* {info['is_public']}
🏢 *Business:* {info['is_business_account']}
🔗 *URL:* {info['external_url']}
🕐 *Search Time:* {info['search_timestamp']}
            """
            
            keyboard = [
                [InlineKeyboardButton("🔍 Search Another", callback_data='lookup'),
                 InlineKeyboardButton("📋 View History", callback_data='history')],
                [InlineKeyboardButton("📥 Export", callback_data='export')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await update.message.reply_text(info)
        
        context.user_data['mode'] = None
    
    elif mode == 'batch':
        # Batch lookup
        await update.message.chat.send_action(ChatAction.TYPING)
        
        usernames = [u.strip() for u in user_text.split(',')]
        
        await update.message.reply_text(f"🔍 Searching {len(usernames)} users...")
        
        results = []
        for i, user in enumerate(usernames, 1):
            info = scraper.get_user_info(user)
            if isinstance(info, dict):
                results.append(info)
                # Update progress
                if i % 3 == 0:  # Update every 3 users
                    await update.message.reply_text(f"⏳ Progress: {i}/{len(usernames)} users fetched...")
        
        # Summary
        summary = f"""
✅ *Batch Search Complete*

📊 Results: {len(results)}/{len(usernames)} users found

Users fetched:
        """
        
        for result in results:
            summary += f"\n• @{result['username']} ({result['full_name']}) - {result['followers']} followers"
        
        keyboard = [
            [InlineKeyboardButton("📥 Export to Excel", callback_data='export'),
             InlineKeyboardButton("📋 View History", callback_data='history')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(summary, parse_mode='Markdown', reply_markup=reply_markup)
        context.user_data['mode'] = None
    
    else:
        # Default: treat as username lookup
        await update.message.chat.send_action(ChatAction.TYPING)
        
        info = scraper.get_user_info(user_text)
        
        if isinstance(info, dict):
            response = f"""
✅ *@{info['username']}*

👤 *Full Name:* {info['full_name']}
👥 *Followers:* {info['followers']}
📤 *Following:* {info['following']}
📝 *Bio:* {info['bio']}
📍 *Location:* {info['full_location']}
📊 *Posts:* {info['posts_count']}
✓ *Verified:* {info['is_verified']}
🌐 *Public:* {info['is_public']}
🏢 *Business:* {info['is_business_account']}
🔗 *URL:* {info['external_url']}
            """
            
            keyboard = [
                [InlineKeyboardButton("🔍 Search Another", callback_data='lookup'),
                 InlineKeyboardButton("📥 Export", callback_data='export')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await update.message.reply_text(info)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors"""
    logger.error(f'Update {update} caused error {context.error}')
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred. Please try again or use /help"
        )


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

