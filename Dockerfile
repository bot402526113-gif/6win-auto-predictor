FROM python:3.10-slim

# Tesseract နဲ့ လိုအပ်တာတွေ သွင်းမယ်
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Library များ သွင်းမယ်
RUN pip install --no-cache-dir -r requirements.txt

# Render အတွက် Port ဖွင့်မယ်
EXPOSE 8080

# Error ကင်းအောင် ပြင်ထားတဲ့ Start Command
CMD gunicorn -b 0.0.0.0:8080 bot:app & python bot.py
