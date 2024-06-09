import os
from telegram import Update
from telegram.ext import ContextTypes
from pymongo import MongoClient

# Access the MongoDB URI from the environment variables
MONGODB_URI = os.getenv('MONGODB_URI', 'your_mongodb_connection_string')

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['telebot']  # Replace with your database name
collection = db['nfl_teams']

async def list_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teams = collection.find({}).sort('price', -1)  # Sorting teams by price in descending order
    response = "Here are the NFL teams, their prices, and shares:\n\n"
    response += "{:<25} {:<10} {:<10}\n".format("Team", "Price", "Shares")
    response += "-"*45 + "\n"

    for team in teams:
        response += "{:<25} ${:<9} {:<10}\n".format(team['team'], team['price'], team['shares'])

    await update.message.reply_text(f"<pre>{response}</pre>", parse_mode='HTML')
