import os
import logging
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ========== КОНФИГ ==========
TOKEN = "ТВОЙ_ТОКЕН_ОТ_BOTFATHER"
AI_API_KEY = "AQ.Ab8RN6JJM_6qcVPk1Imbq5TbGDaveAUsO07Op9EdplozH6pQBA"

# Лимит сообщений на пользователя
MAX_MESSAGES = 20

# Хранилище: история сообщений и счётчик
user_histories = {}
user_counts = {}

logging.basicConfig(level=logging.INFO)

# ========== КЛАВИАТУРА (с кнопкой 🎛️) ==========
main_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("💼 Услуги"), KeyboardButton("🚀 Проекты")],
    [KeyboardButton("📧 Контакты"), KeyboardButton("❓ Помощь")],
    [KeyboardButton("🎛️ Меню")]
], resize_keyboard=True)

# ========== AI ФУНКЦИЯ ==========
def ask_ai(prompt, user_id):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Инициализируем историю
    if user_id not in user_histories:
        user_histories[user_id] = []

    # Добавляем вопрос пользователя
    user_histories[user_id].append({"role": "user", "content": prompt})

    # Обрезаем историю до 20 сообщений (10 вопросов + 10 ответов)
    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = user_histories[user_id][-20:]

    payload = {
        "model": "deepseek-chat",
        "messages": user_histories[user_id],
        "temperature": 0.8,
        "max_tokens": 1500
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        user_histories[user_id].append({"role": "assistant", "content": answer})
        return answer
    except Exception as e:
        return f"⚠️ Ошибка: {str(e)}"

# ========== ПРОВЕРКА ЛИМИТА ==========
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
        "🤖 *GimPrograms Бот-менеджер*\n"
        "Привет! Я — твой ИИ-помощник и менеджер студии.\n\n"
        "📌 Я умею:\n"
        "— Отвечать на вопросы (с помощью нейросети)\n"
        "— Показывать услуги, проекты и контакты\n"
        "— Помнить до 20 сообщений в диалоге\n\n"
        "Используй кнопки внизу или просто пиши!",
        reply_markup=main_keyboard,
        parse_mode="Markdown"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Кнопка 🎛️ Меню
    if text == "🎛️ Меню":
        await update.message.reply_text(
            "🏠 *Главное меню*\n\nВыбери, что тебя интересует:",
            reply_markup=main_keyboard,
            parse_mode="Markdown"
        )
        return

    # Обработка кнопок
    if text == "💼 Услуги":
        await update.message.reply_text(
            "💼 *Услуги GimPrograms*\n\n"
            "⚡ **Сайты под ключ** — от 3 000 ₽\n"
            "🤖 **Telegram-боты** — от 4 000 ₽\n"
            "🎮 **Скрипты для GTA SA** — от 3 000 ₽\n"
            "🎨 **Дизайн** — от 2 000 ₽\n\n"
            "⚠️ *Временно новые заказы не принимаем.*\n"
            "Свяжитесь для уточнения деталей.",
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
            "🔗 MAX: https://clck.ru/3TLeHu\n\n"
            "💬 Пишите по любым вопросам!",
            parse_mode="Markdown"
        )
        return

    if text == "❓ Помощь":
        await update.message.reply_text(
            "❓ *Часто задаваемые вопросы:*\n\n"
            "🔹 **Как заказать?**\n"
            "Напишите в Telegram @Kitty_Kittys или на почту.\n\n"
            "🔹 **Есть ли гарантия?**\n"
            "Да, на все услуги.\n\n"
            "🔹 **Когда возобновятся заказы?**\n"
            "Временно приостановлены. Следите за новостями!",
            parse_mode="Markdown"
        )
        return

    # Если это не кнопка — отправляем в ИИ
    if not check_limit(user_id):
        await update.message.reply_text(
            "⚠️ Лимит сообщений для этого диалога исчерпан (20 сообщений).\n"
            "Напишите /start, чтобы начать новый разговор."
        )
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = ask_ai(text, user_id)
    await update.message.reply_text(reply)

# ========== ЗАПУСК ==========
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Бот-менеджер GimPrograms запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
