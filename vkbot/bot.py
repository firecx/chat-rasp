import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import requests
from datetime import datetime, timedelta
import re

# 🔑 ВСТАВЬ СВОЙ ТОКЕН ГРУППЫ VK
#TOKEN = "ТВОЙ_VK_TOKEN"

# Основной адрес API ОмГТУ
API_BASE_URL = "http://144.31.78.248:8080"

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

user_data = {}

# Кнопки
BTN_TODAY = "Сегодня"
BTN_TOMORROW = "Завтра"
BTN_FOR_WEEK = "На неделю"
BTN_OTHER_DATE = "Другая дата"
BTN_CHANGE_GROUP = "Сменить группу"
BTN_CHANGE_TEACHER = "Сменить преподавателя"
BTN_CHANGE_SEARCH = "Сменить поиск"
BTN_BY_TEACHER = "По преподавателю"
BTN_BY_GROUP = "По группе"
BTN_CANCEL = "Отмена"

# для сравнения
TODAY = "сегодня"
TOMORROW = "завтра"
FOR_WEEK = "на неделю"
OTHER_DATE = "другая дата"
CHANGE_GROUP = "сменить группу"
CHANGE_TEACHER = "сменить преподавателя"
CHANGE_SEARCH = "сменить поиск"
BY_TEACHER = "по преподавателю"
BY_GROUP = "по группе"
CANCEL = "отмена"

# -- API --

def get_groups_by_name(group_name):
    url = f"{API_BASE_URL}/api/search?term={group_name}&type=group"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None
        data = response.json()
        if len(data) == 0:
            return None
        else:
            return data
    except:
        pass
    return None

def get_teacher_by_name(teacher_name):
    url = f"{API_BASE_URL}/api/search?term={teacher_name}&type=person"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None
        data = response.json()
        if len(data) == 0:
            return None
        else:
            return data
    except:
        pass
    return None

def fetch_group_schedule(group_id, start, end):
    url = f"{API_BASE_URL}/api/schedule/group/{group_id}?start={start}&finish={end}&lng=1"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def fetch_teacher_schedule(teacher_id, start, end):
    url = f"{API_BASE_URL}/api/schedule/person/{teacher_id}?start={start}&finish={end}&lng=1"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []


def format_lesson(lesson):
    return (
        f"🕒 {lesson.get('beginLesson', '')} - {lesson.get('endLesson', '')}\n"
        f"📘 {lesson.get('discipline', '')}\n"
        f"🏫 {lesson.get('building', '')}, {lesson.get('auditorium', '')}\n"
        f"👨‍🏫 {lesson.get('lecturer') or 'Не указан'}\n"           
    )


def get_keyboard_for_user(user_id):
    mode = user_data.get(user_id, {}).get("mode")
    if mode == "group":
        return group_keyboard()
    elif mode == "teacher":
        return teacher_keyboard()
    else:
        return initial_keyboard()


def send(user_id, text, keyboard=None):
    # if keyboard is None:
    #     keyboard = get_keyboard_for_user(user_id)

    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=get_random_id(),
        keyboard=keyboard
    )

def initial_keyboard():
    kb = VkKeyboard(one_time=True)
    kb.add_button(BTN_BY_GROUP, color=VkKeyboardColor.PRIMARY)
    kb.add_button(BTN_BY_TEACHER, color=VkKeyboardColor.PRIMARY)
    return kb.get_keyboard()

def change_mode_keyboard():
    kb = VkKeyboard(one_time=True)
    kb.add_button(BTN_BY_GROUP, color=VkKeyboardColor.SECONDARY)
    kb.add_button(BTN_BY_TEACHER, color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button(BTN_CANCEL, color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()

def group_keyboard():
    kb = VkKeyboard(one_time=False)
    kb.add_button(BTN_TODAY, color=VkKeyboardColor.POSITIVE)
    kb.add_button(BTN_TOMORROW, color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button(BTN_FOR_WEEK, color=VkKeyboardColor.PRIMARY)
    kb.add_button(BTN_OTHER_DATE, color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    # swapped positions and colors per request
    kb.add_button(BTN_CHANGE_SEARCH, color=VkKeyboardColor.NEGATIVE)
    kb.add_button(BTN_CHANGE_GROUP, color=VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()


def teacher_keyboard():
    kb = VkKeyboard(one_time=False)
    kb.add_button(BTN_TODAY, color=VkKeyboardColor.POSITIVE)
    kb.add_button(BTN_TOMORROW, color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button(BTN_FOR_WEEK, color=VkKeyboardColor.PRIMARY)
    kb.add_button(BTN_OTHER_DATE, color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    # swapped positions and colors per request
    kb.add_button(BTN_CHANGE_SEARCH, color=VkKeyboardColor.NEGATIVE)
    kb.add_button(BTN_CHANGE_TEACHER, color=VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()

def cancel_keyboard():
    kb = VkKeyboard(one_time=True)
    kb.add_button(BTN_CANCEL, color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()

# -- ЛОГИКА --

def handle_start(user_id):
    user_data[user_id] = {"mode": None}


def handle_group(user_id, text):
    if text.lower() == CANCEL:
        if user_data[user_id].get("group_id") == None:
            user_data[user_id].pop("mode", None)
            send(user_id, "Действие отменено.")
            send(user_id, "Пожалуйста, выбери способ поиска:", keyboard=initial_keyboard())
            return
        else:
            send(user_id, "Действие отменено.", keyboard=group_keyboard())
            user_data[user_id]["mode"] = "group"
            return
    
    send(user_id, "⏳ Ищу группу...")

    groups = get_groups_by_name(text)

    if groups == None:
        send(user_id, "❌ Группа не найдена, попробуй снова", keyboard=cancel_keyboard())
        return
    elif len(groups) == 1:
        if groups[0].get("label", "").lower() == text.lower():
            user_data[user_id]["group_name"] = text.lower()
            user_data[user_id]["group_id"] = groups[0].get("id")
            user_data[user_id]["mode"] = "group"
            send(user_id,
                f"✅ Группа {text} сохранена!",
                keyboard=group_keyboard())
        else:
            send(user_id, f"Возможно вы имели в виду: {groups[0].get('label', '')}")
    else:
        groups_found = ""
        for group in groups:
            groups_found += "\n" + group.get("label", "")
        send(user_id, f"Возможно вы имели в виду: {groups_found}")

def handle_teacher(user_id, text):
    if text.lower() == CANCEL:
        if user_data[user_id].get("teacher_id") == None:
            user_data[user_id].pop("mode", None)
            send(user_id, "Действие отменено.")
            send(user_id, "Пожалуйста, выбери способ поиска:", keyboard=initial_keyboard())
            return
        else:
            send(user_id, "Действие отменено.", keyboard=teacher_keyboard())
            user_data[user_id]["mode"] = "teacher"
            return
    
    send(user_id, "⏳ Ищу преподавателя...")

    teachers = get_teacher_by_name(text)

    if teachers == None:
        send(user_id, "❌ Преподаватель не найден, попробуй снова", keyboard=cancel_keyboard())
        return
    elif len(teachers) == 1:
        if teachers[0].get("label", "").lower() == text.lower():
            user_data[user_id]["teacher_name"] = text
            user_data[user_id]["teacher_id"] = teachers[0].get("id")
            user_data[user_id]["mode"] = "teacher"
            send(user_id,
                 f"✅ Преподаватель {text} сохранён!",
                 keyboard=teacher_keyboard())
        else:
            send(user_id, f"Возможно вы имели в виду: {teachers[0].get('label', '')}")
    else:
        teachers_found = ""
        for teacher in teachers:
            teachers_found += "\n" + teacher.get("label", "")
        send(user_id, f"Возможно вы имели в виду: {teachers_found}")


def get_group_schedule(user_id, start, end, title):
    group_id = user_data[user_id]["group_id"]
    group_name = user_data[user_id]["group_name"]

    data = fetch_group_schedule(group_id, start, end)

    if not data:
        send(user_id, f"{title} | {group_name}\n\n🎉 Пар нет!")
        return

    text = f"{title} | {group_name}\n\n"

    for lesson in data:
        text += format_lesson(lesson) + "\n"

    send(user_id, text)


def get_teacher_schedule(user_id, start, end, title):
    teacher_id = user_data[user_id]["teacher_id"]
    teacher_name = user_data[user_id]["teacher_name"]

    data = fetch_teacher_schedule(teacher_id, start, end)

    if not data:
        send(user_id, f"{title} | {teacher_name}\n\n🎉 Пар нет!")
        return

    text = f"{title} | {teacher_name}\n\n"

    for lesson in data:
        text += format_lesson(lesson) + "\n"

    send(user_id, text)


def handle_buttons(user_id, text):
    today = datetime.now()

    norm = text.strip().lower()

    # Переключение режимов
    if norm == BY_TEACHER:
        user_data[user_id]["mode"] = "teacher"
        user_data[user_id].pop("group_id", None)
        user_data[user_id].pop("group_name", None)
        send(user_id, "Введите имя преподавателя (например: Фамилия И.О.):", keyboard=cancel_keyboard())
        return

    if norm == CHANGE_GROUP:
        # Сменить группу — попросим ввести новую группу
        user_data[user_id]["mode"] = "CHANGE_GROUP"
        send(user_id, "Введи свою группу (например: ПЭ-231н):", keyboard=cancel_keyboard())
        return

    if norm == CHANGE_TEACHER:
        # Сменить преподавателя — попросим ввести фамилию
        user_data[user_id]["mode"] = "CHANGE_TEACHER"
        send(user_id, "Введите имя преподавателя (например: Фамилия И.О.):", keyboard=cancel_keyboard())
        return

    if norm == CHANGE_SEARCH:
        # Вернуться к выбору поиска (группа/преподаватель)
        user_data[user_id]["change_mode"] = True
        send(user_id, "Выберите поиск:", keyboard=change_mode_keyboard())
        return

    if norm == TODAY:
        d = today.strftime("%Y.%m.%d")
        if user_data[user_id].get("mode") == "teacher":
            get_teacher_schedule(user_id, d, d, "Сегодня")
        else:
            get_group_schedule(user_id, d, d, "Сегодня")

    elif norm == TOMORROW:
        d = (today + timedelta(days=1)).strftime("%Y.%m.%d")
        if user_data[user_id].get("mode") == "teacher":
            get_teacher_schedule(user_id, d, d, "Завтра")
        else:
            get_group_schedule(user_id, d, d, "Завтра")

    elif norm == FOR_WEEK:
        start = today.strftime("%Y.%m.%d")
        end = (today + timedelta(days=6)).strftime("%Y.%m.%d")
        if user_data[user_id].get("mode") == "teacher":
            get_teacher_schedule(user_id, start, end, "🗓 Неделя")
        else:
            get_group_schedule(user_id, start, end, "🗓 Неделя")

    elif norm == OTHER_DATE:
        user_data[user_id]["awaiting_date"] = True
        send(user_id, "Введи дату: ДД ММ ГГ или диапазон: ДД ММ ГГ - ДД ММ ГГ (например: 10 11 26 или 10 11 26 - 12 11 26)", keyboard=cancel_keyboard())


def handle_custom_date(user_id, text):
    if text.strip().lower() == CANCEL:
        user_data[user_id].pop("awaiting_date", None)
        if user_data[user_id].get("mode") == "teacher":
            send(user_id, "Действие отменено.", keyboard=teacher_keyboard())
        elif user_data[user_id].get("mode") == "group":
            send(user_id, "Действие отменено.", keyboard=group_keyboard())
        return
    # This handler supports single date (`DD MM YY`) or range (`DD MM YY - DD MM YY`).
    try:
        parts = re.split(r"\s*[-–—−]\s*", text.strip())

        def parse_dmY(s):
            d, m, y = s.split()
        if len(y) == 2:
            y = "20" + y
            return datetime(int(y), int(m), int(d))

        if len(parts) == 1:
            date = parse_dmY(parts[0])
            date_str = date.strftime("%Y.%m.%d")
            title = f"🔍 {date.strftime('%d.%m.%Y')}"
            if user_data[user_id].get("mode") == "teacher":
                get_teacher_schedule(user_id, date_str, date_str, title)
            elif user_data[user_id].get("mode") == "group":
                get_group_schedule(user_id, date_str, date_str, title)

        elif len(parts) == 2:
            start = parse_dmY(parts[0])
            end = parse_dmY(parts[1])
            if start > end:
                start, end = end, start
            start_str = start.strftime("%Y.%m.%d")
            end_str = end.strftime("%Y.%m.%d")
            title = f"🔍 {start.strftime('%d.%m.%Y')} - {end.strftime('%d.%m.%Y')}"
            if user_data[user_id].get("mode") == "teacher":
                get_teacher_schedule(user_id, start_str, end_str, title)
            elif user_data[user_id].get("mode") == "group":
                get_group_schedule(user_id, start_str, end_str, title)

        else:
            raise ValueError("invalid format")

    except Exception:
        send(user_id, "❌ Ошибка даты, попробуй ещё раз")




# -- ОСНОВНОЙ ЦИКЛ --

print("VK бот запущен...")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:

        user_id = event.user_id
        text = event.text.strip()

        if user_id not in user_data:
            handle_start(user_id)

        # Если режим еще не выбран — ожидаем выбор кнопки "По группе"/"По преподавателю"
        if user_data[user_id].get("mode") is None or user_data[user_id].get("mode") == None:
            norm = text.strip().lower()
            if norm == BY_TEACHER:
                user_data[user_id]["mode"] = "teacher"
                send(user_id, "Введите имя преподавателя (например: Фамилия И.О.):", keyboard=cancel_keyboard())
                continue
            elif norm == BY_GROUP:
                user_data[user_id]["mode"] = "group"
                send(user_id, "Введи свою группу (например: ПЭ-231н):", keyboard=cancel_keyboard())
                continue
            else:
                send(user_id, "Пожалуйста, выбери способ поиска:", keyboard=initial_keyboard())
                continue

        if user_data[user_id].get("awaiting_date"):
            handle_custom_date(user_id, text)
            continue
        elif user_data[user_id].get("change_mode"):
            user_data[user_id].pop("change_mode", None)
            if text.strip().lower() == CANCEL:
                send(user_id, "Действие отменено.", keyboard=get_keyboard_for_user(user_id))
                continue
            elif text.strip().lower() == BY_TEACHER:
                user_data[user_id].pop("teacher_name", None)
                user_data[user_id].pop("teacher_id", None)
                user_data[user_id]["mode"] = "teacher"
                
                send(user_id, "Введите имя преподавателя (например: Фамилия И.О.):")
                continue
            elif text.strip().lower() == BY_GROUP:
                user_data[user_id].pop("group_name", None)
                user_data[user_id].pop("group_id", None)
                user_data[user_id]["mode"] = "group"
                
                send(user_id, "Введи свою группу (например: ПЭ-231н):")
            continue
        else:
            if user_data[user_id].get("mode") == "teacher":
                if "teacher_id" not in user_data[user_id]:
                    handle_teacher(user_id, text)
                    continue
            elif user_data[user_id].get("mode") == "group":
                if "group_id" not in user_data[user_id]:
                    handle_group(user_id, text)
                    continue
            elif user_data[user_id].get("mode") == "CHANGE_GROUP":
                handle_group(user_id, text)
                continue
            elif user_data[user_id].get("mode") == "CHANGE_TEACHER":
                handle_teacher(user_id, text)
                continue


            handle_buttons(user_id, text)