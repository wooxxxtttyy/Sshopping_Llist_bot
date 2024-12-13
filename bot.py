import telebot
from telebot import types
import os
import json

token ='8111289497:AAHvptrlfwwRlmOPjqdNnEhFsIDs2tHsttk'
bot = telebot.TeleBot(token)

class ListProducts:
    def __init__(self):
        self.dict_products = {}

class ListBot(ListProducts):
    def __init__(self):
        super().__init__()

# Словарь для хранения продуктов для каждого пользователя
products = ListBot()
user_products = products.dict_products
adding_product = {}
command_list = ['add', 'list', 'clear', 'total']


# Функция для загрузки пользовательских данных из JSON
def load_user_products():
    if os.path.exists('user_products.json'):
        with open('user_products.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}


# Функция для сохранения пользовательских данных в JSON
def save_user_products():
    with open('user_products.json', 'w', encoding='utf-8') as file:
        json.dump(user_products, file, ensure_ascii=False, indent=4)


@bot.message_handler(commands=['start'])
def welcome(message):
    chat_id = str(message.chat.id)

    # Загружаем данные пользователя
    if chat_id in user_products:
        product_list = user_products[chat_id]
        if product_list:
            product_message = "Ваш прошлый список продуктов:\n" + "\n".join(
                [f"{product}: Количество - {info['quantity']} {info['measurement']}, Стоимость - {info['price']} руб." for product, info in product_list.items()])
            bot.send_message(chat_id, product_message)
        else:
            bot.send_message(chat_id, "У вас нет ранее добавленных продуктов.")

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton(text="add")
    button1 = telebot.types.KeyboardButton(text="list")
    button2 = telebot.types.KeyboardButton(text="clear")
    button3 = telebot.types.KeyboardButton(text="total")
    button_back = telebot.types.KeyboardButton(text="back")
    keyboard.add(button, button1, button2, button3, button_back)
    bot.send_message(chat_id,
                     'Добро пожаловать в бот для списка покупок! Используйте кнопки add для добавления продукта, list для просмотра списка, clear для очистки списка и total для подсчёта общей стоимости.',
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "back")
def go_back(message):
    chat_id = message.chat.id

    # Сбрасываем данные пользователя
    if chat_id in user_products:
        del user_products[chat_id]  # Удаляем список продуктов пользователя
    if chat_id in adding_product:
        del adding_product[chat_id]  # Удаляем состояние добавления продукта

    bot.send_message(chat_id, "Вы вернулись в главное меню. Все данные были сброшены. Выберите действие:",
                     reply_markup=get_main_menu_keyboard())

def get_main_menu_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton(text="add")
    button1 = telebot.types.KeyboardButton(text="list")
    button2 = telebot.types.KeyboardButton(text="clear")
    button3 = telebot.types.KeyboardButton(text="total")
    button_back = telebot.types.KeyboardButton(text="back")
    keyboard.add(button, button1, button2, button3, button_back)
    return keyboard

@bot.message_handler(func=lambda message: message.text == "add")
def add_product_start(message):
    if message.chat.id not in user_products:
        user_products[message.chat.id] = {}  # Инициализируем список продуктов для нового пользователя
    bot.send_message(message.chat.id, 'Введите название продукта, который хотите добавить:')
    adding_product[message.chat.id] = {'step': 'name'}  # Устанавливаем состояние добавления продукта


@bot.message_handler(func=lambda message: message.chat.id in adding_product)
def add_product(message):
    step = adding_product[message.chat.id]['step']

    if step == 'name':
        product = message.text.strip()
        if product:  # Проверяем, что продукт указан
            # Проверяем, что имя продукта не совпадает с именами команд
            if product in command_list:
                bot.send_message(message.chat.id,
                                 f'Имя продукта не может совпадать с командой: "{product}". Пожалуйста, введите другое имя.')
            else:
                adding_product[message.chat.id]['product'] = product
                adding_product[message.chat.id]['step'] = 'measurement'  # Переходим к следующему шагу
                bot.send_message(message.chat.id,
                                 f'Вы добавили продукт "{product}". Выберите способ измерения: напишите "штуки" или "кг":')
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, укажите продукт для добавления.')

    elif step == 'measurement':
        measurement = message.text.strip().lower()
        if measurement in ['штуки', 'кг']:
            adding_product[message.chat.id]['measurement'] = measurement
            adding_product[message.chat.id]['step'] = 'quantity'  # Переходим к следующему шагу
            bot.send_message(message.chat.id, f'Вы выбрали измерение в "{measurement}". Теперь укажите количество:')
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, выберите "штуки" или "кг".')

    elif step == 'quantity':
        try:
            quantity = float(message.text.strip())  # Изменяем на float для поддержки дробных значений
            if quantity <= 0:  # Проверка на отрицательное значение и на ноль
                bot.send_message(message.chat.id,
                                 'Количество не может быть нулевым или отрицательным. Пожалуйста, введите корректное количество.')
                return
            product = adding_product[message.chat.id]['product']
            measurement = adding_product[message.chat.id]['measurement']
            if measurement == 'штуки' and quantity % 1 != 0:  # Проверка на дробное значение для "штуки"
                bot.send_message(message.chat.id,
                                 'Количество в "штуках" не может быть дробным. Пожалуйста, введите целое число.')
                return
            adding_product[message.chat.id]['quantity'] = quantity  # Сохраняем количество

            if measurement == 'кг' and quantity < 1:  # Если вес меньше 1 кг
                adding_product[message.chat.id]['step'] = 'price_per_kg'  # Запрашиваем цену за кг
                bot.send_message(message.chat.id,
                                 f'Количество для продукта "{product}": {quantity} {measurement}. Пожалуйста, укажите стоимость за килограмм в руб.:')
            else:
                adding_product[message.chat.id]['step'] = 'price'  # Переходим к следующему шагу
                bot.send_message(message.chat.id,
                                 f'Количество для продукта "{product}": {quantity} {measurement}. Если известна стоимость, введите её. Если нет, просто напишите "нет":')
        except ValueError:
            bot.send_message(message.chat.id, 'Пожалуйста, введите корректное количество (число).')


    elif step == 'price_per_kg':
        try:
            price_per_kg = float(message.text.strip())  # Получаем стоимость за кг
            if price_per_kg <= 0:  # Проверка на отрицательную стоимость
                bot.send_message(message.chat.id,
                                 'Стоимость не может быть нулевой или отрицательной. Пожалуйста, введите корректную стоимость.')
                return
            product = adding_product[message.chat.id]['product']
            quantity = adding_product[message.chat.id]['quantity']
            total_price = price_per_kg * quantity  # Рассчитываем общую стоимость

            user_products[message.chat.id][product] = {
                'quantity': quantity,
                'measurement': 'кг',
                'price': total_price  # Сохраняем общую стоимость
            }
            bot.send_message(message.chat.id,
                             f'Продукт "{product}" с количеством {quantity} кг добавлен в список со стоимостью {total_price:.2f} руб.')
            del adding_product[message.chat.id]  # Удаляем состояние добавления продукта


        except ValueError:
            bot.send_message(message.chat.id, 'Пожалуйста, введите корректную стоимость (число).')

    elif step == 'price':
        price_input = message.text.strip()
        product = adding_product[message.chat.id]['product']
        quantity = adding_product[message.chat.id]['quantity']
        measurement = adding_product[message.chat.id]['measurement']

        if price_input.lower() != "нет":  # Если стоимость известна
            try:
                price = float(price_input)  # Пробуем преобразовать в число с плавающей точкой
                if price <= 0:  # Проверка на отрицательную стоимость
                    bot.send_message(message.chat.id,
                                     'Стоимость не может быть нулевой или отрицательной. Пожалуйста, введите корректную стоимость.')
                    return
                user_products[message.chat.id][product] = {'quantity': quantity, 'measurement': measurement,
                                                           'price': price}  # Сохраняем продукт со стоимостью
                bot.send_message(message.chat.id,
                                 f'Продукт "{product}" с количеством {quantity} {measurement} и стоимостью {price} руб. добавлен в список.')
            except ValueError:
                bot.send_message(message.chat.id, 'Пожалуйста, введите корректную стоимость (число).')
        else:  # Если стоимость не известна
            user_products[message.chat.id][product] = {'quantity': quantity,
                                                       'measurement': measurement}  # Сохраняем только количество и измерение
            bot.send_message(message.chat.id,
                             f'Продукт "{product}" с количеством {quantity} {measurement} добавлен в список без указания стоимости.')

        del adding_product[message.chat.id]

@bot.message_handler(func=lambda message: message.text == "list")
def list_products(message):
    chat_id = message.chat.id
    if chat_id in user_products and user_products[chat_id]:
        product_list = '\n'.join([f'{product}: Количество - {info["quantity"]} {info["measurement"]}' + (
            f', Стоимость - {info["price"]:.2f} руб.' if 'price' in info else '') for product, info in
                                  user_products[chat_id].items()])

        # Отправляем список продуктов в сообщении
        bot.send_message(chat_id, f'Ваши продукты:\n{product_list}')

        # Создаем текстовый файл со списком продуктов
        file_name = f'products_{chat_id}.txt'
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(product_list)

        # Отправляем файл пользователю
        with open(file_name, 'rb') as file:
            bot.send_document(chat_id, file)

        # Удаляем файл после отправки
        os.remove(file_name)
    else:
        bot.send_message(chat_id, 'Список продуктов пуст.')


@bot.message_handler(func=lambda message: message.text == "clear")
def clear_products(message):
    user_products.pop(message.chat.id, None)  # Очищаем список продуктов конкретного пользователя
    bot.send_message(message.chat.id, 'Список продуктов очищен.')


@bot.message_handler(func=lambda message: message.text == "total")
def total_cost(message):
    if message.chat.id not in user_products or not user_products[message.chat.id]:
        bot.send_message(message.chat.id, 'Список продуктов пуст.')
        return

    total_cost_with_price = 0.0
    total_quantity_without_price = 0

    for info in user_products[message.chat.id].values():
        if 'price' in info:  # Учитываем только продукты с известной стоимостью
            total_cost_with_price += info['quantity'] * info['price']
        else:  # Учитываем количество продуктов без известной стоимости
            total_quantity_without_price += info['quantity']

    response = f'Итоговая стоимость всех продуктов с известной ценой: {total_cost_with_price:.2f} руб.'

    if total_quantity_without_price > 0:
        response += f'\nКоличество продуктов без известной стоимости: {total_quantity_without_price}.'

    bot.send_message(message.chat.id, response)

# Сохраняем данные перед выходом (например, при завершении программы)
import atexit
atexit.register(save_user_products)

# Загружаем данные при старте бота
user_products.update(load_user_products())

bot.infinity_polling()
