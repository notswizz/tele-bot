import os
from telegram import Update
from telegram.ext import ContextTypes
from pymongo import MongoClient

# Access the MongoDB URI from the environment variables
MONGODB_URI = os.environ['MONGODB_URI']

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['telebot']  # Replace with your database name
collection = db['users']  # Replace with your collection name

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = user.username

    if not username:
        await update.message.reply_text("You don't have a username set in Telegram. Please set a username to use this command.")
        return

    # Query the balance from MongoDB using the username
    user_balance = collection.find_one({"username": username})

    if user_balance:
        balance = user_balance.get("amount")
        await update.message.reply_text(f"Your balance is: ${balance}")
    else:
        await update.message.reply_text("Could not find a balance for your username. Please make sure your username is correct.")
