import os
import telebot
import requests
import time
from threading import Thread
from flask import Flask
from telebot import types

# --- [ 1. CONFIGURATION ] ---
TOKEN = '8641622144:AAGO_f5sc3_V0yho8hTnH_VRX_aH7Xx6BOw'
ADMIN_ID = 6513777887 
ADMIN_USERNAME = "@Dangi_Kan"
APP_URL = "https://sixwin-auto-predictor-1.onrender.com" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_list = set()

# Links Configuration
LINKS = {
    "6L": "https://www.6win999.com/#/register?invitationCode=856411134469",
    "CK": "http://www.cklottery.tv/#/register?invitationCode=15473304912",
    "777": "https://www.777bigwingame.club/#/register?invitationCode=67132596471",
    "TOPUP": "https://t.me/Dangai_colour/10",
    "BIND": "https://t.me/Dangai_colour/8",
    "REGISTER_GUIDE": "https://t.me/Dangai_colour/7"
}

# --- [ 2. ANTI-SLEEP ENGINE ] ---
def keep_alive_engine():
    """Bot ကို ၅ မိနစ်တစ်ခါ ပုတ်နှိုးပေးမယ့်စနစ်"""
    print("🚀 Anti-Sleep Engine Started...")
    while True:
        try:
            requests.get(APP_URL, timeout=20)
            print("💤 Ping Success: Bot remains Awake!")
        except Exception as e:
            print(f"⚠️ Ping Warning: {e}")
        time.sleep(300)

# --- [ 3. ADVANCED FORMULA LOGIC ] ---
def get_advanced_prediction(history):
    if len(history) < 2: return None, None
    # Dragon Trend
    if len(history) >= 3 and history[0] == history[1] == history[2]:
        return history[0], "Dragon Trend 🔥"
    # ZigZag Logic
    if len(history) >= 3 and history[0] != history[1] and history[1] != history[2]:
        pred = "BIG" if history[0] == "SMALL" else "SMALL"
        return pred, "ZigZag Strategy ⚡"
    # Default: Mirror Strategy
    pred = "BIG" if history[0] == "SMALL" else "SMALL"
    return pred, "Mirror Strategy 🔮"

# --- [ 4. HANDLERS ] ---
@bot.message_handler(commands=['admin'])
def admin_panel(m):
    if m.from_user.id == ADMIN_ID:
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("📊 Bot Status", callback_data="status"),
            types.InlineKeyboardButton("📢 Broadcast", callback_data="bc"),
            types.InlineKeyboardButton("👥 User Count", callback_data="u_count")
        )
        bot.send_message(m.chat.id, "👨‍💻 **Admin Control Panel**", parse_mode="Markdown", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "status":
        bot.answer_callback_query(call.id, "Bot is Live! 🟢")
    elif call.data == "u_count":
        bot.answer_callback_query(call.id, f"Users: {len(user_list)}", show_alert=True)
    elif call.data == "bc":
        msg = bot.send_message(call.message.chat.id, "📢 **ပို့ချင်တဲ့စာကို ရိုက်ပေးပါ။**")
        bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(m):
    count = 0
    for user in list(user_list):
        try:
            bot.send_message(user, f"📢 **ADMIN MESSAGE**\n\n{m.text}", parse_mode="Markdown")
            count += 1
        except: pass
    bot.send_message(m.chat.id, f"✅ User {count} ယောက်ထံ ပို့ပြီးပါပြီ!")

@bot.message_handler(commands=['start'])
def start(m):
    user_list.add(m.chat.id)
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🎮 6Lottery Acc ဖောက်ရန်", url=LINKS["6L"]),
        types.InlineKeyboardButton("🎰 CK Lottery Acc ဖောက်ဆော့ရန်", url=LINKS["CK"]),
        types.InlineKeyboardButton("🔥 777 BigWin Acc ဖောက်ရန်", url=LINKS["777"]),
        types.InlineKeyboardButton("📝 Acc ဖောက်နည်း ကြည့်ရန်", url=LINKS["REGISTER_GUIDE"]),
        types.InlineKeyboardButton("💰 ငွေဖြည့်နည်း ကြည့်ရန်", url=LINKS["TOPUP"]),
        types.InlineKeyboardButton("💳 Acc ချိတ်/ငွေထုတ်နည်း", url=LINKS["BIND"]),
        types.InlineKeyboardButton("👨‍💻 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME[1:]}")
    )
    bot.send_message(m.chat.id, "🌟 **WinGo Prediction Bot** 🌟\n\n🎯 **Signal ရယူရန်:** ၅ ပွဲစာ ရိုက်ပို့ပါ။\nဥပမာ - `B S B B S`", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(func=lambda message: True)
def handle_msg(m):
    user_list.add(m.chat.id)
    words = m.text.upper().replace(',', ' ').split()
    history = [w for w in words if w in ['B', 'BIG', 'S', 'SMALL']]
    
    if len(history) >= 2:
        pred, logic_name = get_advanced_prediction(history)
        emoji = "🔴" if pred == "BIG" else "🟢"
        res = (f"🎯 **WIN GO SIGNAL**\n"
               f"🎰 Next Bet: **{pred}** {emoji}\n"
               f"🧠 Logic: {logic_name}\n"
               f"💸 Strategy: 3x Martingale\n\n"
               f"⚠️ **ရှုံးလျှင် ၃ ဆတိုးလောင်းပါ** 🚀")
        bot.reply_to(m, res, parse_mode="Markdown")

# --- [ 5. RENDER WEB SERVER ] ---
@app.route('/')
def home(): return "BOT IS ACTIVE & RUNNING 🟢"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# --- [ 6. MAIN RUNNER WITH AUTO-RESTART ] ---
if __name__ == "__main__":
    # Flask နဲ့ Anti-sleep ကို Background မှာ စတင်မယ်
    Thread(target=run_flask, daemon=True).start()
    Thread(target=keep_alive_engine, daemon=True).start()
    
    print("🤖 Bot is Starting...")
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            print(f"❌ Error: {e}. Restarting in 5s...")
            time.sleep(5)
