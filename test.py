from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет!")


if __name__ == '__main__':
    executor.start_polling(dp)
