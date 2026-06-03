import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Load our catalog
with open("products.json", "r") as f:
    products = json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to ShopSprint! Type a product name or category to check availability."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text.lower()
    match_found = None
    alternative = None

    # Simple keyword match logic (Can be upgraded with OpenAI embeddings later)
    for p in products:
        if any(tag in user_query for tag in p["tags"]):
            if p["stock"] > 0:
                match_found = p
                break
            else:
                # If product is out of stock, look for an alternative in the same category
                alternative = next((alt for alt in products if alt["category"] == p["category"] and alt["stock"] > 0), None)
                match_found = p
                break

    if match_found:
        if match_found["stock"] > 0:
            await update.message.reply_text(f"✅ In Stock: *{match_found['name']}* is available! Would you like to purchase?", parse_mode="Markdown")
        elif alternative:
            await update.message.reply_text(
                f"⚠️ *{match_found['name']}* is currently out of stock.\n\n"
                f"💡 *ShopSprint Match:* Based on your interest, we highly recommend the *{alternative['name']}* as a context-aware alternative! It's currently in stock.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Sorry, that item is out of stock and no close matches are available right now.")
    else:
        await update.message.reply_text("🔍 I couldn't find an exact match. Tell me what features you are looking for, and I'll find an alternative!")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("ShopSprint Bot is running...")
    # Use polling for simple testing; Render will use Webhooks or continuous workers
    app.run_polling()

if __name__ == "__main__":
    main()
