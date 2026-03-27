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
    return "Legendary Tomato Bot is Online! ✅"

def run_server():
    app.run(host='0.0.0.0', port=8080)

# --- [ 2. CONFIGURATION ] ---
TOKEN = '8641622144:AAGO_f5sc3_V0yho8hTnH_VRX_aH7Xx6BOw'
SUPABASE_URL = "https://guthvltysxlibetrbisi.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_KEY_HERE" # မင်းရဲ့ Key အပြည့်အစုံ ပြန်ထည့်ပါ
ADMIN_ID = 6513777887
INVITE_LINK = "https://www.6win333.com/#/register?invitationCode=856411134469"
CHANNEL_LINK = "https://t.me/Dangai_colour"

bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Global Variables
is_maintenance = False

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

# --- [ 4. ADMIN POWER SERVICES ] ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📊 Total Patterns", "🛠 Toggle Maintenance")
        markup.add("📢 Broadcast", "🔙 Exit Admin")
        bot.send_message(message.chat.id, "👨‍💻 Welcome Master! Admin Panel ဖွင့်ပါပြီ။", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ မင်းမှာ Admin Power မရှိပါဘူး။")

@bot.message_handler(func=lambda m: m.text == "🛠 Toggle Maintenance")
def toggle_maint(message):
    if message.from_user.id == ADMIN_ID:
        global is_maintenance
        is_maintenance = not is_maintenance
        status = "On 🔴" if is_maintenance else "Off 🟢"
        bot.send_message(message.chat.id, f"Maintenance Mode is now {status}")

# --- [ 5. BOT HANDLERS ] ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Register Now", url=INVITE_LINK))
    markup.add(types.InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK))
    
    welcome_text = (
        "🎰 **Legendary Tomato VIP Predictor**\n\n"
        "📸 **အသုံးပြုနည်း:**\n"
        "Result History ဇယားကို Screenshot ရိုက်ပို့ပေးပါ။\n\n"
        "💰 **Strategy:** 3x Martingale (100 > 300 > 900)"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def handle_prediction(message):
    if is_maintenance and message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "🛠 Bot ကို ပြင်ဆင်နေလို့ ခဏနားထားပါတယ်။ ခဏနေမှ ပြန်ပို့ပေးပါ။")

    status_msg = bot.reply_to(message, "🔍 AI စနစ်က Pattern ကို ဖတ်နေပါတယ်...")
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
            res = (f"🎯 **NEXT BET:** 【 **{prediction}** 】\n"
                   f"🧠 **Logic:** {logic}\n"
                   f"💰 **Strategy:** 3x Martingale\n\n"
                   f"🔗 [Register Now]({INVITE_LINK})")
        else:
            res = "⚠️ **Risk များနေတယ်၊ တစ်ပွဲ Out ပါ**"
        
        bot.edit_message_text(res, message.chat.id, status_msg.message_id, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {e}", message.chat.id, status_msg.message_id)

# --- [ 6. EXECUTION ] ---
if __name__ == "__main__":
    t = Thread(target=run_server)
    t.start()
    print("Bot & Keep-Alive Server Started... ✅")
    bot.polling(none_stop=True)
