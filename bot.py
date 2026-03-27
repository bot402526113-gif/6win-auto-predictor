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
app = Flask('')

@app.route('/')
def home():
    return "WinGo Free Bot is Online! ✅"

def run_server():
    app.run(host='0.0.0.0', port=8080)

# --- [ 2. CONFIGURATION ] ---
TOKEN = '8641622144:AAGO_f5sc3_V0yho8hTnH_VRX_aH7Xx6BOw'
SUPABASE_URL = "https://guthvltysxlibetrbisi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1dGh2bHR5c3hsaWJldHJiaXNpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1MDg2OTYsImV4cCI6MjA5MDA4NDY5Nn0.7H57Gv7xnB4HkVoV6lZPxZsA9ATp1KfBQF1tulvXIRU"

ADMIN_ID = 6513777887
ADMIN_ACC = "@Dangi_Kan"
INVITE_LINK = "https://www.6win888.com/#/register?invitationCode=856411134469"
CHANNEL_LINK = "https://t.me/Dangai_colour"

bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- [ 3. DATABASE & FORMULA LOGIC ] ---
def manage_cloud_data(raw_text):
    try:
        data = {"pattern": raw_text, "created_at": datetime.now().isoformat()}
        supabase.table("pattern_history").insert(data).execute()
        # တစ်ပတ်ကျော်တာတွေကို ရှင်းထုတ်မယ်
        one_week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        supabase.table("pattern_history").delete().lt("created_at", one_week_ago).execute()
    except: pass

def get_prediction(history):
    if len(history) < 3: return None, None
    # Formula 1: Dragon
    if history[0] == history[1] == history[2]:
        return history[0].upper(), "Dragon Trend"
    # Formula 2: ZigZag
    if history[0] != history[1] and history[1] != history[2]:
        pred = "SMALL" if history[0] == "Big" else "BIG"
        return pred, "ZigZag Strategy"
    # Formula 3: Double-Double
    if len(history) >= 4:
        if history[0] == history[1] and history[2] == history[3] and history[0] != history[2]:
            return history[0].upper(), "Double-Double"
    return None, None 

# --- [ 4. BOT HANDLERS ] ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Register Now (Account ဖွင့်ရန်)", url=INVITE_LINK))
    markup.add(types.InlineKeyboardButton("📢 Join Channel (Link)", url=CHANNEL_LINK))
    
    welcome_text = (
        "🤖 **WinGo Free Bot မှ ကြိုဆိုပါတယ်**\n"
        "----------------------------------\n"
        "📸 **အသုံးပြုနည်း:**\n"
        "6Win Game ထဲက WinGo (1min) ရဲ့ **Result History** ဇယားကို Screenshot ရိုက်ပြီး ပို့ပေးပါ။ AI က Pattern ကို ဖတ်ပြီး နောက်တစ်ပွဲကို ခန့်မှန်းပေးပါလိမ့်မယ်။\n\n"
        "💰 **ဆတိုးထိုးနည်း (Money Management):**\n"
        "ရှုံးရင် အောက်ပါအတိုင်း 3 ဆ တိုးထိုးပါ -\n"
        "👉 **100 > 300 > 900 > 2700 > 8100**\n\n"
        f"👨‍💻 **Admin:** {ADMIN_ACC}\n"
        "----------------------------------"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def handle_prediction(message):
    status_msg = bot.reply_to(message, "🔍 AI စနစ်က Pattern ကို ဖတ်နေပါတယ်၊ ခဏစောင့်ပါ...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        response = requests.get(f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}")
        img = Image.open(BytesIO(response.content))
        raw_text = pytesseract.image_to_string(img)
        manage_cloud_data(raw_text)
        
        history = []
        for word in raw_text.split():
            w = word.strip().capitalize()
            if "Big" in w: history.append("Big")
            elif "Small" in w: history.append("Small")
            
        prediction, logic = get_prediction(history)
        
        if prediction:
            res = (f"🎯 **WinGo Next Prediction** 🎯\n"
                   f"------------------------------\n"
                   f"🔥 **Next Bet:** 【 **{prediction}** 】\n"
                   f"🧠 **Logic:** {logic}\n"
                   f"💹 **Strategy:** 3x Martingale\n"
                   f"------------------------------\n"
                   f"🔗 [Register Now]({INVITE_LINK})")
        else:
            res = "⚠️ **Risk များနေတယ်၊ တစ်ပွဲ Out ပါ**\n\nဒီ Pattern က ခန့်မှန်းရခက်နေလို့ အခုတစ်ပွဲကို ကျော်လိုက်ပါ။ ပုံအသစ်ပြန်ပို့ပေးပါ။"
        
        bot.edit_message_text(res, message.chat.id, status_msg.message_id, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        if "tesseract" in str(e).lower():
            bot.edit_message_text("❌ Error: စက်ထဲမှာ ပုံဖတ်စနစ် (Tesseract) ထည့်မထားရသေးပါ။ Render Environment မှာ APT_PACKAGES ထည့်ပေးပါ။", message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ Error: {e}", message.chat.id, status_msg.message_id)

# --- [ 5. EXECUTION ] ---
if __name__ == "__main__":
    t = Thread(target=run_server)
    t.start()
    bot.polling(none_stop=True)
