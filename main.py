import asyncio
import configparser
from pathlib import Path
from aiogram import *
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InputFile, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import CantParseEntities

from utils.IsAdmin import *
from utils.functions import *
from utils.sql_api import *

# конфиг для всего
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
# Логирование, аиограм бот, хранилище
storage = MemoryStorage()
bot = Bot(token=config['SETTINGS']['TOKEN'])
dp = Dispatcher(bot, storage=MemoryStorage())

# База данных
bd = sqlite3.connect('GoldyTeam-custombot-database.db')
cur = bd.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(user_id INTEGER);""")
cur.execute("""CREATE TABLE IF NOT EXISTS settings_start(
start_mode INTEGER

);""")
bd.commit()
print(f"База данных подключена {bd}")

# SPAM MODULE
class dialog(StatesGroup):
    here_mail_text = State()

# PHOTO
ftype = config['PHOTO']['file_type']
my_file = Path(f"photo/photo.{ftype}")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    config.read("config.ini", encoding="utf-8")
    cur = bd.cursor()
    result = cur.fetchone()


    if message.from_user.id == config['ADMIN']['admin_id']:
        pass
    else:
        if result is None:
            cur = bd.cursor()
            cur.execute(f'''SELECT * FROM users WHERE (user_id="{message.from_user.id}")''')
            entry = cur.fetchone()
            if entry is None:
                cur.execute(f'''INSERT INTO users VALUES ('{message.from_user.id}')''')
                bd.commit()
        else:
            await message.answer('None')


    if my_file.exists():
        photo = InputFile(f"photo/photo.{ftype}")
        await bot.send_photo(message.chat.id, photo=photo)
        await asyncio.sleep(0.1)

    cur.execute("SELECT start_mode FROM settings_start")
    result = cur.fetchall()

    if result == [('text',)]:
        await message.answer(config['SETTINGS']['start_text'])

    if result == [('web',)]:
        # INLINE WEB
        weblink = InlineKeyboardButton(text=config['SETTINGS']['web_button_name'],web_app=types.WebAppInfo(url=config["SETTINGS"]["web_url"]))
        webready = InlineKeyboardMarkup().add(weblink)
        await message.answer(config['SETTINGS']['start_text'], reply_markup=webready)


#Панель Администратора
@dp.message_handler(IsAdmin(), content_types=['text'], text='/admin')
async def admin_menu(message: types.Message):
    adm_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    adm_keyboard.add(types.KeyboardButton(text="📢 Рассылка")), adm_keyboard.add(types.KeyboardButton(text="👥 Статистика"))
    adm_keyboard.add(types.KeyboardButton(text="Настройка кнопок"),)

    await message.answer('👤Меню Администратора', reply_markup=adm_keyboard)

@dp.message_handler(IsAdmin(), text="Настройка кнопок")
async def keyboard_settings(message: types.Message):
    button_settings = [
        [
            types.KeyboardButton(text="🛠 Настройка Start"),
            #types.KeyboardButton(text="Настройка Buttons"),
        ],
    ]

    button_settings_keyboard = types.ReplyKeyboardMarkup(keyboard=button_settings, resize_keyboard=True, one_time_keyboard=True)

    await message.answer("Меню настройки кнопок", reply_markup=button_settings_keyboard)



@dp.message_handler(IsAdmin(), text="🛠 Настройка Start")
async def keyboard_settings(message: types.Message):
    button_start = [
        [
            types.KeyboardButton(text="Текстовый"),
            types.KeyboardButton(text="Веб-переход"),
        ],
    ]

    button_start_keyboard = types.ReplyKeyboardMarkup(keyboard=button_start, resize_keyboard=True, one_time_keyboard=True)

    cur.execute("SELECT start_mode FROM settings_start")
    result = str(cur.fetchall())

    rem = result.replace(',', '')
    rem1 = rem.replace('[', '')
    rem2 = rem1.replace(']', '')
    rem3 = rem2.replace(')', '')
    rem4 = rem3.replace('(', '')

    await message.answer(f"Меню настройки режима работы /start \n Текущий: {rem4}", reply_markup=button_start_keyboard)

@dp.message_handler(IsAdmin(), text="Текстовый")
async def start_standart(message: types.Message):
    cursor = bd.cursor()
    cur.execute("""DELETE FROM settings_start;""")
    cur.execute("SELECT start_mode FROM settings_start")
    if cur.fetchone() is None:
        cur.execute(f'''INSERT INTO settings_start VALUES ('text')''')
        bd.commit()
        await message.answer("Режим работы [Текстовый] установлен")
    else:
        pass


@dp.message_handler(IsAdmin(), text="Веб-переход")
async def start_web(message: types.Message):
    cursor = bd.cursor()
    cur.execute("""DELETE FROM settings_start;""")
    cur.execute("SELECT start_mode FROM settings_start")
    if cur.fetchone() is None:
        cur.execute(f'''INSERT INTO settings_start VALUES ('web')''')
        bd.commit()
        await message.answer("Режим работы [Веб-Переход] установлен")
    else:
        pass


# Статистика

@dp.message_handler(IsAdmin(),text='👥 Статистика')
async def hfandler(message: types.Message):
    getuser = get_all_usersx()
    await message.answer(
    f"👤 Юзеров за Всё время: {len(getuser)}\n")

# Рассылка
mail_confirm_inl = InlineKeyboardMarkup(
).add(
    InlineKeyboardButton("✅ Отправить", callback_data="confirm_mail:yes"),
    InlineKeyboardButton("❌ Отменить", callback_data="confirm_mail:not")
)

@dp.message_handler(IsAdmin(), text="📢 Рассылка", state="*")
async def functions_mail(message: types.Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_mail_text")
    await message.answer("📢 Введите текст для рассылки пользователям")

# Принятие текста для рассылки
@dp.message_handler(IsAdmin(), state="here_mail_text")
async def functions_mail_get(message: types.Message, state: FSMContext):
    await state.update_data(here_mail_text=str(message.text))
    get_users = get_all_usersx()

    try:
        cache_msg = await message.answer(message.text)
        await cache_msg.delete()

        await state.set_state("here_mail_confirm")
        await message.answer(
            f"📢 Отправить {len(get_users)} Юзерам сообщение?\n"
            f"{message.text}",
            reply_markup=mail_confirm_inl,
            disable_web_page_preview=True
        )
    except CantParseEntities:
        await message.answer("❌ Ошибка синтаксиса HTML.\n"
                             "📢 Введите текст для рассылки пользователям.\n")

# Подтверждение отправки рассылки
@dp.callback_query_handler(IsAdmin(), text_startswith="confirm_mail", state="here_mail_confirm")
async def functions_mail_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]

    send_message = (await state.get_data())['here_mail_text']
    await state.finish()
    get_users = get_all_usersx()

    if get_action == "yes":
        await call.message.edit_text(f"📢 Рассылка началась... (0/{len(get_users)})")
        asyncio.create_task(functions_mail_make(send_message, call))
    else:
        await call.message.edit_text("📢 Вы отменили отправку рассылки ✅")



webras = InlineKeyboardButton(text="123",web_app=types.WebAppInfo(url="url"))
webreadyras = InlineKeyboardMarkup().add(webras)

# Сама отправка рассылки
async def functions_mail_make(message, call: CallbackQuery):
    receive_users, block_users, how_users = 0, 0, 0
    get_users = get_all_usersx()
    get_time = get_unix()
    for user in get_users:
        try:
            await bot.send_message(user['user_id'], message, disable_web_page_preview=True)

            print(f"Рассылка: Сообщение успешно отправлено {receive_users}")
            receive_users += 1
        except:
            print(f"Рассылка: Сообщение успешно отправлено {block_users}")
            block_users += 1


        how_users += 1

        if how_users % 10 == 0:
                await call.message.edit_text(f"<b>📢 Рассылка началась... ({how_users}/{len(get_users)})</b>")

    await asyncio.sleep(0.08)
    await call.message.edit_text(
    f"📢 Рассылка была завершена за {get_unix() - get_time} секунд\n"
    f"👤 Всего пользователей: {len(get_users)}\n"
    f"✅ Пользователей получило сообщение: {receive_users}\n"
    f"❌ Пользователей не получило сообщение: {block_users}")


# Выполнение функции после запуска бота
async def on_startup(dp: Dispatcher):
    await asyncio.sleep(1)
    print('')
    print('#####################################################################################')
    print('/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/')
    print('Создатель скрипта: @G_Admin100 \nКанал с обновлениями - https://t.me/+mNSybxI9Wdg3OWZi \nСкрипт написан для Goldy Team 2.0 ')
    print('/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/')
    print('######################################################################################')
    print('')
    await asyncio.sleep(1)
    await dp.bot.send_message(config["ADMIN"]["admin_id"],"Бот успешно запущен✅ \nСоздатель скрипта: @G_Admin100 \nКанал с обновлениями - https://t.me/+mNSybxI9Wdg3OWZi \nСкрипт написан для Goldy Team 2.0 \nПанель Управления /admin")

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)