import os, telebot, requests, time, asyncio, logging
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
user_list = set() # ရှေ့မှာ Supabase သုံးထားရင် အဲ့ဒါနဲ့ ပြန်ချိတ်လို့ရတယ်
logging.basicConfig(level=logging.INFO)

LINKS = {
    "6L": "https://www.6win999.com/#/register?invitationCode=856411134469",
    "CK": "http://www.cklottery.tv/#/register?invitationCode=15473304912",
    "777": "https://www.777bigwingame.club/#/register?invitationCode=67132596471",
    "TOPUP": "https://t.me/Dangai_colour/10",
    "BIND": "https://t.me/Dangai_colour/8",
    "REGISTER_GUIDE": "https://t.me/Dangai_colour/7"
}

# --- [ 2. SELF-PING ENGINE (Render မအိပ်အောင် တားဆီးခြင်း) ] ---
def self_ping():
    time.sleep(30)
    while True:
        try:
            # ကိုယ့် URL ကိုယ်ပြန်ခေါ်ပြီး Traffic ရှိနေအောင်လုပ်မယ်
            requests.get(APP_URL, timeout=20)
            logging.info("💤 Self-Ping: Keeping the bot immortal!")
        except: pass
        time.sleep(300) # ၅ မိနစ်တစ်ခါ

# --- [ 3. VIP FORMULA LOGIC ] ---
def get_advanced_prediction(history, last_number=None):
    if len(history) < 2: return None, None
    
    # VIP 1: Number 9 Rule (သားကြီးပေးတဲ့ Formula)
    if last_number == 9:
        return "BIG", "VIP 9-Rule: High Chance BIG 🔥"

    # VIP 2: Trend Following (၃ ခါတူရင် လိုက်မယ်)
    if len(history) >= 3 and all(x == history[0] for x in history[:3]):
        return history[0], "Trend Following Strategy 🚀"

    # VIP 3: ZigZag Logic (B S B S သို့မဟုတ် S B S B)
    if len(history) >= 4:
        pattern = "".join([h[0] for h in history[:4]])
        if pattern == "BSBS": return "BIG", "ZigZag VIP: Bet BIG ✅"
        if pattern == "SBSB": return "SMALL", "ZigZag VIP: Bet SMALL ✅"

    # VIP 4: Double-Double Pattern (BB SS သို့မဟုတ် SS BB)
    if len(history) >= 4:
        if history[0] == history[1] and history[2] == history[3] and history[0] != history[2]:
            pred = "BIG" if history[0] == "SMALL" else "SMALL"
            return pred, "2-2 Pattern VIP 🔄"

    # VIP 5: Sandwich Pattern (B S B သို့မဟုတ် S B S)
    if len(history) >= 3:
        if history[1] != history[0] and history[1] != history[2] and history[0] == history[2]:
            return history[0], "Sandwich Pattern VIP 🥪"

    # DEFAULT: MIRROR STRATEGY
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
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🎮 6Lottery", url=LINKS["6L"]),
        types.InlineKeyboardButton("🎰 CK Lottery", url=LINKS["CK"]),
        types.InlineKeyboardButton("🔥 777 BigWin", url=LINKS["777"]),
        types.InlineKeyboardButton("📝 Acc ဖောက်နည်း", url=LINKS["REGISTER_GUIDE"]),
        types.InlineKeyboardButton("💰 ငွေဖြည့်နည်း", url=LINKS["TOPUP"]),
        types.InlineKeyboardButton("💳 ငွေထုတ်နည်း", url=LINKS["BIND"]),
        types.InlineKeyboardButton("👨‍💻 Admin", url=f"https://t.me/{ADMIN_USERNAME[1:]}")
    )
    welcome = (
        "🌟 **WinGo VIP Prediction Bot** 🌟\n\n"
        "🎯 **Signal ရယူရန်:** ၅ ပွဲစာ ရိုက်ပို့ပါ။\n"
        "ဥပမာ - `B S B B S` သို့မဟုတ် `9` (နောက်ဆုံးဂဏန်း ၉ ဆိုလျှင်)\n\n"
        "💡 **💡 Tip:** ဂဏန်း ၉ ထွက်ပြီးတိုင်း **BIG** လာနိုင်ခြေ ၉၀% ရှိပါသည်။"
    )
    bot.send_message(m.chat.id, welcome, parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(func=lambda message: True)
def handle_msg(m):
    user_list.add(m.chat.id)
    text = m.text.upper().replace(',', ' ')
    words = text.split()
    
    # ဂဏန်း ၉ ပါ၊ မပါ စစ်မယ်
    last_num = None
    if "9" in words: last_num = 9
    
    history = [w for w in words if w in ['B', 'BIG', 'S', 'SMALL']]
    
    # VIP Formula နဲ့ တွက်ချက်မယ်
    if len(history) >= 2 or last_num == 9:
        pred, logic_name = get_advanced_prediction(history, last_num)
        emoji = "🔴" if pred == "BIG" else "🟢"
        res = (f"🎯 **WIN GO VIP SIGNAL**\n\n"
               f"🎰 Next Bet: **{pred}** {emoji}\n"
               f"🧠 Logic: {logic_name}\n"
               f"💸 Strategy: 3x Martingale\n\n"
               f"⚠️ **ရှုံးလျှင် ၃ ဆတိုးလောင်းပါ** 🚀")
        bot.reply_to(m, res, parse_mode="Markdown")
    else:
        bot.reply_to(m, "❌ အနည်းဆုံး ၂ ပွဲစာ (B S) သို့မဟုတ် ဂဏန်း ၉ ကို ပို့ပေးပါ။")

# --- [ 5. WEB SERVER FOR RENDER ] ---
@app.route('/')
def home(): return "✅ SYSTEM ACTIVE", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- [ 6. MAIN RUNNER ] ---
if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    Thread(target=self_ping, daemon=True).start()
    print("🤖 WinGo VIP Bot is Awake...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
