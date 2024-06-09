import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from pymongo import MongoClient

# Access the MongoDB URI from the environment variables
MONGODB_URI = os.environ['MONGODB_URI']

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['telebot']  # Replace with your database name
user_collection = db['users']  # Collection for user registration
teams_collection = db['nfl_teams']  # Collection for NFL teams

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = user.username

    if not username:
        await update.message.reply_text("You don't have a username set in Telegram. Please set a username to use this command.")
        return

    # Check if the user is already registered
    registered_user = user_collection.find_one({"username": username})
    if registered_user:
        await update.message.reply_text("You are already registered. Use /help to see what you can do.")
        return

    # Initialize teams with zero shares
    teams = teams_collection.find()
    user_teams = {team['team']: 0 for team in teams}

    # Ask for the user's phone number
    phone_button = KeyboardButton(text="Share my phone number", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[phone_button]], one_time_keyboard=True)
    await update.message.reply_text("Please share your phone number to register:", reply_markup=reply_markup)

    # Register the user with the initialized teams
    def register_user(contact):
        user_collection.insert_one({
            'user_id': user.id,
            'username': username,
            'phone_number': contact.phone_number,
            'teams': user_teams,
            'amount': 0,
            'timestamp': update.message.date
        })

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.message.from_user
    username = user.username

    if contact and contact.user_id == user.id:
        # Save the user's phone number to the database
        register_user(contact)

        await update.message.reply_text("You are now registered! Here are the rules:\n1. Rule 1\n2. Rule 2\n3. Rule 3")
    else:
        await update.message.reply_text("Please share your phone number using the button provided.")
