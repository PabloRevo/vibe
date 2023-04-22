"""Файл для запуска бота. Содержит в себе все регистраторы приложения"""
import asyncio
from aiogram import types, Dispatcher
from loader import dp
from aiogram.utils import executor
from handlers import start, echo, timer, rates, admin, support


async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Старт"),
        ]
    )


start.register_start_handlers(dp)
rates.register_rates_handlers(dp)
admin.register_admin_handlers(dp)
support.register_support_handlers(dp)
echo.register_echo_handlers(dp)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(timer.timer_func(40))
    executor.start_polling(dp, on_startup=set_default_commands, skip_updates=True)
