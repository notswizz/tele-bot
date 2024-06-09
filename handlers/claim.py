import os
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the MongoDB URI from the environment variables
MONGODB_URI = os.environ['MONGODB_URI']

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['telebot']  # Replace with your database name
claim_collection = db['claims']  # Collection for claim records
balance_collection = db['users']  # Collection for balances

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = user.username

    if not username:
        await update.message.reply_text("You don't have a username set in Telegram. Please set a username to use this command.")
        return

    # Check if the user has already claimed today
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    existing_claim = claim_collection.find_one({"username": username, "date": today})

    if existing_claim:
        await update.message.reply_text("You have already claimed your reward for today. Please come back tomorrow.")
        return

    # Record the claim
    claim_record = {
        'user_id': user.id,
        'username': username,
        'date': today,
        'timestamp': datetime.utcnow()
    }
    claim_collection.insert_one(claim_record)

    # Update the user's balance
    user_balance = balance_collection.find_one({"username": username})
    if user_balance:
        new_balance = user_balance.get('amount', 0) + 10
        balance_collection.update_one(
            {"username": username},
            {"$set": {"amount": new_balance, "timestamp": datetime.utcnow()}}
        )
    else:
        new_balance = 10
        balance_collection.insert_one({
            'user_id': user.id,
            'username': username,
            'amount': new_balance,
            'timestamp': datetime.utcnow()
        })

    await update.message.reply_text(f"You have successfully claimed 10 points. Your new balance is: {new_balance}")
