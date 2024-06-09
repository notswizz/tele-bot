import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from pymongo import MongoClient

# Access the MongoDB URI from the environment variables
MONGODB_URI = os.environ['MONGODB_URI']

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['telebot']  # Replace with your database name
collection = db['nfl_teams']

# Define states for the conversation
ASK_TEAM = 1

async def start_team_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Which NFL team are you interested in?")
    return ASK_TEAM

async def receive_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    team_name = update.message.text
    team_data = collection.find_one({"team": team_name})

    if team_data:
        price = team_data.get('price')
        await update.message.reply_text(f'The price for {team_name} is: ${price}')
    else:
        await update.message.reply_text('Sorry, the team you mentioned does not exist. Please try again.')
        return ASK_TEAM

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END
