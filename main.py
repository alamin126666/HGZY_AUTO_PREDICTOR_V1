import telebot from telebot import types import os

BOT_TOKEN = os.getenv("BOT_TOKEN") or "7962322784:AAGG4n8SH2OdhSLxTfCk31Xk-SX1MvHWyZo" bot = telebot.TeleBot(BOT_TOKEN)

In-memory storage for channels

added_channels = []

Utility function to safely edit messages

def safe_edit_message_text(bot, text, chat_id, message_id, reply_markup=None, parse_mode="Markdown"): try: bot.edit_message_text( text=text, chat_id=chat_id, message_id=message_id, reply_markup=reply_markup, parse_mode=parse_mode ) except telebot.apihelper.ApiTelegramException as e: if "message is not modified" in str(e): print("⚠️ Message not modified, skipping edit...") else: raise e

Handle button callbacks

@bot.callback_query_handler(func=lambda call: True) def handle_callback(call): if call.data == "signal_on": keyboard = types.InlineKeyboardMarkup() keyboard.add(types.InlineKeyboardButton("SIGNAL OFF", callback_data="signal_off")) safe_edit_message_text(bot, "✅ SIGNAL ON COMPLETED", call.message.chat.id, call.message.message_id, keyboard)

elif call.data == "signal_off":
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("SIGNAL ON", callback_data="signal_on"))
    safe_edit_message_text(bot, "❌ *SIGNAL OFF COMPLETED*", call.message.chat.id, call.message.message_id, keyboard)

elif call.data == "add_channel":
    msg = bot.send_message(call.message.chat.id, "📥 *TELEGRAM CHANNEL LINK ⬇️*", parse_mode="Markdown")
    bot.register_next_step_handler(msg, save_channel_link)

elif call.data == "channel_list":
    if not added_channels:
        bot.send_message(call.message.chat.id, "❗ No channels added yet.")
    else:
        text = "🔴 *All Channel Link* ⤵️\n\n"
        for ch in added_channels:
            text += f"Channel -----> @{ch}\n🔗 [Click to Visit](https://t.me/{ch})\n\n"
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

Save channel link from user

def save_channel_link(message): link = message.text.strip() if link.startswith("https://t.me/"): username = link.split("https://t.me/")[-1].strip("/") elif link.startswith("@"): username = link[1:] else: username = link added_channels.append(username) bot.send_message(message.chat.id, f"✅ Channel @{username} added successfully!", parse_mode="Markdown")

Start command

@bot.message_handler(commands=['start']) def send_welcome(message): markup = types.InlineKeyboardMarkup() markup.row( types.InlineKeyboardButton("SIGNAL ON", callback_data="signal_on"), types.InlineKeyboardButton("SIGNAL OFF", callback_data="signal_off") ) markup.row( types.InlineKeyboardButton("ADD CHANNEL", callback_data="add_channel"), types.InlineKeyboardButton("CHANNEL LIST", callback_data="channel_list") ) bot.send_message( message.chat.id, "💢 HGZY Prediction Bot 💢\n\nWelcome! নিচের বাটনগুলো দিয়ে সিগন্যাল নিয়ন্ত্রণ করো।", parse_mode="Markdown", reply_markup=markup )

bot.remove_webhook() bot.infinity_polling()
