from aiogram import types

from gino import Gino
from sqlalchemy import (Column, Integer, BigInteger, String, Sequence, TIMESTAMP, Boolean, ARRAY)
from sqlalchemy import sql
from gino.schema import GinoSchemaVisitor
from config import DB_USER, DB_PASSWORD, HOST


db = Gino()


class Users(db.Model):
    """ Table 'users' """
    __tablename__ = "users"
    query: sql.Select

    id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
    user_id = Column(Integer)
    user_name = Column(String)
    first_name = Column(String)
    email = Column(String)
    phone_num = Column(String)
    registered = Column(Boolean)


class Polls(db.Model):
    """ Table 'polls' """
    __tablename__ = "polls"
    query: sql.Select

    id = Column(Integer, Sequence("poll_id_seq"), primary_key=True)
    poll_id = Column(BigInteger)
    owner_id = Column(BigInteger)
    question = Column(String)
    options = Column(ARRAY(String, as_tuple=True))
    correct_option_id = Column(String)
    type = Column(String)
    is_anonymous = Column(Boolean)
    allows_multiple_answers = Column(Boolean)
    explanation = Column(String)
    video_link = Column(String)
    new_poll_id = Column(String)


class DBCommands:
    """ Commands for managing the data base """
    async def get_user(self, user_id) -> Users:
        """ Getting new user by his id """
        user = await Users.query.where(Users.user_id == user_id).gino.first()
        return user

    async def add_user(self):
        """ Adding new user """
        user = types.User.get_current()
        user_exists = await self.get_user(user.id)
        if user_exists:
            return user_exists
        new_user = Users()
        new_user.user_id = user.id
        new_user.user_name = user.username
        await new_user.create()
        return new_user

    async def add_phone_num(self, phone_num):
        """ Adding phone number """
        user_id = types.User.get_current().id
        user = await self.get_user(user_id)
        if phone_num[0] == "+":
            await user.update(phone_num=phone_num).apply()
        else:
            raise Exception

    async def add_email(self, email):
        """ Adding e-mail """
        user_id = types.User.get_current().id
        user = await self.get_user(user_id)
        await user.update(email=email).apply()

    async def add_first_name(self, first_name):
        """ Adding fiirst name """
        user_id = types.User.get_current().id
        user = await self.get_user(user_id)
        await user.update(first_name=first_name).apply()

    async def count_users(self):
        """ Returning quantity of users """
        total = await db.func.count(Users.user_id).scalar()
        return total

    async def register_bool(self, registered=False):
        """ Setting state of registration """
        user_id = types.User.get_current().id
        user = await self.get_user(user_id)
        await user.update(registered=registered).apply()

    async def get_poll(self, owner_id) -> Polls:
        """ Getting poll """
        poll = await Polls.query.where(Polls.owner_id == owner_id).gino.first()
        return poll

    async def get_owner_id(self, new_poll_id) -> Polls:
        """ Getting poll owner's id """
        owner_id = await Polls.select("owner_id").where(Polls.new_poll_id == new_poll_id).gino.first()
        return owner_id

    async def get_new_poll_id(self, poll_id) -> Polls:
        """ Getting new poll id """
        new_poll_id = await Polls.select("new_poll_id").where(Polls.new_poll_id == poll_id).gino.first()
        return new_poll_id

    async def add_poll(self, poll_id, owner_id, question, options, correct_option_id,  poll_type, is_anonymous,
                       allows_multiple_answers, explanation):
        """ Adding poll """
        new_poll = Polls()
        new_poll.poll_id = poll_id
        new_poll.owner_id = owner_id
        new_poll.question = question
        new_poll.options = options
        new_poll.correct_option_id = correct_option_id
        new_poll.type = poll_type
        new_poll.is_anonymous = is_anonymous
        new_poll.allows_multiple_answers = allows_multiple_answers
        new_poll.explanation = explanation
        await new_poll.create()
        return new_poll

    async def add_new_poll_id(self, owner_id, new_poll_id):
        """ Adding new poll id """
        poll = await self.get_poll(owner_id)
        await poll.update(new_poll_id=new_poll_id).apply()

    async def add_link(self, owner_id, video_link):
        """ Adding link """
        poll = await self.get_poll(owner_id)
        await poll.update(video_link=video_link).apply()


async def create_db():
    """ Creating data base """
    await db.set_bind(f"postgresql://{DB_USER}:{DB_PASSWORD}@{HOST}/postgres")
    db.gino: GinoSchemaVisitor
    await db.gino.create_all()
