# Python version 3.10 ကို အခြေခံအဖြစ် သုံးမယ်
FROM python:3.10-slim

# Render ရဲ့ စက်ထဲမှာ ပုံဖတ်ဖို့ (Tesseract OCR) ကို သွင်းမယ်
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Bot ဖိုင်တွေ ထည့်ဖို့ folder ဆောက်မယ်
WORKDIR /app
COPY . /app

# လိုအပ်တဲ့ Python library တွေ အကုန်သွင်းမယ်
RUN pip install --no-cache-dir -r requirements.txt

# Render အတွက် Port 8080 ကို ဖွင့်ပေးမယ်
EXPOSE 8080

# Bot ကို စမောင်းမယ် (bot.py ထဲက app ကို Flask အတွက် သုံးပြီး bot.py ကို run မယ်)
CMD gunicorn -b 0.0.0.0:8080 bot:app & python bot.py
