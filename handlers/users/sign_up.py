from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher import FSMContext
from loader import dp
from states.states import SignupState
from database import DBCommands
from keyboards.inline import sign_up, confirm_keyboard
from keyboards.default import phone_num_button, cancel_button

db = DBCommands()


"""@dp.message_handler(CommandStart(), state="*")
async def start(mes: types.Message, state: FSMContext):
    await state.reset_state()
    user = await db.get_user(user_id=mes.from_user.id)
    if user:
        return user
    await mes.answer(text="Welcome to TestBot!", reply_markup=types.ReplyKeyboardRemove())
    await mes.answer(text="If you want to join to our channel you have to sign up!")
    await mes.answer(text="To sign up send me /sign_up")

    await db.add_user()
    await db.register_bool(False)"""


# If handled message 'Cancel' on any state
@dp.message_handler(text_contains="Cancel", state="*")
async def cancel_func(message: types.Message, state: FSMContext):
    """ Canceling any actions """
    await state.reset_state()  # Resetting state
    await message.answer(text="You canceled actions!", reply_markup=types.ReplyKeyboardRemove())
    user = await db.get_user(message.from_user.id)
    if not user:  # If user is not registered
        await message.answer(text="If you want to join to our channel you have to sign up!")
        await message.answer(text="To sign up send me /sign_up")


# If handled command 'sign_up' on any state
@dp.message_handler(commands=["sign_up"], state="*")
async def signup(message: types.Message, state: FSMContext):
    """ Signing up and asking name """
    await state.reset_state()  # Resetting state
    user = await db.get_user(user_id=message.from_user.id)
    if not user:  # If user is not registered
        await db.add_user()  # Adding to db user's available data
        await db.register_bool(False)
    elif user:  # If user is registered
        if user.registered:  # If user's registration state is True
            await message.answer("You have already registered!", reply_markup=types.ReplyKeyboardRemove())
            await state.reset_state()  # Resetting state
            return user
    await message.answer("What is your name?", reply_markup=cancel_button)  # Asking name
    await state.set_state(SignupState.first_name)  # Setting state


# If state is 'first_name' and in 'SignupState'
@dp.message_handler(state=SignupState.first_name)
async def get_name(message: types.Message, state: FSMContext):
    """ Signing up and asking the type of registration  """
    first_name = message.text
    await db.add_first_name(first_name=first_name)  # Adding the first name of user to db
    await message.answer("How will you sign up?", reply_markup=sign_up)  # Asking the type of registration
    await state.set_state(SignupState.email_or_number)  # Setting state


# If handled button 'email' on state 'email_or_number'
@dp.callback_query_handler(text_contains="email", state=SignupState.email_or_number)
async def email(call: types.CallbackQuery, state: FSMContext):
    """ Signing up via email and asking email """
    await call.message.edit_reply_markup()  # Removing the button
    await call.message.answer("Send me your email", reply_markup=cancel_button)
    await state.set_state(SignupState.email)  # Setting state


# If state is 'email' and in 'SignupState'
@dp.message_handler(state=SignupState.email)
async def get_email(message: types.Message, state: FSMContext):
    """ Signing up via email and confirming email """
    email_text = message.text
    await message.answer("Is your email correct?")
    await message.answer(text=email_text, reply_markup=confirm_keyboard)
    await state.update_data(email=email_text)  # Adding the email to storage
    await state.set_state(SignupState.confirm_email)  # Setting state


# If handled button 'yes' on state 'confirm_email'
@dp.callback_query_handler(text_contains="yes", state=SignupState.confirm_email)
async def yes_email(call: types.CallbackQuery, state: FSMContext):
    """ Finishing the registration """
    await call.message.edit_reply_markup()  # Removing the keyboard
    await call.message.answer("You signed up successfully!")
    await call.message.answer("Welcome to our channel")
    await call.message.answer("# here will be button or link of your private channel/group")
    email_text_dict = await state.get_data("email")  # Getting data from the storage
    email_text = email_text_dict["email"]
    await db.add_email(email=email_text)  # Adding user's email to the db
    await db.register_bool(True)  # Setting registration state to the True
    await state.reset_state()  # Resetting state


# If handled button 'no' on state 'confirm_email'
@dp.callback_query_handler(text_contains="no", state=SignupState.confirm_email)
async def no_email(call: types.CallbackQuery, state: FSMContext):
    """ Signing up via email and asking another email """
    await call.message.edit_reply_markup()  # Removing the keyboard
    await call.message.answer("Send me your email", reply_markup=cancel_button)
    await state.set_state(SignupState.email)  # Setting state


# If handled button 'phone_num' on state 'email_or_number'
@dp.callback_query_handler(text_contains="phone_num", state=SignupState.email_or_number)
async def phone_number(call: types.CallbackQuery, state: FSMContext):
    """ Signing up via phone number and asking phone number """
    await call.message.edit_reply_markup()  # Removing the keyboard
    await call.message.answer(text="Send me your mobile number without '+'\n"
                                   "or click the button\U00002B07", reply_markup=phone_num_button)
    await state.set_state(SignupState.phone_num)  # Setting state


# If state is 'phone_num' and in 'SignupStates'
@dp.message_handler(state=SignupState.phone_num)
async def get_phone_num(message: types.Message, state: FSMContext):
    """ Signing up via phone number and confirming it """
    try:  # Converting the number to integer and checking for errors
        mobile_num = int(message.text)
    except Exception:  # If there are any errors
        await message.answer("You wrote incorrect number!")
        await state.set_state(SignupState.phone_num)  # Setting state
        return
    await message.answer("Is your mobile number correct?", reply_markup=types.ReplyKeyboardRemove())
    await message.answer(text=f"+{mobile_num}", reply_markup=confirm_keyboard)
    await state.update_data(phone_num=mobile_num)  # Adding phone number to the storage
    await state.set_state(SignupState.confirm_phone_num)  # Setting state


# If type of the message is contact and on state 'phone_num'
@dp.message_handler(state=SignupState.phone_num, content_types=types.ContentType.CONTACT)
async def get_phone_num(message: types.Message, state: FSMContext):
    """ Signing up via phone number and confirming the contact """
    mobile_num = int(message.contact.phone_number)  # Converting the contact to the integer
    await message.answer("Is your mobile number correct?", reply_markup=types.ReplyKeyboardRemove())
    await message.answer(text=f"+{mobile_num}", reply_markup=confirm_keyboard)
    await state.update_data(phone_num=mobile_num)  # Adding number to the storage
    await state.set_state(SignupState.confirm_phone_num)  # Setting state


# If handled button 'yes' on state 'confirm_phone_num'
@dp.callback_query_handler(text_contains="yes", state=SignupState.confirm_phone_num)
async def yes_phone_num(call: types.CallbackQuery, state: FSMContext):
    """ Finishing the registration """
    await call.message.edit_reply_markup()
    await call.message.answer("You signed up successfully!")
    await call.message.answer("Welcome to our channel")
    await call.message.answer("# here will be button or link of your private channel/group")
    phone_num_dict = await state.get_data("phone_num")  # Getting phone number from the storage
    number = phone_num_dict["phone_num"]  # Getting integer from the dictionary
    await db.add_phone_num(phone_num=f"+{number}")  # Adding phone number to the db
    await db.register_bool(True)  # Setting registration state to the True
    await state.reset_state()  # Resetting state


# If handled button 'no' on state 'confirm_phone_num'
@dp.callback_query_handler(text_contains="no", state=SignupState.confirm_phone_num)
async def no_phone_num(call: types.CallbackQuery, state: FSMContext):
    """ Signing up via phone number and confirming it """
    await call.message.edit_reply_markup()  # Removing rhe keyboard
    await call.message.answer(text="Send me your mobile number or click the button\U00002B07",
                              reply_markup=phone_num_button)
    await state.set_state(SignupState.phone_num)  # Setting state
