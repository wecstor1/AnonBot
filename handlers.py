import asyncio
import datetime
import logging
from html import escape

from aiogram import Router, F, types
from aiogram.filters import Command

from config import ADMIN_CHAT_ID
from database import save_message, get_stats
from keyboards import get_start_keyboard

router = Router()
logger = logging.getLogger(__name__)

last_message_times = {}
SPAM_COOLDOWN = 30


def check_antispam(user_id: int) -> bool:
    current_time = asyncio.get_event_loop().time()

    if user_id in last_message_times:
        if current_time - last_message_times[user_id] < SPAM_COOLDOWN:
            return False

    last_message_times[user_id] = current_time
    return True


def format_admin_info(user: types.User, date_str: str, time_str: str) -> str:
    first_name = escape(user.first_name or "Не указано")
    last_name = escape(user.last_name or "")
    username = f"@{escape(user.username)}" if user.username else "нет"

    return (
        "━━━━━━━━━━━━━━\n\n"
        "👤 Отправитель:\n"
        f"{first_name} {last_name}\n\n"
        "🔗 Username:\n"
        f"{username}\n\n"
        "🆔 ID:\n"
        f"{user.id}\n\n"
        f"📅 Дата: {date_str}\n"
        f"🕐 Время: {time_str}"
    )


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "💌 Добро пожаловать!\n"
        "Отправь мне любое анонимное сообщение.\n\n"
        "Можно отправить:\n"
        "• текст;\n"
        "• фото;\n"
        "• видео;\n"
        "• фото с подписью;\n"
        "• видео с подписью.",
        reply_markup=get_start_keyboard()
    )


@router.message(F.text == "ℹ️ Помощь / О боте")
async def help_handler(message: types.Message):
    await message.answer(
        "💌 Это бот для анонимных сообщений.\n"
        "Поддержка: @Wecstor\n\n"
        "Отправьте текст, фото или видео — сообщение придёт администратору."
    )


@router.message(Command("id"))
async def cmd_id(message: types.Message):
    await message.answer(
        f"🆔 Ваш Telegram ID: {message.from_user.id}"
    )


@router.message(Command("stats"))
async def cmd_stats(message: types.Message):

    if message.from_user.id != ADMIN_CHAT_ID:
        await message.answer(
            "❌ У вас нет прав для выполнения этой команды."
        )
        return

    stats = get_stats()

    await message.answer(
        f"📊 Статистика бота:\n\n"
        f"👥 Пользователей: {stats['users']}\n"
        f"💬 Сообщений: {stats['messages']}\n"
        f"📷 Фото: {stats['photos']}\n"
        f"🎥 Видео: {stats['videos']}"
    )


@router.message(
    F.text &
    ~F.text.startswith("/") &
    (F.text != "ℹ️ Помощь / О боте")
)
async def handle_text(message: types.Message):

    user_id = message.from_user.id

    if not check_antispam(user_id):
        await message.answer(
            "⚠️ Слишком частая отправка сообщений. Подождите немного."
        )
        return

    try:
        now = datetime.datetime.now()

        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M:%S")

        data = {
            "telegram_id": user_id,
            "username": message.from_user.username or "",
            "first_name": message.from_user.first_name or "",
            "last_name": message.from_user.last_name or "",
            "text": message.text,
            "media_type": "text",
            "telegram_file_id": None,
            "date": date_str,
            "time": time_str
        }

        save_message(data)


        # 1 сообщение — текст
        await message.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                "💌 У тебя новое анонимное сообщение\n\n"
                "📝 Сообщение:\n"
                f"{escape(message.text)}"
            )
        )


        # 2 сообщение — данные
        await message.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=format_admin_info(
                message.from_user,
                date_str,
                time_str
            )
        )


        await message.answer(
            "✅ Сообщение успешно отправлено."
        )

    except Exception as e:
        logger.error(f"Ошибка при обработке текста: {e}")
        await message.answer(
            "❌ Произошла ошибка при отправке сообщения."
        )


@router.message(F.photo | F.video)
async def handle_media(message: types.Message):

    user_id = message.from_user.id

    if not check_antispam(user_id):
        await message.answer(
            "⚠️ Слишком частая отправка сообщений. Подождите немного."
        )
        return

    try:
        now = datetime.datetime.now()

        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M:%S")

        caption = message.caption or ""

        media_type = (
            "photo"
            if message.photo
            else "video"
        )

        file_id = (
            message.photo[-1].file_id
            if message.photo
            else message.video.file_id
        )


        data = {
            "telegram_id": user_id,
            "username": message.from_user.username or "",
            "first_name": message.from_user.first_name or "",
            "last_name": message.from_user.last_name or "",
            "text": caption,
            "media_type": media_type,
            "telegram_file_id": file_id,
            "date": date_str,
            "time": time_str
        }

        save_message(data)


        # медиа отдельно
        if media_type == "photo":

            await message.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=file_id,
                caption="💌 У тебя новое анонимное сообщение"
            )

        else:

            await message.bot.send_video(
                chat_id=ADMIN_CHAT_ID,
                video=file_id,
                caption="💌 У тебя новое анонимное сообщение"
            )


        # информация отдельным сообщением
        await message.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=format_admin_info(
                message.from_user,
                date_str,
                time_str
            )
        )


        await message.answer(
            "✅ Сообщение успешно отправлено."
        )


    except Exception as e:
        logger.error(f"Ошибка при обработке медиа: {e}")

        await message.answer(
            "❌ Произошла ошибка при отправке сообщения."
        )