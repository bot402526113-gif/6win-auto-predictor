import os
import telebot
import requests
from PIL import Image
import pytesseract
from io import BytesIO
from datetime import datetime, timedelta
from supabase import create_client, Client
from threading import Thread
from flask import Flask
from telebot import types

# --- [ 1. KEEP-ALIVE SERVER FOR RENDER ] ---
app = Flask(__name__)

@app.route('/')
def home():
    return "WinGo Free Bot is Online! ✅"

def run_server():
    # Render port requirement အတွက် 10000 ကို သုံးတာ ပိုအဆင်ပြေတယ်
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- [ 2. CONFIGURATION ] ---
TOKEN = '8641622144:AAGO_f5sc3_V0yho8hTnH_VRX_aH7Xx6BOw'
SUPABASE_URL = "https://guthvltysxlibetrbisi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1dGh2bHR5c3hsaWJldHJiaXNpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1MDg2OTYsImV4cCI6MjA5MDA4NDY5Nn0.7H57Gv7xnB4HkVoV6lZPxZsA9ATp1KfBQF1tulvXIRU"

ADMIN_ACC = "@Dangi_Kan"
INVITE_LINK = "https://www.6win888.com/#/register?invitationCode=856411134469"
CHANNEL_LINK = "https://t.me/Dangai_colour"

bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- [ 3. DATABASE & FORMULA LOGIC ] ---
def get_prediction(history):
    if len(history) < 3: return None, None
    # Dragon Trend
    if history[0] == history[1] == history[2]:
        return history[0].upper(), "Dragon Trend"
    # ZigZag Strategy
    if history[0] != history[1] and history[1] != history[2]:
        pred = "SMALL" if history[0] == "Big" else "BIG"
        return pred, "ZigZag Strategy"
    return None, None 

# --- [ 4. BOT HANDLERS ] ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Register Now", url=INVITE_LINK))
    welcome_text = "🤖 **WinGo Free Bot မှ ကြိုဆိုပါတယ်**\n\nScreenshot ပို့ပေးပါ။"
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def handle_prediction(message):
    status_msg = bot.reply_to(message, "🔍 AI က ဖတ်နေတယ်...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        response = requests.get(f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}")
        img = Image.open(BytesIO(response.content))
        raw_text = pytesseract.image_to_string(img)
        
        history = []
        for word in raw_text.split():
            w = word.strip().capitalize()
            if "Big" in w: history.append("Big")
            elif "Small" in w: history.append("Small")
            
        prediction, logic = get_prediction(history)
        res = f"🎯 **Next Bet:** {prediction}" if prediction else "⚠️ ကျော်လိုက်ပါ"
        bot.edit_message_text(res, message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", message.chat.id, status_msg.message_id)

# --- [ 5. EXECUTION ] ---
if __name__ == "__main__":
    # Server ကို thread နဲ့ run မယ်
    t = Thread(target=run_server)
    t.start()
    # Bot ကို polling စတင်မယ်
    print("Bot is Polling...")
    bot.infinity_polling(none_stop=True)
