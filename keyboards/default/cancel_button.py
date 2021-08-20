from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


cancel_button = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Cancel")
        ]
    ],
    resize_keyboard=True
)
