import os, telebot, requests, time, logging
from threading import Thread
from flask import Flask
from telebot import types

# --- [ 1. CONFIGURATION ] ---
TOKEN = '8641622144:AAGO_f5sc3_V0yho8hTnH_VRX_aH7Xx6BOw'
ADMIN_ID = 6513777887 
APP_URL = "https://sixwin-auto.onrender.com" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_list = set()
logging.basicConfig(level=logging.INFO)

# --- [ 2. SELF-PING (Render မအိပ်အောင် နှိုးစနစ်) ] ---
def self_ping():
    """Render က Free Plan ဆိုရင် ခဏနေရင် အိပ်ပျော်သွားတတ်လို့ ၅ မိနစ်တစ်ခါ လှမ်းနှိုးတဲ့စနစ်"""
    time.sleep(30) # Server အရင်တက်အောင် စောင့်မယ်
    while True:
        try:
            # သားကြီးရဲ့ URL ကို Traffic ပေးပြီး နိုးနေအောင်လုပ်တာ
            requests.get(APP_URL, timeout=20)
            logging.info("💤 Self-Ping: Keeping the bot immortal!")
        except: pass
        time.sleep(300) # ၅ မိနစ် (၃၀၀ စက္ကန့်) တစ်ခါ နှိုးမယ်

# --- [ 3. VIP FORMULA LOGIC ] ---
def get_prediction(history, last_number=None):
    if last_number == 9: 
        return "BIG", "VIP 9-Rule: High Chance BIG 🔥"
    if len(history) < 2: return None, None
    if len(history) >= 3 and all(x == history[0] for x in history[:3]):
        return history[0], "Trend Following 🚀"
    if len(history) >= 4:
        pat = "".join([h[0] for h in history[:4]])
        if pat == "BSBS": return "BIG", "ZigZag VIP ✅"
        if pat == "SBSB": return "SMALL", "ZigZag VIP ✅"
    pred = "BIG" if history[0] == "SMALL" else "SMALL"
    return pred, "Mirror Strategy 🔮"

# --- [ 4. HANDLERS ] ---
@bot.message_handler(commands=['admin'])
def admin_panel(m):
    if m.from_user.id == ADMIN_ID:
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("📊 Bot Status", callback_data="status"),
            types.InlineKeyboardButton("📢 Broadcast (ပို့စာ)", callback_data="bc"),
            types.InlineKeyboardButton("👥 User Count", callback_data="u_count")
        )
        bot.send_message(m.chat.id, "👨‍💻 **Admin Control Panel**", parse_mode="Markdown", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "status": bot.answer_callback_query(call.id, "Bot is Live! 🟢")
    elif call.data == "u_count": bot.answer_callback_query(call.id, f"Users: {len(user_list)}", show_alert=True)
    elif call.data == "bc":
        msg = bot.send_message(call.message.chat.id, "📢 **အားလုံးကို ပို့ချင်တဲ့စာ ရိုက်ပေးပါ။**")
        bot.register_next_step_handler(msg, process_broadcast)
    bot.answer_callback_query(call.id)

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
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("👨‍💻 Admin", url="https://t.me/Dangi_Kan"))
    bot.send_message(m.chat.id, "🌟 **WinGo VIP Bot** 🌟\n\n🎯 ၅ ပွဲစာ (B S) သို့မဟုတ် `9` ကို ပို့ပေးပါ။", parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    user_list.add(m.chat.id)
    text = m.text.upper()
    words = text.replace(',', ' ').split()
    last_num = 9 if "9" in words else None
    history = [w for w in words if w in ['B', 'BIG', 'S', 'SMALL']]
    
    if len(history) >= 2 or last_num == 9:
        pred, logic = get_prediction(history, last_num)
        emoji = "🔴" if pred == "BIG" else "🟢"
        res = (f"🎯 **WIN GO VIP SIGNAL**\n\n🎰 Next Bet: **{pred}** {emoji}\n🧠 Logic: {logic}\n💸 Strategy: 3x Martingale\n\n⚠️ **ရှုံးလျှင် ၃ ဆတိုးလောင်းပါ** 🚀")
        bot.reply_to(m, res, parse_mode="Markdown")

# --- [ 5. WEB SERVER FOR RENDER ] ---
@app.route('/')
def home(): return "✅ BOT IS AWAKE", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- [ 6. THE IMMORTAL RUNNER ] ---
if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    Thread(target=self_ping, daemon=True).start()
    
    print("🤖 Bot is Starting...")
    while True: # Bot ကို လုံးဝမရပ်သွားအောင် ပတ်ထားတဲ့ Loop
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            logging.error(f"❌ Error: {e}. Restarting in 5 seconds...")
            time.sleep(5) # Error တက်ရင် ၅ စက္ကန့်နေရင် ပြန်စမယ်

