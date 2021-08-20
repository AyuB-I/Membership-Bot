from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


cancel_and_skip_key = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Skip")
        ],
        [
            KeyboardButton(text="Cancel")

        ]
    ],
    resize_keyboard=True
)
