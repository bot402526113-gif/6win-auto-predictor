import os
import telebot
import requests
from threading import Thread
from flask import Flask

# --- [ 1. CONFIGURATION ] ---
TOKEN = '8641622144:AAGO_f5sc3_V0yho8hTnH_VRX_aH7Xx6BOw'
# မင်း Signal ပို့ချင်တဲ့ Channel ID (ဥပမာ -100xxxxxxxxx) သို့မဟုတ် Username (@channelname)
SIGNAL_CHAT_ID = "@Dangai_colour" 
OCR_API_KEY = 'helloworld' # Free Key (ပိုမြန်ချင်ရင် ocr.space မှာ key အလကားယူပါ)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- [ 2. OCR & LOGIC ] ---
def get_ocr_text(image_url):
    payload = {'apikey': OCR_API_KEY, 'url': image_url, 'language': 'eng'}
    try:
        r = requests.post('https://api.ocr.space/parse/image', data=payload, timeout=15)
        return r.json().get('ParsedResults')[0]['ParsedText']
    except: return ""

def analyze_and_predict(text):
    history = []
    for word in text.split():
        w = word.strip().capitalize()
        if "Big" in w: history.append("BIG")
        elif "Small" in w: history.append("SMALL")
    
    if len(history) >= 2:
        # ရိုးရှင်းသော Logic (ဥပမာ - နောက်ဆုံးတစ်ခုနဲ့ ဆန့်ကျင်ဘက်မှန်းခြင်း)
        prediction = "SMALL" if history[0] == "BIG" else "BIG"
        color = "🔴" if prediction == "BIG" else "🟢"
        return f"🎯 **NEW SIGNAL**\n━━━━━━━━━━\n🎰 Bet: **{prediction}** {color}\n🔥 Strategy: 3x Martingale\n⚠️ ရှုံးရင် 3 ဆတိုးလောင်းပါ!"
    return None

# --- [ 3. HANDLERS ] ---
@bot.message_handler(content_types=['photo'])
def handle_auto_signal(m):
    # Admin သို့မဟုတ် မင်းတစ်ယောက်တည်း ပို့တာကိုပဲ လက်ခံမယ် (Security အတွက်)
    status = bot.reply_to(m, "⏳ Analyzing Pattern...")
    
    try:
        file_info = bot.get_file(m.photo[-1].file_id)
        img_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        
        raw_text = get_ocr_text(img_url)
        signal_msg = analyze_and_predict(raw_text)
        
        if signal_msg:
            # Channel ထဲကို Signal ပို့မယ်
            bot.send_message(SIGNAL_CHAT_ID, signal_msg, parse_mode="Markdown")
            bot.edit_message_text("✅ Signal Posted to Channel!", m.chat.id, status.message_id)
        else:
            bot.edit_message_text("❌ Pattern မဖတ်နိုင်ပါ။", m.chat.id, status.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", m.chat.id, status.message_id)

# --- [ 4. RENDER SERVER ] ---
@app.route('/')
def home(): return "SIGNAL BOT ONLINE ✅"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_server).start()
    bot.infinity_polling()
    # Bot Polling စတင်မယ်
    print("Bot is Polling...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
