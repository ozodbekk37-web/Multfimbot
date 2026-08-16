import telebot
from telebot import types
import os
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@Multfilmlar2026m"

bot = telebot.TeleBot(TOKEN)

# O'Z TELEGRAM ID RAQAMINGNI SHU YERGA YOZ
ADMIN_ID = 7927602820


def subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


def subscribe_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            "📢 Kanalga obuna bo‘lish",
            url="https://t.me/Multfilmlar2026m"
        )
    )
    kb.add(
        types.InlineKeyboardButton(
            "✅ Obunani tekshirish",
            callback_data="check_sub"
        )
    )
    return kb


@bot.message_handler(commands=["start"])
def start(message):
    if not subscribed(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "👋 Botdan foydalanish uchun kanalimizga obuna bo‘ling:",
            reply_markup=subscribe_menu()
        )
        return

    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.add("🎬 Kino", "📺 Serial")

    bot.send_message(
        message.chat.id,
        "✅ Obuna tasdiqlandi!\n\nKerakli bo‘limni tanlang:",
        reply_markup=menu
    )


@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    if subscribed(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Obuna tasdiqlandi!")
        bot.send_message(
            call.message.chat.id,
            "🎉 Hammasi joyida! /start ni bosing."
        )
    else:
        bot.answer_callback_query(
            call.id,
            "❌ Avval kanalga obuna bo‘ling!",
            show_alert=True
        )


@bot.message_handler(func=lambda message: message.text == "🎬 Kino")
def kino(message):
    if not subscribed(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❌ Avval kanalga obuna bo‘ling!",
            reply_markup=subscribe_menu()
        )
        return

    bot.send_message(
        message.chat.id,
        "🎬 Kino bo‘limi\n\nHozircha kino qo‘shilmagan."
    )


@bot.message_handler(func=lambda message: message.text == "📺 Serial")
def serial(message):
    if not subscribed(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❌ Avval kanalga obuna bo‘ling!",
            reply_markup=subscribe_menu()
        )
        return

    bot.send_message(
        message.chat.id,
        "📺 Serial bo‘limi\n\nHozircha serial qo‘shilmagan."
    )


bot.infinity_polling() 
@bot.message_handler(content_types=["video"])
def get_file_id(message):
    file_id = message.video.file_id
    bot.reply_to(message, f"File ID:\n{file_id}")
