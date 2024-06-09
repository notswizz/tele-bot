import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, ApplicationBuilder
from pymongo import MongoClient

# Access the MongoDB URI from the environment variables
MONGODB_URI = os.getenv('MONGODB_URI', 'your_mongodb_connection_string')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['telebot']  # Replace with your database name
collection = db['users']  # Replace with your collection name

# Define states for the conversation
ASK_AMOUNT = 1

async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("How much do you want to deposit?")
    return ASK_AMOUNT

async def receive_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Convert the received text to an integer
        amount = int(update.message.text)
        user = update.message.from_user

        # Directly update the user's balance in MongoDB without payment processing
        user_balance = collection.find_one({"username": user.username})

        if user_balance:
            new_balance = user_balance.get('amount', 0) + amount
            collection.update_one(
                {"username": user.username},
                {"$set": {"amount": new_balance}}
            )
        else:
            new_balance = amount
            collection.insert_one({
                'user_id': user.id,
                'username': user.username,
                'amount': new_balance,
                'timestamp': update.message.date
            })

        await update.message.reply_text(f'You have successfully added ${amount} to your balance. Your new balance is: ${new_balance}')
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text('Please enter a valid integer amount.')
        return ASK_AMOUNT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', start_add)],
        states={
            ASK_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
