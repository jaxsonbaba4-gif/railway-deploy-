from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Document
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import requests
import asyncio
import os
import time

# ====================================
# CONFIG
# ====================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

API_URL = "https://api-of-naone-1.onrender.com/bot/check"

# ====================================
# START COMMAND
# ====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "🔥 STATUS",
                callback_data="status"
            ),

            InlineKeyboardButton(
                "⚡ READY",
                callback_data="ready"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = """
╔════════════════════╗
      ⚡ PREMIUM BOT
╚════════════════════╝

📂 Send TXT File
📝 Or Send Single Input

⚡ Railway Hosted
🔥 Ultra Fast
"""

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )

# ====================================
# SINGLE CHECK
# ====================================

async def single_check(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    msg = await update.message.reply_text(
        "⚡ Processing..."
    )

    try:

        params = {
            "card": text,
            "gate": "pp"
        }

        r = requests.get(
            API_URL,
            params=params,
            timeout=30
        )

        data = r.json()

        status = data.get("status", "UNKNOWN")
        response = data.get("response", "NONE")
        gate = data.get("gate", "pp")
        brand = data.get("brand", "UNKNOWN")
        taken = data.get("time", "0")

        emoji = "✅" if status == "APPROVED" else "❌"

        result = f"""
╔════════════════╗
     {emoji} {status}
╚════════════════╝

💳 {text}

🏦 Brand: {brand}
⚡ Gate: {gate}

📌 Response:
{response}

⏱ Time: {taken}s
"""

        await msg.edit_text(result)

    except Exception as e:

        await msg.edit_text(
            f"❌ Error:\n{e}"
        )

# ====================================
# TXT CHECKER
# ====================================

async def txt_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document: Document = update.message.document

    if not document.file_name.endswith(".txt"):

        await update.message.reply_text(
            "❌ TXT only."
        )
        return

    status_msg = await update.message.reply_text(
        "📥 Downloading File..."
    )

    file = await context.bot.get_file(
        document.file_id
    )

    path = f"./{document.file_name}"

    await file.download_to_drive(path)

    with open(path, "r", encoding="utf-8", errors="ignore") as f:

        lines = [
            x.strip()
            for x in f
            if x.strip()
        ]

    total = len(lines)

    approved = []
    declined = []

    checked = 0

    start_time = time.time()

    session = requests.Session()

    for line in lines:

        checked += 1

        try:

            params = {
                "card": line,
                "gate": "pp"
            }

            r = session.get(
                API_URL,
                params=params,
                timeout=30
            )

            data = r.json()

            status = data.get(
                "status",
                "DECLINED"
            )

            if status == "APPROVED":

                approved.append(line)

            else:

                declined.append(line)

        except:

            declined.append(line)

        # LIVE UPDATE
        if checked % 5 == 0:

            await status_msg.edit_text(
                f"""
⚡ PROCESSING FILE...

📄 Total: {total}

✅ Approved: {len(approved)}
❌ Declined: {len(declined)}

🔄 Checked:
{checked}/{total}
"""
            )

    # ====================================
    # SAVE RESULTS
    # ====================================

    with open("approved.txt", "w") as f:

        f.write("\n".join(approved))

    with open("declined.txt", "w") as f:

        f.write("\n".join(declined))

    end_time = round(
        time.time() - start_time,
        2
    )

    final_text = f"""
╔══════════════════╗
    ⚡ COMPLETED
╚══════════════════╝

📄 Total: {total}

✅ Approved:
{len(approved)}

❌ Declined:
{len(declined)}

⏱ Time:
{end_time}s
"""

    await status_msg.edit_text(final_text)

    # SEND FILES

    if approved:

        await update.message.reply_document(
            document=open("approved.txt", "rb"),
            filename="approved.txt",
            caption="✅ Approved"
        )

    if declined:

        await update.message.reply_document(
            document=open("declined.txt", "rb"),
            filename="declined.txt",
            caption="❌ Declined"
        )

    # CLEANUP

    os.remove(path)

    if os.path.exists("approved.txt"):
        os.remove("approved.txt")

    if os.path.exists("declined.txt"):
        os.remove("declined.txt")

# ====================================
# MAIN
# ====================================

def main():

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.Document.ALL,
            txt_checker
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            single_check
        )
    )

    print("🔥 BOT RUNNING ON RAILWAY")

    app.run_polling()

# ====================================

if __name__ == "__main__":
    main()