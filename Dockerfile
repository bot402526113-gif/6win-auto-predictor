# Python image ကို အခြေခံမယ်
FROM python:3.10-slim

# System အတွက် လိုအပ်တဲ့ Tesseract နဲ့ အခြား package တွေ သွင်းမယ်
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean

# Bot ဖိုင်တွေ ထည့်မယ်
WORKDIR /app
COPY . /app

# Library တွေ သွင်းမယ်
RUN pip install --no-cache-dir -r requirements.txt

# Port 8080 ကို ဖွင့်ပေးမယ်
EXPOSE 8080

# Bot ကို စမောင်းမယ်
CMD gunicorn -b 0.0.0.0:8080 bot:app & python bot.py
