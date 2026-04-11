import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import requests
from datetime import datetime, timedelta

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
BTN_WEEK = "На неделю"
BTN_OTHER = "Другая дата"
BTN_CHANGE_GROUP = "Сменить группу"
BTN_BY_TEACHER = "По преподавателю"
BTN_SEARCH_GROUP = "По группе"

# ---------- API ОмГТУ ----------

def get_group_id(group_name):
    url = f"{API_BASE_URL}/api/search?term={group_name}&type=group"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            for item in data:
                if item.get("label", "").lower() == group_name.lower():
                    return item.get("id")
    except:
        pass
    return None


def fetch_schedule(group_id, start, end):
    url = f"{API_BASE_URL}/api/schedule/group/{group_id}?start={start}&finish={end}&lng=1"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []


def get_teacher_id(teacher_name):
    url = f"{API_BASE_URL}/api/search?term={teacher_name}&type=person"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            for item in data:
                if item.get("label", "").lower() == teacher_name.lower():
                    return item.get("id")
    except:
        pass
    return None


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
    if mode in ("group", "teacher"):
        return main_keyboard()
    return initial_keyboard()


def send(user_id, text, keyboard=None):
    # If no keyboard explicitly provided, choose one based on user's mode
    if keyboard is None:
        keyboard = get_keyboard_for_user(user_id)

    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=get_random_id(),
        keyboard=keyboard
    )


def main_keyboard():
    kb = VkKeyboard(one_time=False)
    kb.add_button(BTN_TODAY, color=VkKeyboardColor.POSITIVE)
    kb.add_button(BTN_TOMORROW, color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button(BTN_WEEK, color=VkKeyboardColor.PRIMARY)
    kb.add_button(BTN_OTHER, color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button(BTN_CHANGE_GROUP, color=VkKeyboardColor.NEGATIVE)
    kb.add_button(BTN_BY_TEACHER, color=VkKeyboardColor.PRIMARY)
    return kb.get_keyboard()


def initial_keyboard():
    kb = VkKeyboard(one_time=True)
    kb.add_button(BTN_SEARCH_GROUP, color=VkKeyboardColor.PRIMARY)
    kb.add_button(BTN_BY_TEACHER, color=VkKeyboardColor.PRIMARY)
    return kb.get_keyboard()


# ---------- ЛОГИКА ----------

def handle_start(user_id):
    user_data[user_id] = {"mode": None}
    send(user_id, "Привет! 👋\nВыберите поиск:", keyboard=initial_keyboard())


def handle_group(user_id, text):
    send(user_id, "⏳ Ищу группу...")

    group_id = get_group_id(text)

    if not group_id:
        send(user_id, "❌ Группа не найдена, попробуй снова:")
        return

    user_data[user_id]["group_name"] = text
    user_data[user_id]["group_id"] = group_id
    user_data[user_id]["mode"] = "group"

    send(user_id,
        f"✅ Группа {text} сохранена!",
        keyboard=main_keyboard())


def get_schedule(user_id, start, end, title):
    group_id = user_data[user_id]["group_id"]
    group_name = user_data[user_id]["group_name"]

    data = fetch_schedule(group_id, start, end)

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
    if norm == BTN_BY_TEACHER.lower():
        user_data[user_id]["mode"] = "teacher"
        user_data[user_id].pop("group_id", None)
        user_data[user_id].pop("group_name", None)
        send(user_id, "Введите фамилию преподавателя (например: Иванов):")
        return

    if norm == BTN_CHANGE_GROUP.lower():
        # Сбросим режим и вернём выбор поиска
        user_data[user_id] = {"mode": None}
        send(user_id, "Выберите поиск:", keyboard=initial_keyboard())
        return

    if norm == BTN_TODAY.lower():
        d = today.strftime("%Y.%m.%d")
        if user_data[user_id].get("mode") == "teacher":
            get_teacher_schedule(user_id, d, d, "Сегодня")
        else:
            get_schedule(user_id, d, d, "Сегодня")

    elif norm == BTN_TOMORROW.lower():
        d = (today + timedelta(days=1)).strftime("%Y.%m.%d")
        if user_data[user_id].get("mode") == "teacher":
            get_teacher_schedule(user_id, d, d, "Завтра")
        else:
            get_schedule(user_id, d, d, "Завтра")

    elif norm == BTN_WEEK.lower():
        start = today.strftime("%Y.%m.%d")
        end = (today + timedelta(days=6)).strftime("%Y.%m.%d")
        if user_data[user_id].get("mode") == "teacher":
            get_teacher_schedule(user_id, start, end, "🗓 Неделя")
        else:
            get_schedule(user_id, start, end, "🗓 Неделя")

    elif norm == BTN_OTHER.lower():
        send(user_id, "Введи дату: ДД ММ ГГ (например: 10 11 26)")


def handle_custom_date(user_id, text):
    try:
        d, m, y = text.split()

        if len(y) == 2:
            y = "20" + y

        date = datetime(int(y), int(m), int(d))
        date_str = date.strftime("%Y.%m.%d")

        get_schedule(user_id, date_str, date_str,
                     f"🔍 {date.strftime('%d.%m.%Y')}")

    except:
        send(user_id, "❌ Ошибка даты, попробуй ещё раз")


def handle_teacher(user_id, text):
    send(user_id, "⏳ Ищу преподавателя...")

    teacher_id = get_teacher_id(text)

    if not teacher_id:
        send(user_id, "❌ Преподаватель не найден, попробуй снова:")
        return

    user_data[user_id]["teacher_name"] = text
    user_data[user_id]["teacher_id"] = teacher_id
    user_data[user_id]["mode"] = "teacher"

    send(user_id,
         f"✅ Преподаватель {text} сохранён!",
         keyboard=main_keyboard())


# ---------- ОСНОВНОЙ ЦИКЛ ----------

print("VK бот запущен...")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:

        user_id = event.user_id
        text = event.text.strip()

        if user_id not in user_data:
            handle_start(user_id)
            continue

        # Если режим еще не выбран — ожидаем выбор кнопки "По группе"/"По преподавателю"
        if user_data[user_id].get("mode") is None:
            norm = text.strip().lower()
            if norm == BTN_SEARCH_GROUP.lower():
                user_data[user_id]["mode"] = "group"
                send(user_id, "Введи свою группу (например: ПЭ-231н):")
                continue
            elif norm == BTN_BY_TEACHER.lower():
                user_data[user_id]["mode"] = "teacher"
                send(user_id, "Введите фамилию преподавателя (например: Иванов):")
                continue
            else:
                send(user_id, "Пожалуйста, выбери способ поиска:", keyboard=initial_keyboard())
                continue

        if user_data[user_id].get("mode") == "group" and "group_id" not in user_data[user_id]:
            handle_group(user_id, text)
            continue

        if user_data[user_id].get("mode") == "teacher" and "teacher_id" not in user_data[user_id]:
            handle_teacher(user_id, text)
            continue

        if text.replace(" ", "").isdigit():
            handle_custom_date(user_id, text)
        else:
            handle_buttons(user_id, text)