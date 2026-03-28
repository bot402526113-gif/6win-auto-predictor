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

# --- [ 2. ANTI-SLEEP PING SYSTEM ] ---
def keep_alive():
    while True:
        try:
            requests.get(APP_URL, timeout=10)
            print("💤 Anti-Sleep: Bot is active and awake!")
        except:
            print("⚠️ Anti-Sleep: Connection error, retrying...")
        time.sleep(300) 

# --- [ 3. ADVANCED FORMULA LOGIC ] ---
def get_advanced_prediction(history):
    if len(history) < 2: return None, None
    
    # Formula 1: Dragon Trend (🔴/🟢 ဆက်တိုက်ထွက်လျှင် လိုက်မည်)
    if len(history) >= 3 and history[0] == history[1] == history[2]:
        return history[0], "Dragon Trend 🔥"
    
    # Formula 2: ZigZag Logic (တစ်လှည့်စီထွက်လျှင် ပြောင်းပြန်ယူ)
    if len(history) >= 3 and history[0] != history[1] and history[1] != history[2]:
        pred = "BIG" if history[0] == "SMALL" else "SMALL"
        return pred, "ZigZag Strategy ⚡"
    
    # Formula 3: 2-1 Pattern (B B S -> B)
    if len(history) >= 3 and history[0] == history[1] and history[1] != history[2]:
        return history[0], "Double Logic ✨"

    # Default: Mirror Strategy (နောက်ဆုံးထွက်တာကို ပြောင်းပြန်ယူ)
    pred = "BIG" if history[0] == "SMALL" else "SMALL"
    return pred, "Mirror Strategy 🔮"

# --- [ 4. ADMIN & USER HANDLERS ] ---

@bot.message_handler(commands=['admin'])
def admin_panel(m):
    if m.from_user.id == ADMIN_ID:
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("📊 Bot Status", callback_data="status"),
            types.InlineKeyboardButton("📢 Broadcast (စာလှမ်းပို့ရန်)", callback_data="bc"),
            types.InlineKeyboardButton("👥 User Count", callback_data="u_count")
        )
        bot.send_message(m.chat.id, "👨‍💻 **Admin Control Panel**", parse_mode="Markdown", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "status":
        bot.answer_callback_query(call.id, "System Online & Awake 🟢")
    elif call.data == "u_count":
        bot.answer_callback_query(call.id, f"Current Users: {len(user_list)}", show_alert=True)
    elif call.data == "bc":
        msg = bot.send_message(call.message.chat.id, "📢 **Broadcast လုပ်မည့်စာကို ပို့ပေးပါ။**")
        bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(m):
    count = 0
    for user in list(user_list):
        try:
            bot.send_message(user, f"📢 **MESSAGE FROM ADMIN**\n\n{m.text}", parse_mode="Markdown")
            count += 1
        except: pass
    bot.send_message(m.chat.id, f"✅ User {count} ယောက်ထံ စာပို့ပြီးပါပြီ!")

@bot.message_handler(commands=['start'])
def start(m):
    user_list.add(m.chat.id)
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🎮 6Lottery Acc ဖောက်ရန်", url=LINKS["6L"]),
        types.InlineKeyboardButton("🎰 CK Lottery Acc ဖောက်ဆော့ရန်", url=LINKS["CK"]),
        types.InlineKeyboardButton("🔥 777 BigWin Acc ဖောက်ရန်", url=LINKS["777"]),
        types.InlineKeyboardButton("📝 Acc ဖောက်နည်း ကြည့်ရန်", url=LINRLS["REGISTER_GUIDE"]),
        types.InlineKeyboardButton("💰 ငွေဖြည့်နည်း ကြည့်ရန်", url=LINKS["TOPUP"]),
        types.InlineKeyboardButton("💳 Acc ချိတ်/ငွေထုတ်နည်း", url=LINKS["BIND"]),
        types.InlineKeyboardButton("👨‍💻 Contact Admin (Or) Agent", url=f"https://t.me/{ADMIN_USERNAME[1:]}")
    )
    bot.send_message(m.chat.id, "🌟 **WinGo Prediction Bot** 🌟\n\n🎯 **Signal ရယူရန်:**\nရလဒ်ဇယား၏ **အောက်ဆုံးမှ အပေါ်ဆုံးသို့** ၅ ပွဲစာ ရိုက်ပို့ပါ။\nဥပမာ - `B S B B S`", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(func=lambda message: True)
def handle_msg(m):
    user_list.add(m.chat.id)
    words = m.text.upper().replace(',', ' ').split()
    history = [w for w in words if w in ['B', 'BIG', 'S', 'SMALL']]
    
    if len(history) >= 2:
        pred, logic_name = get_advanced_prediction(history)
        emoji = "🔴" if pred == "BIG" else "🟢"
        res = (f"🎯 **WIN GO SIGNAL**\n"
               f"━━━━━━━━━━━━━━\n"
               f"🎰 Next Bet: **{pred}** {emoji}\n"
               f"🧠 Logic: **{logic_name}**\n"
               f"💸 Strategy: 3x Martingale\n\n"
               f"⚠️ **ရှုံးလျှင် 3 ဆတိုးလောင်းပါ** 🚀\n"
               f"━━━━━━━━━━━━━━")
        bot.reply_to(m, res, parse_mode="Markdown")
    elif history:
        bot.reply_to(m, "❌ Formula မှန်ရန် အနည်းဆုံး ၂ ပွဲ သို့မဟုတ် ၅ ပွဲစာ ရိုက်ပို့ပေးပါ။")

# --- [ 5. RENDER SERVER ] ---
@app.route('/')
def home(): return "BOT IS LIVE & AWAKE 🟢"

if __name__ == "__main__":
    Thread(target=keep_alive).start()
    port = int(os.environ.get("PORT", 10000))
    Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
    bot.infinity_polling()
