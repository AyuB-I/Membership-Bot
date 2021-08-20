from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


confirm_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="\U00002713", callback_data="yes"),
            InlineKeyboardButton(text="\U00002715", callback_data="no")
        ]
    ]
)
