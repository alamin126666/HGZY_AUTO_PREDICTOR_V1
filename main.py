import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("Error: BOT_TOKEN environment variable not set!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# Data file for storing channels and signals
DATA_FILE = "channels.json"

# Load data from JSON or initialize
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"channels": [], "signal_status": {}}

# Save data to JSON
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# Keyboard buttons for main menu
def main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("SIGNAL ON", callback_data="signal_on"),
        InlineKeyboardButton("SIGNAL OFF", callback_data="signal_off"),
        InlineKeyboardButton("ADD CHANNEL", callback_data="add_channel"),
        InlineKeyboardButton("CHANNEL LIST", callback_data="channel_list")
    )
    return keyboard

# Start command handler
@bot.message_handler(commands=["start"])
def start_handler(message):
    text = "💢 *HGZY Prediction Bot* 💢\n\nWelcome! নিচের বাটনগুলো দিয়ে সিগন্যাল নিয়ন্ত্রণ করো।"
    bot.send_message(message.chat.id, text, reply_markup=main_keyboard(), parse_mode="Markdown")

# Callback query handler (button clicks)
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data_loaded = load_data()  # fresh load for concurrency
    chat_id = call.message.chat.id

    if call.data == "signal_on":
        if not data_loaded["channels"]:
            bot.answer_callback_query(call.id, "কোনো চ্যানেল এড করা হয়নি!")
            return
        # Show list of channels to select for signal ON
        kb = InlineKeyboardMarkup()
        for ch in data_loaded["channels"]:
            kb.add(InlineKeyboardButton(ch, callback_data=f"signal_on_{ch}"))
        bot.edit_message_text("🚦 সিগন্যাল চালু করতে চ্যানেল সিলেক্ট করো:", chat_id, call.message.message_id, reply_markup=kb)

    elif call.data.startswith("signal_on_"):
        channel = call.data.replace("signal_on_", "")
        data_loaded["signal_status"][channel] = True
        save_data(data_loaded)
        bot.edit_message_text(f"✅ Signal ON completed for {channel}", chat_id, call.message.message_id, reply_markup=main_keyboard())

    elif call.data == "signal_off":
        if not data_loaded["channels"]:
            bot.answer_callback_query(call.id, "কোনো চ্যানেল এড করা হয়নি!")
            return
        # Show list of channels to select for signal OFF
        kb = InlineKeyboardMarkup()
        for ch in data_loaded["channels"]:
            kb.add(InlineKeyboardButton(ch, callback_data=f"signal_off_{ch}"))
        bot.edit_message_text("🛑 সিগন্যাল বন্ধ করতে চ্যানেল সিলেক্ট করো:", chat_id, call.message.message_id, reply_markup=kb)

    elif call.data.startswith("signal_off_"):
        channel = call.data.replace("signal_off_", "")
        data_loaded["signal_status"][channel] = False
        save_data(data_loaded)
        bot.edit_message_text(f"✅ Signal OFF completed for {channel}", chat_id, call.message.message_id, reply_markup=main_keyboard())

    elif call.data == "add_channel":
        msg = bot.send_message(chat_id, "👉 এখন চ্যানেল এর ইউজারনেম বা লিংক পাঠাও (যেমন: @yourchannel)")
        bot.register_next_step_handler(msg, add_channel_handler)

    elif call.data == "channel_list":
        if not data_loaded["channels"]:
            bot.answer_callback_query(call.id, "কোনো চ্যানেল এড করা হয়নি!")
            return
        text = "🔴 All Channel Link ⤵️\n\n"
        for ch in data_loaded["channels"]:
            signal = data_loaded["signal_status"].get(ch, False)
            status = "🟢 ON" if signal else "🔴 OFF"
            text += f"Channel: {ch}\nStatus: {status}\n🔗 [Click to Visit](https://t.me/{ch.lstrip('@')})\n\n"
        bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=main_keyboard())

# Handler to add channel after user sends channel username/link
def add_channel_handler(message):
    ch = message.text.strip()
    if not ch.startswith("@"):
        ch = "@" + ch
    data_loaded = load_data()
    if ch in data_loaded["channels"]:
        bot.reply_to(message, "এই চ্যানেলটি ইতিমধ্যে অ্যাড করা আছে।")
        bot.send_message(message.chat.id, "মেইন মেনুতে ফিরে আসো:", reply_markup=main_keyboard())
        return
    data_loaded["channels"].append(ch)
    data_loaded["signal_status"][ch] = False  # default off
    save_data(data_loaded)
    bot.reply_to(message, f"{ch} চ্যানেল সফলভাবে অ্যাড করা হয়েছে।")
    bot.send_message(message.chat.id, "মেইন মেনুতে ফিরে আসো:", reply_markup=main_keyboard())

# Run the bot
if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling()