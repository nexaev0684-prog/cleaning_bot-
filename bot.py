import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
from datetime import datetime
import time

# ========== ВАШ ТОКЕН ==========
TOKEN = "8514292885:AAFfAFykQvQS0eE76qGxToERtF3TQiIFxKo"
bot = telebot.TeleBot(TOKEN)

# Пароль для сотрудников
STAFF_PASSWORD = "love2026"

# ID сотрудников
STAFF_USERS = {}

# Файл для хранения заявок
ORDERS_FILE = "orders.json"

# Загрузка заявок
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Сохранение заявок
def save_orders(orders):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

# Генерация номера заявки
def get_next_order_number():
    orders = load_orders()
    if not orders:
        return 1
    return max([int(k) for k in orders.keys()]) + 1

# ========== КЛАВИАТУРЫ ==========

def main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_client = InlineKeyboardButton("👤 Я КЛИЕНТ", callback_data="mode_client")
    btn_staff = InlineKeyboardButton("👥 Я СОТРУДНИК", callback_data="mode_staff")
    keyboard.add(btn_client, btn_staff)
    return keyboard

def client_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton("💰 Цены", callback_data="client_prices")
    btn2 = InlineKeyboardButton("📝 Оставить заявку", callback_data="client_order")
    btn3 = InlineKeyboardButton("📞 Контакты", callback_data="client_contacts")
    btn4 = InlineKeyboardButton("ℹ️ О компании", callback_data="client_about")
    btn5 = InlineKeyboardButton("🔙 Выход", callback_data="back_to_main")
    keyboard.add(btn1, btn2, btn3, btn4, btn5)
    return keyboard

def staff_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("📋 Новые заявки", callback_data="staff_new_orders")
    btn2 = InlineKeyboardButton("📊 Статистика", callback_data="staff_stats")
    btn3 = InlineKeyboardButton("🔙 Выход", callback_data="back_to_main")
    keyboard.add(btn1, btn2, btn3)
    return keyboard

# ========== ФУНКЦИИ КЛИЕНТА ==========

def send_client_prices(user_id):
    text = """
💰 **Наши цены**

🏠 Уборка квартир: от 2500 ₽
🧹 Генеральная уборка: от 5000 ₽
🪟 Мойка окон: от 500 ₽/окно
🏢 Уборка офисов: от 3000 ₽
    """
    bot.send_message(user_id, text, parse_mode="Markdown")

def send_client_contacts(user_id):
    text = """
📞 **Контакты**
Менеджер: @Lubasha9999
    """
    bot.send_message(user_id, text, parse_mode="Markdown")

def send_client_about(user_id):
    text = """
ℹ️ **О компании**
Клининговая компания "С Любовью"
Работаем с 2020 года
    """
    bot.send_message(user_id, text, parse_mode="Markdown")

# ========== ОБРАБОТЧИК КОМАНД ==========

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    if user_id in STAFF_USERS:
        del STAFF_USERS[user_id]
    
    welcome_text = f"""
👋 Здравствуйте, {user_name}!

Добро пожаловать в клининговую компанию **'С Любовью'** ✨

Выберите ваш режим:
    """
    
    bot.send_message(user_id, welcome_text, parse_mode="Markdown", 
                     reply_markup=main_keyboard())

# ========== ОБРАБОТЧИК CALLBACK (КНОПОК) ==========

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    data = call.data
    
    # Главное меню
    if data == "mode_client":
        bot.send_message(user_id, "👤 Режим КЛИЕНТ\nВыберите действие:", 
                        reply_markup=client_keyboard())
        bot.answer_callback_query(call.id)
    
    elif data == "mode_staff":
        STAFF_USERS[user_id] = {'step': 'auth'}
        bot.send_message(user_id, "🔐 **Режим СОТРУДНИКА**\n\nВведите пароль:", 
                        parse_mode="Markdown")
        bot.answer_callback_query(call.id)
    
    elif data == "back_to_main":
        if user_id in STAFF_USERS:
            del STAFF_USERS[user_id]
        start(call.message)
        bot.answer_callback_query(call.id)
    
    # Клиентские кнопки
    elif data == "client_prices":
        send_client_prices(user_id)
        bot.answer_callback_query(call.id)
    
    elif data == "client_contacts":
        send_client_contacts(user_id)
        bot.answer_callback_query(call.id)
    
    elif data == "client_about":
        send_client_about(user_id)
        bot.answer_callback_query(call.id)
    
    elif data == "client_order":
        STAFF_USERS[user_id] = {'step': 'order_name', 'data': {}}
        bot.send_message(user_id, "📝 **Оформление заявки**\n\nВведите ваше имя:", 
                        parse_mode="Markdown")
        bot.answer_callback_query(call.id)
    
    # Сотруднические кнопки
    elif data == "staff_new_orders":
        orders = load_orders()
        pending = {k: v for k, v in orders.items() if v.get('status') == 'pending'}
        
        if not pending:
            bot.send_message(user_id, "📭 Нет новых заявок")
        else:
            for order_id, order in pending.items():
                text = f"""
📋 **ЗАЯВКА #{order_id}**

👤 Имя: {order.get('name', 'не указано')}
📞 Телефон: {order.get('phone', 'не указан')}
🏠 Адрес: {order.get('address', 'не указан')}
📅 Дата: {order.get('date', 'не указана')}
                """
                bot.send_message(user_id, text, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
    
    elif data == "staff_stats":
        orders = load_orders()
        total = len(orders)
        pending = sum(1 for o in orders.values() if o.get('status') == 'pending')
        
        stats_text = f"""
📊 **СТАТИСТИКА**

📋 Всего заявок: {total}
⏳ В обработке: {pending}
        """
        bot.send_message(user_id, stats_text, parse_mode="Markdown")
        bot.answer_callback_query(call.id)

# ========== ОБРАБОТЧИК ТЕКСТА ==========

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text
    
    # Проверка пароля сотрудника
    if user_id in STAFF_USERS and STAFF_USERS[user_id].get('step') == 'auth':
        if text == STAFF_PASSWORD:
            STAFF_USERS[user_id] = {'role': 'staff'}
            bot.send_message(user_id, "✅ Доступ разрешен!\n\nДобро пожаловать в панель сотрудника.", 
                           reply_markup=staff_keyboard())
        else:
            bot.send_message(user_id, "❌ Неверный пароль!\n\nПопробуйте снова или нажмите /start.")
            del STAFF_USERS[user_id]
    
    # Оформление заявки
    elif user_id in STAFF_USERS and STAFF_USERS[user_id].get('step') == 'order_name':
        STAFF_USERS[user_id]['data']['name'] = text
        STAFF_USERS[user_id]['step'] = 'order_phone'
        bot.send_message(user_id, "📞 Введите ваш номер телефона:")
    
    elif user_id in STAFF_USERS and STAFF_USERS[user_id].get('step') == 'order_phone':
        STAFF_USERS[user_id]['data']['phone'] = text
        STAFF_USERS[user_id]['step'] = 'order_address'
        bot.send_message(user_id, "🏠 Введите адрес уборки:")
    
    elif user_id in STAFF_USERS and STAFF_USERS[user_id].get('step') == 'order_address':
        data = STAFF_USERS[user_id]['data']
        data['address'] = text
        data['status'] = 'pending'
        data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        order_id = get_next_order_number()
        orders = load_orders()
        orders[str(order_id)] = data
        save_orders(orders)
        
        bot.send_message(user_id, f"✅ Заявка #{order_id} успешно отправлена!\n\nНаш менеджер свяжется с вами.")
        del STAFF_USERS[user_id]
    
    else:
        bot.send_message(user_id, "Используйте /start для начала работы.")

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("🤖 Бот 'С Любовью' запущен!")
    
    # Проверяем подключение
    try:
        bot.get_me()
        print("✅ Соединение с Telegram API установлено!")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        exit()
    
    # Запускаем бота
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except KeyboardInterrupt:
            print("\n❌ Бот остановлен")
            break
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            print("🔄 Переподключение через 15 секунд...")
            time.sleep(15)
