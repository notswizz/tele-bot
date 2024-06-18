import os
import plotly.graph_objs as go
from plotly.io import to_image
from telegram import Update
from telegram.ext import ContextTypes
from pymongo import MongoClient
from datetime import datetime
import io

# Access the MongoDB URI from the environment variables
MONGODB_URI = os.getenv('MONGODB_URI', 'your_mongodb_connection_string')

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['telebot']  # Replace with your database name
transactions_collection = db['transactions']

async def transactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Retrieve the last 15 transactions
    recent_transactions = transactions_collection.find().sort("timestamp", -1).limit(15)
    response = "📋 **Transaction History:**\n\n"
    response += "| **Username** | Type | **Team** | **Price** | **Timestamp** |\n"
    response += "|--------------|----------|----------|-----------|----------------|\n"

    usernames = []
    types = []
    teams = []
    prices = []
    timestamps = []

    for transaction in recent_transactions:
        username = transaction['username']
        type_ = transaction['type']
        team = transaction['team']
        price = transaction['price']
        timestamp = transaction['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

        response += f"| {username} | {type_.capitalize()} | {team} | ${price} | {timestamp} |\n"

        usernames.append(username)
        types.append(type_)
        teams.append(team)
        prices.append(price)
        timestamps.append(timestamp)

    await update.message.reply_text(f"<pre>{response}</pre>", parse_mode='HTML')
