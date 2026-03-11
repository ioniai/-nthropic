import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")

claude = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

user_histories = {}


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот с искусственным интеллектом. Напиши мне что-нибудь!"
    )


async def handle_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_histories[user_id] = []
    await update.message.reply_text("История очищена. Начнём заново!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_text = update.message.text

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({"role": "user", "content": user_text})

    await update.message.chat.send_action("typing")

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="Ты дружелюбный помощник. Отвечай на русском языке.",
        messages=user_histories[user_id]
    )

    bot_reply = response.content[0].text

    user_histories[user_id].append({"role": "assistant", "content": bot_reply})

    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = user_histories[user_id][-20:]

    await update.message.reply_text(bot_reply)


app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", handle_start))
app.add_handler(CommandHandler("reset", handle_reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Бот запущен!")
app.run_polling()
