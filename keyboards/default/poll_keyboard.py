from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonPollType, PollType


poll_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Create Poll", request_poll=KeyboardButtonPollType(type=PollType.mode))
        ],
        [
            KeyboardButton(text="Cancel")
        ]
    ],
    resize_keyboard=True
)