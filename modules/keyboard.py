
from aiogram import Bot, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from modules import config, shop

db = sqlite3.connect('shop.db')
cursor = db.cursor()
owners_id = config.owners_id

#[Главное меню] =================================================================

okay = types.KeyboardButton("Заявка отправлена")
start = types.ReplyKeyboardMarkup(resize_keyboard=True)
products = types.KeyboardButton("Детский центр")
start.add(products)

backToAdmin = types.KeyboardButton("Назад")
backToStartMenu = types.KeyboardButton("◀  Назад")
cancelBtn = types.KeyboardButton("Отмена")
#[Магазин] ======================================================================

def genmarkup(callback_query = types.CallbackQuery):
    catID = str(callback_query.data).replace('cat ', '')
    getProductsByCatID = cursor.execute('SELECT * FROM shop WHERE catID = ?', ([catID])).fetchall()
    print(getProductsByCatID)
    shop = InlineKeyboardMarkup()
    shop.row_width = 2
    backBtn = types.InlineKeyboardButton(text='Назад', callback_data='back')
    for i in getProductsByCatID:
        prodCount = cursor.execute('SELECT COUNT(*) FROM sendData WHERE prodName = ?', (i[0], )).fetchall()
        prodAmount = str(prodCount).replace('[(', '').replace(',)]', '')
        prodDataStatus = cursor.execute('SELECT status FROM sendData WHERE prodName = ?', (i[0], )).fetchall()
        prodDataStatus = str(prodDataStatus).replace('[(', '').replace(',)]', '').replace("'", "")
        print(prodDataStatus)
        if prodDataStatus == "Y":
            productAmount = "∞"
        else:
            productAmount = prodAmount
        print(productAmount)
        shop.add(InlineKeyboardButton(text=f'{i[0]}', callback_data=f'prod {str(i[4])}'))
    shop.add(backBtn)
    return shop
def genmarkup2(data):
    data = cursor.execute('SELECT * FROM shop').fetchall()
    shop = InlineKeyboardMarkup()
    shop.row_width = 1
    for i in data:
        shop.add(InlineKeyboardButton(i[0], callback_data='rem ' + str(i[4])))
    return shop

def genmarkup3(data):
    data = cursor.execute('SELECT * FROM shop').fetchall()
    prodProfile = InlineKeyboardMarkup()
    shop.row_width = 1
    for i in data:
        prodProfile.add(InlineKeyboardButton(text=i[0], callback_data='buy ' + str(i[4])))
    return prodProfile

def genmarkup4(data):
    data = cursor.execute('SELECT * FROM shop').fetchall()
    dataChooseProd = InlineKeyboardMarkup()
    shop.row_width = 1
    for i in data:
        dataChooseProd.add(InlineKeyboardButton(text=i[0], callback_data='addData ' + str(i[4])))
    return dataChooseProd

def genmarkup7(users):
    users = cursor.execute('SELECT * FROM users').fetchall()
    chooseUser = InlineKeyboardMarkup()
    shop.row_width = 1
    for i in users:
        chooseUser.add(InlineKeyboardButton(text=str(i[2]), callback_data='setMoney ' + str(i[0])))
    return chooseUser

def genmarkup8(user):
    user = cursor.execute('SELECT * FROM users').fetchall()
    dbUsers = InlineKeyboardMarkup()
    shop.row_width = 1
    for i in user:
        dbUsers.add(InlineKeyboardButton(text=str(i[2]), callback_data='showUser ' + i[2]))
    return dbUsers

def genmarkup11(categories):
     categories = cursor.execute('SELECT * FROM categories').fetchall()
     categoriesList = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
     for i in categories:
          categoriesList.insert(types.InlineKeyboardButton(text=str(i[1]), callback_data=f'cat {i[3]}'))
     return categoriesList
def genmarkup12(categories):
     categories = cursor.execute('SELECT * FROM categories').fetchall()
     addProdCategoriesList = InlineKeyboardMarkup()
     addProdCategoriesList.row_width = 2
     for i in categories:
          addProdCategoriesList.add(InlineKeyboardButton(text=str(i[1]), callback_data=f'setcat {i[3]}'))
     return addProdCategoriesList

def genmarkup13(categories):
     categories = cursor.execute('SELECT * FROM categories').fetchall()
     categoriesListDel = InlineKeyboardMarkup()
     categoriesListDel.row_width = 2
     for i in categories:
          categoriesListDel.add(InlineKeyboardButton(text=str(i[1]), callback_data=f'delcat {i[3]}'))
     return categoriesListDel

def genmarkup14(users):
     users = cursor.execute('SELECT * FROM users').fetchall()
     usersList = InlineKeyboardMarkup()
     usersList.row_width = 2
     for i in users:
          usersList.add(InlineKeyboardButton(text=str(i[2]), callback_data=f"purc {i[0]}"))
     return usersList


userProfile = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

userProfile.add(products)

#[Админка] ======================================================================

ownerDashboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

ownerCategoriesMenu = types.KeyboardButton("Категории")
ownerProductsMenu = types.KeyboardButton("Товары")

ownerDashboard.add(ownerCategoriesMenu, ownerProductsMenu, backToStartMenu)

categoriesMenu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
categoriesAdd = types.KeyboardButton('Добавить категорию')
categoriesRem = types.KeyboardButton('Удалить категорию')
categoriesRen = types.KeyboardButton('Переименовать категорию')

categoriesMenu.add(categoriesAdd, categoriesRem, categoriesRen, backToAdmin)

productsMenu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
ownerAddProducts = types.KeyboardButton('Добавить товар')
ownerDeleteProducts = types.KeyboardButton('Удалить товар')

productsMenu.add(ownerAddProducts, ownerDeleteProducts, backToAdmin)





