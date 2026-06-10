#!/usr/bin/env python3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

BOT_TOKEN  = "8820231336:AAGI0V83PJ4oihM4O6PilogEas6vUtsDjGE"
ADMIN_ID   = 7059821729
UPI_ID     = "9363904060@ptyes"
UPI_QR_IMG = "upi_qr.jpg"

# Products — simple keys for callback_data
PRODUCTS = {
    "p1": {"name": "Basic Panel — 1 Day",   "price": 59,  "file": "files/basic_1day.txt",  "desc": "⏰ Validity: 1 Day (24 Hours)\n✅ Full Basic Panel Access\n🎮 Free Fire Panel Login"},
    "p2": {"name": "Basic Panel — 7 Days",  "price": 139, "file": "files/basic_7day.txt",  "desc": "⏰ Validity: 7 Days\n✅ Full Basic Panel Access\n🎮 Free Fire Panel Login\n💰 Save vs daily!"},
    "p3": {"name": "Basic Panel — 30 Days", "price": 599, "file": "files/basic_30day.txt", "desc": "⏰ Validity: 30 Days\n✅ Full Basic Panel Access\n🎮 Free Fire Panel Login\n🏆 Best Value!"},
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
pending_orders: dict[int, str] = {}


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("1️⃣ Basic Panel — 1 Day   • ₹59",  callback_data="prod_p1")],
        [InlineKeyboardButton("7️⃣ Basic Panel — 7 Days  • ₹139", callback_data="prod_p2")],
        [InlineKeyboardButton("3️⃣ Basic Panel — 30 Days • ₹599", callback_data="prod_p3")],
        [InlineKeyboardButton("ℹ️ How to Buy", callback_data="help")],
    ]
    await update.message.reply_text(
        "🎮 *FF Basic Panel Store*\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔥 *Basic Panel Pricing:*\n"
        "1️⃣  1 Day   →  ₹59\n"
        "7️⃣  7 Days  →  ₹139\n"
        "3️⃣  30 Days →  ₹599\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "👇 Select a plan to buy:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def product_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.replace("prod_", "")
    info = PRODUCTS.get(key)
    if not info:
        await query.answer("Product not found!", show_alert=True)
        return
    text = (
        f"🎮 *{info['name']}*\n\n"
        f"📋 {info['desc']}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 Price: *₹{info['price']}*\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        "Tap *Buy Now* to proceed 👇"
    )
    buttons = [
        [InlineKeyboardButton("💳 Buy Now", callback_data=f"buy_{key}")],
        [InlineKeyboardButton("🔙 Back",    callback_data="back_main")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))


async def buy_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.replace("buy_", "")
    info = PRODUCTS.get(key)
    if not info:
        return
    user_id = query.from_user.id
    pending_orders[user_id] = key
    caption = (
        f"💳 *Payment Details*\n\n"
        f"🎮 Plan: *{info['name']}*\n"
        f"💰 Amount: *₹{info['price']}*\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"UPI ID: `{UPI_ID}`\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"📲 *Steps:*\n"
        f"1️⃣ Pay *₹{info['price']}* to UPI ID above\n"
        f"2️⃣ Take *screenshot* of payment\n"
        f"3️⃣ Send screenshot here 👇\n\n"
        f"⚡ Panel sent after admin approval!"
    )
    try:
        with open(UPI_QR_IMG, "rb") as qr:
            await ctx.bot.send_photo(chat_id=query.message.chat_id, photo=qr, caption=caption, parse_mode="Markdown")
    except FileNotFoundError:
        await ctx.bot.send_message(chat_id=query.message.chat_id, text=caption, parse_mode="Markdown")
    await query.delete_message()


async def screenshot_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    key = pending_orders.get(user_id)
    if not key:
        await update.message.reply_text("⚠️ Please use /start and select a plan first!")
        return
    info = PRODUCTS.get(key)
    caption = (
        f"📥 *New Payment — FF Panel*\n\n"
        f"👤 User: [{user.full_name}](tg://user?id={user_id})\n"
        f"🆔 ID: `{user_id}`\n"
        f"🎮 Plan: *{info['name']}*\n"
        f"💰 Amount: ₹{info['price']}"
    )
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Approve & Send", callback_data=f"approve_{user_id}_{key}"),
        InlineKeyboardButton("❌ Reject",         callback_data=f"reject_{user_id}"),
    ]])
    if update.message.photo:
        await ctx.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption, parse_mode="Markdown", reply_markup=buttons)
    elif update.message.document:
        await ctx.bot.send_document(chat_id=ADMIN_ID, document=update.message.document.file_id, caption=caption, parse_mode="Markdown", reply_markup=buttons)
    await update.message.reply_text(
        "✅ *Screenshot received!*\n\n"
        "⏳ Admin verifying payment...\n"
        "🎮 Panel will be sent shortly! 🙏",
        parse_mode="Markdown"
    )


async def approve_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Not authorized!", show_alert=True)
        return
    parts = query.data.replace("approve_", "").split("_")
    user_id = int(parts[0])
    key = parts[1]
    info = PRODUCTS.get(key)
    if not info:
        return
    try:
        with open(info["file"], "rb") as f:
            await ctx.bot.send_document(
                chat_id=user_id, document=f,
                caption=(
                    f"🎉 *Payment Approved!*\n\n"
                    f"🎮 Plan: *{info['name']}*\n\n"
                    f"📄 Panel login details in the file above!\n\n"
                    f"Thank you! 🙏 Type /start to buy again."
                ),
                parse_mode="Markdown"
            )
        await query.edit_message_caption(caption=query.message.caption + "\n\n✅ *APPROVED — Panel sent!*", parse_mode="Markdown")
    except FileNotFoundError:
        await ctx.bot.send_message(chat_id=user_id, text=f"🎉 *Payment Approved!*\n\n🎮 Plan: *{info['name']}*\n\n⚠️ Panel details coming shortly.", parse_mode="Markdown")
        await query.answer("⚠️ File not found on server!", show_alert=True)
    pending_orders.pop(user_id, None)
    await query.answer("✅ Approved & panel sent!")


async def reject_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Not authorized!", show_alert=True)
        return
    user_id = int(query.data.replace("reject_", ""))
    await ctx.bot.send_message(
        chat_id=user_id,
        text="❌ *Payment Rejected*\n\nYour payment was not verified.\n\n• Screenshot unclear\n• Wrong amount\n• Invalid payment\n\nPlease retry with /start",
        parse_mode="Markdown"
    )
    await query.edit_message_caption(caption=query.message.caption + "\n\n❌ *REJECTED*", parse_mode="Markdown")
    pending_orders.pop(user_id, None)
    await query.answer("❌ Rejected & user notified.")


async def back_main(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    buttons = [
        [InlineKeyboardButton("1️⃣ Basic Panel — 1 Day   • ₹59",  callback_data="prod_p1")],
        [InlineKeyboardButton("7️⃣ Basic Panel — 7 Days  • ₹139", callback_data="prod_p2")],
        [InlineKeyboardButton("3️⃣ Basic Panel — 30 Days • ₹599", callback_data="prod_p3")],
        [InlineKeyboardButton("ℹ️ How to Buy", callback_data="help")],
    ]
    await query.edit_message_text(
        "🎮 *FF Basic Panel Store*\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔥 *Basic Panel Pricing:*\n"
        "1️⃣  1 Day   →  ₹59\n"
        "7️⃣  7 Days  →  ₹139\n"
        "3️⃣  30 Days →  ₹599\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "👇 Select a plan to buy:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def help_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
    await query.edit_message_text(
        "ℹ️ *How to Buy*\n\n"
        "1️⃣ Plan select pannu\n"
        "2️⃣ *Buy Now* tap pannu\n"
        "3️⃣ UPI-la payment pannu\n"
        "4️⃣ Screenshot send pannu\n"
        "5️⃣ Admin verify → Panel deliver ✅\n\n"
        "📞 Issues? Contact admin.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(product_handler, pattern=r"^prod_"))
    app.add_handler(CallbackQueryHandler(buy_handler,     pattern=r"^buy_"))
    app.add_handler(CallbackQueryHandler(approve_handler, pattern=r"^approve_"))
    app.add_handler(CallbackQueryHandler(reject_handler,  pattern=r"^reject_"))
    app.add_handler(CallbackQueryHandler(back_main,       pattern=r"^back_main$"))
    app.add_handler(CallbackQueryHandler(help_handler,    pattern=r"^help$"))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, screenshot_handler))
    print("🤖 FF Panel Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
