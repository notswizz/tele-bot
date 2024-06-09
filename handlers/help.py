from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Welcome to the NFL Shares Bot! 🏈

Here's how you can use this bot:

1. **Add Funds to Your Account**:
   - Use the /add command to deposit funds into your account.
   - Example: `/add`
   - Follow the prompts to specify the amount you wish to deposit.

2. **Buy Shares**:
   - Use the /buy command to purchase shares of your favorite NFL teams.
   - Example: `/buy`
   - Follow the prompts to specify the team you want to buy shares of.

3. **Sell Shares**:
   - Use the /sell command to sell shares you own.
   - Example: `/sell`
   - Follow the prompts to specify the team you want to sell shares of.

4. **Check Your Balance**:
   - Use the /balance command to check your current balance.
   - Example: `/balance`

5. **View Your Portfolio**:
   - Use the /portfolio command to view the shares you own.
   - Example: `/portfolio`

6. **View Team Prices**:
   - Use the /list_teams command to see the current prices of all NFL teams.
   - Example: `/list_teams`

### Game Mechanics:

- **Buying Shares**:
  - When you buy a share of a team, the price of the team increases by 10%.
  - The new share is added to your portfolio.

- **Selling Shares**:
  - When you sell a share of a team, the price of the team decreases by 10%.
  - You receive 80% of the sale price, and 20% goes to the community pot.

- **Community Pot**:
  - The community pot accumulates funds from the 20% cut of all sales.
  - You can check the pot balance using the /pot command.

- **Transactions**:
  - Use the /transactions command to view your transaction history.
  - Example: `/transactions`

### Tips:
- You can view detailed transaction receipts and your balance updates after each transaction.
- Use the help command whenever you need a refresher on how to use the bot.

Happy Trading! 🎉
"""
    await update.message.reply_text(help_text)

