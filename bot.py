import os
import logging
import requests
import json
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== КОНФИГ ==========
TOKEN = "ТВОЙ_ТОКЕН_ОТ_BOTFATHER"
GEMINI_API_KEY = "AQ.Ab8RN6JJM_6qcVPk1Imbq5TbGDaveAUsO07Op9EdplozH6pQBA"

MAX_MESSAGES = 20

user_histories = {}
user_counts = {}

logging.basicConfig(level=logging.INFO)

# ========== КЛАВИАТУРА ==========
main_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("💼 Услуги"), KeyboardButton("🚀 Проекты")],
    [KeyboardButton("📧 Контакты"), KeyboardButton("❓ Помощь")],
    [KeyboardButton("🎛️ Меню")]
], resize_keyboard=True)

# ========== GEMINI AI ФУНКЦИЯ ==========
def ask_gemini(prompt, user_id):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({"role": "user", "parts": [{"text": prompt}]})
    if len(user_histories[user_id]) > 10:
        user_histories[user_id] = user_histories[user_id][-10:]

    payload = {
        "contents": user_histories[user_id],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 1500,
            "topP": 0.95
        }
    }

    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=20)
        data = response.json()
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
        user_histories[user_id].append({"role": "model", "parts": [{"text": answer}]})
        return answer
    except Exception as e:
        return f"⚠️ Ошибка: {str(e)}"

def check_limit(user_id):
    if user_id not in user_counts:
        user_counts[user_id] = 0
    if user_counts[user_id] >= MAX_MESSAGES:
        return False
    user_counts[user_id] += 1
    return True

# ========== КОМАНДЫ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *GimPrograms Бот-менеджер (Gemini)*\n"
        "Привет! Я — ИИ-помощник @Kitty_Kittys .\n\n"
        "📌 Я умею:\n"
        "— Отвечать на вопросы\n"
        "— Показывать услуги, проекты, контакты\n"
        "— Помнить до 20 сообщений\n\n"
        "Используй кнопки внизу или просто пиши!",
        reply_markup=main_keyboard,
        parse_mode="Markdown"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text == "🎛️ Меню":
        await update.message.reply_text("🏠 Главное меню" , reply_markup=main_keyboard, parse_mode="Markdown")
        return

    if text == "💼 Услуги":
        await update.message.reply_text(
            "💼 Услуги GimPrograms\n\n"
            "⚡ Сайты под ключ — от 100 ₽\n"
            "🤖 Telegram-боты — от 50 ₽\n"
            "🎨 Дизайн** — от 20 ₽\n\n"
            "⚠️ Временно новые заказы не принимаем.",
            parse_mode="Markdown"
        )
        return

    if text == "🚀 Проекты":
        await update.message.reply_text(
            "🚀 *Наши проекты:*\n\n"
            "🔹 [Xile Mobile](https://dimastwa0sopsi.github.io/XileMobile/)\n"
            "🔹 [GimGame](https://dimastwa0sopsi.github.io/sgames/)\n"
            "🔹 [GimStudios Hub](https://dimastwa0sopsi.github.io/GimProgramsWeb/)\n",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return

    if text == "📧 Контакты":
        await update.message.reply_text(
            "📧 *Связь с нами:*\n\n"
            "📨 Email: dimastvincs@gmail.com\n"
            "📱 Telegram: @Kitty_Kittys\n"
            "🔗 MAX: https://clck.ru/3TLeHu",
            parse_mode="Markdown"
        )
        return

    if text == "❓ Помощь":
        await update.message.reply_text(
            "❓ *Часто задаваемые вопросы:*\n\n"
            "🔹 **Как заказать?** — Напиши @Kitty_Kittys.\n"
            "🔹 **Есть ли гарантия?** — Да, на все услуги.\n"
            "🔹 **Когда возобновятся заказы?** — Временно приостановлены.",
            parse_mode="Markdown"
        )
        return

    if not check_limit(user_id):
        await update.message.reply_text(
            "⚠️ Лимит сообщений исчерпан (20)."
        )
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = ask_gemini(text, user_id)
    await update.message.reply_text(reply)

# ========== ЗАПУСК ==========
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("🤖 Бот-менеджер на запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
