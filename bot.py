import os
import sqlite3
from datetime import datetime, timedelta

import telebot
from telebot import types


# =========================
# SOZLAMALAR
# =========================

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 7927602820

CHANNEL = "@Multfilmlar2026m"

UZUM_CARD = "4916990361459941"


if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")


bot = telebot.TeleBot(TOKEN)

# =========================
# TIL TANLASH + START
# =========================

user_languages = {}


def language_keyboard():

    kb = types.InlineKeyboardMarkup(row_width=1)

    kb.add(
        types.InlineKeyboardButton(
            "🇺🇿 O‘zbek tili",
            callback_data="lang_uz"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "🇷🇺 Русский",
            callback_data="lang_ru"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "🇬🇧 English",
            callback_data="lang_en"
        )
    )

    return kb


@bot.message_handler(commands=["start"])
def start(message):

    bot.send_message(
        message.chat.id,
        "🌐 Tilni tanlang:",
        reply_markup=language_keyboard()
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("lang_")
)
def select_language(call):

    user_id = call.from_user.id

    lang = call.data.replace("lang_", "")

    user_languages[user_id] = lang

    bot.answer_callback_query(call.id)

    # Kanal tekshiruvi
    if not is_admin(user_id):

        if not is_subscribed(user_id):

            bot.edit_message_text(
                "👋 Botdan foydalanish uchun avval kanalga obuna bo‘ling.",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=subscribe_keyboard()
            )

            return

    # =========================
    # ASOSIY MENYU
    # =========================

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.row(
        "🎬 Kino",
        "👑 VIP"
    )

    if lang == "uz":

        text = (
            "🇺🇿 O‘zbek tili tanlandi!\n\n"
            "🎬 Assalomu alaykum!\n\n"
            "🔢 Kino kodini yuboring."
        )

    elif lang == "ru":

        text = (
            "🇷🇺 Русский язык выбран!\n\n"
            "🎬 Отправьте код фильма."
        )

    else:

        text = (
            "🇬🇧 English selected!\n\n"
            "🎬 Send the movie code."
        )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id
    )

    bot.send_message(
        call.message.chat.id,
        "👇 Menyu:",
        reply_markup=kb
    )



# =========================
# DATABASE
# =========================

db = sqlite3.connect(
    "bot.db",
    check_same_thread=False
)

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


# YANGI KINOLAR UCHUN
cur.execute("""
CREATE TABLE IF NOT EXISTS admin_movies (
    code INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    file_id TEXT NOT NULL
)
""")


db.commit()
cur.execute("""
CREATE TABLE IF NOT EXISTS required_channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT UNIQUE NOT NULL
)
""")

db.commit()

# =========================
# ADMIN KINO HOLATI
# =========================

admin_movie = {}
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

    521: {
        "name": "Sonik",
        "vip": True,
        "parts": {
            1: "BAACAgQAAxkBAANMaoGhMtXTYcsu8viV4pJncAfMO3MAAgsWAAK1LYBSnO98o-jZK-k9BA",
            2: "BAACAgQAAxkBAANKaoGhLysylKniL854NCQV4YYOUfMAAj8WAAK1LYBSYWzKmGAdRbc9BA",
            3: "BAACAgQAAxkBAANIaoGhKxfPhov1oim7UcXliPSn30QAAlIWAAK1LYBS6cqLhkUURJo9BA"
        }
    },

    522: {
        "name": "Boshqotirma",
        "vip": False,
        "parts": {
            1: "BAACAgQAAxkBAAM8aoGhEuI_L2vnuq0qNZARdDdb1CIAAvgdAAKF7RhRygoFd9mj2OI9BA",
            2: "BAACAgQAAxkBAAM6aoGhDgF05mkjcx6r-ZhB2-G9UhEAAv0dAAKF7RhR52gyYRQzt-o9BA"
        }
    },

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
# KANAL QO‘SHISH / O‘CHIRISH
# FAQAT ADMIN
# =========================

channel_add_state = {}


# /channels
@bot.message_handler(commands=["channels"])
def channels_menu(message):

    if not is_admin(message.from_user.id):
        return

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "➕ Kanal qo‘shish",
            callback_data="channel_add"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "🗑 Kanal o‘chirish",
            callback_data="channel_delete"
        )
    )

    bot.send_message(
        message.chat.id,
        "📢 Kanal boshqaruvi:",
        reply_markup=kb
    )


# =========================
# KANAL QO‘SHISH
# =========================
@bot.message_handler(
    func=lambda m: m.from_user.id in channel_add_state
)
def save_channel(message):

    if not is_admin(message.from_user.id):
        return

    channel = message.text.strip()

    # Ochiq kanal: @username
    # Maxfiy kanal: -1001234567890

    if not (
        channel.startswith("@")
        or channel.startswith("-100")
    ):

        bot.reply_to(
            message,
            "❌ Kanal noto‘g‘ri.\n\n"
            "📢 Ochiq kanal:\n"
            "@Multfilmlar2026m\n\n"
            "🔒 Maxfiy kanal:\n"
            "-1001234567890"
        )
        return

    try:

        cur.execute(
            "INSERT INTO required_channels (channel) VALUES (?)",
            (channel,)
        )

        db.commit()

        del channel_add_state[message.from_user.id]

        bot.reply_to(
            message,
            f"✅ Kanal qo‘shildi!\n\n"
            f"📢 {channel}"
        )

    except sqlite3.IntegrityError:

        bot.reply_to(
            message,
            "❌ Bu kanal allaqachon qo‘shilgan."
        )

# =========================
# KANAL O‘CHIRISH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "channel_delete"
)
def channel_delete(call):

    if not is_admin(call.from_user.id):
        return

    cur.execute(
        "SELECT id, channel FROM required_channels"
    )

    channels = cur.fetchall()

    if not channels:

        bot.answer_callback_query(call.id)

        bot.send_message(
            call.message.chat.id,
            "📭 Hozircha kanal qo‘shilmagan."
        )

        return

    kb = types.InlineKeyboardMarkup()

    for channel_id, channel in channels:

        kb.add(
            types.InlineKeyboardButton(
                f"🗑 {channel}",
                callback_data=f"delete_channel:{channel_id}"
            )
        )

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "🗑 O‘chirmoqchi bo‘lgan kanalni tanlang:",
        reply_markup=kb
    )


# =========================
# TANLANGAN KANALNI O‘CHIRISH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("delete_channel:")
)
def delete_channel(call):

    if not is_admin(call.from_user.id):
        return

    channel_id = int(
        call.data.split(":")[1]
    )

    cur.execute(
        "SELECT channel FROM required_channels WHERE id=?",
        (channel_id,)
    )

    row = cur.fetchone()

    if not row:

        bot.answer_callback_query(
            call.id,
            "❌ Kanal topilmadi!"
        )
        return

    channel = row[0]

    cur.execute(
        "DELETE FROM required_channels WHERE id=?",
        (channel_id,)
    )

    db.commit()

    bot.answer_callback_query(
        call.id,
        "✅ Kanal o‘chirildi!"
    )

    bot.send_message(
        call.message.chat.id,
        f"🗑 Kanal o‘chirildi:\n\n"
        f"📢 {channel}"
    )
# =========================
# ADMIN KINO QO‘SHISH
# =========================

admin_add_state = {}


def add_movie_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.add(
        types.InlineKeyboardButton(
            "📺 Serial",
            callback_data="add_serial_yes"
        ),
        types.InlineKeyboardButton(
            "🎬 Oddiy kino",
            callback_data="add_serial_no"
        )
    )

    return kb


def vip_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.add(
        types.InlineKeyboardButton(
            "👑 VIP",
            callback_data="add_vip_yes"
        ),
        types.InlineKeyboardButton(
            "🆓 Oddiy",
            callback_data="add_vip_no"
        )
    )

    return kb


# =========================
# /addmovie
# =========================

@bot.message_handler(commands=["addmovie"])
def add_movie_start(message):

    if not is_admin(message.from_user.id):
        bot.reply_to(
            message,
            "❌ Bu buyruq faqat admin uchun."
        )
        return

    admin_add_state[message.from_user.id] = {
        "step": "name"
    }

    bot.reply_to(
        message,
        "🎬 Yangi kino qo‘shamiz.\n\n"
        "1️⃣ Kino nomini yozing:"
    )


# =========================
# KINO NOMI
# =========================

@bot.message_handler(
    func=lambda m:
    m.from_user.id in admin_add_state
    and admin_add_state[m.from_user.id]["step"] == "name"
)
def add_movie_name(message):

    name = message.text.strip()

    if not name:
        bot.reply_to(
            message,
            "❌ Kino nomini yozing."
        )
        return

    admin_add_state[message.from_user.id] = {
        "step": "code",
        "name": name
    }

    bot.reply_to(
        message,
        f"🎬 Nomi: {name}\n\n"
        "2️⃣ Kino kodini yozing:"
    )


# =========================
# KINO KODI
# =========================

@bot.message_handler(
    func=lambda m:
    m.from_user.id in admin_add_state
    and admin_add_state[m.from_user.id]["step"] == "code"
)
def add_movie_code(message):

    if not message.text.isdigit():

        bot.reply_to(
            message,
            "❌ Kod faqat raqam bo‘lsin.\n\n"
            "Masalan: 600"
        )
        return

    code = int(message.text)

    if code in MOVIES or code in SERIES:

        bot.reply_to(
            message,
            "❌ Bu kod allaqachon mavjud.\n"
            "Boshqa kod kiriting."
        )
        return

    data = admin_add_state[message.from_user.id]

    data["code"] = code
    data["step"] = "type"

    bot.send_message(
        message.chat.id,
        f"🎬 Kino: {data['name']}\n"
        f"🔢 Kod: {code}\n\n"
        "3️⃣ Bu serialmi yoki oddiy kinomi?",
        reply_markup=add_movie_keyboard()
    )


# =========================
# SERIAL / ODDIY
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data in (
        "add_serial_yes",
        "add_serial_no"
    )
)
def choose_movie_type(call):

    if not is_admin(call.from_user.id):
        return

    data = admin_add_state.get(call.from_user.id)

    if not data:
        bot.answer_callback_query(
            call.id,
            "❌ Buyruq muddati tugagan."
        )
        return

    if call.data == "add_serial_yes":

        data["serial"] = True
        data["step"] = "parts_count"

        bot.answer_callback_query(call.id)

        bot.send_message(
            call.message.chat.id,
            "📺 Serial tanlandi.\n\n"
            "4️⃣ Nechta qism bor?\n\n"
            "Masalan: 10"
        )

    else:

        data["serial"] = False
        data["step"] = "video"

        bot.answer_callback_query(call.id)

        bot.send_message(
            call.message.chat.id,
            "🎬 Oddiy kino tanlandi.\n\n"
            "5️⃣ Endi kino videosini yuboring."
        )


# =========================
# QISM SONI
# =========================

@bot.message_handler(
    func=lambda m:
    m.from_user.id in admin_add_state
    and admin_add_state[m.from_user.id]["step"] == "parts_count"
)
def add_parts_count(message):

    if not message.text.isdigit():

        bot.reply_to(
            message,
            "❌ Faqat raqam yozing.\n"
            "Masalan: 6"
        )
        return

    count = int(message.text)

    if count < 1 or count > 100:

        bot.reply_to(
            message,
            "❌ Qism soni 1 dan 100 gacha bo‘lsin."
        )
        return

    data = admin_add_state[message.from_user.id]

    data["parts_count"] = count
    data["current_part"] = 1
    data["parts"] = {}
    data["step"] = "serial_video"

    bot.reply_to(
        message,
        f"📺 Jami {count} ta qism.\n\n"
        "▶️ 1-qism videosini yuboring."
    )


# =========================
# ODDIY KINO VIDEO
# =========================

@bot.message_handler(
    content_types=["video"],
    func=lambda m:
    m.from_user.id in admin_add_state
    and admin_add_state[m.from_user.id]["step"] == "video"
)
def add_normal_video(message):

    data = admin_add_state[message.from_user.id]

    data["file_id"] = message.video.file_id
    data["step"] = "vip"

    bot.send_message(
        message.chat.id,
        "✅ Video qabul qilindi.\n\n"
        "6️⃣ Bu kino VIPmi yoki oddiymi?",
        reply_markup=vip_keyboard()
    )


# =========================
# SERIAL QISMLARI
# =========================

@bot.message_handler(
    content_types=["video"],
    func=lambda m:
    m.from_user.id in admin_add_state
    and admin_add_state[m.from_user.id]["step"] == "serial_video"
)
def add_serial_video(message):

    data = admin_add_state[message.from_user.id]

    part = data["current_part"]

    data["parts"][part] = message.video.file_id

    total = data["parts_count"]

    if part < total:

        data["current_part"] += 1

        bot.reply_to(
            message,
            f"✅ {part}-qism saqlandi.\n\n"
            f"▶️ Endi {part + 1}-qism videosini yuboring."
        )

        return

    data["step"] = "vip"

    bot.send_message(
        message.chat.id,
        f"✅ Barcha {total} ta qism qabul qilindi!\n\n"
        "6️⃣ Bu serial VIPmi yoki oddiymi?",
        reply_markup=vip_keyboard()
    )


# =========================
# VIP / ODDIY TANLASH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data in (
        "add_vip_yes",
        "add_vip_no"
    )
)
def choose_movie_vip(call):

    if not is_admin(call.from_user.id):
        return

    data = admin_add_state.get(call.from_user.id)

    if not data:
        bot.answer_callback_query(
            call.id,
            "❌ Ma'lumot topilmadi."
        )
        return

    vip = call.data == "add_vip_yes"

    data["vip"] = vip

    name = data["name"]
    code = data["code"]

    # =====================
    # SERIALNI SAQLASH
    # =====================

    if data["serial"]:

        SERIES[code] = {
            "name": name,
            "vip": vip,
            "parts": data["parts"]
        }

        movie_type = "📺 Serial"

    # =====================
    # ODDIY KINONI SAQLASH
    # =====================

    else:

        MOVIES[code] = (
            name,
            data["file_id"]
        )

        movie_type = "🎬 Oddiy kino"

    del admin_add_state[call.from_user.id]

    bot.answer_callback_query(
        call.id,
        "✅ Kino qo‘shildi!"
    )

    bot.send_message(
        call.message.chat.id,
        "🎉 KINO MUVAFFAQIYATLI QO‘SHILDI!\n\n"
        f"🎬 Nomi: {name}\n"
        f"🔢 Kodi: {code}\n"
        f"{movie_type}\n"
        f"👑 VIP: {'Ha' if vip else 'Yo‘q'}\n\n"
        "✅ Endi foydalanuvchi kodni yuborsa,\n"
        "kino avtomatik chiqadi."
    )    
# =========================
# KINO O‘CHIRISH — FAQAT ADMIN
# =========================

@bot.message_handler(commands=["delmovie"])
def delete_movie_start(message):

    if not is_admin(message.from_user.id):
        bot.reply_to(
            message,
            "❌ Bu buyruq faqat admin uchun."
        )
        return

    bot.reply_to(
        message,
        "🗑 Kino o‘chirish\n\n"
        "O‘chirmoqchi bo‘lgan kino kodini yuboring.\n\n"
        "Masalan: 600"
    )


@bot.message_handler(
    func=lambda m:
    is_admin(m.from_user.id)
    and m.text
    and m.text.strip().isdigit()
)
def delete_movie(message):

    code = int(message.text.strip())

    # Oddiy kino
    if code in MOVIES:

        name = MOVIES[code][0]

        del MOVIES[code]

        bot.reply_to(
            message,
            f"✅ Kino o‘chirildi!\n\n"
            f"🎬 Nomi: {name}\n"
            f"🔢 Kodi: {code}"
        )

        return

    # Serial
    if code in SERIES:

        name = SERIES[code]["name"]

        del SERIES[code]

        bot.reply_to(
            message,
            f"✅ Serial o‘chirildi!\n\n"
            f"📺 Nomi: {name}\n"
            f"🔢 Kodi: {code}"
        )

        return

    bot.reply_to(
        message,
        "❌ Bunday kodli kino yoki serial topilmadi."
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
            "✅ Tayyor!\n\n"
            "🔢 Kino kodini yuboring."
        )

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Avval kanalga obuna bo‘ling!",
            show_alert=True
        )


# =========================
# QISMLI KINO TUGMALARI
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

    title = (
        f"👑 {data['name']} — VIP"
        if data["vip"]
        else f"🎬 {data['name']}"
    )

    bot.send_message(
        chat_id,
        f"{title}\n\n"
        "👇 Qismni tanlang:",
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

    # VIP tekshirish
    if data["vip"]:

        if not is_admin(call.from_user.id):

            if not is_vip(call.from_user.id):

                bot.answer_callback_query(
                    call.id,
                    "🔒 Bu kino VIP uchun!",
                    show_alert=True
                )

                return

    if part not in data["parts"]:

        bot.answer_callback_query(
            call.id,
            "❌ Qism topilmadi!"
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
# KINO KODI
# =========================

@bot.message_handler(
    func=lambda m:
    m.text and m.text.strip().isdigit()
)
def movie_code(message):

    user_id = message.from_user.id

    # Admin kanal tekshiruvisiz ishlatadi
    if not is_admin(user_id):

        if not is_subscribed(user_id):

            bot.send_message(
                message.chat.id,
                "❌ Avval kanalga obuna bo‘ling.",
                reply_markup=subscribe_keyboard()
            )

            return

    code = int(message.text.strip())

    # QISMLI KINO
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

    # KOD TOPILMASA
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

    user_id = message.from_user.id

    # ADMIN
    if is_admin(user_id):

        bot.send_message(
            message.chat.id,
            "👑 Siz adminsiz!\n\n"
            "♾ VIP siz uchun cheksiz."
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

    if is_vip(user_id):

        cur.execute(
            "SELECT until FROM vip_users WHERE user_id=?",
            (user_id,)
        )

        row = cur.fetchone()

        if row:

            until = datetime.fromisoformat(row[0])

            bot.send_message(
                message.chat.id,
                "👑 Sizda VIP mavjud!\n\n"
                f"⏰ Tugash vaqti:\n"
                f"{until.strftime('%d.%m.%Y %H:%M')}",
                reply_markup=kb
            )

        return

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
        f"💳 Uzum Bank:\n"
        f"{UZUM_CARD}\n\n"
        "💸 To‘lovni amalga oshiring.\n"
        "🧾 Keyin chekni shu botga yuboring.\n\n"
        f"🆔 To‘lov ID: {payment_id}"
    )
    # =========================
# CHEK QABUL QILISH
# =========================

@bot.message_handler(content_types=["photo", "document"])
def receive_check(message):

    user_id = message.from_user.id

    cur.execute(
        """
        SELECT id, plan, days, amount
        FROM payments
        WHERE user_id=?
        AND status='pending'
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    )

    payment = cur.fetchone()

    if not payment:
        bot.reply_to(
            message,
            "❌ Avval 👑 VIP tarifni tanlang."
        )
        return

    payment_id, plan, days, amount = payment

    username = (
        "@" + message.from_user.username
        if message.from_user.username
        else "username yo‘q"
    )

    caption = (
        "🧾 YANGI VIP TO‘LOV\n\n"
        f"👤 User ID: {user_id}\n"
        f"👤 Username: {username}\n"
        f"👑 Tarif: {plan}\n"
        f"💰 Summa: {amount:,} so‘m\n"
        f"📅 Muddat: {days} kun\n"
        f"🆔 To‘lov ID: {payment_id}"
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

    elif message.content_type == "document":

        bot.send_document(
            ADMIN_ID,
            message.document.file_id,
            caption=caption,
            reply_markup=kb
        )

    bot.reply_to(
        message,
        "✅ Chek adminga yuborildi.\n\n"
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

    payment_id = int(call.data.split(":")[1])

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
        bot.answer_callback_query(
            call.id,
            "❌ To‘lov topilmadi!"
        )
        return

    user_id, days, status = row

    if status != "pending":
        bot.answer_callback_query(
            call.id,
            "⚠️ Bu to‘lov allaqachon ko‘rib chiqilgan."
        )
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
        (user_id, until.isoformat())
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
        f"📅 Muddat: {days} kun\n"
        f"⏰ Tugash: {until.strftime('%d.%m.%Y %H:%M')}"
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

    payment_id = int(call.data.split(":")[1])

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
        bot.answer_callback_query(
            call.id,
            "❌ To‘lov topilmadi!"
        )
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
# VIDEO FILE ID
# =========================

@bot.message_handler(content_types=["video"])
def get_file_id(message):

    bot.reply_to(
        message,
        "🆔 Video File ID:\n\n"
        + message.video.file_id
    )
   # =========================
# BOTNI ISHGA TUSHIRISH
# =========================

print("🤖 Bot ishlayapti...")

bot.infinity_polling(
    skip_pending=True
) 
