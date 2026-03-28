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

# --- [ 2. SELF-PING (၂၄ နာရီ နှိုးစနစ်) ] ---
def self_ping():
    """Render မအိပ်အောင် ၅ မိနစ်တစ်ခါ ကိုယ့်ကိုယ်ကို လှမ်းနှိုးမည့်စနစ်"""
    time.sleep(25) # Server တက်လာအောင် ခဏစောင့်မယ်
    while True:
        try:
            # ကိုယ့် URL ကိုယ်ပြန်ခေါ်ပြီး Traffic ရှိနေအောင်လုပ်မယ်
            requests.get(APP_URL, timeout=15)
            logging.info("💤 Self-Ping: Bot is keeping itself awake!")
        except: pass
        time.sleep(300) # ၅ မိနစ်တစ်ခါ ပုံမှန်နှိုးမယ်

# --- [ 3. VIP FORMULA LOGIC ] ---
def get_prediction(history, last_number=None):
    # VIP 1: ၉ ဂဏန်းလာလျှင် အကြီးလာတတ်သည် (သားကြီးရဲ့ VIP Rule)
    if last_number == 9: 
        return "BIG", "VIP 9-Rule: High Chance BIG 🔥"
    
    if len(history) < 2: return None, None
    
    # VIP 2: Trend Following (၃ ခါတူလျှင်)
    if len(history) >= 3 and all(x == history[0] for x in history[:3]):
        return history[0], "Trend Following 🚀"
        
    # VIP 3: ZigZag (B S B S)
    if len(history) >= 4:
        pat = "".join([h[0] for h in history[:4]])
        if pat == "BSBS": return "BIG", "ZigZag VIP ✅"
        if pat == "SBSB": return "SMALL", "ZigZag VIP ✅"
        
    # Default: Mirror Strategy
    pred = "BIG" if history[0] == "SMALL" else "SMALL"
    return pred, "Mirror Strategy 🔮"

# --- [ 4. HANDLERS ] ---

# Admin Panel Handler
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
    welcome_text = (
        "🌟 **WinGo VIP Bot** 🌟\n\n"
        "🎯 **Signal ရယူရန်:** ၅ ပွဲစာ (B S) သို့မဟုတ် `9` ကို ပို့ပေးပါ။\n"
        "ဥပမာ - `B S B B S` (သို့) `9`"
    )
    bot.send_message(m.chat.id, welcome_text, parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    user_list.add(m.chat.id)
    text = m.text.upper()
    words = text.replace(',', ' ').split()
    
    # ဂဏန်း ၉ ပါ၊ မပါ စစ်မယ်
    last_num = 9 if "9" in words else None
    history = [w for w in words if w in ['B', 'BIG', 'S', 'SMALL']]
    
    if len(history) >= 2 or last_num == 9:
        pred, logic = get_prediction(history, last_num)
        emoji = "🔴" if pred == "BIG" else "🟢"
        res = (f"🎯 **WIN GO VIP SIGNAL**\n\n"
               f"🎰 Next Bet: **{pred}** {emoji}\n"
               f"🧠 Logic: {logic}\n"
               f"💸 Strategy: 3x Martingale\n\n"
               f"⚠️ **ရှုံးလျှင် ၃ ဆတိုးလောင်းပါ** 🚀")
        bot.reply_to(m, res, parse_mode="Markdown")
    else:
        bot.reply_to(m, "❌ အနည်းဆုံး ၂ ပွဲစာ (B S) သို့မဟုတ် ဂဏန်း ၉ ကို ပို့ပေးပါ။")

# --- [ 5. WEB SERVER FOR RENDER ] ---
@app.route('/')
def home(): 
    return "✅ BOT IS FULLY AWAKE AND OPERATIONAL", 200

def run_flask():
    # Render မှာ PORT 10000 ဖြည့်ထားဖို့ မမေ့နဲ့နော်
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- [ 6. MAIN RUNNER ] ---
if __name__ == "__main__":
    # Flask Web Server နဲ့ Self-Ping ကို Background Thread တွေနဲ့ run မယ်
    Thread(target=run_flask, daemon=True).start()
    Thread(target=self_ping, daemon=True).start()

    print("🤖 WinGo VIP Bot is starting...")
    # Infinity Polling နဲ့ Bot ကို အမြဲတမ်း run နေစေမယ်
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
def home(): return "✅ BOT IS AWAKE", 200

def run_flask():
    # Render Dashboard ထဲက Environment မှာ PORT 10000 ဖြည့်ထားဖို့လိုတယ်
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- [ 6. MAIN RUNNER ] ---
if __name__ == "__main__":
    # Flask Web Server ကို Background မှာ run မယ်
    Thread(target=run_flask, daemon=True).start()
    
    # Self-Ping Loop ကို Background မှာ run မယ်
    Thread(target=self_ping, daemon=True).start()

    print("🤖 WinGo VIP Bot is Starting...")
    bot.infinity_polling(timeout=60)
