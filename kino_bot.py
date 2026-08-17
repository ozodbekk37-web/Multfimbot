import os
import sqlite3
from datetime import datetime, timedelta

import telebot
from telebot import types


# =========================================================
# SOZLAMALAR
# =========================================================

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not TOKEN:
    raise RuntimeError("TOKEN Environment Variable topilmadi!")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

DB_NAME = "kino_bot.db"


# =========================================================
# DATABASE
# =========================================================

def connect_db():
    return sqlite3.connect(DB_NAME)


def init_db():
    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            lang TEXT DEFAULT 'uz',
            vip_until TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            title TEXT,
            description TEXT,
            movie_type TEXT,
            part INTEGER DEFAULT 1,
            vip INTEGER DEFAULT 0,
            file_id TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            title TEXT,
            invite_link TEXT,
            chat_type TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            number TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS states (
            user_id INTEGER PRIMARY KEY,
            state TEXT,
            data TEXT
        )
    """)

    cur.execute("""
        INSERT OR IGNORE INTO settings(key, value)
        VALUES(
            'about',
            '🎬 Bu bot orqali kino va seriallarni topishingiz mumkin.'
        )
    """)

    con.commit()
    con.close()


init_db()


# =========================================================
# YORDAMCHI FUNKSIYALAR
# =========================================================

def is_admin(user_id):
    return user_id == ADMIN_ID


def add_user(user_id):
    con = connect_db()
    con.execute(
        "INSERT OR IGNORE INTO users(user_id) VALUES(?)",
        (user_id,)
    )
    con.commit()
    con.close()


def set_language(user_id, lang):
    con = connect_db()
    con.execute(
        "UPDATE users SET lang=? WHERE user_id=?",
        (lang, user_id)
    )
    con.commit()
    con.close()


def save_state(user_id, state, data=""):
    con = connect_db()
    con.execute("""
        INSERT OR REPLACE INTO states(user_id, state, data)
        VALUES(?,?,?)
    """, (user_id, state, data))
    con.commit()
    con.close()


def get_state(user_id):
    con = connect_db()
    row = con.execute(
        "SELECT state, data FROM states WHERE user_id=?",
        (user_id,)
    ).fetchone()
    con.close()

    if row:
        return row[0], row[1]

    return None, ""


def clear_state(user_id):
    con = connect_db()
    con.execute(
        "DELETE FROM states WHERE user_id=?",
        (user_id,)
    )
    con.commit()
    con.close()


def is_vip(user_id):
    con = connect_db()

    row = con.execute(
        "SELECT vip_until FROM users WHERE user_id=?",
        (user_id,)
    ).fetchone()

    con.close()

    if not row or not row[0]:
        return False

    try:
        return datetime.fromisoformat(row[0]) > datetime.now()
    except Exception:
        return False


# =========================================================
# TIL TANLASH
# =========================================================

def language_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=3)

    kb.add(
        types.InlineKeyboardButton(
            "🇺🇿 O'zbek",
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


# =========================================================
# START
# =========================================================

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    add_user(user_id)

    bot.send_message(
        user_id,
        "🌐 <b>Tilni tanlang:</b>",
        reply_markup=language_keyboard()
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("lang_")
)
def choose_language(call):
    lang = call.data.replace("lang_", "")

    set_language(call.from_user.id, lang)

    bot.answer_callback_query(call.id)

    send_subscription(call.message)


# =========================================================
# KANALLAR
# =========================================================

def get_channels():
    con = connect_db()

    rows = con.execute("""
        SELECT id, chat_id, title, invite_link, chat_type
        FROM channels
    """).fetchall()

    con.close()

    return rows


def check_subscription(user_id):
    channels = get_channels()

    for channel in channels:
        chat_id = channel[1]

        try:
            member = bot.get_chat_member(
                chat_id,
                user_id
            )

            if member.status in ("left", "kicked"):
                return False

        except Exception:
            return False

    return True


def send_subscription(message):
    channels = get_channels()

    if not channels:
        main_menu(message)
        return

    kb = types.InlineKeyboardMarkup()

    for channel in channels:
        title = channel[2]
        invite_link = channel[3]

        if invite_link:
            kb.add(
                types.InlineKeyboardButton(
                    "📢 " + title,
                    url=invite_link
                )
            )

    kb.add(
        types.InlineKeyboardButton(
            "✅ Tekshirish",
            callback_data="check_subscription"
        )
    )

    bot.send_message(
        message.chat.id,
        "📢 <b>Botdan foydalanish uchun quyidagi kanal/guruhlarga qo‘shiling:</b>",
        reply_markup=kb
    )


@bot.callback_query_handler(
    func=lambda call: call.data == "check_subscription"
)
def check_subscription_callback(call):

    if check_subscription(call.from_user.id):
        bot.answer_callback_query(
            call.id,
            "✅ Obuna tasdiqlandi!"
        )

        main_menu(call.message)

    else:
        bot.answer_callback_query(
            call.id,
            "❌ Avval barcha kanal/guruhlarga qo‘shiling!",
            show_alert=True
        )


# =========================================================
# ASOSIY MENYU
# =========================================================

def main_menu(message):

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.row(
        "🎬 Kino",
        "📺 Serial"
    )

    kb.row(
        "👑 VIP",
        "ℹ️ Bot haqida"
    )

    bot.send_message(
        message.chat.id,
        "🏠 <b>Asosiy menyu</b>",
        reply_markup=kb
    )


# =========================================================
# BOT HAQIDA
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "ℹ️ Bot haqida"
)
def about_bot(message):

    con = connect_db()

    row = con.execute(
        "SELECT value FROM settings WHERE key='about'"
    ).fetchone()

    con.close()

    text = row[0] if row else "Ma'lumot mavjud emas."

    bot.send_message(
        message.chat.id,
        "ℹ️ <b>Bot haqida</b>\n\n" + text
    )


# =========================================================
# KINO QIDIRISH
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "🎬 Kino"
)
def movie_search_start(message):

    save_state(
        message.from_user.id,
        "search_movie"
    )

    bot.send_message(
        message.chat.id,
        "🔢 Kino kodini yuboring:"
    )


@bot.message_handler(
    func=lambda message: message.text == "📺 Serial"
)
def serial_search_start(message):

    save_state(
        message.from_user.id,
        "search_serial"
    )

    bot.send_message(
        message.chat.id,
        "🔢 Serial kodini yuboring:"
    )


# =========================================================
# VIP
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "👑 VIP"
)
def vip_menu(message):

    if is_vip(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "👑 <b>Siz VIP foydalanuvchisiz!</b>"
        )
        return

    con = connect_db()

    cards = con.execute(
        "SELECT name, number FROM cards"
    ).fetchall()

    con.close()

    text = "👑 <b>VIP OBUNA</b>\n\n"

    if cards:

        text += "💳 To‘lov uchun kartalar:\n\n"

        for name, number in cards:
            text += (
                f"💳 <b>{name}</b>\n"
                f"<code>{number}</code>\n\n"
            )

        text += "🧾 To‘lov qilgach chekni adminga yuboring."

    else:
        text += "💳 Hozircha karta qo‘shilmagan."

    bot.send_message(
        message.chat.id,
        text
    )


# =========================================================
# ADMIN PANEL
# =========================================================

def admin_keyboard():

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    kb.row(
        "➕ Kino qo‘shish",
        "🗑 Kino o‘chirish"
    )

    kb.row(
        "📢 Kanal qo‘shish",
        "🗑 Kanal o‘chirish"
    )

    kb.row(
        "💳 Karta qo‘shish",
        "🗑 Karta o‘chirish"
    )

    kb.row(
        "👑 VIP berish",
        "❌ VIP o‘chirish"
    )

    kb.row(
        "📊 Statistika",
        "📋 Ro‘yxatlar"
    )

    kb.row(
        "ℹ️ Bot haqida o‘zgartirish"
    )

    kb.row(
        "🏠 Asosiy menyu"
    )

    return kb


@bot.message_handler(commands=["admin"])
def admin_panel(message):

    if not is_admin(message.from_user.id):
        return

    bot.send_message(
        message.chat.id,
        "👨‍💻 <b>ADMIN PANEL</b>",
        reply_markup=admin_keyboard()
    )


# =========================================================
# KINO QO‘SHISH
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "➕ Kino qo‘shish"
)
def add_movie(message):

    if not is_admin(message.from_user.id):
        return

    save_state(
        message.from_user.id,
        "movie_type"
    )

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

    kb.row(
        "🎥 Oddiy kino",
        "📺 Serial"
    )

    bot.send_message(
        message.chat.id,
        "🎬 <b>Turini tanlang:</b>",
        reply_markup=kb
    )


# =========================================================
# KINO O‘CHIRISH
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "🗑 Kino o‘chirish"
)
def delete_movie_start(message):

    if not is_admin(message.from_user.id):
        return

    save_state(
        message.from_user.id,
        "delete_movie"
    )

    bot.send_message(
        message.chat.id,
        "🗑 Kino/serial kodini yuboring:"
    )


# =========================================================
# KANAL QO‘SHISH
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "📢 Kanal qo‘shish"
)
def add_channel_start(message):

    if not is_admin(message.from_user.id):
        return

    save_state(
        message.from_user.id,
        "channel_id"
    )

    bot.send_message(
        message.chat.id,
        "📢 Kanal/guruh ID sini yuboring.\n\n"
        "Masalan:\n"
        "<code>-1001234567890</code>"
    )


# =========================================================
# KANAL O‘CHIRISH
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "🗑 Kanal o‘chirish"
)
def delete_channel_start(message):

    if not is_admin(message.from_user.id):
        return

    save_state(
        message.from_user.id,
        "delete_channel"
    )

    bot.send_message(
        message.chat.id,
        "🗑 O‘chiriladigan kanal/guruh ID sini yuboring:"
    )


# =========================================================
# KARTA QO‘SHISH
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "💳 Karta qo‘shish"
)
def add_card_start(message):

    if not is_admin(message.from_user.id):
        return

    save_state(
        message.from_user.id,
        "card_name"
    )

    bot.send_message(
        message.chat.id,
        "💳 Karta nomini yuboring.\n"
        "Masalan: Uzcard"
    )


# =========================================================
# KARTA O‘CHIRISH
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "🗑 Karta o‘chirish"
)
def delete_card_start(message):

    if not is_admin(message.from_user.id):
        return

    save_state(
        message.from_user.id,
        "delete_card"
    )

    bot.send_message(
        message.chat.id,
        "🗑 Karta ID sini yuboring:"
    )


# =========================================================
# VIP BERISH
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "👑 VIP berish"
)
def give_vip_start(message):

    if not is_admin(message.from_user.id):
        return

    save_state(
        message.from_user.id,
        "vip_user"
    )

    bot.send_message(
        message.chat.id,
        "👤 VIP beriladigan foydalanuvchi ID sini yuboring:"
    )


# =========================================================
# VIP O‘CHIRISH
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "❌ VIP o‘chirish"
)
def remove_vip_start(message):

    if not is_admin(message.from_user.id):
        return

    save_state(
        message.from_user.id,
        "remove_vip"
    )

    bot.send_message(
        message.chat.id,
        "👤 VIP bekor qilinadigan foydalanuvchi ID sini yuboring:"
    )


# =========================================================
# STATISTIKA
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "📊 Statistika"
)
def statistics(message):

    if not is_admin(message.from_user.id):
        return

    con = connect_db()

    users = con.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    movies = con.execute(
        "SELECT COUNT(*) FROM movies"
    ).fetchone()[0]

    channels = con.execute(
        "SELECT COUNT(*) FROM channels"
    ).fetchone()[0]

    cards = con.execute(
        "SELECT COUNT(*) FROM cards"
    ).fetchone()[0]

    con.close()

    bot.send_message(
        message.chat.id,
        f"""
📊 <b>STATISTIKA</b>

👥 Foydalanuvchilar: <b>{users}</b>
🎬 Kino/qismlar: <b>{movies}</b>
📢 Kanal/guruhlar: <b>{channels}</b>
💳 Kartalar: <b>{cards}</b>
"""
    )


# =========================================================
# RO‘YXATLAR
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "📋 Ro‘yxatlar"
)
def lists(message):

    if not is_admin(message.from_user.id):
        return

    con = connect_db()

    movies = con.execute("""
        SELECT code, title, movie_type, part, vip
        FROM movies
    """).fetchall()

    channels = con.execute("""
        SELECT id, title, chat_type
        FROM channels
    """).fetchall()

    cards = con.execute("""
        SELECT id, name, number
        FROM cards
    """).fetchall()

    con.close()

    text = "📋 <b>RO‘YXATLAR</b>\n\n"

    text += "🎬 <b>KINOLAR</b>\n"

    if movies:
        for movie in movies:
            vip = "👑 VIP" if movie[4] else "🟢 Oddiy"

            text += (
                f"🔢 {movie[0]} — "
                f"{movie[1]} — {vip}\n"
            )
    else:
        text += "Yo‘q\n"

    text += "\n📢 <b>KANALLAR/GURUHLAR</b>\n"

    if channels:
        for channel in channels:
            text += (
                f"{channel[0]}. "
                f"{channel[1]} — "
                f"{channel[2]}\n"
            )
    else:
        text += "Yo‘q\n"

    text += "\n💳 <b>KARTALAR</b>\n"

    if cards:
        for card in cards:
            text += (
                f"{card[0]}. "
                f"{card[1]} — "
                f"<code>{card[2]}</code>\n"
            )
    else:
        text += "Yo‘q\n"

    bot.send_message(
        message.chat.id,
        text
    )


# =========================================================
# BOT HAQIDA O‘ZGARTIRISH
# =========================================================

@bot.message_handler(
    func=lambda message: message.text == "ℹ️ Bot haqida o‘zgartirish"
)
def change_about_start(message):

    if not is_admin(message.from_user.id):
        return

    save_state(
        message.from_user.id,
        "change_about"
    )

    bot.send_message(
        message.chat.id,
        "ℹ️ Yangi ma'lumotni yuboring:"
    )


# =========================================================
# BARCHA XABARLAR
# =========================================================

@bot.message_handler(
    content_types=[
        "text",
        "video"
    ]
)
def process_message(message):

    user_id = message.from_user.id

    state, data = get_state(user_id)

    # =====================================================
    # ADMIN
    # =====================================================

    if is_admin(user_id):

        # -----------------------------------------------
        # Kino turi
        # -----------------------------------------------

        if state == "movie_type":

            if message.text == "🎥 Oddiy kino":

                save_state(
                    user_id,
                    "movie_title",
                    "movie"
                )

                bot.send_message(
                    user_id,
                    "🎬 Kino nomini yuboring:"
                )

                return

            if message.text == "📺 Serial":

                save_state(
                    user_id,
                    "movie_title",
                    "serial"
                )

                bot.send_message(
                    user_id,
                    "📺 Serial nomini yuboring:"
                )

                return

        # -----------------------------------------------
        # Kino nomi
        # -----------------------------------------------

        if state == "movie_title":

            save_state(
                user_id,
                "movie_description",
                data + "|" + message.text
            )

            bot.send_message(
                user_id,
                "📝 Tavsif yuboring yoki <b>-</b> yuboring:"
            )

            return

        # -----------------------------------------------
        # Tavsif
        # -----------------------------------------------

        if state == "movie_description":

            movie_type, title = data.split("|", 1)

            save_state(
                user_id,
                "movie_vip",
                f"{movie_type}|{title}|{message.text}"
            )

            kb = types.ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True
            )

            kb.row(
                "👑 VIP",
                "🟢 VIP emas"
            )

            bot.send_message(
                user_id,
                "👑 <b>VIP kinomi?</b>",
                reply_markup=kb
            )

            return

        # -----------------------------------------------
        # VIP yoki oddiy
        # -----------------------------------------------

        if state == "movie_vip":

            if message.text == "👑 VIP":
                vip = 1

            elif message.text == "🟢 VIP emas":
                vip = 0

            else:
                return

            movie_type, title, description = data.split("|", 2)

            save_state(
                user_id,
                "movie_code",
                f"{movie_type}|{title}|{description}|{vip}"
            )

            bot.send_message(
                user_id,
                "🔢 Kino/serial kodini yuboring:"
            )

            return

        # -----------------------------------------------
        # Kod
        # -----------------------------------------------

        if state == "movie_code":

            movie_type, title, description, vip = data.split("|", 3)

            save_state(
                user_id,
                "movie_file",
                f"{movie_type}|{title}|{description}|{vip}|{message.text}"
            )

            bot.send_message(
                user_id,
                "🎬 Endi video yuboring:"
            )

            return

        # -----------------------------------------------
        # Video
        # -----------------------------------------------

        if state == "movie_file":

            if message.content_type != "video":

                bot.send_message(
                    user_id,
                    "❌ Iltimos, video yuboring."
                )

                return

            movie_type, title, description, vip, code = data.split(
                "|",
                4
            )

            try:

                con = connect_db()

                con.execute("""
                    INSERT INTO movies(
                        code,
                        title,
                        description,
                        movie_type,
                        part,
                        vip,
                        file_id
                    )
                    VALUES(?,?,?,?,?,?,?)
                """, (
                    code,
                    title,
                    "" if description == "-" else description,
                    movie_type,
                    1,
                    int(vip),
                    message.video.file_id
                ))

                con.commit()
                con.close()

                clear_state(user_id)

                bot.send_message(
                    user_id,
                    "✅ <b>Kino saqlandi!</b>",
                    reply_markup=admin_keyboard()
                )

            except sqlite3.IntegrityError:

                bot.send_message(
                    user_id,
                    "❌ Bu kod allaqachon mavjud."
                )

            return

        # -----------------------------------------------
        # Kanal ID
        # -----------------------------------------------

        if state == "channel_id":

            save_state(
                user_id,
                "channel_title",
                message.text
            )

            bot.send_message(
                user_id,
                "📛 Kanal/guruh nomini yuboring:"
            )

            return

        # -----------------------------------------------
        # Kanal nomi
        # -----------------------------------------------

        if state == "channel_title":

            save_state(
                user_id,
                "channel_link",
                data + "|" + message.text
            )

            bot.send_message(
                user_id,
                "🔗 Taklif havolasini yuboring:"
            )

            return

        # -----------------------------------------------
        # Kanal link
        # -----------------------------------------------

        if state == "channel_link":

            chat_id, title = data.split("|", 1)

            save_state(
                user_id,
                "channel_type",
                f"{chat_id}|{title}|{message.text}"
            )

            kb = types.ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True
            )

            kb.row(
                "📢 Kanal",
                "👥 Guruh"
            )

            bot.send_message(
                user_id,
                "📌 Turini tanlang:",
                reply_markup=kb
            )

            return

        # -----------------------------------------------
        # Kanal turi
        # -----------------------------------------------

        if state == "channel_type":

            if message.text not in (
                "📢 Kanal",
                "👥 Guruh"
            ):
                return

            chat_type = (
                "channel"
                if message.text == "📢 Kanal"
                else "group"
            )

            chat_id, title, invite = data.split("|", 2)

            con = connect_db()

            con.execute("""
                INSERT INTO channels(
                    chat_id,
                    title,
                    invite_link,
                    chat_type
                )
                VALUES(?,?,?,?)
            """, (
                chat_id,
                title,
                invite,
                chat_type
            ))

            con.commit()
            con.close()

            clear_state(user_id)

            bot.send_message(
                user_id,
                "✅ Kanal/guruh qo‘shildi!",
                reply_markup=admin_keyboard()
            )

            return

        # -----------------------------------------------
        # Karta nomi
        # -----------------------------------------------

        if state == "card_name":

            save_state(
                user_id,
                "card_number",
                message.text
            )

            bot.send_message(
                user_id,
                "🔢 Karta raqamini yuboring:"
            )

            return

        # -----------------------------------------------
        # Karta raqami
        # -----------------------------------------------

        if state == "card_number":

            con = connect_db()

            con.execute(
                "INSERT INTO cards(name, number) VALUES(?,?)",
                (data, message.text)
            )

            con.commit()
            con.close()

            clear_state(user_id)

            bot.send_message(
                user_id,
                "✅ Karta qo‘shildi!",
                reply_markup=admin_keyboard()
            )

            return

        # -----------------------------------------------
        # VIP user
        # -----------------------------------------------

        if state == "vip_user":

            try:

                target_id = int(message.text)

                save_state(
                    user_id,
                    "vip_days",
                    str(target_id)
                )

                bot.send_message(
                    user_id,
                    "📅 Necha kun VIP berilsin?"
                )

            except ValueError:

                bot.send_message(
                    user_id,
                    "❌ ID faqat raqam bo‘lishi kerak."
                )

            return

        # -----------------------------------------------
        # VIP kun
        # -----------------------------------------------

        if state == "vip_days":

            try:

                days = int(message.text)
                target_id = int(data)

                until = datetime.now() + timedelta(
                    days=days
                )

                con = connect_db()

                con.execute(
                    """
                    UPDATE users
                    SET vip_until=?
                    WHERE user_id=?
                    """,
                    (
                        until.isoformat(),
                        target_id
                    )
                )

                con.commit()
                con.close()

                clear_state(user_id)

                bot.send_message(
                    user_id,
                    "✅ VIP berildi!",
                    reply_markup=admin_keyboard()
                )

            except ValueError:

                bot.send_message(
                    user_id,
                    "❌ Kun sonini raqam bilan yozing."
                )

            return

        # -----------------------------------------------
        # Bot haqida
        # -----------------------------------------------

        if state == "change_about":

            con = connect_db()

            con.execute(
                """
                UPDATE settings
                SET value=?
                WHERE key='about'
                """,
                (message.text,)
            )

            con.commit()
            con.close()

            clear_state(user_id)

            bot.send_message(
                user_id,
                "✅ Bot haqida ma'lumot o‘zgartirildi.",
                reply_markup=admin_keyboard()
            )

            return

        # -----------------------------------------------
        # Kino o‘chirish
        # -----------------------------------------------

        if state == "delete_movie":

            con = connect_db()

            cur = con.execute(
                "DELETE FROM movies WHERE code=?",
                (message.text,)
            )

            con.commit()
            con.close()

            clear_state(user_id)

            bot.send_message(
                user_id,
                "✅ Kino o‘chirildi."
                if cur.rowcount
                else "❌ Bunday kod topilmadi.",
                reply_markup=admin_keyboard()
            )

            return

        # -----------------------------------------------
        # Kanal o‘chirish
        # -----------------------------------------------

        if state == "delete_channel":

            con = connect_db()

            cur = con.execute(
                "DELETE FROM channels WHERE chat_id=?",
                (message.text,)
            )

            con.commit()
            con.close()

            clear_state(user_id)

            bot.send_message(
                user_id,
                "✅ Kanal/guruh o‘chirildi."
                if cur.rowcount
                else "❌ Topilmadi.",
                reply_markup=admin_keyboard()
            )

            return

        # -----------------------------------------------
        # Karta o‘chirish
        # -----------------------------------------------

        if state == "delete_card":

            try:

                card_id = int(message.text)

                con = connect_db()

                cur = con.execute(
                    "DELETE FROM cards WHERE id=?",
                    (card_id,)
                )

                con.commit()
                con.close()

                clear_state(user_id)

                bot.send_message(
                    user_id,
                    "✅ Karta o‘chirildi."
                    if cur.rowcount
                    else "❌ Karta topilmadi.",
                    reply_markup=admin_keyboard()
                )

            except ValueError:

                bot.send_message(
                    user_id,
                    "❌ Karta ID raqam bo‘lishi kerak."
                )

            return

        # -----------------------------------------------
        # VIP o‘chirish
        # -----------------------------------------------

        if state == "remove_vip":

            try:

                target_id = int(message.text)

                con = connect_db()

                con.execute(
                    """
                    UPDATE users
                    SET vip_until=NULL
                    WHERE user_id=?
                    """,
                    (target_id,)
                )

                con.commit()
                con.close()

                clear_state(user_id)

                bot.send_message(
                    user_id,
                    "✅ VIP bekor qilindi.",
                    reply_markup=admin_keyboard()
                )

            except ValueError:

                bot.send_message(
                    user_id,
                    "❌ ID noto‘g‘ri."
                )

            return

    # =====================================================
    # FOYDALANUVCHI KINO/SERIAL QIDIRISH
    # =====================================================

    if state in (
        "search_movie",
        "search_serial"
    ):

        code = message.text.strip()

        con = connect_db()

        row = con.execute("""
            SELECT
                code,
                title,
                description,
                movie_type,
                part,
                vip,
                file_id
            FROM movies
            WHERE code=?
        """, (code,)).fetchone()

        con.close()

        clear_state(user_id)

        if not row:

            bot.send_message(
                user_id,
                "❌ Bunday koddagi kino topilmadi."
            )

            return

        (
            code,
            title,
            description,
            movie_type,
            part,
            vip,
            file_id
        ) = row

        if vip and not is_vip(user_id):

            bot.send_message(
                user_id,
                "👑 <b>Bu VIP kino.</b>\n\n"
                "Uni ko‘rish uchun VIP obuna kerak."
            )

            return

        caption = (
            f"🎬 <b>{title}</b>\n"
        )

        if description:
            caption += (
                f"\n📝 {description}\n"
            )

        if movie_type == "serial":
            caption += (
                f"\n📺 {part}-qism"
            )

        if vip:
            caption += "\n\n👑 VIP"

        bot.send_video(
            user_id,
            file_id,
            caption=caption
        )


# =========================================================
# BOTNI ISHGA TUSHIRISH
# =========================================================

print("🤖 Bot ishga tushdi...")

bot.infinity_polling(
    skip_pending=True
)
