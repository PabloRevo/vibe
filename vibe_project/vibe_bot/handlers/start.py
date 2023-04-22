"""
Файл с хэндлерами старт/хэлп и регистрация
"""
import asyncio
import re
from datetime import date
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from database.states import FSMSignUp
from handlers import rates, support
from handlers.echo import delete_message, active_user, total_signup_invite, set_user_commands
from keyboards import key_text
from keyboards.keyboards import cities_keyboard, schools_keyboard, back_keyboard, school_class_keyboard, \
    gender_keyboard, rate_friends_keyboard, view_question_keyboard, view_question_pagination_keyboard, \
    where_install_keyboard
from loader import bot, logger
from database.models import *
from settings.constants import MESSAGES, YOUR_FRIEND


async def start_command(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает команду /start. Спрашивает у пользователя город проживания.
    Входит в машину состояния FSMSignUp.
    :param state: FSMContext
    :param message: Message
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == message.from_user.id)
        if user:
            await message.delete()
            if user.status_city is True and user.status_school is True:
                value = Variables.get(Variables.variable == 'quantity').value
                count = Users.select().where(
                    Users.city == user.city, Users.school == user.school,
                    Users.school_class == user.school_class
                ).count()
                if count >= value:
                    if user.count == 12:
                        await rates.count_twelve(message, user)
                    else:
                        await rates.send_question(message, user)
                else:
                    signup_complete = MESSAGES['signup_complete']
                    bot_message = await bot.send_photo(
                        message.from_user.id, photo=open(f'media/{signup_complete["photo"]}', 'rb'),
                        caption=signup_complete['text'].format(value, value),
                        reply_markup=await view_question_keyboard()
                    )
                    DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        else:
            SignUp(user_id=message.from_user.id, change_at=date.today()).save()
            await FSMSignUp.city.set()
            if isinstance(message, types.Message):
                if re.findall(r'\d+', message.text):
                    async with state.proxy() as data:
                        data['friend'] = int(re.findall(r'\b\d+\b', message.text)[0])
            signup = MESSAGES['signup']
            await delete_message(message.from_user.id)
            bot_message = await bot.send_photo(
                message.from_user.id, photo=open(f'media/{signup["photo"]}', 'rb'), caption=signup['text'],
                reply_markup=await cities_keyboard()
            )
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def city_state(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - обабатывает нажатие на кнопку с городом. (Состояние FSMSignUp.city).
    Запрашивает у пользователя номер школы.
    :param state: FSMContext
    :param call: CallbackQuery
    :return: None
    """
    try:
        async with state.proxy() as data:
            if call.data != key_text.BACK_SCHOOL:
                data['city'] = int(call.data.split('&')[1])
                SignUp.update({SignUp.is_city: True}).execute()
        await delete_message(call.from_user.id)
        school = MESSAGES['school']
        bot_message = await bot.send_photo(
            call.from_user.id, photo=open(f'media/{school["photo"]}', 'rb'), caption=school['text'],
            reply_markup=await schools_keyboard(data['city'])
        )
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        await FSMSignUp.school.set()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def no_city_state(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку нет города. (Состояние FSMSignUp.city).
    :param call: CallbackQuery
    :return: None
    """
    try:
        await delete_message(call.from_user.id)
        your_city = MESSAGES['your_city']
        bot_message = await bot.send_photo(
            call.from_user.id, photo=open(f'media/{your_city["photo"]}', 'rb'), caption=your_city['text'],
            reply_markup=await back_keyboard(key_text.BACK_CITY)
        )
        await FSMSignUp.your_city.set()
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def your_city_state(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает состояние FSMSignUp.your_city. Получает на вход введенный пользователем город.
    :param message: Message
    :return: None
    """
    try:
        await message.delete()
        await delete_message(message.from_user.id)
        empty_city = MESSAGES['empty_city']
        bot_message = await bot.send_photo(
            message.from_user.id, photo=open(f'media/{empty_city["photo"]}', 'rb'), caption=empty_city['text'],
        )
        DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        Users(user_id=message.from_user.id, username=message.from_user.username, choice_city=message.text).save()
        await FSMSignUp.blocked.set()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def school_state(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние FSMSignUp.school. Нажатие на кнопку выбора школы
    :param call: CallbackQuery
    :param state: FSMContext
    :return: None
    """
    try:
        async with state.proxy() as data:
            if call.data != key_text.BACK_SCHOOL_CLASS:
                data['school'] = int(call.data.split('&')[1])
                SignUp.update({SignUp.is_school: True}).execute()
        await delete_message(call.from_user.id)
        school_class = MESSAGES['class']
        bot_message = await bot.send_photo(
            call.from_user.id, photo=open(f'media/{school_class["photo"]}', 'rb'), caption=school_class['text'],
            reply_markup=await school_class_keyboard()
        )
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        await FSMSignUp.school_class.set()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def no_school_state(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку нет школы. (Состояние FSMSignUp.city).
    :param call: CallbackQuery
    :return: None
    """
    try:
        await delete_message(call.from_user.id)
        your_school = MESSAGES['your_school']
        bot_message = await bot.send_photo(
            call.from_user.id, photo=open(f'media/{your_school["photo"]}', 'rb'), caption=your_school['text'],
            reply_markup=await back_keyboard(key_text.BACK_SCHOOL)
        )
        await FSMSignUp.your_school.set()
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def your_school_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние FSMSignUp.your_school. Получает на вход веденную пользователем школу.
    :param state: FSMContext
    :param message: Message
    :return: None
    """
    try:
        await message.delete()
        await delete_message(message.from_user.id)
        empty_school = MESSAGES['empty_school']
        bot_message = await bot.send_photo(
            message.from_user.id, photo=open(f'media/{empty_school["photo"]}', 'rb'), caption=empty_school['text'],
        )
        DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        async with state.proxy() as data:
            Users(
                user_id=message.from_user.id, username=message.from_user.username, city=data['city'],
                choice_school=message.text, status_city=True
            ).save()
        await FSMSignUp.blocked.set()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def school_class_state(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние FSMSignUp.school_class. Нажатие на кнопку выбора класса.
    :param call: CallbackQuery
    :param state: FSMContext
    :return: None
    """
    try:
        async with state.proxy() as data:
            if call.data != key_text.BACK_GENDER:
                data['school_class'] = int(call.data)
                SignUp.update({SignUp.is_class: True}).execute()
        await delete_message(call.from_user.id)
        gender = MESSAGES['gender']
        bot_message = await bot.send_photo(
            call.from_user.id, photo=open(f'media/{gender["photo"]}', 'rb'), caption=gender['text'],
            reply_markup=await gender_keyboard()
        )
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        await FSMSignUp.gender.set()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def gender_state(call: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает состояние FSMSignUp.gender. Нажатие на кнопку выбора пола.
    :param call: CallbackQuery
    :param state: FSMContext
    :return: None
    """
    try:
        async with state.proxy() as data:
            data['gender'] = call.data
            SignUp.update({SignUp.is_gender: True}).execute()
        await delete_message(call.from_user.id)
        full_name = MESSAGES['full_name']
        bot_message = await bot.send_photo(
            call.from_user.id, photo=open(f'media/{full_name["photo"]}', 'rb'), caption=full_name['text'],
            reply_markup=await back_keyboard(key_text.BACK_GENDER)
        )
        DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        await FSMSignUp.full_name.set()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def full_name_state(message: types.Message, state: FSMContext) -> None:
    """
    хэндлер - обрабатывает состояние SMSignUp.full_name. Ввод пользователем ФИО
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        await message.delete()
        await delete_message(message.from_user.id)
        if [message.text] == re.findall(r'[а-яА-ЯёЁ]+ [а-яА-ЯёЁ]+', message.text):
            async with state.proxy() as data:
                Users(
                    user_id=message.from_user.id, username=message.from_user.username, city=data['city'],
                    school=data['school'], school_class=data['school_class'], gender=data['gender'],
                    full_name=message.text, status_city=True, status_school=True, count=0, signup_at=date.today(),
                    active_at=date.today()
                ).save()
                sign_up = SignUp.get_or_none(SignUp.user_id == message.from_user.id)
                if sign_up:
                    sign_up.delete_instance()
                await sign_count(data['city'], data['school'], data['school_class'])
                if data.get('friend', None):
                    await total_signup_invite()
                    referral = Users.get(Users.user_id == message.from_user.id).id
                    user = Users.get(Users.user_id == data['friend'])
                    Friends(user=user.id, referral=referral).save()
                    user.balance += 10
                    user.save()
                    if user.count != 999:
                        try:
                            bot_message = await bot.send_message(
                                user.user_id, YOUR_FRIEND.format(message.text)
                            )
                            delete = DeleteMessage.get_or_none(DeleteMessage.chat_id == user.user_id)
                            if delete:
                                delete.message_id += f'&{str(bot_message.message_id)}'
                                delete.save()
                        except:
                            pass
                value = Variables.get(Variables.variable == 'quantity').value
                count = Users.select().where(
                    Users.city == data['city'], Users.school == data['school'],
                    Users.school_class == data['school_class']
                ).count()
                if count >= value:
                    users = Users.select().where(
                        Users.city == data['city'], Users.school == data['school'],
                        Users.school_class == data['school_class'], Users.count == 999,
                    )
                    await set_user_commands(message.from_user.id)
                    await_complete = MESSAGES['await_complete']
                    for elem in users:
                        try:
                            await delete_message(elem.user_id)
                            bot_message = await bot.send_photo(
                                elem.user_id, photo=open(f'media/{await_complete["photo"]}', 'rb'),
                                caption=await_complete['text'].format(value),
                                reply_markup=await rate_friends_keyboard()
                            )
                            await set_user_commands(elem.user_id)
                            DeleteMessage(chat_id=elem.user_id, message_id=str(bot_message.message_id)).save()
                            elem.count = 0
                            elem.save()
                        except Exception as ex:
                            logger.error('Ошибка при рассылке', exc_info=ex)
                    signup_complete_two = MESSAGES['signup_complete_two']
                    bot_message = await bot.send_photo(
                        message.from_user.id, photo=open(f'media/{signup_complete_two["photo"]}', 'rb'),
                        caption=signup_complete_two['text'],
                        reply_markup=await rate_friends_keyboard()
                    )
                else:
                    Users.update({Users.count: 999}).where(Users.user_id == message.from_user.id).execute()
                    signup_complete = MESSAGES['signup_complete']
                    bot_message = await bot.send_photo(
                        message.from_user.id, photo=open(f'media/{signup_complete["photo"]}', 'rb'),
                        caption=signup_complete['text'].format(value, value),
                        reply_markup=await view_question_keyboard()
                    )
                await state.finish()
        else:
            incorrect_name = MESSAGES['incorrect_name']
            bot_message = await bot.send_photo(
                message.from_user.id, photo=open(f'media/{incorrect_name["photo"]}', 'rb'),
                caption=incorrect_name['text'],
                reply_markup=await back_keyboard(key_text.BACK_GENDER)
            )
        DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def view_question_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку view_question
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await active_user(user, call.from_user.username)
            first_question = MESSAGES['first_question']
            await delete_message(call.from_user.id)
            bot_message = await bot.send_photo(
                call.from_user.id, photo=open(f'media/{first_question["photo"]}', 'rb'),
                caption=first_question['text'],
                reply_markup=await view_question_pagination_keyboard(1)
            )
            DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def view_pagination_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку пагинации просмотра примеров вопросов
    :param call: CallbackQuery
    :return: None
    """
    global question
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await active_user(user, call.from_user.username)
            num_page = int(call.data.split('&')[1])
            if num_page == 1:
                question = MESSAGES['first_question']
            elif num_page == 2:
                question = MESSAGES['second_question']
            elif num_page == 3:
                question = MESSAGES['third_question']
            await delete_message(call.from_user.id)
            bot_message = await bot.send_photo(
                call.from_user.id, photo=open(f'media/{question["photo"]}', 'rb'),
                caption=question['text'],
                reply_markup=await view_question_pagination_keyboard(num_page)
            )
            DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def clear_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку clear
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await active_user(user, call.from_user.username)
            value = Variables.get(Variables.variable == 'quantity').value
            signup_complete = MESSAGES['signup_complete']
            await delete_message(call.from_user.id)
            bot_message = await bot.send_photo(
                call.from_user.id, photo=open(f'media/{signup_complete["photo"]}', 'rb'),
                caption=signup_complete['text'].format(value, value),
                reply_markup=await view_question_keyboard()
            )
            DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def where_install_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку where_install. Предлагает пользователю пригласить друзей.
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await active_user(user, call.from_user.username)
            value = Variables.get(Variables.variable == 'quantity').value
            where_install = MESSAGES['where_install']
            await delete_message(call.from_user.id)
            bot_message = await bot.send_photo(
                call.from_user.id, photo=open(f'media/{where_install["photo"]}', 'rb'),
                caption=where_install['text'].format(value),
                reply_markup=await where_install_keyboard(call.from_user.id)
            )
            DeleteMessage(chat_id=call.from_user.id, message_id=str(bot_message.message_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def sign_count(city: str, school: str, school_class: str) -> None:
    """
    Функция - обновления данных в таблице statistics
    :param school_class: str
    :param school: str
    :param city: str
    :return: None
    """
    try:
        city = Cities.get_or_none(Cities.id == int(city))
        if city:
            statistics = Statistics.get_or_none(Statistics.created_at == date.today())
            if statistics:
                statistics.new_user += 1
                if city.title == 'Москва':
                    statistics.moscow += 1
                elif city.title == 'Санкт-Петербург':
                    statistics.spb += 1
                elif city.title == 'Екатеринбург':
                    statistics.ekb += 1
                elif city.title == 'Новосибирск':
                    statistics.nsb += 1
                elif city.title == 'Сочи':
                    statistics.sochi += 1
                statistics.save()
            else:
                if city.title == 'Москва':
                    Statistics(created_at=date.today(), new_user=1, moscow=1).save()
                elif city.title == 'Санкт-Петербург':
                    Statistics(created_at=date.today(), new_user=1, spb=1).save()
                elif city.title == 'Екатеринбург':
                    Statistics(created_at=date.today(), new_user=1, ekb=1).save()
                elif city.title == 'Новосибирск':
                    Statistics(created_at=date.today(), new_user=1, nsb=1).save()
                elif city.title == 'Сочи':
                    Statistics(created_at=date.today(), new_user=1, sochi=1).save()
        school_cl = SchoolClass.get_or_none(SchoolClass.created_at == date.today(), SchoolClass.school == int(school))
        if school_cl:
            if int(school_class) == 11:
                school_cl.class11 += 1
            elif int(school_class) == 10:
                school_cl.class10 += 1
            elif int(school_class) == 9:
                school_cl.class9 += 1
            elif int(school_class) == 8:
                school_cl.class8 += 1
            elif int(school_class) == 7:
                school_cl.class7 += 1
            elif int(school_class) == 6:
                school_cl.class6 += 1
            elif int(school_class) == 5:
                school_cl.class5 += 1
            school_cl.save()
        else:
            await school_class_logic(city.id)
            school_cl = SchoolClass.get_or_none(
                SchoolClass.created_at == date.today(), SchoolClass.school == int(school))
            if school_cl:
                if int(school_class) == 11:
                    school_cl.class11 += 1
                elif int(school_class) == 10:
                    school_cl.class10 += 1
                elif int(school_class) == 9:
                    school_cl.class9 += 1
                elif int(school_class) == 8:
                    school_cl.class8 += 1
                elif int(school_class) == 7:
                    school_cl.class7 += 1
                elif int(school_class) == 6:
                    school_cl.class6 += 1
                elif int(school_class) == 5:
                    school_cl.class5 += 1
                school_cl.save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def school_class_logic(city: int) -> None:
    """
    Функция - для создания ежедневной статистики по классам
    :return: None
    """
    try:
        schools = Schools.select().where(Schools.city == city).order_by(Schools.id.asc())
        if len(schools) > 0:
            for school in schools:
                SchoolClass(created_at=date.today(), city=city, school=school.id).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def cancel_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает выход из состояния
    :param message: Message
    :param state: FSMContext
    :return: None
    """
    try:
        if await state.get_state():
            await state.finish()
        if message.text == '/ratefriends' or message.text == key_text.RATE_FRIENDS:
            await rates.rate_friends_handler(message)
        elif message.text == '/myrate' or message.text == key_text.REQUEST:
            await rates.my_rate_handler(message)
        elif message.text == '/requests' or message.text == key_text.MY_RATE:
            await rates.request_handler(message)
        elif message.text == '/change_name':
            await support.change_name_handler(message)
        elif message.text == '/write_support':
            await support.write_support_handler(message)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_start_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start_command, commands=['start'], state=None)
    dp.register_callback_query_handler(start_command, lambda call: call.data == key_text.BACK_CITY, state='*')
    dp.register_callback_query_handler(city_state, lambda call: call.data == key_text.BACK_SCHOOL, state='*')
    dp.register_callback_query_handler(school_state, lambda call: call.data == key_text.BACK_SCHOOL_CLASS, state='*')
    dp.register_callback_query_handler(school_class_state, lambda call: call.data == key_text.BACK_GENDER, state='*')
    dp.register_callback_query_handler(no_city_state, lambda call: call.data == key_text.NO_CITY, state=FSMSignUp.city)
    dp.register_callback_query_handler(city_state, state=FSMSignUp.city)
    dp.register_message_handler(your_city_state, content_types=['text'], state=FSMSignUp.your_city)
    dp.register_callback_query_handler(
        no_school_state, lambda call: call.data == key_text.NO_SCHOOL, state=FSMSignUp.school)
    dp.register_callback_query_handler(school_state, state=FSMSignUp.school)
    dp.register_message_handler(your_school_state, content_types=['text'], state=FSMSignUp.your_school)
    dp.register_callback_query_handler(school_class_state, state=FSMSignUp.school_class)
    dp.register_callback_query_handler(gender_state, state=FSMSignUp.gender)
    dp.register_message_handler(full_name_state, content_types=['text'], state=FSMSignUp.full_name)
    dp.register_callback_query_handler(
        view_question_handler, lambda call: call.data == key_text.VIEW_QUESTION, state=None)
    dp.register_callback_query_handler(
        view_pagination_handler, lambda call: call.data.split('&')[0] == 'view_pag', state=None)
    dp.register_callback_query_handler(clear_handler, lambda call: call.data == key_text.CLEAR, state=None)
    dp.register_callback_query_handler(where_install_handler, lambda call: call.data == 'where_install', state=None)
