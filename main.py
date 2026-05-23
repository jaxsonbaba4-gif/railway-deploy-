from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import requests
import os
import time

# ======================================
# CONFIG
# ======================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

API_URL = "https://api-of-naone-1.onrender.com/bot/check"

# ======================================
# FILTER WORDS
# ======================================

approved_keywords = [
    "APPROVED",
    "SUCCESS",
    "LIVE",
    "VALID",
    "PASS"
]

declined_keywords = [
    "DECLINED",
    "FAILED",
    "INVALID",
    "DEAD",
    "ERROR"
]

# ======================================
# START COMMAND
# ======================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
╔══════════════════╗
      ⚡ API BOT
╚══════════════════╝

📂 Send TXT File
📝 Or Send Single Line

🔥 Railway Hosted
"""

    await update.message.reply_text(text)

# ======================================
# SINGLE CHECK
# ======================================

async def single_check(update: Update, context: ContextTypes.DEFAULT_TYPE):

    line = update.message.text.strip()

    msg = await update.message.reply_text(
        "⚡ Checking..."
    )

    try:

        start = time.time()

        r = requests.get(
            API_URL,
            params={
                "card": line,
                "gate": "pp"
            },
            timeout=40
        )

        end = round(
            time.time() - start,
            2
        )

        raw = r.text.strip()

        raw_upper = raw.upper()

        result = "⚠ UNKNOWN"

        if any(
            x in raw_upper
            for x in approved_keywords
        ):

            result = "✅ APPROVED"

        elif any(
            x in raw_upper
            for x in declined_keywords
        ):

            result = "❌ DECLINED"

        text = f"""
{result}

💳 {line}

⏱ Time:
{end}s

📨 Raw:
{raw}
"""

        await msg.edit_text(text)

    except Exception as e:

        await msg.edit_text(
            f"❌ ERROR\n\n{e}"
        )

# ======================================
# TXT CHECKER
# ======================================

async def txt_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if not document.file_name.endswith(".txt"):

        await update.message.reply_text(
            "❌ TXT only"
        )

        return

    status_msg = await update.message.reply_text(
        "📥 Downloading TXT..."
    )

    file = await context.bot.get_file(
        document.file_id
    )

    path = f"./{document.file_name}"

    await file.download_to_drive(path)

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        lines = [
            x.strip()
            for x in f
            if x.strip()
        ]

    total = len(lines)

    checked = 0

    approved = []
    declined = []
    unknown = []

    session = requests.Session()

    start_time = time.time()

    for line in lines:

        try:

            print(f"\nCHECKING -> {line}")

            start = time.time()

            r = session.get(
                API_URL,
                params={
                    "card": line,
                    "gate": "pp"
                },
                timeout=40
            )

            end = round(
                time.time() - start,
                2
            )

            raw = r.text.strip()

            print("\nRAW RESPONSE:")
            print(raw)

            # ======================================
            # VERIFY RESPONSE
            # ======================================

            if not raw:
                continue

            if len(raw) < 5:
                continue

            valid_words = [
                "STATUS",
                "RESPONSE",
                "OK",
                "ERROR",
                "DECLINED",
                "APPROVED"
            ]

            verified = any(
                x in raw.upper()
                for x in valid_words
            )

            if not verified:

                print("\n⚠ UNVERIFIED")
                continue

            checked += 1

            raw_upper = raw.upper()

            # ======================================
            # FILTER
            # ======================================

            if any(
                x in raw_upper
                for x in approved_keywords
            ):

                approved.append(line)

                print("\n✅ APPROVED")

            elif any(
                x in raw_upper
                for x in declined_keywords
            ):

                declined.append(line)

                print("\n❌ DECLINED")

            else:

                unknown.append(line)

                print("\n⚠ UNKNOWN")

            print(f"\n⏱ {end}s")

            # ======================================
            # LIVE SAVE
            # ======================================

            with open("approved.txt", "w") as f:
                f.write("\n".join(approved))

            with open("declined.txt", "w") as f:
                f.write("\n".join(declined))

            with open("unknown.txt", "w") as f:
                f.write("\n".join(unknown))

            # ======================================
            # LIVE TELEGRAM UPDATE
            # ======================================

            if checked % 3 == 0:

                await status_msg.edit_text(
                    f"""
⚡ PROCESSING

📄 Total:
{total}

✅ Approved:
{len(approved)}

❌ Declined:
{len(declined)}

⚠ Unknown:
{len(unknown)}

🔄 Checked:
{checked}/{total}
"""
                )

        except Exception as e:

            print("\nERROR:")
            print(e)

    # ======================================
    # FINAL
    # ======================================

    total_time = round(
        time.time() - start_time,
        2
    )

    final_text = f"""
╔══════════════════╗
      ⚡ COMPLETED
╚══════════════════╝

📄 Total:
{total}

✅ Approved:
{len(approved)}

❌ Declined:
{len(declined)}

⚠ Unknown:
{len(unknown)}

🔄 Checked:
{checked}/{total}

⏱ Time:
{total_time}s
"""

    await status_msg.edit_text(final_text)

    # ======================================
    # SEND FILES
    # ======================================

    if approved:

        await update.message.reply_document(
            document=open("approved.txt", "rb"),
            filename="approved.txt"
        )

    if declined:

        await update.message.reply_document(
            document=open("declined.txt", "rb"),
            filename="declined.txt"
        )

    if unknown:

        await update.message.reply_document(
            document=open("unknown.txt", "rb"),
            filename="unknown.txt"
        )

# ======================================
# MAIN
# ======================================

def main():

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
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

# ======================================

if __name__ == "__main__":
    main()
