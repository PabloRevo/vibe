import os
import re
import csv
from datetime import date
from aiogram import Dispatcher, types
from handlers.echo import delete_message
from keyboards.keyboards import rate_friends_keyboard
from loader import logger, bot
from database.models import *
from settings.constants import ADMIN_NAME, ADMIN_START, MESSAGES, TOTALS, EMPTY_TOTALS, MOSCOW, SPB, EKB, NSB, SCH, \
    HEADER


async def change_name_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает смену имени пользователя
    :param message: Message
    :return: None
    """
    try:
        await message.delete()
        administrator = Administrators.get_or_none(Administrators.user_id == message.from_user.id)
        if administrator:
            text = message.text.replace('/changename ', '')
            user_id = re.findall(r'\b\d+\b', text)
            if user_id:
                full_name = re.findall(r'\b\D+\b', text)[0][1:]
                Users.update({Users.full_name: full_name}).where(Users.user_id == int(user_id[0])).execute()
                bot_message = await bot.send_message(message.from_user.id, ADMIN_NAME)
                delete = DeleteMessage.get_or_none(DeleteMessage.chat_id == message.from_user.id)
                if delete:
                    delete.message_id += f'&{bot_message.message_id}'
                    delete.save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def change_start_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает смену переменной количества пользователей из одного класса
    :param message: Message
    :return: None
    """
    try:
        await message.delete()
        administrator = Administrators.get_or_none(Administrators.user_id == message.from_user.id)
        if administrator:
            value = message.text.replace('/changestart ', '')
            Variables.update({Variables.value: int(value)}).where(Variables.variable == 'quantity').execute()
            bot_message = await bot.send_message(message.from_user.id, ADMIN_START)
            delete = DeleteMessage.get_or_none(DeleteMessage.chat_id == message.from_user.id)
            if delete:
                delete.message_id += f'&{bot_message.message_id}'
                delete.save()
            users = Users.select().where(Users.count == 999)
            if len(users) > 0:
                await_complete = MESSAGES['await_complete']
                for user in users:
                    count = Users.select().where(
                        Users.school == user.school, Users.school_class == user.school_class).count()
                    if count >= int(value):
                        await delete_message(user.user_id)
                        bot_message = await bot.send_photo(
                            user.user_id, photo=open(f'media/{await_complete["photo"]}', 'rb'),
                            caption=await_complete['text'].format(value),
                            reply_markup=await rate_friends_keyboard()
                        )
                        DeleteMessage(chat_id=user.user_id, message_id=str(bot_message.message_id)).save()
                        user.count = 0
                        user.save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def total_handler(message: types.Message) -> None:
    """
    Хэндлер - выгружает итоговый отчет общий
    :param message: Message
    :return: None
    """
    try:
        await message.delete()
        administrator = Administrators.get_or_none(Administrators.user_id == message.from_user.id)
        if administrator:
            last_date = date.today()
            statistics = Statistics.get_or_none(Statistics.created_at == last_date)
            if statistics:
                statistics.is_city = SignUp.select().where(
                    SignUp.change_at == last_date, SignUp.is_city == False).count()
                statistics.is_school = SignUp.select().where(
                    SignUp.change_at == last_date, SignUp.is_school == False).count()
                statistics.is_class = SignUp.select().where(
                    SignUp.change_at == last_date, SignUp.is_class == False).count()
                statistics.is_gender = SignUp.select().where(
                    SignUp.change_at == last_date, SignUp.is_gender == False).count()
                statistics.is_name = SignUp.select().where(
                    SignUp.change_at == last_date, SignUp.is_name == False).count()
                statistics.save()
            stats = Statistics.select()
            if len(stats) > 0:
                data = [TOTALS]
                for stat in stats:
                    count = Users.select().where(
                        (Users.active_at.day == stat.created_at.day) & (Users.active_at.month == stat.created_at.month) & (Users.active_at.year == stat.created_at.year)
                    ).count()
                    no_signup = stat.is_city + stat.is_school + stat.is_class + stat.is_gender + stat.is_name
                    data.append([
                        stat.created_at, stat.new_user, stat.moscow, stat.spb, stat.sochi, stat.ekb, stat.nsb,
                        no_signup, stat.is_city, stat.is_school, stat.is_class, stat.is_gender, stat.is_name, count,
                        stat.answers, stat.timeouts, stat.send_requests, stat.confirm_requests, stat.signup_invite,
                        stat.buy
                    ])
                file_path = f'total_{date.today()}.csv'
                with open(file_path, 'w') as f:
                    writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
                    for row in data:
                        writer.writerow(row)
                await bot.send_document(administrator.user_id, document=open(file_path, 'rb'))
                os.remove(file_path)
            else:
                await bot.send_message(administrator.user_id, EMPTY_TOTALS)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def city_statistics(message: types.Message) -> None:
    """
    Хэндлер - выгружает статистику по городам
    :param message: Message
    :return: None
    """
    try:
        await message.delete()
        administrator = Administrators.get_or_none(Administrators.user_id == message.from_user.id)
        if administrator:
            if message.text == '/msk':
                city = 'Москва'
                con = MOSCOW
            elif message.text == '/spb':
                city = 'Санкт-Петербург'
                con = SPB
            elif message.text == '/ekb':
                city = 'Екатеринбург'
                con = EKB
            elif message.text == '/nsk':
                city = 'Новосибирск'
                con = NSB
            elif message.text == '/sch':
                city = 'Сочи'
                con = SCH
            city = Cities.get_or_none(Cities.title == city)
            if city:
                school_cls = SchoolClass.select().where(SchoolClass.city == city.id).order_by(SchoolClass.id.asc())
                if len(school_cls) > 0:
                    header = HEADER.format(con[0], con[1], con[2], con[3], con[4], con[5], con[6]).split('&')
                    data = [header]
                    index = 1
                    templ = []
                    for school in school_cls:
                        if index == 1:
                            templ.append(school.created_at)
                            count = Users.select().where(
                                Users.signup_at == school.created_at, Users.city == city.id).count()
                            templ.append(count)
                        total_signup = school.class11 + school.class10 + school.class9 + school.class8 + school.class7 + school.class6 + school.class5
                        templ.extend([
                            total_signup, school.class11, school.class10, school.class9,
                            school.class8, school.class7, school.class6, school.class5
                        ])
                        if index == 6:
                            index = 0
                            data.append(templ)
                            templ = []
                        index += 1
                    file_path = f'{message.text[1:]}_{date.today()}.csv'
                    with open(file_path, 'w') as f:
                        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
                        for row in data:
                            writer.writerow(row)
                    await bot.send_document(administrator.user_id, document=open(file_path, 'rb'))
                    os.remove(file_path)
                else:
                    await bot.send_message(administrator.user_id, EMPTY_TOTALS)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(change_name_handler, lambda message: message.text.startswith('/changename'), state=None)
    dp.register_message_handler(
        change_start_handler, lambda message: message.text.startswith('/changestart'), state=None)
    dp.register_message_handler(total_handler, lambda message: message.text == '/total', state=None)
    dp.register_message_handler(
        city_statistics, lambda message: message.text in ['/msk', '/spb', '/ekb', '/nsk', '/sch'], state=None)
