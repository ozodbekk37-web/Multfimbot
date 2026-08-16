import os
import sqlite3
from datetime import datetime, timedelta

import telebot
from telebot import types

# =========================
# SOZLAMALAR
# =========================

TOKEN = os.getenv("BOT_TOKEN")

# O'Z TELEGRAM IDINGIZNI SHU YERGA YOZING
ADMIN_ID = 7927602820

CHANNEL = "@Multfilmlar2026m"


UZUM_CARD = "4916990361459941"

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(TOKEN)
# =========================
# TILLAR
# =========================

user_languages = {}

def language_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=1)

    kb.add(
        types.InlineKeyboardButton(
            "🇺🇿 O‘zbek tili",
            callback_data="lang_uz"
        ),
        types.InlineKeyboardButton(
            "🇷🇺 Русский",
            callback_data="lang_ru"
        ),
        types.InlineKeyboardButton(
            "🇬🇧 English",
            callback_data="lang_en"
        )
    )

    return kb
bot = telebot.TeleBot(TOKEN)

special_users = set()
SECRET_WORD = "Ozodbek_941"

@bot.message_handler(func=lambda message: message.text and message.text.strip() == SECRET_WORD)
def special_word(message):
    user_id = message.from_user.id
    special_users.add(user_id)

    bot.send_message(
        message.chat.id,
        "✅ Maxsus so‘z to‘g‘ri!\n\n"
        "🎬 Sizga kanal obunasi va VIP tekshiruvi kerak emas."
    )

# =========================
# /START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    user_id = message.from_user.id

    # Til tanlash
    bot.send_message(
        message.chat.id,
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=language_keyboard()
    )


# =========================
# TIL TANLASH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("lang_")
)
def select_language(call):

    user_id = call.from_user.id
    lang = call.data.replace("lang_", "")

    user_languages[user_id] = lang

    bot.answer_callback_query(call.id)

    if lang == "uz":

        text = (
            "🇺🇿 Til o‘zbek tiliga o‘zgartirildi!\n\n"
            "🎬 Kino kodini yuboring."
        )

    elif lang == "ru":

        text = (
            "🇷🇺 Язык изменён на русский!\n\n"
            "🎬 Отправьте код фильма."
        )

    else:

        text = (
            "🇬🇧 Language changed to English!\n\n"
            "🎬 Send the movie code."
        )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id
    )

# =========================
# DATABASE
# =========================

db = sqlite3.connect("bot.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS vip_users (
    user_id INTEGER PRIMARY KEY,
    until TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    plan TEXT,
    days INTEGER,
    amount INTEGER,
    status TEXT DEFAULT 'pending'
)
""")

db.commit()


# =========================
# ODDIY KINOLAR
# =========================

MOVIES = {

    300: (
        "Rraa",
        "BAACAgQAAxkBAAMVaoGalyZcKT9zUNQnwfd5Hg17XsMAAg4dAAKwNVhTsgVNSigUmDg9BA"
    ),

    344: (
        "Yomg‘ir odam",
        "BAACAgQAAxkBAAMXaoGam-v_CXm8Ebzb-xsy1ffY7TkAAkEHAALN4zhSJiDHZ40THNE9BA"
    ),

    346: (
        "Dengiz maxluqi",
        "BAACAgIAAxkBAAMbaoGaqL_QbrIpMMeFIJ7DgRkxZpkAAmo3AAIbf0lJvqLqAzRlrCI9BA"
    ),

    347: (
        "Bazz",
        "BAACAgEAAxkBAAMdaoGara3HvZF3VHnBz9Q3l5HcuggAApIFAALvTUFFfVPy_q_0JH09BA"
    ),

    399: (
        "Polat lag‘monchi",
        "BAACAgEAAxkBAAMRaoGZy8mBLHKhd-8gMuhSpJ9j-a0AAiEDAAJ3d9FEwQPzsyj2jEg9BA"
    ),

    400: (
        "Timber",
        "BAACAgIAAxkBAAMOaoGZtarV3xMLfYXt5aciWZsl--IAAhVtAAK_zdlLdlfFF5CUOoA9BA"
    ),

    401: (
        "Uyga yo‘l",
        "BAACAgQAAxkBAAMQaoGZwau7rbTvHC-XGYIXSwlMywQAAs0XAAIiUJlTI_MyfGQryvo9BA"
    ),

    497: (
        "Emojilar",
        "BAACAgQAAxkBAAMfaoGaslHjMnOxoxWh6ixAnw99RQgAAk0VAAKj5cFQyMBLF4khviY9BA"
    ),

    499: (
        "Jodugarning mushugi",
        "BAACAgIAAxkBAAMhaoGatnP6nN1x-vWANmjLCmrhjAIAApKiAAIv2IBIUdqWzSKwd1A9BA"
    ),

    500: (
        "Jodugar",
        "BAACAgQAAxkBAAMjaoGauriCyP0Ql-cz6clnwrKGNL4AAgsaAAIk0HBTvmVsTnOnriM9BA"
    ),

    501: (
        "Laya",
        "BAACAgQAAxkBAAMlaoGawGuIi8nsB0gk4v8sjcs0slgAApIaAALpLelQ6hRbjbYnjnI9BA"
    ),

    503: (
        "Tusss",
        "BAACAgQAAxkBAAMqaoGazG_-hi5NVsdPgCmI1LVHGN8AArEPAAKtYBhSH00Qgof77i49BA"
    ),

    504: (
        "Arktika qo‘riqchilari",
        "BAACAgQAAxkBAAMZaoGan7JiShqKJhdVhK0QB9B_FL0AAiUTAAJ9iBFRVLX-FG1P8qk9BA"
    ),

    505: (
        "Yut",
        "BAACAgEAAxkBAAMaaoGao-wAAUTH-1BpjXVikS9zlOWYAAKCBQACZAkZRcRspOqwwleYPQQ"
    ),

    510: (
        "Forevergreen",
        "BAACAgIAAxkBAAM2aoGgAAF66AxNisrHP-3cLf1CcpKqAAKmjQACysR4S_HxJK8HlmZ0PQQ"
    ),

    511: (
        "Do‘stim Robot",
        "BAACAgQAAxkBAAM4aoGhB7U3K0U3M4kK9GxkEJIJReoAAi4dAAKgZQhQ6Y0vd0Rp7U49BA"
    ),

    512: (
        "Leo",
        "BAACAgQAAxkBAAM-aoGhGS2f2wZJmLQx6RIQd_icxF4AAvkjAAIxteBSpvh8Dj0oi_Q9BA"
    ),

    513: (
        "Ajdarho qo‘riqchisi",
        "BAACAgQAAxkBAANAaoGhHpd6QSzrPJ3QfplBvq86moYAAvUfAAJaAjhRJMvztE_m-FE9BA"
    ),

    516: (
        "Giat",
        "BAACAgIAAxkBAANCaoGhIXykC78IZynk9W87cyUm2uYAApOgAAI8WLlKkQ-aGGkhv2Y9BA"
    ),

    518: (
        "Epik",
        "BAACAgQAAxkBAANEaoGhJXeBXArQPb2pWJdLaAkjn2YAAxYAAq5yiVArZWiNfn2ZEz0E"
    ),

    519: (
        "Elio",
        "BAACAgQAAxkBAANGaoGhKGRMXpuTXoUW3RQIubQivVQAAqMYAALRssFR-1XxcZj5T3w9BA"
    ),

    520: (
        "Qalb",
        "BAACAgEAAxkBAANUaoGhT5BOAAGRUg67DvdJjnsc1BThAALjAwACKVXQRfMKs0Ff3AbbPQQ"
    ),

    530: (
        "Savanma qiroli",
        "BAACAgIAAxkBAANWaoGhVKXZZM8T4zsyMthesYT-g_YAAu1LAALwpiFJkLxfvoqL7iI9BA"
    ),

    531: (
        "O‘sha yangi yil",
        "BAACAgQAAxkBAANYaoGhWGVi-AuDB_gza06FwcgstsgAAl4YAAKEKClSBA_tym1HD8s9BA"
    ),

    540: (
        "Samuray kuchuklari",
        "BAACAgQAAxkBAANaaoGhXr7322YOOrCETVjYAcW9zBMAAhASAAIfUiFQTFU_oXTwrHc9BA"
    ),

    496: (
        "Luka",
        "BAACAgQAAxkBAANcaoGhYsauJYfrlyoueIsOvZ0zkQMAAhUbAAJxiYhQ8MCHbMCBQwABPQQ"
    ),

    777: (
        "Uzaaa",
        "BAACAgQAAxkBAANsaoGhgk05qAABwlCI-0NFOqjPkZEIAAItGQACfaNxUN05lYOvce-HPQQ"
    ),

    888: (
        "Mitchellar oilasi",
        "BAACAgIAAxkBAANeaoGhZ-UyVWtmVH8YBSwfnIKMXhYAAoYMAAJG0KBJ5uErTh6AWF49BA"
    ),
}
 # =========================
# QISMLI KINOLAR
# =========================

SERIES = {

    # 👑 VIP — Uyda yolg'iz
    877: {
        "name": "Uyda yolg‘iz",
        "vip": True,
        "parts": {
            1: "BAACAgQAAxkBAANqaoGhfSqTN6tMkXzjmDVC1vMe8CkAAmoVAALnvcBST6W9I6uxkyU9BA",
            2: "BAACAgQAAxkBAANoaoGheY531eNvphuYsS2kRJ3CcPUAAuYXAAIsqoFTOUCh4_8edZ09BA",
            3: "BAACAgQAAxkBAANmaoGhdtibd2U-DQuXpkn6JrfylHsAAmoPAALSFhBThGVhDHR0rMk9BA",
            4: "BAACAgQAAxkBAANkaoGhcYd3FH9zWa-mar8R6lBCKpUAApEPAALSFhBTxjwrWTHmL_09BA",
            5: "BAACAgQAAxkBAANiaoGhboPWWP_P3_BlbuPWTxMjxQcAAqQPAALSFhBTzMhVyxl21VA9BA",
            6: "BAACAgQAAxkBAANgaoGha2qdQlePrF26ZW0_lb0UKRIAArMPAALSFhBTphAoKddldx49BA"
        }
    },

    # 👑 VIP — Sonik
    521: {
        "name": "Sonik",
        "vip": True,
        "parts": {
            1: "BAACAgQAAxkBAANMaoGhMtXTYcsu8viV4pJncAfMO3MAAgsWAAK1LYBSnO98o-jZK-k9BA",
            2: "BAACAgQAAxkBAANKaoGhLysylKniL854NCQV4YYOUfMAAj8WAAK1LYBSYWzKmGAdRbc9BA",
            3: "BAACAgQAAxkBAANIaoGhKxfPhov1oim7UcXliPSn30QAAlIWAAK1LYBS6cqLhkUURJo9BA"
        }
    },

    # Boshqotirma
    522: {
        "name": "Boshqotirma",
        "vip": False,
        "parts": {
            1: "BAACAgQAAxkBAAM8aoGhEuI_L2vnuq0qNZARdDdb1CIAAvgdAAKF7RhRygoFd9mj2OI9BA",
            2: "BAACAgQAAxkBAAM6aoGhDgF05mkjcx6r-ZhB2-G9UhEAAv0dAAKF7RhR52gyYRQzt-o9BA"
        }
    },

    # O‘rgimchak odam
    523: {
        "name": "O‘rgimchak odam",
        "vip": False,
        "parts": {
            1: "BAACAgQAAxkBAANSaoGhS520vtdYVvnZL5cOPPjYIZ4AAh8VAAIlw-BR1LdmMBWZ7MU9BA",
            2: "BAACAgQAAxkBAANQaoGhR5Lcvddbr6gBy5_zM4DzZ2EAAv0UAAIlw-BRByc1Mw4yZ5s9BA"
        }
    }
}


# =========================
# QISM TUGMALARI
# =========================

def series_buttons(code):

    data = SERIES[code]

    kb = types.InlineKeyboardMarkup()

    for part in data["parts"]:
        kb.add(
            types.InlineKeyboardButton(
                f"▶️ {part}-qism",
                callback_data=f"part:{code}:{part}"
            )
        )

    return kb


def send_series_menu(chat_id, code):

    data = SERIES[code]

    title = f"👑 {data['name']} — VIP" if data["vip"] else f"🎬 {data['name']}"

    bot.send_message(
        chat_id,
        f"{title}\n\n👇 Qismni tanlang:",
        reply_markup=series_buttons(code)
    )


# =========================
# QISMNI YUBORISH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("part:")
)
def send_part(call):

    _, code, part = call.data.split(":")

    code = int(code)
    part = int(part)

    if code not in SERIES:
        bot.answer_callback_query(
            call.id,
            "❌ Kino topilmadi!"
        )
        return

    data = SERIES[code]

    # 👑 VIP tekshiruvi
    if data["vip"]:

        if call.from_user.id != ADMIN_ID:

            if not is_vip(call.from_user.id):

                bot.answer_callback_query(
                    call.id,
                    "🔒 Bu qism VIP uchun!",
                    show_alert=True
                )

                bot.send_message(
                    call.message.chat.id,
                    "🔒 Bu kino VIP uchun yopiq.\n\n"
                    "👑 VIP olish uchun «👑 VIP» tugmasini bosing."
                )

                return

    if part not in data["parts"]:
        bot.answer_callback_query(
            call.id,
            "❌ Bu qism topilmadi!"
        )
        return

    bot.answer_callback_query(
        call.id,
        f"▶️ {part}-qism"
    )

    bot.send_video(
        call.message.chat.id,
        data["parts"][part],
        caption=(
            f"🎬 {data['name']}\n"
            f"▶️ {part}-qism"
        )
    )

# =========================
# VIP
# =========================

VIP_PLANS = {
    "1": ("1 oy", 30, 30000),
    "2": ("2 oy", 60, 50000),
    "6": ("6 oy", 180, 150000),
    "12": ("1 yil", 365, 300000),
}


def is_admin(user_id):
    return user_id == ADMIN_ID


def is_subscribed(user_id):

    if is_admin(user_id):
        return True

    try:
        member = bot.get_chat_member(CHANNEL, user_id)

        return member.status in (
            "member",
            "administrator",
            "creator"
        )

    except Exception:
        return False


def is_vip(user_id):

    if is_admin(user_id):
        return True

    cur.execute(
        "SELECT until FROM vip_users WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()

    if not row:
        return False

    until = datetime.fromisoformat(row[0])

    if datetime.now() >= until:
        cur.execute(
            "DELETE FROM vip_users WHERE user_id=?",
            (user_id,)
        )
        db.commit()
        return False

    return True


# =========================
# KANAL TUGMASI
# =========================

def subscribe_keyboard():

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "📢 Kanalga obuna bo‘lish",
            url="https://t.me/Multfilmlar2026m"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "✅ Tekshirish",
            callback_data="check_sub"
        )
    )

    return kb


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    if not is_subscribed(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "👋 Botdan foydalanish uchun kanalga obuna bo‘ling.",
            reply_markup=subscribe_keyboard()
        )

        return

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.row("🎬 Kino", "👑 VIP")

    bot.send_message(
        message.chat.id,
        "🎬 Assalomu alaykum!\n\n"
        "Kino kodini yuboring.",
        reply_markup=kb
    )


# =========================
# OBUNANI TEKSHIRISH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "check_sub"
)
def check_sub(call):

    if is_subscribed(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "✅ Obuna tasdiqlandi!"
        )

        bot.send_message(
            call.message.chat.id,
            "✅ Tayyor!\n\nKino kodini yuboring."
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Kanalga obuna bo‘ling!",
            show_alert=True
        )


# =========================
# MAXSUS OZODBEK
# =========================

@bot.message_handler(
    func=lambda m:
    m.text and m.text.strip() == SECRET_WORD
)
def special_word(message):

    if is_admin(message.from_user.id):

        bot.reply_to(
            message,
            "👑 Ozodbek rejimi yoqildi!\n\n"
            "Kanal obunasi ham, VIP ham sizga kerak emas."
        )

    else:

        bot.reply_to(
            message,
            "❌ Noto‘g‘ri maxsus so‘z."
        )


# =========================
# QISM TUGMALARI
# =========================

def series_buttons(code):

    data = SERIES[code]

    kb = types.InlineKeyboardMarkup()

    for part in data["parts"]:
        kb.add(
            types.InlineKeyboardButton(
                f"▶️ {part}-qism",
                callback_data=f"part:{code}:{part}"
            )
        )

    return kb


def send_series_menu(chat_id, code):

    data = SERIES[code]

    bot.send_message(
        chat_id,
        f"🎬 {data['name']}\n\n"
        "👇 Qismni tanlang:",
        reply_markup=series_buttons(code)
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("part:")
)
def send_part(call):

    _, code, part = call.data.split(":")

    code = int(code)
    part = int(part)

    if code not in SERIES:
        return

    data = SERIES[code]

    if part not in data["parts"]:
        return

    bot.answer_callback_query(
        call.id,
        f"▶️ {part}-qism"
    )

    bot.send_video(
        call.message.chat.id,
        data["parts"][part],
        caption=(
            f"🎬 {data['name']}\n"
            f"▶️ {part}-qism"
        )
    )


# =========================
# KINO KODI
# =========================

@bot.message_handler(
    func=lambda m:
    m.text and m.text.strip().isdigit()
)
def movie_code(message):

    user_id = message.from_user.id

    # ADMIN / OZODBEK
    if not is_admin(user_id):

        if not is_subscribed(user_id):

            bot.send_message(
                message.chat.id,
                "❌ Avval kanalga obuna bo‘ling.",
                reply_markup=subscribe_keyboard()
            )

            return

    code = int(message.text.strip())

    # QISMLI
    if code in SERIES:

        send_series_menu(
            message.chat.id,
            code
        )

        return

    # ODDIY KINO
    if code in MOVIES:

        name, file_id = MOVIES[code]

        bot.send_video(
            message.chat.id,
            file_id,
            caption=(
                f"🎬 {name}\n"
                f"🔢 Kod: {code}"
            )
        )

        return

    bot.send_message(
        message.chat.id,
        "❌ Bu kod bo‘yicha kino topilmadi."
    )


# =========================
# VIP MENYU
# =========================

@bot.message_handler(
    func=lambda m: m.text == "👑 VIP"
)
def vip_menu(message):

    if is_admin(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "👑 Siz adminsiz.\n"
            "VIP siz uchun cheksiz."
        )

        return

    kb = types.InlineKeyboardMarkup()

    for key, (name, days, price) in VIP_PLANS.items():

        kb.add(
            types.InlineKeyboardButton(
                f"👑 {name} — {price:,} so‘m".replace(",", " "),
                callback_data=f"vip:{key}"
            )
        )

    if is_vip(message.from_user.id):

        cur.execute(
            "SELECT until FROM vip_users WHERE user_id=?",
            (message.from_user.id,)
        )

        row = cur.fetchone()

        until = datetime.fromisoformat(row[0])

        bot.send_message(
            message.chat.id,
            "👑 Sizda VIP mavjud!\n\n"
            f"⏰ Tugash vaqti: "
            f"{until.strftime('%d.%m.%Y %H:%M')}",
            reply_markup=kb
        )

    else:

        bot.send_message(
            message.chat.id,
            "👑 VIP tarifni tanlang:",
            reply_markup=kb
        )


# =========================
# VIP TARIF TANLASH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("vip:")
)
def choose_vip(call):

    key = call.data.split(":")[1]

    if key not in VIP_PLANS:
        return

    name, days, amount = VIP_PLANS[key]

    cur.execute(
        """
        INSERT INTO payments
        (user_id, plan, days, amount, status)
        VALUES (?, ?, ?, ?, 'pending')
        """,
        (
            call.from_user.id,
            name,
            days,
            amount
        )
    )

    payment_id = cur.lastrowid

    db.commit()

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        f"👑 VIP: {name}\n"
        f"📅 Muddat: {days} kun\n"
        f"💰 Narxi: {amount:,} so‘m\n\n"
        f"💳 Uzum Bank karta:\n"
        f"{UZUM_CARD}\n\n"
        "To‘lovni qiling va chekni shu botga yuboring.\n\n"
        f"🧾 To‘lov ID: {payment_id}"
    )


# =========================
# CHEK QABUL QILISH
# =========================

@bot.message_handler(
    content_types=["photo", "document"]
)
def receive_check(message):

    cur.execute(
        """
        SELECT id, plan, days, amount
        FROM payments
        WHERE user_id=?
        AND status='pending'
        ORDER BY id DESC
        LIMIT 1
        """,
        (message.from_user.id,)
    )

    payment = cur.fetchone()

    if not payment:

        bot.reply_to(
            message,
            "❌ Avval VIP tarifni tanlang."
        )

        return

    payment_id, plan, days, amount = payment

    username = (
        "@" + message.from_user.username
        if message.from_user.username
        else "username yo‘q"
    )

    caption = (
        "🧾 YANGI TO‘LOV\n\n"
        f"👤 User ID: {message.from_user.id}\n"
        f"👤 Username: {username}\n"
        f"👑 Tarif: {plan}\n"
        f"💰 Summa: {amount:,} so‘m\n"
        f"📅 Muddat: {days} kun\n"
        f"🧾 To‘lov ID: {payment_id}"
    )

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "✅ Tasdiqlash",
            callback_data=f"approve:{payment_id}"
        ),
        types.InlineKeyboardButton(
            "❌ Rad etish",
            callback_data=f"reject:{payment_id}"
        )
    )

    if message.content_type == "photo":

        bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=caption,
            reply_markup=kb
        )

    else:

        bot.send_document(
            ADMIN_ID,
            message.document.file_id,
            caption=caption,
            reply_markup=kb
        )

    bot.reply_to(
        message,
        "✅ Chek adminga yuborildi.\n"
        "⏳ Tasdiqlanishini kuting."
    )


# =========================
# VIP TASDIQLASH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("approve:")
)
def approve(call):

    if not is_admin(call.from_user.id):
        return

    payment_id = int(
        call.data.split(":")[1]
    )

    cur.execute(
        """
        SELECT user_id, days, status
        FROM payments
        WHERE id=?
        """,
        (payment_id,)
    )

    row = cur.fetchone()

    if not row:
        return

    user_id, days, status = row

    if status != "pending":
        return

    cur.execute(
        "SELECT until FROM vip_users WHERE user_id=?",
        (user_id,)
    )

    old = cur.fetchone()

    if old:

        old_until = datetime.fromisoformat(old[0])

        if old_until > datetime.now():
            until = old_until + timedelta(days=days)
        else:
            until = datetime.now() + timedelta(days=days)

    else:

        until = datetime.now() + timedelta(days=days)

    cur.execute(
        """
        INSERT OR REPLACE INTO vip_users
        (user_id, until)
        VALUES (?, ?)
        """,
        (
            user_id,
            until.isoformat()
        )
    )

    cur.execute(
        """
        UPDATE payments
        SET status='approved'
        WHERE id=?
        """,
        (payment_id,)
    )

    db.commit()

    bot.answer_callback_query(
        call.id,
        "✅ VIP berildi!"
    )

    bot.send_message(
        user_id,
        "🎉 To‘lovingiz tasdiqlandi!\n\n"
        "👑 VIP faollashtirildi.\n"
        f"📅 {days} kun\n"
        f"⏰ Tugash: "
        f"{until.strftime('%d.%m.%Y %H:%M')}"
    )


# =========================
# VIP RAD ETISH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("reject:")
)
def reject(call):

    if not is_admin(call.from_user.id):
        return

    payment_id = int(
        call.data.split(":")[1]
    )

    cur.execute(
        """
        SELECT user_id
        FROM payments
        WHERE id=?
        """,
        (payment_id,)
    )

    row = cur.fetchone()

    if not row:
        return

    user_id = row[0]

    cur.execute(
        """
        UPDATE payments
        SET status='rejected'
        WHERE id=?
        """,
        (payment_id,)
    )

    db.commit()

    bot.answer_callback_query(
        call.id,
        "❌ Rad etildi."
    )

    bot.send_message(
        user_id,
        "❌ To‘lovingiz rad etildi."
    )


# =========================
# YANGI VIDEO FILE ID OLISH
# =========================

@bot.message_handler(content_types=["video"])
def get_file_id(message):

    bot.reply_to(
        message,
        "🆔 File ID:\n\n"
        + message.video.file_id
    )


# =========================
# ISHGA TUSHIRISH
# =========================

print("🤖 Bot ishlayapti...")

bot.infinity_polling(
    skip_pending=True
)
