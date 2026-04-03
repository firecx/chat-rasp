import telebot
from telebot import types
import requests
from datetime import datetime, timedelta
import random

# Замени на свой токен
bot = telebot.TeleBot('YOUR_BOT_TOKEN_HERE')

user_data = {}

# Названия кнопок
BTN_TODAY = '📅 Сегодня'
BTN_TOMORROW = '📆 Завтра'
BTN_WEEK = '🗓 На неделю'
BTN_OTHER = '🔍 Другая дата'
BTN_CHANGE_GROUP = '🔄 Сменить группу'

# --- 1. ФУНКЦИИ РАБОТЫ С API ОМГТУ ---

def get_group_id(group_name):
    url = f"https://rasp.omgtu.ru/api/search?term={group_name}&type=group"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for item in data:
                if item.get('label', '').lower() == group_name.lower():
                    return item.get('id')
    except Exception as e:
        print(f"Ошибка при поиске группы: {e}")
    return None

def fetch_schedule_from_api(group_id, start_date, end_date):
    url = f"https://rasp.omgtu.ru/api/schedule/group/{group_id}?start={start_date}&finish={end_date}&lng=1"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Ошибка при скачивании расписания: {e}")
    return []

def format_lesson(lesson):
    time = f"{lesson.get('beginLesson', '')} - {lesson.get('endLesson', '')}"
    discipline = lesson.get('discipline', 'Без названия')
    kind = lesson.get('kindOfWork', '')
    auditorium = f"{lesson.get('building', '')} корп., ауд. {lesson.get('auditorium', '')}"
    lecturer = lesson.get('lecturer_title') or lesson.get('lecturer') or "Не указан"
    
    return (
        f"🕒 *{time}*\n"
        f"📘 {discipline} ({kind})\n"
        f"🏫 {auditorium}\n"
        f"👨‍🏫 Преп: {lecturer}"
    )

# --- 2. ПРИВЕТСТВИЕ И СОХРАНЕНИЕ ГРУППЫ ---

@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    
    markup = types.ReplyKeyboardRemove()
    bot.send_message(
        chat_id, 
        "Привет! 👋 Я бот-расписание ОмГТУ.\n\nВведи название своей группы (например: ПЭ-231н):",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_group)

def process_group(message):
    chat_id = message.chat.id
    group_name = message.text.strip()
    
    bot.send_message(chat_id, "⏳ Ищу группу на сервере РУЗ...")
    
    group_id = get_group_id(group_name)
    
    if not group_id:
        msg = bot.send_message(
            chat_id, 
            f"❌ Группа `{group_name}` не найдена на сайте ОмГТУ.\nПроверь опечатку и введи заново:"
        )
        bot.register_next_step_handler(msg, process_group)
        return

    user_data[chat_id]['group_name'] = group_name
    user_data[chat_id]['group_id'] = group_id
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton(BTN_TODAY), types.KeyboardButton(BTN_TOMORROW),
        types.KeyboardButton(BTN_WEEK), types.KeyboardButton(BTN_OTHER)
    )
    markup.add(types.KeyboardButton(BTN_CHANGE_GROUP))
    
    bot.send_message(
        chat_id, 
        f"✅ Группа *{group_name}* успешно найдена и привязана!\n\nВыбери период:", 
        reply_markup=markup, parse_mode='Markdown'
    )

# --- 3. ОБРАБОТКА ЗАПРОСОВ ---

@bot.message_handler(content_types=['text'])
def handle_requests(message):
    chat_id = message.chat.id
    text = message.text
    
    if text == BTN_CHANGE_GROUP:
        msg = bot.send_message(
            chat_id, 
            "Введи название новой группы (например: ПЭ-231н):",
            reply_markup=types.ReplyKeyboardRemove() 
        )
        bot.register_next_step_handler(msg, process_group)
        return

    if chat_id not in user_data or 'group_id' not in user_data[chat_id]:
        start_message(message)
        return
        
    group_id = user_data[chat_id]['group_id']
    group_name = user_data[chat_id]['group_name']
    
    today = datetime.now()
    
    if text == BTN_TODAY:
        date_str = today.strftime("%Y.%m.%d")
        get_and_send_schedule(chat_id, group_id, group_name, date_str, date_str, f"📅 *Сегодня ({date_str})*")
        
    elif text == BTN_TOMORROW:
        tomorrow = today + timedelta(days=1)
        date_str = tomorrow.strftime("%Y.%m.%d")
        get_and_send_schedule(chat_id, group_id, group_name, date_str, date_str, f"📆 *Завтра ({date_str})*")
        
    elif text == BTN_WEEK:
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        start_str = start_of_week.strftime("%Y.%m.%d")
        end_str = end_of_week.strftime("%Y.%m.%d")
        get_and_send_schedule(chat_id, group_id, group_name, start_str, end_str, f"🗓 *Неделя ({start_str} - {end_str})*")
        
    elif text == BTN_OTHER:
        # ОБНОВЛЕННАЯ ПОДСКАЗКА
        msg = bot.send_message(
            chat_id, 
            "Напиши дату (день, месяц, год)\n"
            "Например: `10 11 26` или `1 9 25`",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, handle_custom_date)

# --- УМНАЯ ОБРАБОТКА ПОЛЬЗОВАТЕЛЬСКОЙ ДАТЫ ---
def handle_custom_date(message):
    chat_id = message.chat.id
    raw_text = message.text.strip()
    
    # Меняем возможные точки, запятые и слэши на пробелы, чтобы юзер не ошибся
    normalized_text = raw_text.replace('.', ' ').replace(',', ' ').replace('/', ' ')
    parts = normalized_text.split()
    
    # Проверяем, что введено именно 3 блока цифр
    if len(parts) != 3:
        msg = bot.send_message(chat_id, "❌ Неверный формат. Нужно ввести 3 числа: день, месяц и год (например: 10 11 26):")
        bot.register_next_step_handler(msg, handle_custom_date)
        return

    day, month, year = parts
    
    # Функция zfill(2) автоматически добавляет ноль спереди, если строка из 1 символа (1 -> 01, 10 -> 10)
    day = day.zfill(2)
    month = month.zfill(2)
    
    # Если юзер ввел год двумя цифрами (26), делаем из него 2026
    if len(year) == 2:
        year = "20" + year
        
    try:
        # Пытаемся собрать реальную дату (это заодно отсеет несуществующие даты вроде 32 13 26)
        valid_date = datetime(int(year), int(month), int(day))
        
        # Формат для API ОмГТУ (ГГГГ.ММ.ДД)
        api_date_str = valid_date.strftime("%Y.%m.%d")
        # Красивый формат для вывода в чат (ДД.ММ.ГГГГ)
        display_date_str = valid_date.strftime("%d.%m.%Y")
        
        group_id = user_data[chat_id]['group_id']
        group_name = user_data[chat_id]['group_name']
        
        get_and_send_schedule(chat_id, group_id, group_name, api_date_str, api_date_str, f"🔍 *Расписание на {display_date_str}*")
        
    except ValueError:
        # Сработает, если ввели буквы вместо цифр или 30 февраля
        msg = bot.send_message(chat_id, "❌ Ошибка в дате. Проверь числа и попробуй снова (например: 10 11 26):")
        bot.register_next_step_handler(msg, handle_custom_date)

# --- 4. ВЫВОД РАСПИСАНИЯ ПО ДАТАМ ---

def get_and_send_schedule(chat_id, group_id, group_name, start_date, end_date, title_text):
    bot.send_chat_action(chat_id, 'typing')
    
    schedule_data = fetch_schedule_from_api(group_id, start_date, end_date)
    
    if not schedule_data:
        bot.send_message(chat_id, f"{title_text} | {group_name}\n\n🎉 Пар нет, можно отдыхать!", parse_mode='Markdown')
        return

    schedule_by_date = {}
    for lesson in schedule_data:
        d = lesson.get("date")
        if d not in schedule_by_date:
            schedule_by_date[d] = []
        schedule_by_date[d].append(lesson)

    response_text = f"{title_text} | {group_name}\n\n"
    
    for d in sorted(schedule_by_date.keys()):
        day_str = schedule_by_date[d][0].get("dayOfWeekString", "")
        response_text += f"🔹 *{d} ({day_str})*\n\n"
        
        daily_lessons = sorted(schedule_by_date[d], key=lambda x: x.get('beginLesson', ''))
        for lesson in daily_lessons:
            response_text += format_lesson(lesson) + "\n\n"

    if len(response_text) > 4000:
        response_text = response_text[:4000] + "\n\n... (обрезано)"

    bot.send_message(chat_id, response_text, parse_mode='Markdown')

if __name__ == '__main__':
    print("Бот запущен, парсер дат улучшен!")
    bot.polling(none_stop=True)