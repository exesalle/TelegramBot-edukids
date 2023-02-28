
# [Модули] ==============================================================

from aiogram import types, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command
from modules import config, keyboard, shop, handler, logger
import sqlite3
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from time import sleep
# [Основные переменные] =================================================
	
db = sqlite3.connect('shop.db')
cursor = db.cursor()
storage = MemoryStorage()
bot = Bot(token=config.botkey, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

# [Машины состояний] ====================================================

class FSMAdmin(StatesGroup):
    catID = State()
    prodName = State()
    prodDesc = State()
    prodPrice = State()

class FSMProdAddData(StatesGroup):
    prodDataText = State()
    prodDataUnlimited = State()

class FSMSetMoney(StatesGroup):
    money = State()

class FSMCreateAd(StatesGroup):
    adPhoto = State()
    adText = State()
    adName = State()

class FSMCreateCategory(StatesGroup):
    catPhoto = State()
    catName = State()
    catDesc = State()

class FSMReportAnswer(StatesGroup):
    text = State()

class FSMReportCloseWithReason(StatesGroup):
    reason = State()
# [Вызов меню для администратора] =======================================

async def checkAccess(userID):
    owners_id = config.owners_id
    if userID in owners_id:
        return True
    else:
        return False

async def callOwnerMenu(message):
 userID = str(message.from_user.id)
 userName = str(message.from_user.username)
 if await checkAccess(userID) == True:
     logger.warn(f'Пользователь {userName} получил доступ к панели администратора.')
     await message.answer('''
<b>Панель администратора</b>
''', reply_markup=keyboard.ownerDashboard, parse_mode='HTML')
 else:
    return

async def ownerBackBtn(message):
     await message.answer('''
 <b>👋 | Добро пожаловать!</b>
''', reply_markup=keyboard.start, parse_mode='HTML')

async def ownerBackToAdmin(message):
    userID = str(message.from_user.id)
    if await checkAccess(userID) == True:
        await callOwnerMenu(message)
    else:
        return

async def prodDeleteChoose(message):
 db = sqlite3.connect('shop.db')
 cursor = db.cursor()
 userID = str(message.from_user.id)
 if await checkAccess(userID) == True:
    data = cursor.execute('SELECT * FROM shop').fetchall()
    await bot.send_message(message.from_user.id, '''
💻 Админ-панель / Удаление товара

Выберите товар, который вы хотите удалить
''', reply_markup=keyboard.genmarkup2(data))
 else:
    return
 cursor.close()
 db.close()

async def ownerCategoryMenu(message : types.Message):
 userID = str(message.from_user.id)
 if await checkAccess(userID) == True:
    await message.answer('''
<b>🗃️ Панель администратора / Категории</b>

''', reply_markup=keyboard.categoriesMenu)

 else:
    return

async def ownerCategoryCreate(message : types.Message):
 db = sqlite3.connect('shop.db')
 cursor = db.cursor()
 userID = str(message.from_user.id)
 if await checkAccess(userID) == True:
     await FSMCreateCategory.catPhoto.set()
     await message.answer('''
Создание категории #1

Загрузите обложку для категории (Фото):
''')
 else:
     return

async def ownerCatPhotoLoad(message : types.Message, state : FSMContext):
    async with state.proxy() as catData:
        catData['photo'] = message.photo[0].file_id
    await FSMCreateCategory.next()
    await message.answer('''
Создание категории #2

Введите название для категории:
''')

async def ownerCatNameLoad(message : types.Message, state : FSMContext):
    async with state.proxy() as catData:
        catData['name'] = message.text
        await FSMCreateCategory.next()
        await message.answer('''
Создание категории #3

Введите описание для категории:
''')

async def ownerCatDescLoad(message : types.Message, state : FSMContext):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    async with state.proxy() as catData:
        catData['desc'] = message.text
        catPhoto = catData['photo']
        catName = catData['name']
        catDesc = catData['desc']
        cursor.execute('INSERT INTO categories(catPhoto, catName, catDesc) VALUES(?, ?, ?)', (catPhoto, catName, catDesc))
        db.commit()
        catID = cursor.execute('SELECT catID from categories WHERE catName = ?', ([catName])).fetchall()
        logger.success(f'Добавлена категория {catName}.')
    await state.finish()
    await message.answer('Категория добавлена!')
    cursor.close()
    db.close()

async def ownerCatDelete(message : types.Message):
    userID = str(message.from_user.id)
    if await checkAccess(userID) == True:
        db = sqlite3.connect('shop.db')
        cursor = db.cursor()
        categories = cursor.execute('SELECT * FROM categories')
        await bot.send_message(message.from_user.id, '''
Выберите категорию, которую вы хотите удалить.
Товары из этой категории будут удалены!
''', reply_markup=keyboard.genmarkup13(categories))
        cursor.close()
        db.close()
    else:
        return

async def catDelete(callback_query : types.CallbackQuery):
 db = sqlite3.connect('shop.db')
 cursor = db.cursor()
 userID = str(callback_query.from_user.id)
 if await checkAccess(userID) == True:
    catID = str(callback_query.data).replace('delcat ', '')
    cursor.execute('DELETE FROM shop WHERE catID = ?', ([catID]))
    cursor.execute('DELETE FROM categories WHERE catID = ?', ([catID]))
    logger.success(f'Категория №{catID} была удалена.')
    db.commit()
    cursor.close()
    db.close()

 else:
    return

async def addProductChooseCategory(message : types.Message):
 db = sqlite3.connect('shop.db')
 cursor = db.cursor()
 userID = str(message.from_user.id)
 if await checkAccess(userID) == True:
    categories = cursor.execute('SELECT * FROM categories').fetchall()
    await bot.send_message(message.from_user.id, 'Выберите категорию, в которую бы вы хотели добавить товар', reply_markup=keyboard.genmarkup12(categories))
 else:
    return
 cursor.close()
 db.close()

async def ownerProductsMenu(message : types.Message):
    userID = str(message.from_user.id)
    if await checkAccess(userID) == True:
        await bot.send_message(message.from_user.id, '''<b>Панель администратора / Товары</b>

Здесь вы можете добавлять или удалять товары.
''', reply_markup=keyboard.productsMenu)
    else:
        return

async def addProduct(callback_query : types.CallbackQuery, state : FSMContext):
    userID = str(callback_query.from_user.id)
    if await checkAccess(userID) == True:
        await FSMAdmin.catID.set()
        catID = str(callback_query.data).replace('setcat ', '')
        async with state.proxy() as prodData:
            prodData['catID'] = catID
        await FSMAdmin.next()
        await bot.send_message(callback_query.from_user.id, 'Укажите название товара:')
    else:
        return

async def prodNameLoad(message: types.Message, state: FSMContext):
    async with state.proxy() as prodData:
        cursor = db.cursor()
        prodData['name'] = message.text
    await FSMAdmin.next()
    await message.reply("Укажите описание к товару:")
    cursor.close()

async def prodDescLoad(message: types.Message, state: FSMContext):
    cursor = db.cursor()
    async with state.proxy() as prodData:
        prodData['desc'] = message.text
    await FSMAdmin.next()
    await message.reply('Укажите стоимость товара:')
    cursor.close()

async def prodPriceLoad(message: types.Message, state: FSMContext):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    async with state.proxy() as prodData:
        username = message.from_user.username
        cursor = db.cursor()
        prodName = prodData['name']
        prodDesc = prodData['desc']
        prodData['price'] = message.text
        prodPrice = prodData['price']
        catID = prodData['catID']
        cursor.execute('INSERT INTO shop(prodName, prodDesc, prodPrice, catID) VALUES (?, ?, ?, ?)', (prodName, prodDesc, prodPrice, catID))
        db.commit()
        logger.success(f'Пользователь {username} добавил товар {prodName}.')
        cursor.close()
    await state.finish()
    cursor.close()
    db.close()


async def prodDelete(callback_query : types.CallbackQuery):
 db = sqlite3.connect('shop.db')
 cursor = db.cursor()
 userID = str(callback_query.from_user.id)
 if await checkAccess(userID) == True:
    cb_data = callback_query.data
    prodID = cb_data.replace('rem ', '')
    product = cursor.execute('SELECT * FROM shop WHERE prodID = ?', ([prodID])).fetchall()
    userName = callback_query.from_user.username
    for i in product:
        prodName = i[0]
    cursor.execute('DELETE FROM shop WHERE prodName = ?', ([prodName]))
    cursor.execute('DELETE FROM sendData WHERE prodName = ?', ([prodName]))
    db.commit()
    await bot.send_message(callback_query.from_user.id, '''
<b>💻 Админ-панель / Удаление товара</b>

Товар был успешно удалён.
''')
    logger.success(f"Пользователь {userName} удалил товар {prodName}!")

 else:
    return
 cursor.close()
 db.close()


def register_handlers(dp : Dispatcher):
 dp.register_message_handler(callOwnerMenu, text='Admin')
 dp.register_message_handler(ownerBackBtn, text='⤵️ Назад')
 dp.register_message_handler(addProductChooseCategory, text='Добавить товар')
 dp.register_callback_query_handler(addProduct, lambda x: x.data.startswith('setcat '))
 dp.register_message_handler(prodNameLoad, state=FSMAdmin.prodName)
 dp.register_message_handler(prodDescLoad, state=FSMAdmin.prodDesc)
 dp.register_message_handler(prodPriceLoad, state=FSMAdmin.prodPrice)
 dp.register_callback_query_handler(prodDelete, lambda x: x.data.startswith('rem '))
 dp.register_message_handler(prodDeleteChoose, text='Удалить товар')
 dp.register_message_handler(ownerCategoryMenu, text="Категории")
 dp.register_message_handler(ownerCategoryCreate, text="Добавить категорию")
 dp.register_message_handler(ownerCatDelete, text="Удалить категорию")
 dp.register_callback_query_handler(catDelete, lambda x: x.data.startswith('delcat '))
 dp.register_message_handler(ownerCatPhotoLoad, content_types=['photo'], state=FSMCreateCategory.catPhoto)
 dp.register_message_handler(ownerCatNameLoad, state=FSMCreateCategory.catName)
 dp.register_message_handler(ownerCatDescLoad, state=FSMCreateCategory.catDesc)
 dp.register_message_handler(ownerProductsMenu, text='Товары')
 dp.register_message_handler(ownerBackToAdmin, text='Назад')
