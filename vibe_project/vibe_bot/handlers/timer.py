import asyncio
from datetime import datetime, timedelta
from database.models import *
from loader import logger, bot
from settings.constants import ONE_HOUR


async def timer_func(sleep_for: int) -> None:
    """
    Функция работающая в отдельном потоке. Разблокирует и оповещает пользователя, после 1 часа.
    :param sleep_for: int
    :return: None
    """
    try:
        while True:
            await asyncio.sleep(sleep_for)
            users = Users.select().where(Users.created_at is not None, Users.count == 12)
            if len(users) > 0:
                for user in users:
                    cur_time = datetime.today().time()
                    cur_date = datetime.today().date()
                    my_date = user.created_at + timedelta(hours=1)
                    if my_date.time().hour == cur_time.hour and my_date.time().minute == cur_time.minute and my_date.date() == cur_date:
                        user.count = 0
                        user.created_at = None
                        user.save()
                        try:
                            bot_message = await bot.send_message(user.user_id, ONE_HOUR)
                            delete = DeleteMessage.get_or_none(DeleteMessage.chat_id == user.user_id)
                            if delete:
                                delete.message_id += f'&{bot_message.message_id}'
                                delete.save()
                        except:
                            pass
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)
