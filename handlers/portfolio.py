import os
from telegram import Update
from telegram.ext import ContextTypes
from pymongo import MongoClient
import cairosvg
import io

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

    total_value = 0
    has_shares = False

    rows = ""
    for team, count in user_data['teams'].items():
        if count > 0:
            team_data = teams_collection.find_one({"team": team})
            if team_data:
                current_price = team_data['price']
                total_team_value = current_price * count
                total_value += total_team_value
                rows += f"""
                <tr>
                    <td>{team}</td>
                    <td>{count}</td>
                    <td>${current_price}</td>
                    <td>${total_team_value:.2f}</td>
                </tr>
                """
                has_shares = True

    if not has_shares:
        await update.message.reply_text("You do not own any shares.")
        return

    svg_template = f"""
    <svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
        <style>
            .title {{
                font: bold 24px sans-serif;
                fill: #333;
            }}
            .header {{
                font: bold 18px sans-serif;
                fill: #555;
            }}
            .cell {{
                font: 16px sans-serif;
                fill: #777;
            }}
            .footer {{
                font: bold 20px sans-serif;
                fill: #000;
            }}
            .background {{
                fill: #f9f9f9;
            }}
            .table {{
                fill: #fff;
                stroke: #ccc;
                stroke-width: 1px;
            }}
        </style>
        <rect x="0" y="0" width="800" height="400" class="background"/>
        <text x="20" y="40" class="title">Your Portfolio</text>
        <rect x="20" y="50" width="760" height="300" class="table"/>
        <text x="40" y="80" class="header">Team</text>
        <text x="200" y="80" class="header">Shares</text>
        <text x="360" y="80" class="header">Current Price</text>
        <text x="520" y="80" class="header">Total Value</text>
        <line x1="20" y1="90" x2="780" y2="90" stroke="#ccc" stroke-width="1"/>
        {rows}
        <text x="20" y="370" class="footer">Total Portfolio Value: ${total_value:.2f}</text>
    </svg>
    """

    # Convert SVG to PNG
    png_image = cairosvg.svg2png(bytestring=svg_template.encode('utf-8'))

    # Send the image
    await update.message.reply_photo(photo=io.BytesIO(png_image))

# Don't forget to add the portfolio command handler to your bot's setup
# Example:
# app.add_handler(CommandHandler("portfolio", portfolio))
