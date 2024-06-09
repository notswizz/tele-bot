import os
from telegram import Update
from telegram.ext import ContextTypes
from pymongo import MongoClient

# Access the MongoDB URI from the environment variables
MONGODB_URI = os.getenv('MONGODB_URI', 'your_mongodb_connection_string')

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['telebot']  # Replace with your database name
users_collection = db['users']

async def pot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pot_data = users_collection.find_one({"username": "pot"})

    if pot_data and 'amount' in pot_data:
        pot_amount = pot_data['amount']
        await update.message.reply_text(f'The current amount in the pot is ${pot_amount}.')
    else:
        await update.message.reply_text('The pot is currently empty.')
