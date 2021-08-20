from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


sign_up = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Email\U0001F4E7", callback_data="email"),
            InlineKeyboardButton(text="Phone Number\U0001F4DE", callback_data="phone_num")
        ]
    ]
)
