import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
import database
import favicon_extractor
import image_converter
import utils
from config import TEMP_DIR, ADMIN_ID

AWAITING_URL = 1

def main_menu():
    keyboard = [
        [InlineKeyboardButton("🌐 Extract Favicon", callback_data="nav_extract")],
        [InlineKeyboardButton("📜 History", callback_data="nav_history"),
         InlineKeyboardButton("⚙️ Settings", callback_data="nav_settings")],
        [InlineKeyboardButton("❓ Help", callback_data="nav_help")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utils.ensure_temp_directory()
    welcome = (
        "👋 Welcome to *FaviconPro Bot*!\n"
        "Extract and download high-quality website favicons in seconds.\n\n"
        "🌐 *Enter any website URL*\n"
        "🖼️ *Detect the highest-quality favicon*\n"
        "📥 *Download in PNG, ICO, JPEG, or WEBP*\n"
        "📜 *Save search history and favorites*\n\n"
        "Tap one of the buttons below or send a website URL to begin."
    )
    if update.message:
        await update.message.reply_text(welcome, reply_markup=main_menu(), parse_mode="Markdown")
    return ConversationHandler.END

async def menu_routing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    
    if query.data == "nav_extract":
        await query.message.reply_text("🌐 Please send the website URL or domain name you want to extract:")
        return AWAITING_URL
    elif query.data == "nav_history":
        hist = await database.get_history(uid)
        if not hist:
            await query.message.reply_text("📜 Your extraction history is empty.")
        else:
            await query.message.reply_text("📜 *Your Recent Searches:*\n\n" + "\n".join([f"- `{u}`" for u in hist]), parse_mode="Markdown")
    elif query.data == "nav_settings":
        settings = await database.get_settings(uid)
        msg = f"⚙️ *Settings Dashboard:*\n\nDefault Download Format: `{settings['default_format']}`"
        kb = [[InlineKeyboardButton("Set PNG", callback_data="set_PNG"), InlineKeyboardButton("Set ICO", callback_data="set_ICO")],
              [InlineKeyboardButton("🔙 Menu", callback_data="go_home")]]
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    elif query.data.startswith("set_"):
        fmt = query.data.split("_")[1]
        await database.update_setting(uid, "default_format", fmt)
        await query.message.reply_text(f"✅ Download format preference updated to: `{fmt}`")
    elif query.data == "go_home":
        await query.edit_message_text("Choose an option below or send a website URL to begin.", reply_markup=main_menu())
    elif query.data == "nav_help":
        await query.message.reply_text("❓ *How it works:*\nSimply type or send any web domain name (e.g. `google.com`). The bot crawls the web tags and fetches the native highest-resolution favicon graphic elements.")
    return ConversationHandler.END

async def process_url_extraction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    url_text = update.message.text.strip()
    
    status_msg = await update.message.reply_text("⏳ Searching for highest-quality favicon graphic streams across target metadata rules indices...")
    
    urls = await favicon_extractor.fetch_favicon_urls(url_text)
    if not urls:
        await update.message.reply_text("❌ Invalid URL or failure to discover graphic elements asset payloads.")
        await status_msg.delete()
        return ConversationHandler.END
        
    await database.add_history(uid, url_text)
    local_src = os.path.join(TEMP_DIR, f"fav_{uid}_source.ico")
    
    success = False
    for favicon_url in urls:
        if await utils.download_file(favicon_url, local_src):
            success = True
            context.user_data['active_src'] = local_src
            context.user_data['target_domain'] = url_text
            break
            
    if success and os.path.exists(local_src):
        kb = [[InlineKeyboardButton("📥 Download PNG", callback_data="dl_PNG"),
               InlineKeyboardButton("📥 Download ICO", callback_data="dl_ICO")],
              [InlineKeyboardButton("📥 Download WEBP", callback_data="dl_WEBP")]]
        await update.message.reply_text(f"🖼️ Favicon discovered successfully for `{url_text}`! Select export output format:", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Failed to resolve or download any matching favicon target layers.")
        
    await status_msg.delete()
    return ConversationHandler.END

async def download_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    fmt = query.data.split("_")[1]
    
    src = context.user_data.get('active_src')
    domain = context.user_data.get('target_domain', 'favicon')
    
    if not src or not os.path.exists(src):
        await query.message.reply_text("❌ Active session file expired. Send the website URL again.")
        return
        
    out_path = os.path.join(TEMP_DIR, f"fav_{uid}_out.{fmt.lower()}")
    if image_converter.process_and_convert_icon(src, out_path, fmt):
        with open(out_path, 'rb') as f:
            await query.message.reply_document(document=f, filename=f"{domain}_favicon.{fmt.lower()}")
        utils.clean_user_files(uid)
    else:
        await query.message.reply_text("❌ Error converting image vector layers configuration elements context.")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text("📊 *System Admin Dashboard:*\n\nStatus Operational: `Active` Engine Line.\nMonitoring background threads via Render pooling worker maps.", parse_mode="Markdown")
