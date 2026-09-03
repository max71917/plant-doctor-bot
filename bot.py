import os
import logging
import base64
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# НАСТРОЙКИ
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8919020586:AAHZ2ji5aOI8Mg4dYFH1KF9ezBrZ_9bA-04")
API_KEY = os.getenv("API_KEY", "sk-dc9d4b7df36ba555-91cb65-77e01611")
BASE_URL = os.getenv("BASE_URL", "https://anymodel.org/v1")
MODEL = os.getenv("MODEL", "am/minimax-m3")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌿 Привет! Я Доктор Растений.\nОтправь фото листа или растения, и я определю болезнь и лечение.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔍 Анализирую фото... (это может занять 20-40 секунд)")
    
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_path = "temp.jpg"
        await file.download_to_drive(file_path)
        
        with open(file_path, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode("utf-8")
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Ты агроном. Определи: 1. Растение, 2. Диагноз, 3. Лечение, 4. Уход. Отвечай кратко и по делу на русском."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Что за болезнь на этом фото?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]}
            ],
            max_tokens=1000
        )
        
        await msg.edit_text(response.choices[0].message.content)
        
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await msg.edit_text(f"❌ Ошибка анализа. Попробуйте другое фото.\n(Детали: {str(e)[:150]})")
    finally:
        if os.path.exists("temp.jpg"):
            os.remove("temp.jpg")

def main():
    print("🚀 Бот запускается на сервере...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()