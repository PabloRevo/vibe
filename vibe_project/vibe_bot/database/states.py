"""
Файл с моделями машины состояний
"""


from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMSignUp(StatesGroup):
    city = State()
    school = State()
    school_class = State()
    gender = State()
    full_name = State()
    your_city = State()
    your_school = State()
    blocked = State()


class FSMChangeName(StatesGroup):
    name = State()


class FSMWriteSupport(StatesGroup):
    support = State()
