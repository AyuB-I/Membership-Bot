import aiogram
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils import deep_linking
from aiogram.utils.exceptions import PollCanBeRequestedInPrivateChatsOnly

from loader import dp, bot
from config import ADMIN_ID
from keyboards.default import poll_keyboard, cancel_and_skip_key
from states.states import PollState
from aiogram.types import ReplyKeyboardRemove
from database import DBCommands

db = DBCommands()


# If user is admin and handled command 'contest' on any state
@dp.message_handler(commands=["contest"], user_id=ADMIN_ID, state="*")
async def comm_poll(message: types.Message, state: FSMContext):
    """ Creating contest, if the user is in group, directing his to the chat """
    poll = await db.get_poll(message.from_user.id)  # Getting poll from the db
    if poll:  # If there are any polls in db
        await poll.delete()  # Delete the poll from the db
    if message.chat.type != types.ChatType.PRIVATE:  # If current chat is group or channel
        bot_info = await bot.get_me()
        go_dm_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="Go to DM", url=f"t.me/{bot_info.username}?start=anything")
                ]
            ]
        )
        await message.answer("You can create contest only in DM",
                             reply_markup=go_dm_keyboard)  # Sending message with redirection button
        return

    await message.answer("Tap to the button to create a poll.", reply_markup=poll_keyboard)  # Send poll creation button

    await state.set_state(PollState.asking_poll)  # Setting state


# If handled poll on state 'asking_poll'
@dp.message_handler(content_types=["poll"], state=PollState.asking_poll)
async def ask_mailing(message: types.Message, state: FSMContext):
    """ Saving to database and asking the video link"""
    # Saving to database
    poll_id = int(message.poll.id)
    question = message.poll.question
    options = (option.text for option in message.poll.options)
    correct_option_id = str(message.poll.correct_option_id)
    owner_id = int(message.from_user.id)
    poll_type = message.poll.type
    is_anonymous = message.poll.is_anonymous
    allows_multiple_answers = message.poll.allows_multiple_answers
    explanation = message.poll.explanation
    await db.add_poll(poll_id=poll_id, question=question, options=options, correct_option_id=correct_option_id,
                      owner_id=owner_id, poll_type=poll_type, is_anonymous=is_anonymous,
                      allows_multiple_answers=allows_multiple_answers, explanation=explanation)

    # Asking the link of the video
    await message.answer("Send me link of the video", reply_markup=cancel_and_skip_key)
    await state.set_state(PollState.asking_link)  # Sending state


# If handled link on state 'asking_link'
@dp.message_handler(regexp=r"(?P<domain>\w+\.\w{2,3})", state=PollState.asking_link)
async def creating_poll(message: types.Message, state: FSMContext):
    """ Finishing creation of the contest """
    await db.add_link(owner_id=message.from_user.id, video_link=message.text)  # Adding the link to db
    poll = await db.get_poll(message.from_user.id)
    # Keyboard for sharing the created contest
    share_key = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Share", url=await deep_linking.get_startgroup_link(poll.poll_id)),
                types.InlineKeyboardButton(text="Mass Mailing", callback_data="mailing")
            ]
        ]
    )

    # Showing the created contest
    await message.answer("Your contest is done!")
    await message.answer(text=str(poll.video_link))
    await bot.send_poll(chat_id=message.from_user.id, question=poll.question,
                        options=list(poll.options),
                        correct_option_id=poll.correct_option_id,
                        type=poll.type, is_anonymous=poll.is_anonymous,
                        allows_multiple_answers=poll.allows_multiple_answers,
                        explanation=poll.explanation, reply_markup=share_key)
    await state.reset_state()  # Resetting state


# If handled button 'skip' on state 'asking_link'
@dp.message_handler(text_contains="Skip", state=PollState.asking_link)
async def skip_handler(message: types.Message, state: FSMContext):
    """ Finishing creation of the contest without video link """
    poll = await db.get_poll(message.from_user.id)  # Getting poll from the db
    # Creating a keyboard for sharing the created contest
    share_key = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Share", url=await deep_linking.get_startgroup_link(poll.poll_id)),
                types.InlineKeyboardButton(text="Mass Mailing", callback_data="mailing")
            ]
        ]
    )

    # Showing the created contest
    await message.answer("Your contest is done!", reply_markup=ReplyKeyboardRemove())
    await bot.send_poll(chat_id=message.from_user.id, question=poll.question,
                        options=list(poll.options),
                        correct_option_id=poll.correct_option_id,
                        type=poll.type, is_anonymous=poll.is_anonymous,
                        allows_multiple_answers=poll.allows_multiple_answers,
                        explanation=poll.explanation, reply_markup=share_key)
    await state.reset_state()  # Resetting state


# If handled command 'start' on any state
@dp.message_handler(commands=["start"], state="*")
async def admin_start(message: types.Message, state: FSMContext):
    """ If command start is in chat, greet the user. If its in group send the poll to the group """
    await state.reset_state()  # Resetting state
    words = message.text.split()
    poll = await db.get_poll(message.from_user.id)  # Getting poll from the db
    # Checking is there any parameter with command 'start' and looking for errors
    try:
        # If the parameter of start is similar with poll id send it to the chat
        if words[1] == str(poll.poll_id):  # If the parameter of start is similar with poll id
            video_link = poll.video_link
            # If there isn contest's video link send it to the chat
            if video_link is not None:
                await bot.send_message(chat_id=message.chat.id, text=video_link)
            # Sending the contest to the current chat
            msg = await bot.send_poll(chat_id=message.chat.id, question=poll.question,
                                      options=list(poll.options),
                                      correct_option_id=poll.correct_option_id,
                                      type=poll.type, is_anonymous=poll.is_anonymous,
                                      allows_multiple_answers=poll.allows_multiple_answers,
                                      explanation=poll.explanation)
            await db.add_new_poll_id(owner_id=message.from_user.id, new_poll_id=msg.poll.id) # Adding new poll id
            return
    except Exception:  # If there are any errors pass it
        pass

    user = await db.get_user(message.from_user.id)  # Get current user's data from db
    # If current chat isn't private return user's data
    if message.chat.type != types.ChatType.PRIVATE:
        # If user isn't signed up redirect him to the private chat for sign up
        if user.registered is False:
            bot_info = await bot.get_me()
            go_dm_keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(text="Go to DM", url=f"t.me/{bot_info.username}?start=anything")
                    ]
                ]
            )

            await message.answer(text="You are not registered. To stay in group you have to be signed up.\n"
                                      "Please go to the bot and sing up there.", reply_markup=go_dm_keyboard)

        return user
    # Greeting the user
    await message.answer(text="Welcome to TestBot!", reply_markup=types.ReplyKeyboardRemove())
    await message.answer(text="If you want to join to our channel you have to sign up!")
    await message.answer(text="To sign up send me /sign_up")
    # Adding his available data to the db
    await db.add_user()
    await db.register_bool(False)


# Handling the poll answer
@dp.poll_answer_handler()
async def poll_answer(quiz_answer: types.PollAnswer):
    """ Congratulating the correct answered user """
    answered_user_id = quiz_answer.user.id
    owner_id = (await db.get_owner_id(str(quiz_answer.poll_id)))[0]
    db_poll = await db.get_poll(owner_id)
    db_user = await db.get_user(answered_user_id)
    new_poll_id = await db.get_new_poll_id(quiz_answer.poll_id)
    print("working")
    if new_poll_id:
        if db_user:
            if db_user.registered is False:
                await bot.send_message(chat_id=answered_user_id, text="To participate in contest you have to sign up.")
                return

        elif not db_user:
            await bot.send_message(chat_id=answered_user_id, text="To participate in contest you have to sign up.")
            return

        winners = []
        print(quiz_answer.option_ids[0])
        print(db_poll.correct_option_id)
        if int(quiz_answer.option_ids[0]) == int(db_poll.correct_option_id):
            winners.append(answered_user_id)
            await bot.send_message(chat_id=answered_user_id, text="you are winner")
