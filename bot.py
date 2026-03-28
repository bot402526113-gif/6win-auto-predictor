import os
import telebot
import requests
from threading import Thread
from flask import Flask
from telebot import types

# --- [ 1. CONFIGURATION ] ---
TOKEN = '8641622144:AAGO_f5sc3_V0yho8hTnH_VRX_aH7Xx6BOw'
SIGNAL_CHAT_ID = "@Dangai_colour" # Signal ပို့မည့် Channel
OCR_API_KEY = 'helloworld' # Free Key (ပိုမြန်ချင်ရင် ocr.space မှာ ကိုယ်ပိုင်ယူပါ)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Links
REG_LINK = "https://6lottery.com/#/register?invitationCode=856411134469"
ACC_OPEN_POST = "https://t.me/Dangai_colour/7"
TOPUP_POST = "https://t.me/Dangai_colour/10"
BIND_ACC_POST = "https://t.me/Dangai_colour/8"
ADMIN_ACC = "@Dangi_Kan"

# --- [ 2. OCR API FUNCTION ] ---
def get_text_from_image(image_url):
    payload = {
        'apikey': OCR_API_KEY,
        'url': image_url,
        'language': 'eng',
        'isOverlayRequired': False,
        'detectOrientation': True
    }
    try:
        r = requests.post('https://api.ocr.space/parse/image', data=payload, timeout=25)
        result = r.json()
        if result.get('ParsedResults'):
            return result['ParsedResults'][0]['ParsedText']
    except Exception as e:
        print(f"OCR Error: {e}")
    return ""

# --- [ 3. PREDICTION LOGIC ] ---
def generate_prediction(text):
    history = []
    # စာသားထဲက Big/Small ကို အသေအချာရှာမယ်
    clean_text = text.replace('\n', ' ').replace('|', '').replace(',', ' ')
    words = clean_text.split()
    for word in words:
        w = word.strip().capitalize()
        if "Big" in w: history.append("BIG")
        elif "Small" in w: history.append("SMALL")
    
    if len(history) >= 2:
        # 3x Martingale Strategy
        prediction = "SMALL" if history[0] == "BIG" else "BIG"
        emoji = "🔴" if prediction == "BIG" else "🟢"
        
        return (f"🎯 **WIN GO SIGNAL**\n"
                f"━━━━━━━━━━━━━━\n"
                f"🎰 Bet: **{prediction}** {emoji}\n"
                f"📈 Strategy: 3x Martingale\n"
                f"⚠️ ရှုံးလျှင် 3 ဆတိုးလောင်းပါ!\n"
                f"━━━━━━━━━━━━━━")
    return None

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
    welcome = "👋 **WinGo Prediction Bot မှ ကြိုဆိုပါတယ်!**\n\nScreenshot ပို့ပေးပါခင်ဗျာ။ ✨"
    bot.send_message(m.chat.id, welcome, parse_mode="Markdown", reply_markup=kb)

@bot.message_handler(content_types=['photo'])
def handle_signal(m):
    status = bot.reply_to(m, "🔍 AI က Pattern ကို ဖတ်နေပါတယ်...")
    try:
        file_info = bot.get_file(m.photo[-1].file_id)
        img_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        
        raw_text = get_text_from_image(img_url)
        signal = generate_prediction(raw_text)
        
        if signal:
            # Channel ထဲကို Signal အလိုအလျောက် ပို့မယ်
            bot.send_message(SIGNAL_CHAT_ID, signal, parse_mode="Markdown")
            bot.edit_message_text("✅ Signal ကို Channel ထဲ တင်ပေးလိုက်ပါပြီ!", m.chat.id, status.message_id)
        else:
            bot.edit_message_text("❌ Pattern ရှာမတွေ့ပါ။ ပုံကို ကြည်လင်အောင် ပြန်ရိုက်ပေးပါ။", m.chat.id, status.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", m.chat.id, status.message_id)

# --- [ 5. RENDER SERVER ] ---
@app.route('/')
def home(): return "SYSTEM ONLINE 🟢"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_server).start()
    bot.infinity_polling(timeout=20)
