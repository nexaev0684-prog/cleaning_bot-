import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import apihelper
import json
import os
from datetime import datetime
import time

# ========== НАСТРОЙКА ПРОКСИ ==========
# Ваши настройки из ссылки: socks5://127.0.0.1:1080
apihelper.proxy = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}

# ========== ВАШ ТОКЕН ==========
# ВСТАВЬТЕ СВОЙ ТОКЕН ОТ @BotFather
TOKEN = "8514292885:AAFfAFykQvQS0eE76qGxToERtF3TQiIFxKo"  # Замените на реальный токен!
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
    btn2 = InlineKeyboardButton("✅ Выполненные", callback_data="staff_completed")
    btn3 = InlineKeyboardButton("📊 Статистика", callback_data="staff_stats")
    btn4 = InlineKeyboardButton("🔙 Выход", callback_data="back_to_main")
    keyboard.add(btn1, btn2, btn3, btn4)
    return keyboard

def order_keyboard(order_id):
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("✅ Принять", callback_data=f"staff_accept_{order_id}")
    btn2 = InlineKeyboardButton("💰 Расчет", callback_data=f"staff_calc_{order_id}")
    btn3 = InlineKeyboardButton("❌ Отказать", callback_data=f"staff_reject_{order_id}")
    btn4 = InlineKeyboardButton("📞 Связаться", callback_data=f"staff_contact_{order_id}")
    keyboard.add(btn1, btn2, btn3, btn4)
    return keyboard

# ========== ОБРАБОТЧИКИ КОМАНД ==========

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

# ========== ОСТАЛЬНЫЕ ФУНКЦИИ (ваш существующий код) ==========
# ... здесь должны быть все остальные функции из вашего кода ...
# (send_client_prices, send_client_contacts, send_client_about, 
#  start_order_flow, process_order_step, save_order, 
#  staff_auth, check_staff_auth, staff_new_orders, staff_stats,
#  handle_callback, handle_text и т.д.)

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("🤖 Бот 'С Любовью' запущен!")
    print(f"✅ Прокси настроен: {apihelper.proxy}")
    
    # Проверяем подключение
    try:
        bot.get_me()
        print("✅ Соединение с Telegram API установлено!")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        print("Проверьте, что прокси-клиент запущен (например, VPN клиент)")
        input("Нажмите Enter для выхода...")
        exit()
    
    # Запускаем бота
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except KeyboardInterrupt:
            print("\n❌ Бот остановлен")
            break
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            print("🔄 Переподключение через 15 секунд...")
            time.sleep(15)