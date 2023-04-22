import asyncio
from typing import Union
from aiogram import Dispatcher, types
from aiogram.types import LabeledPrice
from handlers.echo import delete_message, active_user, total_answers, total_timeouts, total_send_requests, \
    total_confirm_requests, total_buy
from keyboards import key_text
from keyboards.keyboards import menu_keyboard, name_keyboard, oops_keyboard, how_crystal_keyboard, back_keyboard, \
    buy_crystal_keyboard, my_rate_keyboard, hidden_keyboard, request_keyboard, name_state_keyboard
from loader import logger, bot
from database.models import *
from settings.constants import QUESTION, MESSAGES, BUY_CRYSTAL_TITLE, BUY_CRYSTAL_DESC, MY_RATE, YOUR_RATE, NEW_RATE, \
    WANT_OPEN, AUTHOR_UNHIDDEN, YOUR_BALANCE
from datetime import datetime, timedelta
from settings.settings import PAY_TOKEN


async def rate_friends_handler(call: Union[types.CallbackQuery, types.Message]) -> None:
    """
    Хэндлер - обарабатывает нажатие на кнопку rate_friends. выводит пользователю вопрос для оценивания.
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await active_user(user, call.from_user.username)
            if isinstance(call, types.Message):
                await call.delete()
            if user.count == 12:
                await count_twelve(call, user)
            else:
                await send_question(call, user)
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def count_twelve(call: Union[types.CallbackQuery, types.Message], user) -> None:
    """
    Функция - обработки сообщений для заблокированных пользователей (по времени)
    :param user: ModelSelect
    :param call: Union[types.CallbackQuery, types.Message]
    :return: None
    """
    try:
        if user.created_at:
            continue_time = user.created_at + timedelta(hours=1)
            cur_time = continue_time.timestamp() - datetime.now().timestamp()
            minute = int(cur_time / 60) - 180
        else:
            await total_timeouts()
            user.created_at = datetime.now()
            user.save()
            minute = 60
        rate = Answers.select().where(Answers.asking == user.id, Answers.status == 'Новое').count()
        request = Answers.select().where(
            Answers.answering == user.id, Answers.hidden_answering == 'Запрос', Answers.hidden_asking != 'Запрос'
        ).count()
        crystal = Variables.get_or_none(Variables.variable == 'crystal').value
        oops = MESSAGES['oops']
        await delete_message(call.from_user.id)
        bot_message = await bot.send_message(
            call.from_user.id, YOUR_BALANCE.format(user.balance),
            reply_markup=await menu_keyboard(12, rate, request)
        )
        mess_id = str(bot_message.message_id)
        bot_message = await bot.send_photo(
            call.from_user.id, photo=open(f'media/{oops["photo"]}', 'rb'),
            caption=oops['text'].format(minute, crystal, user.balance),
            reply_markup=await oops_keyboard()
        )
        mess_id += f'&{bot_message.message_id}'
        DeleteMessage(chat_id=call.from_user.id, message_id=str(mess_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def send_question(call: Union[types.CallbackQuery, types.Message], user, another_question=False) -> None:
    """
    Функция - отправляет пользователю вопрос
    :param another_question: boolean
    :param call: Union[types.CallbackQuery, types.Message]
    :param user: ModelSelect
    :return: None
    """
    try:
        rate = Answers.select().where(Answers.asking == user.id, Answers.status == 'Новое').count()
        request = Answers.select().where(
            Answers.answering == user.id, Answers.hidden_answering == 'Запрос', Answers.hidden_asking != 'Запрос'
        ).count()
        if user.question_id:
            question = Questions.get_or_none(Questions.id == user.question_id)
        else:
            answers = Answers.select().where(Answers.answering == user.id)
            if len(answers) > 0:
                question_list = [answer.question for answer in answers]
                question = Questions.select().where(Questions.id.not_in(question_list)).order_by(fn.random()).get()
            else:
                question = Questions.select().order_by(fn.random()).get()
            user.question_id = question.id
            user.save()
        await delete_message(call.from_user.id)
        bot_message = await bot.send_message(
            call.from_user.id, YOUR_BALANCE.format(user.balance),
            reply_markup=await menu_keyboard(user.count + 1, rate, request)
        )
        mess_id = str(bot_message.message_id)
        bot_message = await bot.send_photo(
            call.from_user.id, photo=open(f'../vibe/media/{question.image}', 'rb'),
        )
        mess_id += f'&{bot_message.message_id}'
        if another_question:
            keyboard = await name_state_keyboard(user.id, question.id)
        else:
            keyboard = await name_keyboard(user.id, user.school, user.school_class, question.id)
        bot_message = await bot.send_message(
            call.from_user.id, QUESTION.format(user.count + 1, question.question),
            reply_markup=keyboard
        )
        mess_id += f'&{bot_message.message_id}'
        DeleteMessage(chat_id=call.from_user.id, message_id=str(mess_id)).save()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def rate_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - нажатия на кнопку имени пользователя и оценки.
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await total_answers()
            await active_user(user, call.from_user.username)
            text, asking_id, question_id = call.data.split('&')
            Answers(
                created_at=datetime.today(), question=int(question_id), asking=int(asking_id),
                hidden_asking='Скрытый', answering=user.id, hidden_answering='Скрытый', status='Новое'
            ).save()
            asking = Users.get_or_none(Users.id == int(asking_id))
            if asking:
                asking.balance += 1
                asking.save()
            user.count += 1
            user.answer_count += 1
            user.question_id = None
            user.save()
            if user.count == 12:
                await count_twelve(call, user)
            else:
                if asking:
                    if asking.count != 999:
                        try:
                            if user.gender == 'Парень':
                                gender = '👱‍♂️'
                            else:
                                gender = '👩'
                            bot_message = await bot.send_message(
                                asking.user_id, NEW_RATE.format(gender, user.school_class)
                            )
                            delete = DeleteMessage.get_or_none(DeleteMessage.chat_id == asking.user_id)
                            if delete:
                                delete.message_id += f'&{bot_message.message_id}'
                                delete.save()
                        except:
                            pass
                await send_question(call, user)
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def another_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку another. Выдаёт следующий вопрос
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await active_user(user, call.from_user.username)
            question_id = call.data.split('&')[1]
            Answers(
                created_at=datetime.today(), question=int(question_id), answering=user.id, status='Пропустил'
            ).save()
            user.question_id = None
            user.skip_count += 1
            user.save()
            await send_question(call, user, True)
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def change_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку change. Изменяет имена в вопросе.
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await active_user(user, call.from_user.username)
            await send_question(call, user)
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def how_crystal_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку how_crystal.
    Пользователь запрашивает информацию по получению кристаллов
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await active_user(user, call.from_user.username)
            how_crystal = MESSAGES['how_crystal']
            rate = Answers.select().where(Answers.asking == user.id, Answers.status == 'Новое').count()
            request = Answers.select().where(
                Answers.answering == user.id, Answers.hidden_answering == 'Запрос', Answers.hidden_asking != 'Запрос'
            ).count()
            await delete_message(call.from_user.id)
            bot_message = await bot.send_message(
                call.from_user.id, YOUR_BALANCE.format(user.balance),
                reply_markup=await menu_keyboard(12, rate, request)
            )
            mess_id = str(bot_message.message_id)
            bot_message = await bot.send_photo(
                call.from_user.id, photo=open(f'media/{how_crystal["photo"]}', 'rb'),
                caption=how_crystal['text'],
                reply_markup=await how_crystal_keyboard(call.from_user.id)
            )
            mess_id += f'&{bot_message.message_id}'
            DeleteMessage(chat_id=call.from_user.id, message_id=str(mess_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def continue_now_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку continue_now и buy_crystal.
    Или выдаёт новые вопросы, или предлагает купить кристаллы
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await active_user(user, call.from_user.username)
            crystal = Variables.get_or_none(Variables.variable == 'crystal')
            if user.balance < crystal.value or call.data == key_text.BUY_CRYSTAL:
                buy_crystal = MESSAGES['buy_crystal']
                rate = Answers.select().where(Answers.asking == user.id, Answers.status == 'Новое').count()
                request = Answers.select().where(
                    Answers.answering == user.id, Answers.hidden_answering == 'Запрос',
                    Answers.hidden_asking != 'Запрос'
                ).count()
                await delete_message(call.from_user.id)
                bot_message = await bot.send_message(
                    call.from_user.id, YOUR_BALANCE.format(user.balance),
                    reply_markup=await menu_keyboard(12, rate, request)
                )
                mess_id = str(bot_message.message_id)
                bot_message = await bot.send_photo(
                    call.from_user.id, photo=open(f'media/{buy_crystal["photo"]}', 'rb'),
                    caption=buy_crystal['text'].format(user.balance),
                    reply_markup=await buy_crystal_keyboard()
                )
                mess_id += f'&{bot_message.message_id}'
                DeleteMessage(chat_id=call.from_user.id, message_id=str(mess_id)).save()
            else:
                user.balance -= crystal.value
                user.count = 0
                user.created_at = None
                user.save()
                await rate_friends_handler(call)
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def refills_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие кнопки соглашения оплаты
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await active_user(user, call.from_user.username)
            refill_id = int(call.data.split('&')[1])
            refill = Refills.get_or_none(Refills.id == refill_id)
            if refill:
                amount = int(refill.price) * 100
                rate = Answers.select().where(Answers.asking == user.id, Answers.status == 'Новое').count()
                request = Answers.select().where(
                    Answers.answering == user.id, Answers.hidden_answering == 'Запрос',
                    Answers.hidden_asking != 'Запрос'
                ).count()
                await delete_message(call.from_user.id)
                bot_message = await bot.send_message(
                    call.from_user.id, YOUR_BALANCE.format(user.balance),
                    reply_markup=await menu_keyboard(12, rate, request)
                )
                mess_id = str(bot_message.message_id)
                bot_message = await bot.send_invoice(
                    chat_id=call.from_user.id,
                    title=BUY_CRYSTAL_TITLE,
                    description=BUY_CRYSTAL_DESC.format(refill.crystal, refill.price),
                    payload='235678945',
                    provider_token=PAY_TOKEN,
                    currency='RUB',
                    start_parameter='test',
                    prices=[LabeledPrice(label='Руб', amount=amount)]
                )
                mess_id += f'&{bot_message.message_id}'
                DeleteMessage(chat_id=call.from_user.id, message_id=str(mess_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def pre_checkout_handler(pre_checkout_query: types.PreCheckoutQuery) -> None:
    """
    Хэндлер - обрабатывает оплату кристаллов. Отправляет пользователю чек об оплате.
    :param pre_checkout_query: PreCheckoutQuery
    :return: None
    """
    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def process_pay_handler(message: types.Message) -> None:
    """
    Хэндлер - обрабатывает успешную оплату пользователя.
    :param message: Message
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == message.from_user.id)
        if user:
            await total_buy()
            await active_user(user, message.from_user.username)
            pay = message['successful_payment']['total_amount'] / 100
            refill = Refills.get_or_none(Refills.price == pay)
            if refill:
                user.balance += refill.crystal
                user.save()
            complete_buy = MESSAGES['complete_buy']
            rate = Answers.select().where(Answers.asking == user.id, Answers.status == 'Новое').count()
            request = Answers.select().where(
                Answers.answering == user.id, Answers.hidden_answering == 'Запрос', Answers.hidden_asking != 'Запрос'
            ).count()
            await delete_message(message.from_user.id)
            bot_message = await bot.send_message(
                message.from_user.id, YOUR_BALANCE.format(user.balance),
                reply_markup=await menu_keyboard(12, rate, request)
            )
            mess_id = str(bot_message.message_id)
            bot_message = await bot.send_photo(
                message.from_user.id, photo=open(f'media/{complete_buy["photo"]}', 'rb'),
                caption=complete_buy['text'].format(user.balance),
                reply_markup=await back_keyboard(key_text.BUY_CRYSTAL)
            )
            mess_id += f'&{bot_message.message_id}'
            DeleteMessage(chat_id=message.from_user.id, message_id=str(mess_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def my_rate_handler(message: Union[types.Message, types.CallbackQuery]) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку my_rate. Показывает пользователю, кто его оценил.
    :param message: Message
    :return: None
    """
    try:
        if isinstance(message, types.Message):
            await message.delete()
        user = Users.get_or_none(Users.user_id == message.from_user.id)
        if user:
            if user.count != 12:
                question = user.count + 1
            else:
                question = 12
            await active_user(user, message.from_user.username)
            answers = Answers.select().where(Answers.asking == user.id).order_by(Answers.id.asc())
            request = Answers.select().where(
                Answers.answering == user.id, Answers.hidden_answering == 'Запрос', Answers.hidden_asking != 'Запрос'
            ).count()
            if len(answers) > 0:
                count_new = Answers.select().where(Answers.asking == user.id, Answers.status == 'Новое').count()
                my_rate = MESSAGES['my_rate']
                if count_new == 0:
                    text = my_rate['text']
                else:
                    text = my_rate['text'] + MY_RATE.format(count_new)
                await delete_message(message.from_user.id)
                bot_message = await bot.send_message(
                    message.from_user.id, YOUR_BALANCE.format(user.balance),
                    reply_markup=await menu_keyboard(question, count_new, request)
                )
                mess_id = str(bot_message.message_id)
                bot_message = await bot.send_photo(
                    message.from_user.id, photo=open(f'media/{my_rate["photo"]}', 'rb'),
                    caption=text, reply_markup=await my_rate_keyboard(answers)
                )
                mess_id += f'&{bot_message.message_id}'
                DeleteMessage(chat_id=message.from_user.id, message_id=str(mess_id)).save()
            else:
                empty_rate = MESSAGES['empty_rate']
                await delete_message(message.from_user.id)
                bot_message = await bot.send_message(
                    message.from_user.id, YOUR_BALANCE.format(user.balance),
                    reply_markup=await menu_keyboard(question, 0, request)
                )
                mess_id = str(bot_message.message_id)
                bot_message = await bot.send_photo(
                    message.from_user.id, photo=open(f'media/{empty_rate["photo"]}', 'rb'),
                    caption=empty_rate['text'],
                )
                mess_id += f'&{bot_message.message_id}'
                DeleteMessage(chat_id=message.from_user.id, message_id=str(mess_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def one_rate_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на оценку (onerate)
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await active_user(user, call.from_user.username)
        answer_id = int(call.data.split('&')[1])
        answer = Answers.get_or_none(Answers.id == answer_id)
        if answer:
            if answer.status == 'Новое':
                answer.status = 'Просмотрен'
                answer.save()
            one_rate = MESSAGES['one_rate']
            if answer.answering.gender == 'Парень':
                emoji = '👱‍♂️'
            else:
                emoji = '👩'
            if user.count != 12:
                question = user.count + 1
            else:
                question = 12
            rate = Answers.select().where(Answers.asking == user.id, Answers.status == 'Новое').count()
            request = Answers.select().where(
                Answers.answering == user.id, Answers.hidden_answering == 'Запрос', Answers.hidden_asking != 'Запрос'
            ).count()
            await delete_message(call.from_user.id)
            bot_message = await bot.send_message(
                call.from_user.id, YOUR_BALANCE.format(answer.asking.balance),
                reply_markup=await menu_keyboard(question, rate, request)
            )
            mess_id = str(bot_message.message_id)
            bot_message = await bot.send_photo(
                call.from_user.id, photo=open(f'../vibe/media/{answer.question.image}', 'rb'),
                caption=one_rate['text'].format(emoji, answer.answering.school_class, answer.question.question),
                reply_markup=await hidden_keyboard(answer.hidden_answering, answer.id, answer.answering.full_name)
            )
            mess_id += f'&{bot_message.message_id}'
            DeleteMessage(chat_id=call.from_user.id, message_id=str(mess_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def find_who_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку find_who
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await total_send_requests()
            await active_user(user, call.from_user.username)
        answer_id = int(call.data.split('&')[1])
        answer = Answers.get_or_none(Answers.id == answer_id)
        if answer:
            answer.hidden_answering = 'Запрос'
            answer.save()
            if answer.answering.count != 999:
                try:
                    bot_message = await bot.send_message(answer.answering.user_id, WANT_OPEN)
                    delete = DeleteMessage.get_or_none(DeleteMessage.chat_id == answer.answering.user_id)
                    if delete:
                        delete.message_id += f'&{bot_message.message_id}'
                        delete.save()
                except:
                    pass
            find_who = MESSAGES['find_who']
            if user.count != 12:
                question = user.count + 1
            else:
                question = 12
            rate = Answers.select().where(Answers.asking == user.id, Answers.status == 'Новое').count()
            request = Answers.select().where(
                Answers.answering == user.id, Answers.hidden_answering == 'Запрос', Answers.hidden_asking != 'Запрос'
            ).count()
            await delete_message(call.from_user.id)
            bot_message = await bot.send_message(
                call.from_user.id, YOUR_BALANCE.format(answer.asking.balance),
                reply_markup=await menu_keyboard(question, rate, request)
            )
            mess_id = str(bot_message.message_id)
            bot_message = await bot.send_photo(
                call.from_user.id, photo=open(f'media/{find_who["photo"]}', 'rb'),
                caption=find_who['text'], reply_markup=await back_keyboard(f'onerate&{answer_id}')
            )
            mess_id += f'&{bot_message.message_id}'
            DeleteMessage(chat_id=call.from_user.id, message_id=str(mess_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def request_handler(message: Union[types.Message, types.CallbackQuery]) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопку request. Выводит пользователю запросы на раскрытие.
    :param message: Union[types.Message, types.CallbackQuery]
    :return: None
    """
    try:
        if isinstance(message, types.Message):
            await message.delete()
        user = Users.get_or_none(Users.user_id == message.from_user.id)
        if user:
            if user.count != 12:
                question = user.count + 1
            else:
                question = 12
            rate = Answers.select().where(Answers.asking == user.id, Answers.status == 'Новое').count()
            await active_user(user, message.from_user.username)
            answers = Answers.select().where(
                Answers.answering == user.id, Answers.hidden_answering == 'Запрос', Answers.hidden_asking != 'Запрос'
            ).order_by(Answers.id.desc())
            if len(answers) > 0:
                await delete_message(message.from_user.id)
                bot_message = await bot.send_message(
                    message.from_user.id, YOUR_BALANCE.format(user.balance),
                    reply_markup=await menu_keyboard(question, rate, len(answers))
                )
                mess_id = str(bot_message.message_id)
                bot_message = await bot.send_photo(
                    message.from_user.id, photo=open(f'../vibe/media/{answers[0].question.image}', 'rb'),
                )
                mess_id += f'&{bot_message.message_id}'
                bot_message = await bot.send_message(
                    message.from_user.id, YOUR_RATE.format(answers[0].asking.full_name, answers[0].question.question),
                    reply_markup=await request_keyboard(1, len(answers), answers[0].id)
                )
                mess_id += f'&{bot_message.message_id}'
                DeleteMessage(chat_id=message.from_user.id, message_id=str(mess_id)).save()
            else:
                empty_request = MESSAGES['empty_request']
                await delete_message(message.from_user.id)
                bot_message = await bot.send_message(
                    message.from_user.id, YOUR_BALANCE.format(user.balance),
                    reply_markup=await menu_keyboard(question, rate, 0)
                )
                mess_id = str(bot_message.message_id)
                bot_message = await bot.send_photo(
                    message.from_user.id, photo=open(f'media/{empty_request["photo"]}', 'rb'),
                    caption=empty_request['text']
                )
                mess_id += f'&{bot_message.message_id}'
                DeleteMessage(chat_id=message.from_user.id, message_id=str(mess_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def pagination_request_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает пагинацию запросов на раскрытие
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            if user.count != 12:
                question = user.count + 1
            else:
                question = 12
            rate = Answers.select().where(Answers.asking == user.id, Answers.status == 'Новое').count()
            await active_user(user, call.from_user.username)
            num_page = int(call.data.split('&')[1])
            answers = Answers.select().where(
                Answers.answering == user.id, Answers.hidden_answering == 'Запрос', Answers.hidden_asking != 'Запрос'
            ).order_by(Answers.id.desc())
            if len(answers) > 0:
                await delete_message(call.from_user.id)
                bot_message = await bot.send_message(
                    call.from_user.id, YOUR_BALANCE.format(user.balance),
                    reply_markup=await menu_keyboard(question, rate, len(answers))
                )
                mess_id = str(bot_message.message_id)
                bot_message = await bot.send_photo(
                    call.from_user.id, photo=open(f'../vibe/media/{answers[num_page].question.image}', 'rb')
                )
                mess_id += f'&{bot_message.message_id}'
                bot_message = await bot.send_message(
                    call.from_user.id,
                    YOUR_RATE.format(answers[num_page].asking.full_name, answers[num_page].question.question),
                    reply_markup=await request_keyboard(num_page + 1, len(answers), answers[num_page].id)
                )
                mess_id += f'&{bot_message.message_id}'
                DeleteMessage(chat_id=call.from_user.id, message_id=str(mess_id)).save()
            else:
                empty_request = MESSAGES['empty_request']
                bot_message = await bot.send_message(
                    call.from_user.id, YOUR_BALANCE.format(user.balance),
                    reply_markup=await menu_keyboard(question, rate, 0)
                )
                mess_id = str(bot_message.message_id)
                await delete_message(call.from_user.id)
                bot_message = await bot.send_photo(
                    call.from_user.id, photo=open(f'media/{empty_request["photo"]}', 'rb'),
                    caption=empty_request['text']
                )
                mess_id += f'&{bot_message.message_id}'
                DeleteMessage(chat_id=call.from_user.id, message_id=str(mess_id)).save()
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def reveal_reject_handler(call: types.CallbackQuery) -> None:
    """
    Хэндлер - обрабатывает нажатие на кнопки Раскрыть себя и Отклонить
    :param call: CallbackQuery
    :return: None
    """
    try:
        user = Users.get_or_none(Users.user_id == call.from_user.id)
        if user:
            await active_user(user, call.from_user.username)
            key, answer_id = call.data.split('&')
            answer = Answers.get_or_none(Answers.id == int(answer_id))
            if answer:
                if key == 'reveal':
                    await total_confirm_requests()
                    answer.hidden_answering = 'Раскрытый'
                    if answer.asking.count != 999:
                        try:
                            bot_message = await bot.send_message(
                                answer.asking.user_id, AUTHOR_UNHIDDEN.format(
                                    answer.question.question, answer.answering.full_name
                                )
                            )
                            delete = DeleteMessage.get_or_none(DeleteMessage.chat_id == answer.asking.user_id)
                            if delete:
                                delete.message_id += f'&{bot_message.message_id}'
                                delete.save()
                        except:
                            pass
                elif key == 'reject':
                    answer.hidden_asking = 'Запрос'
                answer.save()
            await request_handler(call)
        await asyncio.sleep(0.5)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_rates_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(
        rate_friends_handler, lambda call: call.data == key_text.RATE_FRIENDS, state=None)
    dp.register_message_handler(rate_friends_handler, commands=['ratefriends'], state=None)
    dp.register_message_handler(
        rate_friends_handler, lambda message: message.text.split('  ')[0] == key_text.RATE_FRIENDS, state=None)
    dp.register_callback_query_handler(rate_handler, lambda call: call.data.split('&')[0] == 'rates', state=None)
    dp.register_callback_query_handler(another_handler, lambda call: call.data.split('&')[0] == 'another', state=None)
    dp.register_callback_query_handler(change_handler, lambda call: call.data.split('&')[0] == 'change', state=None)
    dp.register_callback_query_handler(rate_friends_handler, lambda call: call.data == key_text.BACK_OOPS, state=None)
    dp.register_callback_query_handler(
        continue_now_handler, lambda call: call.data in [key_text.CONTINUE_NOW, key_text.BUY_CRYSTAL], state=None)
    dp.register_callback_query_handler(how_crystal_handler, lambda call: call.data == key_text.HOW_CRYSTAL, state=None)
    dp.register_callback_query_handler(how_crystal_handler, lambda call: call.data == key_text.BACK_CRYSTAL, state=None)
    dp.register_callback_query_handler(refills_handler, lambda call: call.data.split('&')[0] == 'refill', state=None)
    dp.register_pre_checkout_query_handler(pre_checkout_handler, lambda query: True, state=None)
    dp.register_message_handler(process_pay_handler, content_types=['successful_payment'], state=None)
    dp.register_message_handler(
        my_rate_handler, lambda message: message.text.split('  ')[0] == key_text.MY_RATE, state=None)
    dp.register_message_handler(my_rate_handler, commands=['myrate'], state=None)
    dp.register_callback_query_handler(my_rate_handler, lambda call: call.data == key_text.MY_RATE, state=None)
    dp.register_callback_query_handler(one_rate_handler, lambda call: call.data.split('&')[0] == 'onerate', state=None)
    dp.register_callback_query_handler(find_who_handler, lambda call: call.data.split('&')[0] == 'findwho', state=None)
    dp.register_message_handler(
        request_handler, lambda message: message.text.split('  ')[0] == key_text.REQUEST, state=None)
    dp.register_message_handler(request_handler, commands=['requests'], state=None)
    dp.register_callback_query_handler(
        pagination_request_handler, lambda call: call.data.split('&')[0] == 'request', state=None)
    dp.register_callback_query_handler(
        reveal_reject_handler, lambda call: call.data.split('&')[0] in ['reveal', 'reject'], state=None)
