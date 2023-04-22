import asyncio
import re
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from database.models import *
from database.states import FSMChangeName, FSMWriteSupport
from handlers.echo import active_user, delete_message
from keyboards.keyboards import menu_keyboard
from loader import logger, bot
from settings.constants import MESSAGES, SUPPORT


async def change_name_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает команду смены имени пользователя
    :param message: Message
    :return: None
    """
    try:
        await message.delete()
        user = Users.get_or_none(Users.user_id == message.from_user.id)
        if user:
            await FSMChangeName.name.set()
            await active_user(user, message.from_user.username)
            change_name = MESSAGES['change_name']
            await delete_message(message.from_user.id)
            bot_message = await bot.send_photo(
                message.from_user.id, photo=open(f'media/{change_name["photo"]}', 'rb'),
                caption=change_name['text'].format(user.full_name),
            )
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def change_name_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает смену имени пользователя
    :param state: FSMContext
    :param message: Message
    :return: None
    """
    try:
        await message.delete()
        await delete_message(message.from_user.id)
        if [message.text] == re.findall(r'[а-яА-ЯёЁ]+[ ][а-яА-ЯёЁ]+', message.text):
            user = Users.get_or_none(Users.user_id == message.from_user.id)
            if user:
                user.full_name = message.text
                user.save()
                rate = Answers.select().where(Answers.asking == user.id, Answers.status == 'Новое').count()
                request = Answers.select().where(
                    Answers.answering == user.id, Answers.hidden_answering == 'Запрос',
                    Answers.hidden_asking != 'Запрос'
                ).count()
                complete_name = MESSAGES['complete_name']
                bot_message = await bot.send_photo(
                    message.from_user.id, photo=open(f'media/{complete_name["photo"]}', 'rb'),
                    caption=complete_name['text'].format(user.full_name),
                    reply_markup=await menu_keyboard(user.count + 1, rate, request)
                )
                await state.finish()
        else:
            no_complete_name = MESSAGES['no_complete_name']
            bot_message = await bot.send_photo(
                message.from_user.id, photo=open(f'media/{no_complete_name["photo"]}', 'rb'),
                caption=no_complete_name['text'],
            )
        DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def write_support_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку написать в поддержку
    :param message: Message
    :return: None
    """
    try:
        await message.delete()
        user = Users.get_or_none(Users.user_id == message.from_user.id)
        if user:
            await FSMWriteSupport.support.set()
            await active_user(user, message.from_user.username)
            write_support = MESSAGES['write_support']
            await delete_message(message.from_user.id)
            bot_message = await bot.send_photo(
                message.from_user.id, photo=open(f'media/{write_support["photo"]}', 'rb'),
                caption=write_support['text'].format(user.full_name),
            )
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def write_support_state(message: types.Message, state: FSMContext) -> None:
    """
    Хэндлер - обрабатывает сообщение для отправки
    :param state: FSMContext
    :param message: Message
    :return: None
    """
    try:
        await message.delete()
        await delete_message(message.from_user.id)
        user = Users.get_or_none(Users.user_id == message.from_user.id)
        if user:
            complete_support = MESSAGES['complete_support']
            rate = Answers.select().where(Answers.asking == user.id, Answers.status == 'Новое').count()
            request = Answers.select().where(
                Answers.answering == user.id, Answers.hidden_answering == 'Запрос',
                Answers.hidden_asking != 'Запрос'
            ).count()
            bot_message = await bot.send_photo(
                message.from_user.id, photo=open(f'media/{complete_support["photo"]}', 'rb'),
                caption=complete_support['text'],
                reply_markup=await menu_keyboard(user.count + 1, rate, request)
            )
            await state.finish()
            DeleteMessage(chat_id=message.from_user.id, message_id=str(bot_message.message_id)).save()
            administrator = Administrators.get_or_none()
            if administrator:
                bot_message = await bot.send_message(
                    administrator.user_id, SUPPORT.format(user.user_id, message.text)
                )
                delete = DeleteMessage.get_or_none(DeleteMessage.chat_id == administrator.user_id)
                if delete:
                    delete.message_id += f'&{str(bot_message.message_id)}'
                    delete.save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_support_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(change_name_handler, commands=['change_name'], state='*')
    dp.register_message_handler(change_name_state, content_types=['text'], state=FSMChangeName.name)
    dp.register_message_handler(write_support_handler, commands=['write_support'], state='*')
    dp.register_message_handler(write_support_state, content_types=['text'], state=FSMWriteSupport.support)
