import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import database
import handlers
from config import BOT_TOKEN

def main():
    # Asynchronously configure global schema layouts tables footprint loops mapping contexts
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(database.init_db())

    if not BOT_TOKEN:
        print("Fatal error: Missing BOT_TOKEN environment credentials definition asset mapping.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", handlers.start),
            CallbackQueryHandler(handlers.menu_routing, pattern="^nav_")
        ],
        states={
            handlers.AWAITING_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.process_url_extraction)]
        },
        fallbacks=[CommandHandler("start", handlers.start)]
    )

    app.add_handler(CommandHandler("stats", handlers.admin_stats))
    app.add_handler(CallbackQueryHandler(handlers.download_trigger, pattern="^dl_"))
    app.add_handler(CallbackQueryHandler(handlers.menu_routing, pattern="^(nav_|set_|go_home)"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.process_url_extraction))
    app.add_handler(conv_handler)

    print("FaviconPro Operational Engine Polling Active...")
    app.run_polling()

if __name__ == '__main__':
    main()

