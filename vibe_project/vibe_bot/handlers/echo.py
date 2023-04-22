"""
Файл - содержит хэндлер для отлова сообщений вне сценария
"""
from datetime import date, datetime
from typing import Union
from aiogram import Dispatcher, types
from loader import logger, bot
from database.models import *


async def echo_handler(message: types.Message) -> None:
    """
    Хэндлер - оповещает бота о некорректной команде (Эхо)
    :param message: Message
    :return: None
    """
    try:
        await message.delete()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def delete_message(user_id: int) -> None:
    """
    Функция - обрабатывает удаление сообщений
    :param user_id: int
    :return: None
    """
    try:
        mess = DeleteMessage.get_or_none(DeleteMessage.chat_id == user_id)
        if mess:
            if '&' in mess.message_id:
                mes_ids = mess.message_id.split('&')
                for elem in mes_ids:
                    try:
                        await bot.delete_message(chat_id=mess.chat_id, message_id=int(elem))
                    except Exception as ex:
                        print(ex)
            else:
                try:
                    await bot.delete_message(chat_id=mess.chat_id, message_id=int(mess.message_id))
                except Exception as ex:
                    print(ex)
            try:
                mess.delete_instance()
            except Exception as ex:
                print(ex)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def active_user(user, username: Union[str, None]) -> None:
    """
    Функция - проверяет, активный пользователь сегодня и записывает его.
    :param username: str
    :param user: ModelSelect
    :return: None
    """
    try:
        if user.username is None:
            user.username = username
        user.active_at = datetime.today()
        user.save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def total_answers() -> None:
    """
    Функция - прибавляет ответы в квизах за день
    :return: None
    """
    try:
        statistics = Statistics.get_or_none(Statistics.created_at == date.today())
        if statistics:
            statistics.answers += 1
            statistics.save()
        else:
            Statistics(created_at=date.today(), answers=1).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def total_timeouts() -> None:
    """
    Функция - прибавляет ожидание 12 вопросов
    :return: None
    """
    try:
        statistics = Statistics.get_or_none(Statistics.created_at == date.today())
        if statistics:
            statistics.timeouts += 1
            statistics.save()
        else:
            Statistics(created_at=date.today(), timeouts=1).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def total_send_requests() -> None:
    """
    Функция - считает количество отправленных запросов на раскрытие
    :return: None
    """
    try:
        statistics = Statistics.get_or_none(Statistics.created_at == date.today())
        if statistics:
            statistics.send_requests += 1
            statistics.save()
        else:
            Statistics(created_at=date.today(), send_requests=1).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def total_confirm_requests() -> None:
    """
    Функция - считает количество подтвержденных запросов на раскрытие
    :return: None
    """
    try:
        statistics = Statistics.get_or_none(Statistics.created_at == date.today())
        if statistics:
            statistics.confirm_requests += 1
            statistics.save()
        else:
            Statistics(created_at=date.today(), confirm_requests=1).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def total_signup_invite() -> None:
    """
    Функция - считает количество регистраций по инвайт-ссылкам
    :return: None
    """
    try:
        statistics = Statistics.get_or_none(Statistics.created_at == date.today())
        if statistics:
            statistics.signup_invite += 1
            statistics.save()
        else:
            Statistics(created_at=date.today(), signup_invite=1).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def total_buy() -> None:
    """
    Функция - считает количество покупок кристаллов
    :return: None
    """
    try:
        statistics = Statistics.get_or_none(Statistics.created_at == date.today())
        if statistics:
            statistics.buy += 1
            statistics.save()
        else:
            Statistics(created_at=date.today(), buy=1).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def set_user_commands(user_id):
    await bot.set_my_commands(
        [
            types.BotCommand("start", "Старт"),
            types.BotCommand("ratefriends", "🎲 Оценивать друзей"),
            types.BotCommand('myrate', '📫 Меня оценили'),
            types.BotCommand("requests", "🥷 Запросы"),
            types.BotCommand("change_name", "Изменить имя"),
            types.BotCommand("write_support", "Написать в поддержу"),
        ],
        scope=types.BotCommandScopeChat(chat_id=user_id)
    )


def register_echo_handlers(dp: Dispatcher) -> None:
    """
    Функция - регистрирует все хэндлеры файла echo.py
    :param dp: Dispatcher
    :return: None
    """
    dp.register_message_handler(echo_handler, state='*')
