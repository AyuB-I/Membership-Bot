from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


phone_num_button = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Send My Contact", request_contact=True)
        ],
        [
            KeyboardButton(text="Cancel")
        ]
    ],
    resize_keyboard=True
)
