import os
import plotly.graph_objs as go
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from pymongo import MongoClient
import io
from PIL import Image

# Access the MongoDB URI from the environment variables
MONGODB_URI = os.getenv('MONGODB_URI', 'your_mongodb_connection_string')

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['telebot']  # Replace with your database name
transactions_collection = db['transactions']

# Define states for the conversation
ASK_TEAM = 1

async def start_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Which NFL team do you want to see the price chart for?")
    return ASK_TEAM

async def receive_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    team_name = update.message.text
    team_transactions = transactions_collection.find({"team": team_name}).sort("timestamp", 1)
    team_transactions_list = list(team_transactions)

    if len(team_transactions_list) == 0:
        await update.message.reply_text(f'❌ No transactions found for the team "{team_name}". Please try again with a valid team name.')
        return ASK_TEAM

    prices = []

    for transaction in team_transactions_list:
        prices.append(transaction['price'])

    # Generate chart with transaction numbers on the x-axis
    fig = go.Figure(data=[go.Scatter(x=list(range(1, len(prices) + 1)), y=prices, mode='lines+markers', marker=dict(size=10, color='blue'))])
    fig.update_layout(
        title=f'Price Chart for {team_name}',
        xaxis_title='Transaction Number',
        yaxis_title='Price',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='black'),
        title_font=dict(size=24, color='black'),
        xaxis=dict(showgrid=True, gridcolor='lightgrey', color='black'),
        yaxis=dict(showgrid=True, gridcolor='lightgrey', color='black')
    )

    # Add team logo if available
    logo_path = f'logos/{team_name}.png'
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        fig.add_layout_image(
            dict(
                source=logo,
                xref="paper", yref="paper",
                x=1, y=1,
                sizex=0.2, sizey=0.2,
                xanchor="right", yanchor="bottom"
            )
        )

    # Convert the figure to a PNG image
    try:
        image_bytes = fig.to_image(format='png')
    except Exception as e:
        await update.message.reply_text(f'❌ Error generating chart: {e}')
        return ConversationHandler.END

    # Send the image
    try:
        await update.message.reply_photo(photo=image_bytes)
    except Exception as e:
        await update.message.reply_text(f'❌ Error sending chart: {e}')
        return ConversationHandler.END

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🛑 **Operation Cancelled.**')
    return ConversationHandler.END

# Define the conversation handler
chart_conversation = ConversationHandler(
    entry_points=[CommandHandler('chart', start_chart)],
    states={
        ASK_TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_team)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)