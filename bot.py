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

CATEGORIES = {
    "🔥 Basic Panel": {
        "Basic Panel — 1 Day": {
            "price": 59,
            "file": "files/basic_1day.txt",
            "desc": "⏰ Validity: 1 Day (24 Hours)\n✅ Full Basic Panel Access\n🎮 Free Fire Panel Login"
        },
        "Basic Panel — 7 Days": {
            "price": 139,
            "file": "files/basic_7day.txt",
            "desc": "⏰ Validity: 7 Days\n✅ Full Basic Panel Access\n🎮 Free Fire Panel Login\n💰 Save vs daily!"
        },
        "Basic Panel — 30 Days": {
            "price": 599,
            "file": "files/basic_30day.txt",
            "desc": "⏰ Validity: 30 Days (1 Month)\n✅ Full Basic Panel Access\n🎮 Free Fire Panel Login\n🏆 Best Value!"
        },
    },
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
pending_orders: dict[int, str] = {}

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton(cat, callback_data=f"cat|{cat}")] for cat in CATEGORIES]
    buttons.append([InlineKeyboardButton("ℹ️ How to Buy", callback_data="help")])
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

async def category_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat = query.data.split("|", 1)[1]
    products = CATEGORIES.get(cat, {})
    buttons = [[InlineKeyboardButton(f"{name}  •  ₹{info['price']}", callback_data=f"prod|{name}")] for name, info in products.items()]
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back_main")])
    await query.edit_message_text(f"*{cat}*\n\n👇 Select a plan:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

async def product_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    name = query.data.split("|", 1)[1]
    info = None
    for cat_prods in CATEGORIES.values():
        if name in cat_prods:
            info = cat_prods[name]
            break
    if not info:
        await query.answer("Product not found!", show_alert=True)
        return
    text = (f"🎮 *{name}*\n\n📋 {info['desc']}\n\n━━━━━━━━━━━━━━━━━━\n💰 Price: *₹{info['price']}*\n━━━━━━━━━━━━━━━━━━\n\nTap *Buy Now* to proceed 👇")
    buttons = [[InlineKeyboardButton("💳 Buy Now", callback_data=f"buy|{name}")], [InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

async def buy_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    name = query.data.split("|", 1)[1]
    info = None
    for cat_prods in CATEGORIES.values():
        if name in cat_prods:
            info = cat_prods[name]
            break
    if not info:
        return
    user_id = query.from_user.id
    pending_orders[user_id] = name
    caption = (f"💳 *Payment Details*\n\n🎮 Plan: *{name}*\n💰 Amount: *₹{info['price']}*\n\n━━━━━━━━━━━━━━━━━━\nUPI ID: `{UPI_ID}`\n━━━━━━━━━━━━━━━━━━\n\n📲 *Steps:*\n1️⃣ Pay *₹{info['price']}* to UPI ID above\n2️⃣ Take *screenshot* of payment\n3️⃣ Send screenshot here 👇\n\n⚡ Panel sent after admin approval!")
    try:
        with open(UPI_QR_IMG, "rb") as qr:
            await ctx.bot.send_photo(chat_id=query.message.chat_id, photo=qr, caption=caption, parse_mode="Markdown")
    except FileNotFoundError:
        await ctx.bot.send_message(chat_id=query.message.chat_id, text=caption, parse_mode="Markdown")
    await query.delete_message()

async def screenshot_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    product_name = pending_orders.get(user_id)
    if not product_name:
        await update.message.reply_text("⚠️ Please use /start and select a plan first!")
        return
    info = None
    for cat_prods in CATEGORIES.values():
        if product_name in cat_prods:
            info = cat_prods[product_name]
            break
    caption = (f"📥 *New Payment — FF Panel*\n\n👤 User: [{user.full_name}](tg://user?id={user_id})\n🆔 ID: `{user_id}`\n🎮 Plan: *{product_name}*\n💰 Amount: ₹{info['price'] if info else 'N/A'}")
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve & Send", callback_data=f"approve|{user_id}|{product_name}"), InlineKeyboardButton("❌ Reject", callback_data=f"reject|{user_id}")]])
    if update.message.photo:
        await ctx.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption, parse_mode="Markdown", reply_markup=buttons)
    elif update.message.document:
        await ctx.bot.send_document(chat_id=ADMIN_ID, document=update.message.document.file_id, caption=caption, parse_mode="Markdown", reply_markup=buttons)
    await update.message.reply_text("✅ *Screenshot received!*\n\n⏳ Admin verifying payment...\n🎮 Panel will be sent shortly! 🙏", parse_mode="Markdown")

async def approve_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Not authorized!", show_alert=True)
        return
    _, user_id_str, product_name = query.data.split("|", 2)
    user_id = int(user_id_str)
    file_path = None
    for cat_prods in CATEGORIES.values():
        if product_name in cat_prods:
            file_path = cat_prods[product_name]["file"]
            break
    try:
        with open(file_path, "rb") as f:
            await ctx.bot.send_document(chat_id=user_id, document=f, caption=(f"🎉 *Payment Approved!*\n\n🎮 Plan: *{product_name}*\n\n📄 Panel login details in the file above!\n\nThank you! 🙏 Type /start to buy again."), parse_mode="Markdown")
        await query.edit_message_caption(caption=query.message.caption + "\n\n✅ *APPROVED — Panel sent!*", parse_mode="Markdown")
    except FileNotFoundError:
        await ctx.bot.send_message(chat_id=user_id, text=f"🎉 *Payment Approved!*\n\n🎮 Plan: *{product_name}*\n\n⚠️ Panel details coming shortly.", parse_mode="Markdown")
        await query.answer("⚠️ File not found! Notified user.", show_alert=True)
    pending_orders.pop(user_id, None)
    await query.answer("✅ Approved & panel sent!")

async def reject_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("Not authorized!", show_alert=True)
        return
    _, user_id_str = query.data.split("|", 1)
    user_id = int(user_id_str)
    await ctx.bot.send_message(chat_id=user_id, text="❌ *Payment Rejected*\n\nYour payment was not verified.\n\n• Screenshot unclear\n• Wrong amount\n• Invalid payment\n\nPlease retry with /start", parse_mode="Markdown")
    await query.edit_message_caption(caption=query.message.caption + "\n\n❌ *REJECTED*", parse_mode="Markdown")
    pending_orders.pop(user_id, None)
    await query.answer("❌ Rejected & user notified.")

async def back_main(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    buttons = [[InlineKeyboardButton(cat, callback_data=f"cat|{cat}")] for cat in CATEGORIES]
    buttons.append([InlineKeyboardButton("ℹ️ How to Buy", callback_data="help")])
    await query.edit_message_text("🎮 *FF Basic Panel Store*\n\n━━━━━━━━━━━━━━━━━━\n🔥 *Basic Panel Pricing:*\n1️⃣  1 Day   →  ₹59\n7️⃣  7 Days  →  ₹139\n3️⃣  30 Days →  ₹599\n━━━━━━━━━━━━━━━━━━\n\n👇 Select a plan to buy:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

async def help_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("ℹ️ *How to Buy*\n\n1️⃣ Plan select pannu\n2️⃣ *Buy Now* tap pannu\n3️⃣ UPI-la payment pannu\n4️⃣ Screenshot send pannu\n5️⃣ Admin verify → Panel deliver ✅\n\n📞 Issues? Contact admin.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]))

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(category_handler, pattern=r"^cat\|"))
    app.add_handler(CallbackQueryHandler(product_handler,  pattern=r"^prod\|"))
    app.add_handler(CallbackQueryHandler(buy_handler,      pattern=r"^buy\|"))
    app.add_handler(CallbackQueryHandler(approve_handler,  pattern=r"^approve\|"))
    app.add_handler(CallbackQueryHandler(reject_handler,   pattern=r"^reject\|"))
    app.add_handler(CallbackQueryHandler(back_main,        pattern=r"^back_main$"))
    app.add_handler(CallbackQueryHandler(help_handler,     pattern=r"^help$"))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, screenshot_handler))
    print("🤖 FF Panel Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
