import os
import telebot
from threading import Thread
from flask import Flask
from telebot import types

# --- [ 1. CONFIGURATION ] ---
TOKEN = '8641622144:AAGO_f5sc3_V0yho8hTnH_VRX_aH7Xx6BOw'
ADMIN_ID = 6513777887 
ADMIN_USERNAME = "@Dangi_Kan"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Links Configuration
LINKS = {
    "6L": "https://www.6win999.com/#/register?invitationCode=856411134469",
    "CK": "http://www.cklottery.tv/#/register?invitationCode=15473304912",
    "777": "https://www.777bigwingame.club/#/register?invitationCode=67132596471",
    "TOPUP": "https://t.me/Dangai_colour/10",
    "BIND": "https://t.me/Dangai_colour/8",
    "REGISTER_GUIDE": "https://t.me/Dangai_colour/7"
}

# --- [ 2. LOGIC ] ---
def get_prediction(history):
    if not history: return None
    last = history[0]
    pred = "SMALL" if last == "BIG" else "BIG"
    emoji = "🔴" if pred == "BIG" else "🟢"
    return pred, emoji

# --- [ 3. HANDLERS ] ---

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.InlineKeyboardMarkup(row_width=1)
    
    # Game Links Section
    kb.add(
        types.InlineKeyboardButton("🎮 6Lottery Acc ဖောက်ရန်", url=LINKS["6L"]),
        types.InlineKeyboardButton("🎰 CK Lottery Acc ဖောက်ဆော့ရန်", url=LINKS["CK"]),
        types.InlineKeyboardButton("🔥 777 BigWin Acc ဖောက်ရန်", url=LINKS["777"])
    )
    
    # Guide Section
    kb.add(
        types.InlineKeyboardButton("📝 Acc ဖောက်နည်း ကြည့်ရန်", url=LINKS["REGISTER_GUIDE"]),
        types.InlineKeyboardButton("💰 ငွေဖြည့်နည်း ကြည့်ရန်", url=LINKS["TOPUP"]),
        types.InlineKeyboardButton("💳 Acc ချိတ်/ငွေထုတ်နည်း", url=LINKS["BIND"])
    )
    
    # Support Section
    kb.add(
        types.InlineKeyboardButton("👨‍💻 Contact Admin (Or) Agent", url=f"https://t.me/{ADMIN_USERNAME[1:]}")
    )
    
    welcome = (
        "🌟 **WinGo Prediction & Support Bot** 🌟\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "မင်္ဂလာပါဗျာ! WinGo ဂိမ်းများအတွက် တိကျတဲ့ Signal တွေနဲ့ "
        "အကူအညီတွေကို ဒီမှာ ရယူနိုင်ပါတယ်။\n\n"
        "💡 **သိထားရန်:**\n"
        "• အကောင့်ဖွင့်ခြင်း၊ ငွေဖြည့်/ထုတ်ခြင်း နည်းလမ်းမသိရင် အောက်က Button တွေကို နှိပ်ကြည့်ပါ။\n"
        "• Agent လုပ်ကိုင်လိုသူများလည်း Admin ဆီ တိုက်ရိုက်ဆက်သွယ်နိုင်ပါတယ်။\n\n"
        "🎯 **Signal ရယူရန်:**\n"
        "ရလဒ်ဇယား၏ **အောက်ဆုံးမှ အပေါ်ဆုံးသို့** ၅ ပွဲစာ ရိုက်ပို့ပါ။\n"
        "ဥပမာ - `B S B B S`\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    bot.send_message(m.chat.id, welcome, parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(func=lambda message: True)
def handle_msg(m):
    # Prediction Logic
    words = m.text.upper().replace(',', ' ').split()
    history = []
    for w in words:
        if w in ['B', 'BIG']: history.append("BIG")
        elif w in ['S', 'SMALL']: history.append("SMALL")
    
    if history:
        pred, emoji = get_prediction(history)
        res = (
            f"🎯 **WIN GO SIGNAL**\n"
            f"━━━━━━━━━━━━━━\n"
            f"🎰 Next Bet: **{pred}** {emoji}\n"
            f"💸 Strategy: 3x Martingale\n\n"
            f"⚠️ **ရှုံးလျှင် 3 ဆတိုးလောင်းပါ** 🚀\n"
            f"━━━━━━━━━━━━━━"
        )
        bot.reply_to(m, res, parse_mode="Markdown")
    else:
        # Admin Message handling (Simple fallback)
        if m.from_user.id == ADMIN_ID:
            bot.reply_to(m, "👨‍💻 Admin Mode Active. Signal မှန်းရန် B သို့မဟုတ် S ရိုက်ပါ။")
        else:
            bot.reply_to(m, "❌ Pattern နားမလည်ပါ။ 'B S B' ဟု ရိုက်ပေးပါ။")

# --- [ 4. RENDER SERVER ] ---
@app.route('/')
def home(): return "CHARITY BOT LIVE 🟢"

if __name__ == "__main__":
    # Render Port Handling
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))).start()
    bot.infinity_polling()
