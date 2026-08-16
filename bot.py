import os
import sqlite3
from datetime import datetime, timedelta

import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@Multfilmlar2026m"

ADMIN_ID = 7927602820
SECRET_WORD = "Ozodbek_941"

UZUM_CARD = "4916990361459941"

bot = telebot.TeleBot(TOKEN)

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
# VIP TARIFLAR
# =========================

VIP_PLANS = {
    "vip1": ("1 oy", 30000, 30),
    "vip2": ("2 oy", 50000, 60),
    "vip6": ("6 oy", 150000, 180),
    "vip12": ("1 yil", 300000, 365),
}


# =========================
# OZODBEK
# =========================

def is_ozodbek(message):
    return (
        message.from_user.id == ADMIN_ID
        and message.text
        and message.text.strip() == SECRET_WORD
    )


def is_admin(user_id):
    return user_id == ADMIN_ID


# =========================
# OBUNA TEKSHIRISH
# =========================

def subscribed(user_id):

    # Ozodbek uchun obuna shart emas
    if user_id == ADMIN_ID:
        return True

    try:
        member = bot.get_chat_member(CHANNEL, user_id)

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

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


# =========================
# VIP TEKSHIRISH
# =========================

def is_vip(user_id):

    # Admin doim VIP
    if user_id == ADMIN_ID:
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
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    if not subscribed(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "👋 Botdan foydalanish uchun kanalimizga obuna bo‘ling:",
            reply_markup=subscribe_menu()
        )

        return

    menu = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    menu.add(
        "🎬 Kino",
        "👑 VIP"
    )

    bot.send_message(
        message.chat.id,
        "✅ Xush kelibsiz!\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=menu
    )


# =========================
# OBUNANI TEKSHIRISH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "check_sub"
)
def check_sub(call):

    if subscribed(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "✅ Obuna tasdiqlandi!"
        )

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


# =========================
# VIP MENYU
# =========================

@bot.message_handler(
    func=lambda message: message.text == "👑 VIP"
)
def vip_menu(message):

    kb = types.InlineKeyboardMarkup()

    for key, data in VIP_PLANS.items():

        name, price, days = data

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

        if row:

            until = datetime.fromisoformat(row[0])

            bot.send_message(
                message.chat.id,
                "👑 Siz VIP foydalanuvchisiz!\n\n"
                f"⏰ Tugash sanasi:\n"
                f"{until.strftime('%d.%m.%Y %H:%M')}",
                reply_markup=kb
            )

        else:

            bot.send_message(
                message.chat.id,
                "👑 Siz administratormiz.\n"
                "VIP siz uchun doimiy.",
                reply_markup=kb
            )

    else:

        bot.send_message(
            message.chat.id,
            "👑 VIP tariflardan birini tanlang:",
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

    name, price, days = VIP_PLANS[key]

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
            price
        )
    )

    payment_id = cur.lastrowid

    db.commit()

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        f"👑 VIP: {name}\n\n"
        f"💰 Narxi: {price:,} so‘m\n"
        f"📅 Muddat: {days} kun\n\n"
        f"💳 Uzum Bank:\n"
        f"{UZUM_CARD}\n\n"
        "1️⃣ To‘lovni amalga oshiring.\n"
        "2️⃣ Chekni shu botga yuboring.\n\n"
        f"🆔 To‘lov raqami: {payment_id}"
    )


# =========================
# CHEK QABUL QILISH
# =========================

@bot.message_handler(
    content_types=["photo", "document"]
)
def payment_check(message):

    user_id = message.from_user.id

    cur.execute(
        """
        SELECT id, plan, days, amount
        FROM payments
        WHERE user_id=? AND status='pending'
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    )

    payment = cur.fetchone()

    if not payment:

        bot.reply_to(
            message,
            "❌ Sizda kutilayotgan to‘lov yo‘q.\n\n"
            "Avval 👑 VIP bo‘limidan tarif tanlang."
        )

        return

    payment_id, plan, days, amount = payment

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "Username yo‘q"
    )

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "✅ TASDIQLASH",
            callback_data=f"approve:{payment_id}"
        ),
        types.InlineKeyboardButton(
            "❌ RAD ETISH",
            callback_data=f"reject:{payment_id}"
        )
    )

    caption = (
        "💰 YANGI VIP TO‘LOV!\n\n"
        f"🆔 To‘lov: {payment_id}\n"
        f"👤 User ID: {user_id}\n"
        f"👤 Username: {username}\n"
        f"👑 Tarif: {plan}\n"
        f"💵 Summa: {amount:,} so‘m\n"
        f"📅 Muddat: {days} kun"
    )

    # CHEKNI DARHOL ADMIN GA YUBORISH

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
        "✅ Chekingiz adminga yuborildi.\n"
        "⏳ Tasdiqlanishini kuting."
    )


# =========================
# ADMIN TASDIQLASH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("approve:")
)
def approve_payment(call):

    if not is_admin(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "❌ Siz admin emassiz!",
            show_alert=True
        )

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

    payment = cur.fetchone()

    if not payment:
        return

    user_id, days, status = payment

    if status != "pending":

        bot.answer_callback_query(
            call.id,
            "⚠️ Bu to‘lov ko‘rib chiqilgan.",
            show_alert=True
        )

        return

    cur.execute(
        "SELECT until FROM vip_users WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()

    if row:

        old_until = datetime.fromisoformat(row[0])

        if old_until > datetime.now():
            new_until = old_until + timedelta(days=days)
        else:
            new_until = datetime.now() + timedelta(days=days)

    else:

        new_until = datetime.now() + timedelta(days=days)

    cur.execute(
        """
        INSERT OR REPLACE INTO vip_users
        (user_id, until)
        VALUES (?, ?)
        """,
        (
            user_id,
            new_until.isoformat()
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

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None
    )

    bot.send_message(
        user_id,
        "🎉 TABRIKLAYMIZ!\n\n"
        "✅ To‘lovingiz tasdiqlandi.\n"
        f"👑 VIP {days} kunga berildi.\n\n"
        f"⏰ Tugash sanasi:\n"
        f"{new_until.strftime('%d.%m.%Y %H:%M')}"
    )


# =========================
# ADMIN RAD ETISH
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("reject:")
)
def reject_payment(call):

    if not is_admin(call.from_user.id):

        bot.answer_callback_query(
            call.id,
            "❌ Siz admin emassiz!",
            show_alert=True
        )

        return

    payment_id = int(
        call.data.split(":")[1]
    )

    cur.execute(
        """
        SELECT user_id, status
        FROM payments
        WHERE id=?
        """,
        (payment_id,)
    )

    payment = cur.fetchone()

    if not payment:
        return

    user_id, status = payment

    if status != "pending":

        bot.answer_callback_query(
            call.id,
            "⚠️ Bu to‘lov ko‘rib chiqilgan.",
            show_alert=True
        )

        return

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
        "❌ To‘lov rad etildi."
    )

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None
    )

    bot.send_message(
        user_id,
        "❌ To‘lovingiz rad etildi.\n\n"
        "Agar xatolik bo‘lgan bo‘lsa, qayta to‘lov qilib "
        "chekni yuboring."
    )


# =========================
# VIDEO → FILE ID
# =========================

@bot.message_handler(
    content_types=["video"]
)
def video_file_id(message):

    file_id = message.video.file_id

    bot.reply_to(
        message,
        "🆔 FILE ID:\n\n"
        f"{file_id}\n\n"
        "🔢 Kino kodini ham yozib yuboring."
    )


# =========================
# ADMIN: VIP BERISH
# =========================

@bot.message_handler(
    commands=["givevip"]
)
def give_vip(message):

    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()

    if len(parts) != 3:

        bot.reply_to(
            message,
            "Format:\n"
            "/givevip USER_ID DAYS\n\n"
            "Masalan:\n"
            "/givevip 123456789 30"
        )

        return

    try:

        user_id = int(parts[1])
        days = int(parts[2])

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

        db.commit()

        bot.reply_to(
            message,
            f"✅ VIP berildi!\n\n"
            f"👤 ID: {user_id}\n"
            f"📅 {days} kun"
        )

        try:

            bot.send_message(
                user_id,
                "🎉 Sizga VIP berildi!\n\n"
                f"👑 Muddat: {days} kun\n"
                f"⏰ Tugash: {until.strftime('%d.%m.%Y %H:%M')}"
            )

        except:
            pass

    except ValueError:

        bot.reply_to(
            message,
            "❌ ID va kun sonini raqamda yozing."
        )


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

bot.infinity_polling()
