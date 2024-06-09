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

async def start_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Which NFL team do you want to buy shares in?")
    return ASK_TEAM

async def receive_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    team_name = update.message.text
    team_data = teams_collection.find_one({"team": team_name})

    if team_data:
        user = update.message.from_user
        user_data = users_collection.find_one({"username": user.username})

        if user_data and user_data['amount'] >= team_data['price']:
            # Subtract the price from the user's balance
            new_balance = user_data['amount'] - team_data['price']
            users_collection.update_one(
                {"username": user.username},
                {"$set": {"amount": new_balance}}
            )

            # Increase the price by 10% and add 1 share
            new_price = round(team_data['price'] * 1.10, 2)
            new_shares = team_data['shares'] + 1

            # Update the team data in the database
            teams_collection.update_one(
                {"team": team_name},
                {"$set": {"price": new_price, "shares": new_shares}}
            )

            # Increment the team's share count for the user
            users_collection.update_one(
                {"username": user.username},
                {"$inc": {f"teams.{team_name}": 1}}
            )

            # Log the transaction
            transaction_id = transactions_collection.insert_one({
                "username": user.username,
                "type": "buy",
                "team": team_name,
                "price": team_data['price'],
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
            header_text = f"Buy Receipt"
            header_text_bbox = d.textbbox((0, 0), header_text, font=header_font)
            header_text_width = header_text_bbox[2] - header_text_bbox[0]
            d.text((img_width//2 - header_text_width//2, 50), header_text, font=header_font, fill=(0, 0, 0))

            # Transaction details
            transaction_details = (
                f"Transaction ID: {transaction_id}\n"
                f"Username: {user.username}\n"
                f"Type: Buy\n"
                f"Team: {team_name}\n"
                f"Shares Bought: 1\n"
                f"Price: ${team_data['price']}\n"
                f"New Price: ${new_price}\n"
                f"New Balance: ${new_balance}\n"
                f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            y_position = 100
            for line in transaction_details.split('\n'):
                d.text((50, y_position), line, font=font, fill=(0, 0, 0))
                y_position += 30

            # Add a border
            border_color = (0, 0, 0)
            d.rectangle([0, 0, img_width-1, img_height-1], outline=border_color)

            # Save the image to a bytes buffer
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)

            # Send the image receipt
            await update.message.reply_photo(photo=buf)

        else:
            await update.message.reply_text('Transaction Failed: You do not have enough balance to buy a share of this team.')
    else:
        await update.message.reply_text('Error: The team you mentioned does not exist. Please try again.')
        return ASK_TEAM

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Operation Cancelled.')
    return ConversationHandler.END

# Define the conversation handler
buy_conversation = ConversationHandler(
    entry_points=[CommandHandler('buy', start_buy)],
    states={
        ASK_TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_team)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
