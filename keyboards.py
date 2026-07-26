from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="ℹ️ Помощь / О боте")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Напишите сообщение или отправьте фото/видео..."
    )