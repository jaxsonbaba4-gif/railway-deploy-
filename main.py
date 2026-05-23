# ======================================
# DEMO API BOT
# ======================================

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
# DEMO FILTER WORDS
# ======================================

success_keywords = [
    "SUCCESS",
    "DONE",
    "OK",
    "VALID",
    "APPROVED"
]

error_keywords = [
    "ERROR",
    "FAILED",
    "INVALID",
    "DECLINED"
]

# ======================================
# START COMMAND
# ======================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
⚡ DEMO API BOT

📂 Send TXT File
📝 Or Send Single Input

🔥 Railway Ready
"""

    await update.message.reply_text(text)

# ======================================
# SINGLE INPUT
# ======================================

async def single_input(update: Update, context: ContextTypes.DEFAULT_TYPE):

    line = update.message.text.strip()

    msg = await update.message.reply_text(
        "⚡ Processing..."
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

        category = "⚠ UNKNOWN"

        if any(
            x in raw_upper
            for x in success_keywords
        ):

            category = "✅ SUCCESS"

        elif any(
            x in raw_upper
            for x in error_keywords
        ):

            category = "❌ ERROR"

        text = f"""
{category}

📨 RAW RESPONSE:
{raw}

⏱ TIME:
{end}s
"""

        await msg.edit_text(text)

    except Exception as e:

        await msg.edit_text(
            f"❌ ERROR\n\n{e}"
        )

# ======================================
# TXT FILE WORKFLOW
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

    # ======================================
    # LOAD FILE
    # ======================================

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

    success = []
    errors = []
    unknown = []

    session = requests.Session()

    start_all = time.time()

    # ======================================
    # MAIN LOOP
    # ======================================

    for line in lines:

        print(f"\n⚡ PROCESSING -> {line}")

        finished = False

        while not finished:

            try:

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

                print("\nRAW:")
                print(raw)

                # ======================================
                # EMPTY RESPONSE
                # ======================================

                if not raw:

                    print("⚠ EMPTY")

                    time.sleep(2)

                    continue

                # ======================================
                # VERIFY FINAL RESPONSE
                # ======================================

                final_words = [
                    "SUCCESS",
                    "FAILED",
                    "ERROR",
                    "DECLINED",
                    "APPROVED"
                ]

                verified = any(
                    x in raw.upper()
                    for x in final_words
                )

                # STILL PROCESSING
                if not verified:

                    print(
                        "⏳ WAITING FINAL RESPONSE"
                    )

                    time.sleep(2)

                    continue

                # ======================================
                # VERIFIED
                # ======================================

                checked += 1

                raw_upper = raw.upper()

                print("✅ VERIFIED")

                # ======================================
                # FILTER
                # ======================================

                if any(
                    x in raw_upper
                    for x in success_keywords
                ):

                    success.append(
                        f"{line}\n{raw}\n"
                    )

                    print("✅ SUCCESS")

                elif any(
                    x in raw_upper
                    for x in error_keywords
                ):

                    errors.append(
                        f"{line}\n{raw}\n"
                    )

                    print("❌ ERROR")

                else:

                    unknown.append(
                        f"{line}\n{raw}\n"
                    )

                    print("⚠ UNKNOWN")

                # ======================================
                # LIVE SAVE
                # ======================================

                with open(
                    "success.txt",
                    "w",
                    encoding="utf-8"
                ) as f:

                    f.write(
                        "\n".join(success)
                    )

                with open(
                    "errors.txt",
                    "w",
                    encoding="utf-8"
                ) as f:

                    f.write(
                        "\n".join(errors)
                    )

                with open(
                    "unknown.txt",
                    "w",
                    encoding="utf-8"
                ) as f:

                    f.write(
                        "\n".join(unknown)
                    )

                # ======================================
                # LIVE TELEGRAM UPDATE
                # ======================================

                if checked % 3 == 0:

                    await status_msg.edit_text(
                        f"""
⚡ DEMO API WORKFLOW

📄 Total:
{total}

✅ Success:
{len(success)}

❌ Errors:
{len(errors)}

⚠ Unknown:
{len(unknown)}

🔄 Checked:
{checked}/{total}
"""
                    )

                print(
                    f"⏱ TIME -> {end}s"
                )

                finished = True

            except Exception as e:

                print("\n❌ ERROR:")
                print(e)

                time.sleep(2)

    # ======================================
    # FINAL
    # ======================================

    total_time = round(
        time.time() - start_all,
        2
    )

    await status_msg.edit_text(
        f"""
⚡ COMPLETED

📄 Total:
{total}

✅ Success:
{len(success)}

❌ Errors:
{len(errors)}

⚠ Unknown:
{len(unknown)}

🔄 Checked:
{checked}/{total}

⏱ Time:
{total_time}s
"""
    )

    # ======================================
    # SEND FILES
    # ======================================

    if success:

        await update.message.reply_document(
            document=open(
                "success.txt",
                "rb"
            ),

            filename="success.txt"
        )

    if errors:

        await update.message.reply_document(
            document=open(
                "errors.txt",
                "rb"
            ),

            filename="errors.txt"
        )

    if unknown:

        await update.message.reply_document(
            document=open(
                "unknown.txt",
                "rb"
            ),

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
            single_input
        )
    )

    print("🔥 DEMO API BOT RUNNING")

    app.run_polling()

# ======================================

if __name__ == "__main__":
    main()
