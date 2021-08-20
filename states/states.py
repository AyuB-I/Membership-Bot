from aiogram.dispatcher.filters.state import StatesGroup, State


class SignupState(StatesGroup):
    first_name = State()
    email_or_number = State()
    email = State()
    confirm_email = State()
    phone_num = State()
    confirm_phone_num = State()


class PollState(StatesGroup):
    asking_link = State()
    asking_poll = State()
