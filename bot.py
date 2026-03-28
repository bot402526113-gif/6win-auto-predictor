import os
import telebot
import requests
from PIL import Image
import pytesseract
from io import BytesIO
from threading import Thread
from flask import Flask
from telebot import types

# --- [ 1. RENDER အတွက် SERVER ဆောက်မယ် ] ---
app = Flask(__name__)

@app.route('/')
def home():
    return "WIN GO MASTER BOT IS LIVE! 🟢"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- [ 2. CONFIGURATION ] ---
TOKEN = '8641622144:AAGO_f5sc3_V0yho8hTnH_VRX_aH7Xx6BOw'
bot = telebot.TeleBot(TOKEN)

# Links & Info
REG_LINK = "https://6lottery.com/#/register?invitationCode=856411134469"
ACC_OPEN_POST = "https://t.me/Dangai_colour/7"
TOPUP_POST = "https://t.me/Dangai_colour/10"
BIND_ACC_POST = "https://t.me/Dangai_colour/8"
ADMIN_ACC = "@Dangi_Kan"

# --- [ 3. FORMULA LOGIC ] ---
def get_prediction(history):
    if len(history) < 3: return None, None
    
    # Formula 1: Dragon Trend (🔴/🟢 ဆက်တိုက်)
    if history[0] == history[1] == history[2]:
        return history[0].upper(), "Dragon Trend 🔥"
    
    # Formula 2: ZigZag (အလှည့်ကျ)
    if history[0] != history[1] and history[1] != history[2]:
        pred = "SMALL" if history[0] == "Big" else "BIG"
        return pred, "ZigZag Strategy ⚡"
        
    return None, None

# --- [ 4. BOT HANDLERS ] ---

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🎮 Game ဆော့ရန်", url=REG_LINK),
        types.InlineKeyboardButton("📝 Acc ဖွင့်နည်း", url=ACC_OPEN_POST),
        types.InlineKeyboardButton("💰 ငွေဖြည့်နည်း", url=TOPUP_POST),
        types.InlineKeyboardButton("💳 Acc ချိတ်နည်း", url=BIND_ACC_POST),
        types.InlineKeyboardButton("👨‍💻 Admin Account", url=f"https://t.me/Dangi_Kan")
    )
    
    welcome = (
        "👋 **WinGo Prediction Bot မှ ကြိုဆိုပါတယ်!**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "အောက်က ခလုတ်များကို အသုံးပြု၍ လိုအပ်သည်များကို ကြည့်ရှုနိုင်ပါသည်။\n\n"
        "📸 **မှန်းပေးစေချင်ရင်:**\n"
        "WinGo Result History ကို Screenshot ရိုက်ပြီး ပို့ပေးပါခင်ဗျာ။ ✨"
    )
    bot.send_message(m.chat.id, welcome, parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(content_types=['photo'])
def handle_prediction(m):
    status_msg = bot.reply_to(m, "🔍 **AI က Pattern ကို ဖတ်နေပါတယ်...**")
    try:
        file_info = bot.get_file(m.photo[-1].file_id)
        response = requests.get(f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}")
        img = Image.open(BytesIO(response.content))
        raw_text = pytesseract.image_to_string(img)
        
        history = []
        for word in raw_text.split():
            w = word.strip().capitalize()
            if "Big" in w: history.append("Big")
            elif "Small" in w: history.append("Small")
            
        prediction, logic = get_prediction(history)
        
        if prediction:
            color_emoji = "🟢 (Green)" if prediction == "SMALL" else "🔴 (Red)"
            res = (
                f"🎯 **Next Prediction Result**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🎰 **Next Bet:** `{prediction}` {color_emoji}\n"
                f"🧠 **Logic:** {logic}\n"
                f"💸 **Strategy:** 3x Martingale\n\n"
                f"⚠️ **ရှုံးသွားလျှင် 3 ဆတိုးလောင်းပေးပါ** 🚀🚀🚀"
            )
        else:
            res = "⚠️ **Pattern မသေချာသေးပါ။ တစ်ပွဲကျော်လိုက်ပါဦး။**"
            
        bot.edit_message_text(res, m.chat.id, status_msg.message_id, parse_mode="Markdown")
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", m.chat.id, status_msg.message_id)

# --- [ 5. RUN BOT ] ---
if __name__ == "__main__":
    # Flask ကို နောက်ကွယ်မှာ run မယ်
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Bot Polling စတင်မယ်
    print("Bot is Polling...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
