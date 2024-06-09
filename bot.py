from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from handlers import start, echo, help_command, status, balance, claim, list_teams, pot, transactions, portfolio
from handlers.add import start_add, receive_amount, cancel, ASK_AMOUNT
from handlers.team_price import start_team_price, receive_team, cancel as cancel_team_price, ASK_TEAM
from handlers.buy import start_buy, receive_team as receive_buy_team, cancel as cancel_buy, ASK_TEAM as BUY_ASK_TEAM
from handlers.sell import start_sell, receive_team as receive_sell_team, cancel as cancel_sell, ASK_TEAM as SELL_ASK_TEAM
from handlers.chart import start_chart, receive_team as receive_chart_team, cancel as cancel_chart, ASK_TEAM as CHART_ASK_TEAM
from handlers.refer import start_refer, receive_referral_username, cancel as cancel_refer, ASK_REFERRAL_USERNAME
from handlers.withdraw import start_withdraw, receive_withdraw_amount, cancel as cancel_withdraw, ASK_WITHDRAW_AMOUNT

# Your bot's token
TOKEN = '7415011597:AAFcXiiF7G9JKeYNAzYachb5c3eEdVPcbh0'

def main():
    # Create the Application and pass it your bot's token
    app = ApplicationBuilder().token(TOKEN).build()

    # Define the conversation handler for the team price command
    team_price_conversation = ConversationHandler(
        entry_points=[CommandHandler('team_price', start_team_price)],
        states={
            ASK_TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_team)],
        },
        fallbacks=[CommandHandler('cancel', cancel_team_price)]
    )

    # Define the conversation handler for the add command
    add_conversation = ConversationHandler(
        entry_points=[CommandHandler('add', start_add)],
        states={
            ASK_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Define the conversation handler for the buy command
    buy_conversation = ConversationHandler(
        entry_points=[CommandHandler('buy', start_buy)],
        states={
            BUY_ASK_TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_buy_team)],
        },
        fallbacks=[CommandHandler('cancel', cancel_buy)]
    )

    # Define the conversation handler for the sell command
    sell_conversation = ConversationHandler(
        entry_points=[CommandHandler('sell', start_sell)],
        states={
            SELL_ASK_TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_sell_team)],
        },
        fallbacks=[CommandHandler('cancel', cancel_sell)]
    )

    # Define the conversation handler for the chart command
    chart_conversation = ConversationHandler(
        entry_points=[CommandHandler('chart', start_chart)],
        states={
            CHART_ASK_TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_chart_team)],
        },
        fallbacks=[CommandHandler('cancel', cancel_chart)]
    )

    # Define the conversation handler for the refer command
    refer_conversation = ConversationHandler(
        entry_points=[CommandHandler('refer', start_refer)],
        states={
            ASK_REFERRAL_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_referral_username)],
        },
        fallbacks=[CommandHandler('cancel', cancel_refer)]
    )

    # Define the conversation handler for the withdraw command
    withdraw_conversation = ConversationHandler(
        entry_points=[CommandHandler('withdraw', start_withdraw)],
        states={
            ASK_WITHDRAW_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_withdraw_amount)],
        },
        fallbacks=[CommandHandler('cancel', cancel_withdraw)]
    )

    # Register the handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(team_price_conversation)
    app.add_handler(add_conversation)
    app.add_handler(buy_conversation)
    app.add_handler(sell_conversation)
    app.add_handler(chart_conversation)
    app.add_handler(refer_conversation)
    app.add_handler(withdraw_conversation)
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("list_teams", list_teams))
    app.add_handler(CommandHandler("pot", pot))
    app.add_handler(CommandHandler("transactions", transactions))
    app.add_handler(CommandHandler("portfolio", portfolio))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the Bot
    app.run_polling()

if __name__ == '__main__':
    main()
