from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)

BOT_TOKEN = "7318022480:AAFN-AvEXPuxMx-Ah0VTlDwkvq19QjGXiVs"
ADMIN_ID = 988260745  # ← آیدی عددی ادمین وارد شده
VALID_TOKEN = "HonerOmerL140450#&@1404"

ASK_TOKEN, ASK_Q1, ASK_Q2, ASK_Q3, ASK_Q4 = range(5)
questions = [
    "❓ سوال ۱: نام کامل خود را وارد نمایید",
    "❓ سوال ۲: شماره ملی خود را وارد نمایید",
    "❓ سوال ۳: شماره تماس خود را وارد نمایید",
    "❓ سوال ۴: لطفاً عکس باکس پایین QR کد را ارسال نمایید"
]
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Register"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("سلام! برای شروع ثبت‌نام دکمه زیر را بزنید:", reply_markup=markup)
    return ASK_TOKEN

async def ask_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 لطفاً توکن دسترسی خود را وارد کنید:")
    return ASK_Q1

async def check_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    user_id = update.message.from_user.id

    if user_input == VALID_TOKEN:
        user_data[user_id] = {"token": user_input, "answers": []}
        await update.message.reply_text(questions[0])
        return ASK_Q2
    else:
        await update.message.reply_text("❌ توکن نامعتبر است. لطفاً دوباره تلاش کنید:")
        return ASK_Q1

async def ask_q2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id]["answers"].append(update.message.text)
    await update.message.reply_text(questions[1])
    return ASK_Q3

async def ask_q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id]["answers"].append(update.message.text)
    await update.message.reply_text(questions[2])
    return ASK_Q4

async def ask_q4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id]["answers"].append(update.message.text)
    await update.message.reply_text(questions[3])
    return ConversationHandler.END

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    last_answer = update.message.photo[-1].file_id if update.message.photo else "بدون عکس"
    user_data[user_id]["answers"].append(last_answer)

    token = user_data[user_id]["token"]
    answers = user_data[user_id]["answers"]

    msg = f"✅ ثبت‌نام جدید:\n\n🔑 توکن: {token}\n\n"
    for i in range(3):
        msg += f"{i+1}. {questions[i]} {answers[i]}\n"

    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

    if last_answer != "بدون عکس":
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=last_answer, caption="📷 عکس باکس QR")

    await update.message.reply_text("✅ ثبت‌نام شما با موفقیت انجام شد. ممنون!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⛔️ عملیات لغو شد.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^Register$"), ask_token)
        ],
        states={
            ASK_Q1: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_token)],
            ASK_Q2: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_q2)],
            ASK_Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_q3)],
            ASK_Q4: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_q4)],
            ConversationHandler.END: [MessageHandler(filters.PHOTO, finish)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    print("🤖 ربات در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()
