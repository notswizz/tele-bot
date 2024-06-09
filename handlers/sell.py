import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from pymongo import MongoClient
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

# Access the MongoDB URI from the environment variables
MONGODB_URI = os.getenv('MONGODB_URI', 'your_mongodb_connection_string')

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['telebot']  # Replace with your database name
teams_collection = db['nfl_teams']
users_collection = db['users']
transactions_collection = db['transactions']

# Define states for the conversation
ASK_TEAM = 1

async def start_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_data = users_collection.find_one({"username": user.username})

    if not user_data or 'teams' not in user_data or not any(user_data['teams'].values()):
        await update.message.reply_text("❌ **Error:** You do not own any shares to sell.")
        return ConversationHandler.END

    response = "📊 **Teams and shares you own:**\n\n"
    for team_name, count in user_data['teams'].items():
        if count > 0:
            response += f"**{team_name}:** {count} shares\n"

    response += "\n💰 **Which NFL team do you want to sell shares in?**"
    await update.message.reply_text(response)
    return ASK_TEAM

async def receive_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    team_name = update.message.text
    team_data = teams_collection.find_one({"team": team_name})
    user = update.message.from_user
    user_data = users_collection.find_one({"username": user.username})

    if team_data and user_data and user_data['teams'].get(team_name, 0) > 0:
        # Calculate the sale price
        sale_price = team_data['price']
        user_share = round(sale_price * 0.80, 2)
        pot_share = round(sale_price * 0.20, 2)

        # Update the user's balance
        new_balance = user_data['amount'] + user_share
        users_collection.update_one(
            {"username": user.username},
            {"$set": {"amount": new_balance}}
        )

        # Add the pot share to the user 'pot'
        users_collection.update_one(
            {"username": "pot"},
            {"$inc": {"amount": pot_share}},
            upsert=True
        )

        # Decrease the price by 10% and subtract 1 share
        new_price = round(sale_price * 0.90, 2)
        new_shares = team_data['shares'] - 1

        # Update the team data in the database
        teams_collection.update_one(
            {"team": team_name},
            {"$set": {"price": new_price, "shares": new_shares}}
        )

        # Decrement the team's share count for the user
        users_collection.update_one(
            {"username": user.username},
            {"$inc": {f"teams.{team_name}": -1}}
        )

        # Log the transaction
        transaction_id = transactions_collection.insert_one({
            "username": user.username,
            "type": "sell",
            "team": team_name,
            "price": sale_price,
            "profit": user_share,
            "pot": pot_share,
            "timestamp": datetime.now()
        }).inserted_id

        # Generate an image receipt
        img_width, img_height = 800, 400
        img = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
        d = ImageDraw.Draw(img)

        # Use a truetype or opentype font file
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font = ImageFont.truetype(font_path, 24)
        header_font = ImageFont.truetype(font_path, 32)
        logo_font = ImageFont.truetype(font_path, 18)

        # Add a background color
        d.rectangle([0, 0, img_width, img_height], fill=(240, 240, 240))

        # Add a logo or custom image
        logo_text = "NFL Shares"
        d.text((10, 10), logo_text, font=logo_font, fill=(0, 0, 128))

        # Header
        header_text = f"Sell Receipt"
        header_text_bbox = d.textbbox((0, 0), header_text, font=header_font)
        header_text_width = header_text_bbox[2] - header_text_bbox[0]
        d.text((img_width // 2 - header_text_width // 2, 50), header_text, font=header_font, fill=(0, 0, 0))

        # Transaction details
        transaction_details = (
            f"Transaction ID: {transaction_id}\n"
            f"Username: {user.username}\n"
            f"Type: Sell\n"
            f"Team: {team_name}\n"
            f"Shares Sold: 1\n"
            f"Sale Price: ${sale_price}\n"
            f"User Share: ${user_share}\n"
            f"Pot Share: ${pot_share}\n"
            f"New Balance: ${new_balance}\n"
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        y_position = 100
        for line in transaction_details.split('\n'):
            d.text((50, y_position), line, font=font, fill=(0, 0, 0))
            y_position += 30

        # Add a border
        border_color = (0, 0, 0)
        d.rectangle([0, 0, img_width - 1, img_height - 1], outline=border_color)

        # Save the image to a bytes buffer
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)

        # Send the image receipt
        await update.message.reply_photo(photo=buf)

    else:
        await update.message.reply_text('❌ **Error:** The team you mentioned does not exist or you do not own shares of this team. Please try again.')
        return ASK_TEAM

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🛑 **Operation Cancelled.**')
    return ConversationHandler.END

# Define the conversation handler
sell_conversation = ConversationHandler(
    entry_points=[CommandHandler('sell', start_sell)],
    states={
        ASK_TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_team)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
