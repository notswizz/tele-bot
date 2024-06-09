import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from pymongo import MongoClient
from datetime import datetime

# Access the MongoDB URI from the environment variables
MONGODB_URI = os.getenv('MONGODB_URI', 'your_mongodb_connection_string')

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['telebot']  # Replace with your database name
referrals_collection = db['referrals']

# Define states for the conversation
ASK_REFERRAL_USERNAME = 1

async def start_refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please provide the Telegram username of the person you are referring (without @).")
    return ASK_REFERRAL_USERNAME

async def receive_referral_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    referral_username = update.message.text
    referrer_username = update.message.from_user.username

    if referral_username and referrer_username:
        # Log the referral
        referral_data = {
            "referrer": referrer_username,
            "referral": referral_username,
            "timestamp": datetime.now()
        }
        referrals_collection.insert_one(referral_data)

        await update.message.reply_text(f"Thank you! You have successfully referred {referral_username}.")
    else:
        await update.message.reply_text("❌ **Error:** Invalid referral username. Please try again.")
        return ASK_REFERRAL_USERNAME

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🛑 **Operation Cancelled.**')
    return ConversationHandler.END

# Define the conversation handler
refer_conversation = ConversationHandler(
    entry_points=[CommandHandler('refer', start_refer)],
    states={
        ASK_REFERRAL_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_referral_username)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
