from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# --- CONFIGURATION ---
ADMIN_ID = 8310700441
TOKEN = '8890969566:AAFS7CF97zSRnNDOW_PyggG5_c3oiqF4SPk'
QR_FILE_ID = 'AgACAgUAAxkBAAMMalEm5tJsHde09PBCZ3bFltx58NcAAhMRaxtWLoBWO_eGLFnSgMsBAAMCAAN5AAM8BA'

VOICE_START_ID = 'AwACAgUAAxkBAAN_alFJLq2XXkBZbIyYKch0wKXK55oAAm8hAALgIPhUnQ7Y8Mo0lzo8BA'
VOICE_MENU_ID = 'AwACAgUAAxkBAAOOalFNd8H696uLPvbO9J25Syai0fgAAnMhAALgIPhUnQ7Y8Mo0lzo8BA'

MAIN_MENU, PLAN_SELECTION, PAYMENT_SENDING = range(3)

async def start(update, context):
    keyboard = [[InlineKeyboardButton("📞 Video Call", callback_data='video_call')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Welcome! Click below to see our plans:\n\nFull open enjoy 💋🫦"
    
    await update.message.reply_voice(voice=VOICE_START_ID)
    await update.message.reply_text(text, reply_markup=reply_markup)
    return MAIN_MENU

async def video_call_menu(update, context):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📞 Demo - ₹20", callback_data='pay_20')],
        [InlineKeyboardButton("📞 5 Min - ₹50", callback_data='pay_50')],
        [InlineKeyboardButton("📞 10 Min - ₹100", callback_data='pay_100')],
        [InlineKeyboardButton("📞 20 Min - ₹200", callback_data='pay_200')],
        [InlineKeyboardButton("📞 30 Min - ₹300", callback_data='pay_300')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back_to_main')]
    ]
    
    await query.message.reply_voice(voice=VOICE_MENU_ID)
    await query.edit_message_text("📞 Select your Video Call Plan:\n\nFull open enjoy 💋🫦", reply_markup=InlineKeyboardMarkup(keyboard))
    return PLAN_SELECTION

async def show_qr(update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_photo(photo=QR_FILE_ID, caption="💳 Scan & Pay to unlock your service.\n\n📥 Pay karke screenshot yahan send karein.")
    return PAYMENT_SENDING

async def handle_payment_proof(update, context):
    await update.message.reply_text("⏳ Proof received! Admin check kar rahe hain, wait karein.")
    await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
    keyboard = [[InlineKeyboardButton("✅ Approve", callback_data=f'approve_{update.message.chat_id}'),
                 InlineKeyboardButton("❌ Reject", callback_data=f'reject_{update.message.chat_id}')]]
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"New Payment from {update.message.from_user.first_name}", reply_markup=InlineKeyboardMarkup(keyboard))
    return PAYMENT_SENDING

async def admin_response(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = int(data.split('_')[1])
    if data.startswith('approve'):
        await context.bot.send_message(chat_id=user_id, text="✅ Aapki payment verify ho gayi hai! Enjoy! 💋")
        await query.edit_message_text("✅ Approved!")
        return ConversationHandler.END
    else:
        await context.bot.send_message(chat_id=user_id, text="❌ Video call karna hai to sahi paymet kro na baby kyu time pass kar rehe ho.")
        await context.bot.send_photo(chat_id=user_id, photo=QR_FILE_ID, caption="Dobara payment karke proof bhejein.")
        await query.edit_message_text("❌ Rejected!")
        return PAYMENT_SENDING

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [CallbackQueryHandler(video_call_menu, pattern='video_call')],
            PLAN_SELECTION: [CallbackQueryHandler(show_qr, pattern='^pay_'), CallbackQueryHandler(start, pattern='back_to_main')],
            PAYMENT_SENDING: [MessageHandler(filters.PHOTO | filters.TEXT, handle_payment_proof)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(admin_response, pattern='^(approve|reject)_'))
    app.run_polling()
