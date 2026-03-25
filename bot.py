import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
from datetime import datetime
import time

TOKEN = "8514292885:AAFfAFykQvQS0eE76qGxToERtF3TQiIFxKo"
bot = telebot.TeleBot(TOKEN)

STAFF_PASSWORD = "love2026"
STAFF_USERS = {}
ORDERS_FILE = "orders.json"

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_orders(orders):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

def get_next_order_number():
    orders = load_orders()
    if not orders:
        return 1
    return max([int(k) for k in orders.keys()]) + 1

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
    btn4 = InlineKeyboardButton("🔙 Выход", callback_data="back_to_main")
    keyboard.add(btn1, btn2, btn3, btn4)
    return keyboard

def staff_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("📋 Новые заявки", callback_data="staff_new_orders")
    btn2 = InlineKeyboardButton("📊 Статистика", callback_data="staff_stats")
    btn3 = InlineKeyboardButton("🔙 Выход", callback_data="back_to_main")
    keyboard.add(btn1, btn2, btn3)
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in STAFF_USERS:
        del STAFF_USERS[user_id]
    bot.send_message(user_id, "👋 Добро пожаловать! Выберите режим:", reply_markup=main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    data = call.data
    
    if data == "mode_client":
        bot.send_message(user_id, "👤 Режим КЛИЕНТ\nВыберите действие:", reply_markup=client_keyboard())
        bot.answer_callback_query(call.id)
    
    elif data == "mode_staff":
        STAFF_USERS[user_id] = {'step': 'auth'}
        bot.send_message(user_id, "🔐 Введите пароль:")
        bot.answer_callback_query(call.id)
    
    elif data == "back_to_main":
        if user_id in STAFF_USERS:
            del STAFF_USERS[user_id]
        start(call.message)
        bot.answer_callback_query(call.id)
    
    elif data == "client_prices":
        bot.send_message(user_id, "💰 Цены:\nУборка квартир — от 2500₽\nГенеральная — от 5000₽")
        bot.answer_callback_query(call.id)
    
    elif data == "client_contacts":
        bot.send_message(user_id, "📞 Контакты: @Lubasha9999")
        bot.answer_callback_query(call.id)
    
    elif data == "client_order":
        STAFF_USERS[user_id] = {'step': 'order_name', 'data': {}}
        bot.send_message(user_id, "📝 Введите ваше имя:")
        bot.answer_callback_query(call.id)
    
    elif data == "staff_new_orders":
        orders = load_orders()
        pending = {k: v for k, v in orders.items() if v.get('status') == 'pending'}
        if not pending:
            bot.send_message(user_id, "📭 Нет новых заявок")
        else:
            for order_id, order in pending.items():
                text = f"📋 Заявка #{order_id}\n👤 {order.get('name')}\n📞 {order.get('phone')}"
                bot.send_message(user_id, text)
        bot.answer_callback_query(call.id)
    
    elif data == "staff_stats":
        orders = load_orders()
        total = len(orders)
        pending = sum(1 for o in orders.values() if o.get('status') == 'pending')
        bot.send_message(user_id, f"📊 Статистика:\nВсего: {total}\nВ работе: {pending}")
        bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text
    
    if user_id in STAFF_USERS and STAFF_USERS[user_id].get('step') == 'auth':
        if text == STAFF_PASSWORD:
            STAFF_USERS[user_id] = {'role': 'staff'}
            bot.send_message(user_id, "✅ Доступ разрешен!", reply_markup=staff_keyboard())
        else:
            bot.send_message(user_id, "❌ Неверный пароль")
            del STAFF_USERS[user_id]
    
    elif user_id in STAFF_USERS and STAFF_USERS[user_id].get('step') == 'order_name':
        STAFF_USERS[user_id]['data']['name'] = text
        STAFF_USERS[user_id]['step'] = 'order_phone'
        bot.send_message(user_id, "📞 Введите номер телефона:")
    
    elif user_id in STAFF_USERS and STAFF_USERS[user_id].get('step') == 'order_phone':
        STAFF_USERS[user_id]['data']['phone'] = text
        STAFF_USERS[user_id]['step'] = 'order_address'
        bot.send_message(user_id, "🏠 Введите адрес:")
    
    elif user_id in STAFF_USERS and STAFF_USERS[user_id].get('step') == 'order_address':
        data = STAFF_USERS[user_id]['data']
        data['address'] = text
        data['status'] = 'pending'
        data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        order_id = get_next_order_number()
        orders = load_orders()
        orders[str(order_id)] = data
        save_orders(orders)
        
        bot.send_message(user_id, f"✅ Заявка #{order_id} отправлена!")
        del STAFF_USERS[user_id]

print("🤖 Бот 'С Любовью' запущен и работает!")
bot.infinity_polling()
