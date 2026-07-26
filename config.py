import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

# Проверяем, что всё заполнено
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в файле .env")

if ADMIN_CHAT_ID == 0:
    raise ValueError("❌ ADMIN_CHAT_ID не найден в файле .env")