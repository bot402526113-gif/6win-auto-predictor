import os
import time
import telebot
import random
from supabase import create_client, Client

# Render ရဲ့ Env Settings ကနေ ဆွဲဖတ်မယ်
TOKEN = os.getenv('BOT_TOKEN')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')

bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- ၃ ဆ တိုး Strategy Logic ---
def get_prediction_and_multiplier():
    # Supabase ကနေ နောက်ဆုံးအခြေအနေကို ဖတ်မယ်
    res = supabase.table("bot_state").select("*").eq("id", 1).execute()
    data = res.data[0]
    level = data['current_level']
    
    multiplier = 3 ** (level - 1)
    prediction = random.choice(["BIG 🟢", "SMALL 🔴"])
    
    return prediction, multiplier, level

def send_tip():
    pred, mult, level = get_prediction_and_multiplier()
    
    # ပွဲစဉ်အမှတ်စဉ်ကို အချိန်ပေါ်မူတည်ပြီး ခန့်မှန်းတွက်ချက်ခြင်း (Example format)
    period = time.strftime("%Y%m%d") + "000" # ဒါကို Web ကနေ ဖတ်ဖို့ ပြင်ရဦးမယ်
    
    msg = (
        f"🔔 **WIN GO 1-MIN VIP TIP**\n"
        f"------------------------------\n"
        f"📅 **Period:** `{period}`\n"
        f"🎯 **Prediction:** 【 **{pred}** 】\n"
        f"💰 **Amount:** **{mult}x**\n"
        f"📈 **Level:** {level}\n"
        f"------------------------------\n"
        f"💬 Admin: @Dangi_Kan"
    )
    
    bot.send_message(CHANNEL_ID, msg, parse_mode="Markdown")

if __name__ == "__main__":
    print("Bot is starting...")
    while True:
        send_tip()
        time.sleep(60) # ၁ မိနစ်တစ်ခါ ပို့မယ်
