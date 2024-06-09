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
users_collection = db['users']
withdrawals_collection = db['withdrawals']

# Define states for the conversation
ASK_WITHDRAW_AMOUNT = 1

async def start_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_data = users_collection.find_one({"username": user.username})

    if not user_data:
        await update.message.reply_text("❌ **Error:** User not found.")
        return ConversationHandler.END

    current_balance = user_data['amount']
    await update.message.reply_text(f"💰 **Your current balance is:** ${current_balance}\n\nPlease enter the amount you wish to withdraw.")
    return ASK_WITHDRAW_AMOUNT

async def receive_withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        withdraw_amount = float(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ **Error:** Invalid amount. Please enter a numeric value.")
        return ASK_WITHDRAW_AMOUNT

    user = update.message.from_user
    user_data = users_collection.find_one({"username": user.username})

    if withdraw_amount <= 0:
        await update.message.reply_text("❌ **Error:** Withdrawal amount must be greater than zero.")
        return ASK_WITHDRAW_AMOUNT

    if not user_data or withdraw_amount > user_data['amount']:
        await update.message.reply_text("❌ **Error:** Insufficient balance.")
        return ASK_WITHDRAW_AMOUNT

    new_balance = user_data['amount'] - withdraw_amount
    users_collection.update_one(
        {"username": user.username},
        {"$set": {"amount": new_balance}}
    )

    # Log the withdrawal
    withdrawal_id = withdrawals_collection.insert_one({
        "username": user.username,
        "amount": withdraw_amount,
        "timestamp": datetime.now()
    }).inserted_id

    await update.message.reply_text(f"✅ **Withdrawal successful!**\n\n💵 **Amount withdrawn:** ${withdraw_amount}\n💰 **New balance:** ${new_balance}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🛑 **Operation Cancelled.**')
    return ConversationHandler.END

# Define the conversation handler
withdraw_conversation = ConversationHandler(
    entry_points=[CommandHandler('withdraw', start_withdraw)],
    states={
        ASK_WITHDRAW_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_withdraw_amount)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
