import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from database.models import *
from keyboards import key_text
from settings.constants import TELL_TEXT


async def cities_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора города
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    cities = Cities.select().order_by(Cities.id)
    for city in cities:
        keyboard.add(InlineKeyboardButton(text=city.title, callback_data='city&' + str(city.id)))
    return keyboard.add(InlineKeyboardButton(text=key_text.NO_CITY, callback_data=key_text.NO_CITY))


async def schools_keyboard(city_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора школы
    :param city_id: int
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    schools = Schools.select().where(Schools.city == city_id).order_by(Schools.id)
    for school in schools:
        keyboard.add(InlineKeyboardButton(text=school.title, callback_data='school&' + str(school.id)))
    return keyboard.add(
        InlineKeyboardButton(text=key_text.NO_SCHOOL, callback_data=key_text.NO_SCHOOL),
        InlineKeyboardButton(text=key_text.BACK, callback_data=key_text.BACK_CITY),
    )


async def school_class_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора класса
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    for i in range(11, 4, -1):
        keyboard.add(InlineKeyboardButton(text=str(i), callback_data=str(i)))
    return keyboard.add(InlineKeyboardButton(text=key_text.BACK, callback_data=key_text.BACK_SCHOOL))


async def gender_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора пола
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(
        InlineKeyboardButton(text=key_text.BOY, callback_data='Парень'),
        InlineKeyboardButton(text=key_text.GIRL, callback_data='Девушка'),
        InlineKeyboardButton(text=key_text.BACK, callback_data=key_text.BACK_SCHOOL_CLASS),
    )


async def back_keyboard(key: str) -> InlineKeyboardMarkup:
    """
    Клавиатура возврата назад
    :param key: str
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(
        InlineKeyboardButton(text=key_text.BACK, callback_data=key)
    )


async def rate_friends_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура оценивания друзей
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(
        InlineKeyboardButton(text=key_text.RATE_FRIENDS, callback_data=key_text.RATE_FRIENDS)
    )


async def view_question_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура просмотра вопросов
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(
        InlineKeyboardButton(text=key_text.VIEW_QUESTION, callback_data=key_text.VIEW_QUESTION)
    )


async def view_question_pagination_keyboard(
        num_page: int, end: int = 3, start: int = 1) -> InlineKeyboardMarkup:
    """
    Клавиатура пагинации выбора примеров вопросов
    :param start: int
    :param end: int
    :param num_page: int
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    if int(num_page) == start:
        left = 'pass'
        right = 'view_pag&' + str(num_page + 1)
    elif int(num_page) == end:
        left = 'view_pag&' + str(num_page - 1)
        right = 'where_install'
    else:
        left = 'view_pag&' + str(num_page - 1)
        right = 'view_pag&' + str(num_page + 1)
    return keyboard.add(
        InlineKeyboardButton(text='⬅️', callback_data=left),
        InlineKeyboardButton(text=f"{num_page}/743", callback_data='pass'),
        InlineKeyboardButton(text='➡️', callback_data=right),
        InlineKeyboardButton(text=key_text.CLEAR, callback_data=key_text.CLEAR)
    )


async def where_install_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура рассказать друзьям
    :param user_id: int
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(
        InlineKeyboardButton(
            text=key_text.TELL_FRIENDS, switch_inline_query=TELL_TEXT.format(user_id),
        ),
        InlineKeyboardButton(text=key_text.CLEAR, callback_data=key_text.CLEAR),
    )


async def name_state_keyboard(user: int, question_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура с текущими именами, без изменений
    :param question_id: int
    :param user: int
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    cur_user = Users.get(Users.id == user)
    current_list = cur_user.current_key.split('&')
    cl_list = [int(cl) for cl in current_list]
    users = Users.select().where(Users.id.in_(cl_list))
    for elem in users:
        keyboard.add(InlineKeyboardButton(text=elem.full_name, callback_data=f'rates&{elem.id}&{question_id}'))
    keyboard.add(InlineKeyboardButton(text='😕 Нет в списке', switch_inline_query=TELL_TEXT.format(cur_user.user_id)))
    return keyboard.add(
        InlineKeyboardButton(text=key_text.ANOTHER_QUESTION, callback_data=f'another&{question_id}'),
        InlineKeyboardButton(text=key_text.CHANGE_NAMES, callback_data=f'change&{question_id}'),
    )


async def name_keyboard(
        user: int, school: int, school_class: int, question_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура имен для оценивания
    :param question_id: int
    :param user: int
    :param school: int
    :param school_class: int
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    cur_user = Users.get(Users.id == user)
    cur_user.current_key = None
    if school_class == 5:
        rand = 1
    elif school_class == 11:
        rand = 0
    else:
        rand = random.randint(0, 1)
    if rand == 0:
        sc_class = school_class - 1
    else:
        sc_class = school_class + 1
    if cur_user.friend:
        friend_list = cur_user.friend.split('&')
        fr_list = [int(fr) for fr in friend_list]
        friends = Friends.select().where(Friends.user == user, Friends.id.not_in(fr_list)).order_by(fn.random())
        if len(friends) == 0:
            cur_user.friend = None
            friends = Friends.select().where(Friends.user == user).order_by(fn.random())
    else:
        friends = Friends.select().where(Friends.user == user).order_by(fn.random())
    if len(friends) > 0:
        friend = friends.get()
        if cur_user.classmate:
            classmate_list = cur_user.classmate.split('&')
            cl_list = [int(cl) for cl in classmate_list]
            cl_list.extend([user, friend.referral.id])
            users = Users.select().where(
                Users.id.not_in(cl_list), Users.school == school, Users.school_class == school_class
            ).order_by(fn.random()).limit(4)
            if len(users) < 4:
                cur_user.classmate = None
                users = Users.select().where(
                    Users.id.not_in([user, friend.referral.id]), Users.school == school,
                    Users.school_class == school_class
                ).order_by(fn.random()).limit(4)
                if cur_user.another:
                    another_list = cur_user.another.split('&')
                    an_list = [int(an) for an in another_list]
                    an_list.append(friend.referral.id)
                    students = Users.select().where(
                        Users.school == school, Users.school_class == sc_class, Users.id.not_in(an_list)
                    ).order_by(fn.random())
                    if len(students) == 0:
                        cur_user.another = None
                        students = Users.select().where(
                            Users.school == school, Users.school_class == sc_class, Users.id != friend.referral.id
                        ).order_by(fn.random())
                else:
                    students = Users.select().where(
                        Users.school == school, Users.school_class == sc_class, Users.id != friend.referral.id
                    ).order_by(fn.random())
            else:
                if cur_user.another:
                    another_list = cur_user.another.split('&')
                    an_list = [int(an) for an in another_list]
                    an_list.append(friend.referral.id)
                    students = Users.select().where(
                        Users.school == school, Users.school_class == sc_class, Users.id.not_in(an_list)
                    ).order_by(fn.random())
                    if len(students) == 0:
                        cur_user.another = None
                        students = Users.select().where(Users.school == school, Users.school_class == sc_class,
                                                        Users.id != friend.referral.id).order_by(fn.random())
                else:
                    students = Users.select().where(Users.school == school, Users.school_class == sc_class,
                                                    Users.id != friend.referral.id).order_by(fn.random())
        else:
            users = Users.select().where(
                Users.id.not_in([user, friend.referral.id]), Users.school == school, Users.school_class == school_class
            ).order_by(fn.random()).limit(4)
            if cur_user.another:
                another_list = cur_user.another.split('&')
                an_list = [int(an) for an in another_list]
                an_list.append(friend.referral.id)
                students = Users.select().where(Users.school == school, Users.school_class == sc_class,
                                                Users.id.not_in(an_list)).order_by(fn.random())
                if len(students) == 0:
                    cur_user.another = None
                    students = Users.select().where(Users.school == school, Users.school_class == sc_class,
                                                    Users.id != friend.referral.id).order_by(fn.random())
            else:
                students = Users.select().where(Users.school == school, Users.school_class == sc_class,
                                                Users.id != friend.referral.id).order_by(fn.random())
    else:
        if cur_user.another:
            another_list = cur_user.another.split('&')
            an_list = [int(an) for an in another_list]
            students = Users.select().where(
                Users.school == school, Users.school_class == sc_class, Users.id.not_in(an_list)
            ).order_by(fn.random())
            if len(students) == 0:
                cur_user.another = None
                students = Users.select().where(
                    Users.school == school, Users.school_class == sc_class
                ).order_by(fn.random())
        else:
            students = Users.select().where(
                Users.school == school, Users.school_class == sc_class
            ).order_by(fn.random())
        if cur_user.classmate:
            classmate_list = cur_user.classmate.split('&')
            cl_list = [int(cl) for cl in classmate_list]
            cl_list.append(user)
            users = Users.select().where(
                Users.id.not_in(cl_list), Users.school == school, Users.school_class == school_class
            ).order_by(fn.random()).limit(4)
            if len(users) < 4:
                cur_user.classmate = None
                users = Users.select().where(
                    Users.id != user, Users.school == school, Users.school_class == school_class
                ).order_by(fn.random()).limit(4)
        else:
            users = Users.select().where(
                Users.id != user, Users.school == school, Users.school_class == school_class
            ).order_by(fn.random()).limit(4)
    if len(students) > 0:
        student = students.get()
    for index, elem in enumerate(users):
        if index == 2:
            if len(friends) > 0:
                if cur_user.friend:
                    cur_user.friend += f"&{friend.referral.id}"
                else:
                    cur_user.friend = str(friend.referral.id)
                cur_user.current_key += f"&{friend.referral.id}"
                keyboard.add(InlineKeyboardButton(
                    text=friend.referral.full_name, callback_data=f'rates&{friend.referral.id}&{question_id}'))
            else:
                cur_user.classmate += f"&{elem.id}"
                cur_user.current_key += f"&{elem.id}"
                keyboard.add(InlineKeyboardButton(text=elem.full_name, callback_data=f'rates&{elem.id}&{question_id}'))
        elif index == 3:
            if len(students) > 0:
                if cur_user.another:
                    cur_user.another += f"&{student.id}"
                else:
                    cur_user.another = str(student.id)
                cur_user.current_key += f"&{student.id}"
                keyboard.add(InlineKeyboardButton(
                    text=student.full_name, callback_data=f'rates&{student.id}&{question_id}'))
            else:
                cur_user.classmate += f"&{elem.id}"
                cur_user.current_key += f"&{elem.id}"
                keyboard.add(InlineKeyboardButton(text=elem.full_name, callback_data=f'rates&{elem.id}&{question_id}'))
            break
        else:
            if cur_user.classmate:
                cur_user.classmate += f"&{elem.id}"
            else:
                cur_user.classmate = str(elem.id)
            if index == 0:
                cur_user.current_key = str(elem.id)
            else:
                cur_user.current_key += f"&{elem.id}"
            keyboard.add(InlineKeyboardButton(text=elem.full_name, callback_data=f'rates&{elem.id}&{question_id}'))
    cur_user.save()
    keyboard.add(InlineKeyboardButton(text='😕 Нет в списке', switch_inline_query=TELL_TEXT.format(cur_user.user_id)))
    return keyboard.add(
        InlineKeyboardButton(text=key_text.ANOTHER_QUESTION, callback_data=f'another&{question_id}'),
        InlineKeyboardButton(text=key_text.CHANGE_NAMES, callback_data=f'change&{question_id}'),
    )


async def menu_keyboard(question: int, rate: int, request: int) -> ReplyKeyboardMarkup:
    """
    Клавиатура главного меню бота
    :return: ReplyKeyboardMarkup
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
    keyboard.add(KeyboardButton(text=key_text.RATE_FRIENDS + f'  ({question}/12)'))
    return keyboard.add(
        KeyboardButton(text=key_text.MY_RATE + f'  ({rate})'),
        KeyboardButton(text=key_text.REQUEST + f'  ({request})'),
    )


async def oops_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура ожидания вопросов
    :return:InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    crystal = Variables.get_or_none(Variables.variable == 'crystal').value
    return keyboard.add(
        InlineKeyboardButton(text=key_text.HOW_CRYSTAL, callback_data=key_text.HOW_CRYSTAL),
        InlineKeyboardButton(text=key_text.CONTINUE_NOW + f"({crystal})", callback_data=key_text.CONTINUE_NOW),
    )


async def how_crystal_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура Меню с опциями о заработке кристалов
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    return keyboard.add(
        InlineKeyboardButton(text=key_text.INVITE_FRIEND, switch_inline_query=TELL_TEXT.format(user_id)),
        InlineKeyboardButton(text=key_text.BUY_CRYSTAL, callback_data=key_text.BUY_CRYSTAL),
        InlineKeyboardButton(text=key_text.BACK, callback_data=key_text.BACK_OOPS),
    )


async def buy_crystal_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура  меню оплаты кристаллов
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    refills = Refills.select().order_by(Refills.id.asc())
    if len(refills) > 0:
        for refill in refills:
            if refill.percent == 0:
                text = key_text.BUY_TEMP.format(refill.crystal, refill.price)
            else:
                text = key_text.BUY_TEMP_2.format(refill.crystal, refill.price, refill.percent)
            keyboard.add(InlineKeyboardButton(text=text, callback_data=f'refill&{refill.id}'))
    return keyboard.add(InlineKeyboardButton(text=key_text.BACK, callback_data=key_text.BACK_OOPS))


async def my_rate_keyboard(answers) -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопками оценок пользователя
    :param answers: ModelSelect
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    for answer in answers:
        gender = answer.answering.gender
        if gender == 'Парень':
            templ = key_text.MY_RATE_BOY
        else:
            templ = key_text.MY_RATE_GIRL
        if answer.status == 'Новое':
            templ += key_text.NEW_RATE_TEMP
        elif answer.hidden_answering == 'Запрос':
            templ += key_text.POST_RATE_TEMP
        elif answer.hidden_answering == 'Раскрытый':
            templ += key_text.RATE_NAME.format(answer.answering.full_name)
        keyboard.add(InlineKeyboardButton(text=templ, callback_data=f'onerate&{answer.id}'))
    return keyboard


async def hidden_keyboard(status: str, answer_id: int, name: str) -> InlineKeyboardMarkup:
    """
    Клавиатура отправки запроса на открытие
    :param name: str
    :param answer_id: int
    :param status: str
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    if status == 'Скрытый':
        keyboard.add(InlineKeyboardButton(text=key_text.FIND_WHO, callback_data=f'findwho&{answer_id}'))
    elif status == 'Запрос':
        keyboard.add(InlineKeyboardButton(text=key_text.REQUEST_SEND, callback_data='pass'))
    elif status == 'Раскрытый':
        keyboard.add(InlineKeyboardButton(text=key_text.AUTHOR.format(name), callback_data='pass'))
    return keyboard.add(
        InlineKeyboardButton(text=key_text.BACK, callback_data=key_text.MY_RATE)
    )


async def request_keyboard(
        num_page: int, end: int, answer_id: int, start: int = 1) -> InlineKeyboardMarkup:
    """
    Клавиатура запросов на раскрытие
    :param answer_id: int
    :param num_page: int
    :param end: int
    :param start: int
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton(text=key_text.REVEAL_YOURSELF, callback_data=f"reveal&{answer_id}"),
        InlineKeyboardButton(text=key_text.REJECT_REQUEST, callback_data=f"reject&{answer_id}"),
    )
    if start == end:
        left = 'pass'
        right = 'pass'
    elif int(num_page) == start:
        left = f'request&{str(end - 1)}'
        right = f'request&{num_page}'
    elif int(num_page) == end:
        left = f'request&{str(int(num_page) - 2)}'
        right = f'request&{str(start - 1)}'
    else:
        left = f'request&{str(int(num_page) - 2)}'
        right = f'request&{num_page}'
    return keyboard.add(
        InlineKeyboardButton(text='⬅️', callback_data=left),
        InlineKeyboardButton(text=f"{num_page}/{end}", callback_data='pass'),
        InlineKeyboardButton(text='➡️', callback_data=right),
    )
