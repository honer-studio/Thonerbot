import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)
from telegram.constants import ParseMode

# ========================
# 🔐 اطلاعات اصلی پروژه
# ========================
# از متغیرهای محیطی برای اطلاعات حساس استفاده کنید
# مقادیر پیش‌فرض برای توسعه محلی هستند، در Render باید تنظیم شوند.
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE") # توکن خود را در Render تنظیم کنید
ADMIN_ID = int(os.environ.get("ADMIN_ID", "YOUR_ADMIN_ID_HERE")) # آیدی عددی ادمین را در Render تنظیم کنید
VALID_TOKEN = os.environ.get("VALID_TOKEN", "YOUR_VALID_TOKEN_HERE") # توکن معتبر خود را در Render تنظیم کنید

# برای Render.com، پورت و URL را از متغیرهای محیطی دریافت کنید
PORT = int(os.environ.get("PORT", "10000")) # پورت پیش‌فرض برای Render معمولاً 10000 است
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") # این را Render به طور خودکار تامین می‌کند

# ========================
# 🎯 مراحل مکالمه
# ========================
ASK_TOKEN, ASK_Q1, ASK_Q2, ASK_Q3, ASK_Q4, ASK_Q5 = range(6)
questions = [
    "❓ سوال ۱: نام کامل خود را وارد نمایید",
    "❓ سوال ۲: شماره ملی خود را وارد نمایید",
    "❓ سوال ۳: شماره تماس خود را وارد نمایید",
    "❓ سوال ۴: شماره اثر خود را وارد نمایید",
    "❓ سوال ۵: لطفاً عکس باکس پایین QR کد را ارسال نمایید"
]
# توجه: در نسخه رایگان، user_data در حافظه با هر بار خاموش شدن Render (به دلیل inactivity) پاک می‌شود.
# برای پایداری داده‌ها، نیاز به دیتابیس خارجی دارید.
user_data = {}

# ========================
# 🚀 شروع
# ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Register"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "سلام! برای شروع ثبت‌نام دکمه زیر را بزنید:",
        reply_markup=markup,
        parse_mode=ParseMode.HTML # در صورت نیاز به فرمت‌بندی HTML در آینده
    )
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
    if user_id not in user_data: # مدیریت حالت‌هایی که داده‌ها از بین رفته‌اند
        await update.message.reply_text("متاسفانه اطلاعات شما پاک شده است. لطفا مجددا /start را بزنید.")
        return ConversationHandler.END
    user_data[user_id]["answers"].append(update.message.text)
    await update.message.reply_text(questions[1])
    return ASK_Q3

async def ask_q3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        await update.message.reply_text("متاسفانه اطلاعات شما پاک شده است. لطفا مجددا /start را بزنید.")
        return ConversationHandler.END
    user_data[user_id]["answers"].append(update.message.text)
    await update.message.reply_text(questions[2])
    return ASK_Q4

async def ask_q4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        await update.message.reply_text("متاسفانه اطلاعات شما پاک شده است. لطفا مجددا /start را بزنید.")
        return ConversationHandler.END
    user_data[user_id]["answers"].append(update.message.text)
    await update.message.reply_text(questions[3])
    return ASK_Q5

async def ask_q5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        await update.message.reply_text("متاسفانه اطلاعات شما پاک شده است. لطفا مجددا /start را بزنید.")
        return ConversationHandler.END
    user_data[user_id]["answers"].append(update.message.text) # برای حالت متنی قبل از عکس
    await update.message.reply_text(questions[4])
    return ConversationHandler.END # انتظار برای عکس در مرحله بعد

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        await update.message.reply_text("متاسفانه اطلاعات شما پاک شده است. لطفا مجددا /start را بزنید.")
        return ConversationHandler.END

    last_answer = update.message.photo[-1].file_id if update.message.photo else "بدون عکس"
    
    # اطمینان حاصل شود که لیست answers به اندازه کافی بزرگ است یا عنصر اضافه شود
    if len(user_data[user_id]["answers"]) == 4: # اگر تا سوال 4 جواب داده شده باشد و هنوز عکس نیامده
        user_data[user_id]["answers"].append(last_answer)
    elif len(user_data[user_id]["answers"]) == 5: # اگر کاربر قبلاً متن برای Q5 داده و حالا عکس می‌فرستد
        user_data[user_id]["answers"][-1] = last_answer
    else: # حالت‌های غیرمنتظره
        user_data[user_id]["answers"].append(last_answer) # صرفا اضافه کردن
        
    token = user_data[user_id]["token"]
    answers = user_data[user_id]["answers"]

    msg = f"✅ *ثبت‌نام جدید:*\n\n🔑 *توکن:* `{token}`\n\n"
    for i, ans in enumerate(answers):
        if i < len(questions): # برای جلوگیری از خطای IndexError
            # حذف "❓ سوال" از ابتدای سوال برای نمایش تمیزتر
            question_text = questions[i].replace("❓ سوال ۱: ", "").replace("❓ سوال ۲: ", "").replace("❓ سوال ۳: ", "").replace("❓ سوال ۴: ", "").replace("❓ سوال ۵: ", "")
            msg += f"*{i+1}.* _{question_text}_: `{ans}`\n"

    # ارسال پیام به ادمین
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=msg,
        parse_mode=ParseMode.MARKDOWN_V2 # برای فرمت‌بندی Markdown
    )

    if last_answer != "بدون عکس":
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=last_answer, caption="📷 عکس باکس QR")

    await update.message.reply_text("✅ ثبت‌نام شما با موفقیت انجام شد. ممنون!")
    
    # پاک کردن داده‌های کاربر از حافظه (برای مدیریت بهتر حافظه در سرویس رایگان)
    if user_id in user_data:
        del user_data[user_id]
        
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_data:
        del user_data[user_id] # پاک کردن داده‌های کاربر
    await update.message.reply_text("⛔️ عملیات لغو شد.")
    return ConversationHandler.END

# ========================
# 🧠 اجرای ربات
# ========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^Register$"), ask_token)
        ],
        states={
            ASK_TOKEN: [MessageHandler(filters.Regex("^Register$"), ask_token)],
            ASK_Q1: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_token)],
            ASK_Q2: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_q2)],
            ASK_Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_q3)],
            ASK_Q4: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_q4)],
            ASK_Q5: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_q5), # برای متنی که ممکن است قبل از عکس ارسال شود
                MessageHandler(filters.PHOTO, finish) # نهایی کردن مکالمه با عکس
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        # داده‌های ConversationHandler در حافظه ذخیره می‌شوند.
        # برای حالت رایگان که ممکن است برنامه خاموش شود، این داده‌ها هم از بین می‌روند.
        # می‌توانید از persist_user_data=True و persist_chat_data=True با یک Storage استفاده کنید
        # اما نیاز به بک‌اند دیتابیس دارید که در طرح رایگان پیچیدگی بیشتری دارد.
    )

    app.add_handler(conv_handler)

    # برای Render.com از webhook استفاده کنید
    # Render پورت را به عنوان یک متغیر محیطی (PORT) تامین می‌کند.
    # WEBHOOK_URL نیز از Render تامین می‌شود.
    # url_path بهتر است یک رشته تصادفی و امن باشد، اما برای سادگی از BOT_TOKEN استفاده شده.
    try:
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN, # از توکن ربات به عنوان مسیر URL استفاده کنید
            webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
        )
        print(f"Webhook started on port {PORT} with URL {WEBHOOK_URL}/{BOT_TOKEN}")
    except Exception as e:
        print(f"Error starting webhook: {e}")
        # در صورت بروز خطا، می‌توانید به حالت long-polling برگردید (فقط برای دیباگ محلی مناسب است)
        # print("Falling back to polling...")
        # app.run_polling()


if __name__ == "__main__":
    main()
