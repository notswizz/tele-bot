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
teams_collection = db['nfl_teams']

async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_data = users_collection.find_one({"username": user.username})

    if not user_data or 'teams' not in user_data or not user_data['teams']:
        await update.message.reply_text("You do not own any shares.")
        return

    response = "📊 **Your Portfolio:**\n\n"
    response += "| **Team**       | **Shares** | **Current Price** | **Total Value**  |\n"
    response += "|----------------|------------|-------------------|------------------|\n"

    total_value = 0
    has_shares = False

    for team, count in user_data['teams'].items():
        if count > 0:
            team_data = teams_collection.find_one({"team": team})
            if team_data:
                current_price = team_data['price']
                total_team_value = current_price * count
                total_value += total_team_value
                response += f"| {team:<15} | {count:<10} | ${current_price:<16} | ${total_team_value:<17.2f} |\n"
                has_shares = True

    if not has_shares:
        await update.message.reply_text("You do not own any shares.")
        return

    response += "\n**Total Portfolio Value:** ${:.2f}".format(total_value)

    await update.message.reply_text(f"<pre>{response}</pre>", parse_mode='HTML')
