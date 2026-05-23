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
import os
import time

# ==========================================
# CONFIG
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

API_URL = "https://api-of-naone-1.onrender.com/bot/check"

# ==========================================
# START COMMAND
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "🔥 ONLINE",
                callback_data="online"
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
      ⚡ PREMIUM API BOT
╚════════════════════╝

📂 Send TXT File
📝 Or Send Single Line

⚡ Optimized Logic
🔥 Real Counting
✅ No Fake Declines
"""

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )

# ==========================================
# SINGLE CHECK
# ==========================================

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
            timeout=40
        )

        data = r.json()

        status = str(
            data.get("status", "UNKNOWN")
        )

        response_text = str(
            data.get("response", "NONE")
        )

        brand = str(
            data.get("brand", "UNKNOWN")
        )

        gate = str(
            data.get("gate", "pp")
        )

        taken = str(
            data.get("time", "0")
        )

        result = f"""
╔════════════════╗
      ⚡ RESULT
╚════════════════╝

💳 {text}

📌 Status:
{status}

🏦 Brand:
{brand}

⚡ Gate:
{gate}

📨 Response:
{response_text}

⏱ Time:
{taken}s
"""

        await msg.edit_text(result)

    except Exception as e:

        await msg.edit_text(
            f"""
❌ ERROR

{e}
"""
        )

# ==========================================
# TXT CHECKER
# ==========================================

async def txt_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document: Document = update.message.document

    if not document.file_name.endswith(".txt"):

        await update.message.reply_text(
            "❌ Send TXT file only."
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

    success = []
    failed = []
    errors = []

    session = requests.Session()

    start_time = time.time()

    for line in lines:

        try:

            params = {
                "card": line,
                "gate": "pp"
            }

            r = session.get(
                API_URL,
                params=params,
                timeout=40
            )

            data = r.json()

            checked += 1

            status = str(
                data.get("status", "UNKNOWN")
            ).upper()

            response_text = str(
                data.get("response", "NONE")
            ).upper()

            combined = (
                status + " " + response_text
            )

            positive_keywords = [
                "APPROVED",
                "LIVE",
                "SUCCESS",
                "VALID",
                "PASS"
            ]

            is_success = any(
                word in combined
                for word in positive_keywords
            )

            if is_success:

                success.append(
                    f"{line} | {status}"
                )

            else:

                failed.append(
                    f"{line} | {status}"
                )

        except Exception as e:

            errors.append(
                f"{line} -> {e}"
            )

            continue

        # ==========================
        # LIVE UPDATE
        # ==========================

        if checked % 3 == 0:

            await status_msg.edit_text(
                f"""
⚡ PROCESSING FILE...

📄 Total:
{total}

✅ Success:
{len(success)}

❌ Failed:
{len(failed)}

⚠ Errors:
{len(errors)}

🔄 Checked:
{checked}/{total}
"""
            )

    # ==========================================
    # SAVE FILES
    # ==========================================

    with open(
        "success.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write("\n".join(success))

    with open(
        "failed.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write("\n".join(failed))

    with open(
        "errors.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write("\n".join(errors))

    end_time = round(
        time.time() - start_time,
        2
    )

    final_text = f"""
╔══════════════════╗
     ⚡ COMPLETED
╚══════════════════╝

📄 Total:
{total}

✅ Success:
{len(success)}

❌ Failed:
{len(failed)}

⚠ Errors:
{len(errors)}

🔄 Checked:
{checked}/{total}

⏱ Time:
{end_time}s
"""

    await status_msg.edit_text(
        final_text
    )

    # ==========================================
    # SEND FILES
    # ==========================================

    if success:

        await update.message.reply_document(
            document=open(
                "success.txt",
                "rb"
            ),

            filename="success.txt",

            caption="✅ Success Results"
        )

    if failed:

        await update.message.reply_document(
            document=open(
                "failed.txt",
                "rb"
            ),

            filename="failed.txt",

            caption="❌ Failed Results"
        )

    if errors:

        await update.message.reply_document(
            document=open(
                "errors.txt",
                "rb"
            ),

            filename="errors.txt",

            caption="⚠ Error Logs"
        )

    # ==========================================
    # CLEANUP
    # ==========================================

    session.close()

    os.remove(path)

    if os.path.exists("success.txt"):
        os.remove("success.txt")

    if os.path.exists("failed.txt"):
        os.remove("failed.txt")

    if os.path.exists("errors.txt"):
        os.remove("errors.txt")

# ==========================================
# MAIN
# ==========================================

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

    print("🔥 BOT RUNNING")

    app.run_polling()

# ==========================================

if __name__ == "__main__":
    main()
