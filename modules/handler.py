from aiogram import types, Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from modules import config, keyboard, logger
import sqlite3
from aiogram.dispatcher.filters.state import State, StatesGroup

db = sqlite3.connect('shop.db')
cursor = db.cursor()
storage = MemoryStorage()
bot = Bot(token=config.botkey, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
data = cursor.execute('SELECT * FROM shop').fetchall()
global owners_id
owners_id = config.owners_id

class FSMMoney(StatesGroup):
    userCash = State()

class FSMSendReport(StatesGroup):
    reportName = State()
    reportText = State()
    reportProof = State()
    proofLoad = State()
# [Ответ на /start и регистрация пользователя] =====================================================

async def cancel(message : types.Message, state : FSMContext):
    await state.finish()

async def welcome(message):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    userid = int(message.from_user.id)
    username = str(message.from_user.username)
    cursor.execute("""INSERT OR IGNORE INTO users (user_id, userName)
    VALUES (?, ?);
""", (userid, username));
    db.commit()
    cursor.close()
    db.close()
    logger.info(f'Пользователь {username} авторизовался в боте')
    await message.answer('''
 <b>👋 Добро пожаловать!</b>

''', reply_markup=keyboard.start, parse_mode='HTML')

# [Открытие списка товаров] ====================================================

async def shopCategoriesList(message):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    categories = cursor.execute('SELECT * FROM categories').fetchall()
    await bot.send_message(message.from_user.id, '''
<b></b>

EDUKIDS - ОБРАЗОВАТЕЛЬНЫЙ ОНЛАЙН-ЦЕНТР ИНТЕЛЛЕКТУАЛЬНОГО И ТВОРЧЕСКОГО РАЗВИТИЯ ДЛЯ ДЕТЕЙ ОТ 4-12 ЛЕТ
''', reply_markup=keyboard.genmarkup11(categories))
    cursor.close()
    db.close()

async def showCategory(callback_query : types.CallbackQuery):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    await callback_query.message.delete()
    catID = str(callback_query.data).replace('cat ', '')
    category = cursor.execute('SELECT * FROM categories WHERE catID = ?', ([catID])).fetchall()
    getProductsByCatID = cursor.execute('SELECT * FROM shop WHERE catID = ?', ([catID]))
    for i in category:
        await bot.send_photo(callback_query.from_user.id, i[0], f'''
<b> {i[1]}</b>

{i[2]}


''', reply_markup=keyboard.genmarkup(callback_query))


async def redirectToProdList(callback_query : types.CallbackQuery):
    await callback_query.message.delete()
    await shopCategoriesList(callback_query)

async def send_z(message:types.Message):

    teext= "Заявка от: @"+ str(message.message.chat.username) + " \n\nВыбранное направление: " + message.message.text

    await bot.send_message('481116761', teext)
    await message.answer('''
 Заявка успешно отправлена!

''')
    await profileOpen(message)
# Обработка кнопок из магазина

async def shopProfileRun(callback_query : types.CallbackQuery):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    prodID = str(callback_query.data).replace('prod ', '')
    getProductByID = cursor.execute('SELECT * FROM shop WHERE prodID = ?', ([prodID])).fetchall()
    await callback_query.message.delete()
    for n in getProductByID:
     prodID = n[4]
     prodName = n[0]
     prodCount = cursor.execute('SELECT COUNT(*) FROM sendData WHERE prodName = ?', ([prodName])).fetchall()
     exc3 = cursor.execute('SELECT status FROM sendData WHERE prodName = ?', ([prodName])).fetchall()
     #for i in prodCount:
      #     prodAmount = i[0]

     for l in exc3:
           status = l[0]
           if status == "Y":
            prodAmount = "∞"
   
           else:
            prodAmount = prodAmount


    shopRedirecter = types.InlineKeyboardMarkup(resize_keyboard=True)
    redirectToProdList = types.InlineKeyboardButton(text='Назад', callback_data='prodListRedirect')
    shopRedirecter.add(redirectToProdList)
    zayavka = types.InlineKeyboardMarkup(resize_keyboard=True)
    send_z = types.InlineKeyboardButton(text='Оставить заявку', callback_data='zayavkaRedirect')
    zayavka.add(send_z)
    for r in getProductByID:
           await bot.send_message(callback_query.from_user.id, f'''
<b>{r[0]}</b>

<b>Стоимость:</b> {r[2]} руб.

''', reply_markup=zayavka)
    cursor.close()
    db.close()
# [Отображение профиля пользователя] ====================================
async def profileOpen(message):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    user_id = str(message.from_user.id)
    userInfo = cursor.execute('SELECT * FROM users WHERE user_id = ?', ([user_id])).fetchall()
    for i in userInfo:
        await bot.send_message(user_id, f'''
<b>👍 Заявка отправлена, с вами скоро свяжутся!</b>


''', reply_markup=keyboard.userProfile)

# [Возвращение в главное меню] ==========================================

async def profileBack(message : types.Message):
    await welcome(message)

async def profileBackCallback(callback_query : types.CallbackQuery):
    await callback_query.message.delete()
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    categories = cursor.execute('SELECT * FROM categories').fetchall()
    await bot.send_message(callback_query.from_user.id, '''
    
EDUKIDS - ОБРАЗОВАТЕЛЬНЫЙ ОНЛАЙН-ЦЕНТР ИНТЕЛЛЕКТУАЛЬНОГО И ТВОРЧЕСКОГО РАЗВИТИЯ ДЛЯ ДЕТЕЙ ОТ 4-12 ЛЕТ

''', reply_markup=keyboard.genmarkup11(categories))
    cursor.close()
    db.close()

def register_handlers(dp : Dispatcher):
    dp.register_message_handler(cancel, text='Отмена', state='*')
    dp.register_message_handler(shopCategoriesList, text="Детский центр")
    dp.register_callback_query_handler(profileBackCallback, text=['back'])
    dp.register_message_handler(welcome, commands=['start'])
    dp.register_message_handler(profileOpen, text="📰 Профиль")
    dp.register_callback_query_handler(shopProfileRun, lambda x: x.data.startswith('prod '))
    dp.register_callback_query_handler(redirectToProdList, text=['prodListRedirect'])
    dp.register_callback_query_handler(send_z, text=['zayavkaRedirect'])
    dp.register_callback_query_handler(showCategory, lambda x: x.data.startswith('cat '))
