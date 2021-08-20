from loader import dp, bot
from aiogram import types
from database import DBCommands

db = DBCommands()


# If handled ant poll answer
@dp.poll_answer_handler()
async def poll_answer(message: types.Message, quiz_answer: types.PollAnswer):
    """ Checking for the answer """
    answered_user_id = quiz_answer.user.id
    owner_id = await db.get_owner_id(quiz_answer.poll_id)  # Getting poll owner's id from the db
    db_poll = await db.get_poll(owner_id)  # Getting poll from the db
    db_user = await db.get_user(answered_user_id)  # Getting user where user's id is similar with answered user from db
    print("working")
    if quiz_answer.poll_id == db_poll.poll_id:  # If current poll id is similar with poll in db
        if db_user:  # If this user there is in db
            if db_user.registered is False:  # If the user didn't sign up
                await bot.send_message(chat_id=answered_user_id, text="To participate in contest you have to sign up.")

        elif not db_user:  # If this user there isn't in db
            await bot.send_message(chat_id=answered_user_id, text="To participate in contest you have to sign up.")

        winners = []
        print(quiz_answer.option_ids[0])
        print(db_poll.correct_option_id)
        if quiz_answer.option_ids[0] == db_poll.correct_option_id:  # If the answer of is correct
            winners.append(answered_user_id)  # Adding to the 'winners' list
        await message.answer("Thanks for participating!")
