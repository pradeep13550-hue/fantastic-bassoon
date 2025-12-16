from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from os import getenv
import sqlite3
import random

load_dotenv()

API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")

app = Client(
    "NoLimitLearningBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================= DATABASE =================
db = sqlite3.connect("chatbot.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger TEXT,
    reply TEXT
)
""")
db.commit()

# ================= MAIN HANDLER =================
@app.on_message(filters.text & ~filters.bot)
async def brain(_, msg: Message):

    text = msg.text.strip().lower()

    # ================= LEARN =================
    if msg.reply_to_message and msg.reply_to_message.text:
        trigger_text = msg.reply_to_message.text.strip().lower()
        reply_text = text

        # save full sentence
        cur.execute(
            "INSERT INTO memory (trigger, reply) VALUES (?, ?)",
            (trigger_text, reply_text)
        )

        # save each word separately (STRONG MEMORY)
        for word in trigger_text.split():
            cur.execute(
                "INSERT INTO memory (trigger, reply) VALUES (?, ?)",
                (word, reply_text)
            )

        db.commit()

    # ================= REPLY =================
    cur.execute(
        "SELECT reply FROM memory WHERE trigger=?",
        (text,)
    )
    rows = cur.fetchall()

    # SILENT if no reply
    if not rows:
        return

    response = random.choice(rows)[0]
    await msg.reply_text(response)

# ================= RUN =================
print("🤖 Bot Started")
app.run()
