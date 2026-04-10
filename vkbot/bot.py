import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

import requests
from datetime import datetime, timedelta

# 🔑 ВСТАВЬ СВОЙ ТОКЕН ГРУППЫ VK
TOKEN = "ТВОЙ_VK_TOKEN"

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


def format_lesson(lesson):
    return (
        f"🕒 {lesson.get('start', '')} - {lesson.get('end', '')}\n"
        f"📘 {lesson.get('description', '')}\n"
        f"🏫 {lesson.get('location', '')}\n"
        f"👨‍🏫 {lesson.get('lecturer') or 'Не указан'}\n"
    )


def send(user_id, text):
    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=get_random_id()
    )


# ---------- ЛОГИКА ----------

def handle_start(user_id):
    user_data[user_id] = {}
    send(user_id, "Привет! 👋\nВведи свою группу (например: ПЭ-231н):")


def handle_group(user_id, text):
    send(user_id, "⏳ Ищу группу...")

    group_id = get_group_id(text)

    if not group_id:
        send(user_id, "❌ Группа не найдена, попробуй снова:")
        return

    user_data[user_id]["group_name"] = text
    user_data[user_id]["group_id"] = group_id

    send(user_id,
         f"✅ Группа {text} сохранена!\n\n"
         f"{BTN_TODAY}\n{BTN_TOMORROW}\n{BTN_WEEK}\n{BTN_OTHER}\n{BTN_CHANGE_GROUP}")


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


def handle_buttons(user_id, text):
    today = datetime.now()

    if text == BTN_TODAY:
        d = today.strftime("%Y.%m.%d")
        get_schedule(user_id, d, d, "Сегодня")

    elif text == BTN_TOMORROW:
        d = (today + timedelta(days=1)).strftime("%Y.%m.%d")
        get_schedule(user_id, d, d, "Завтра")

    elif text == BTN_WEEK:
        start = today.strftime("%Y.%m.%d")
        end = (today + timedelta(days=6)).strftime("%Y.%m.%d")
        get_schedule(user_id, start, end, "🗓 Неделя")

    elif text == BTN_CHANGE_GROUP:
        user_data[user_id] = {}
        send(user_id, "Введи новую группу:")

    elif text == BTN_OTHER:
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


# ---------- ОСНОВНОЙ ЦИКЛ ----------

print("VK бот запущен...")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:

        user_id = event.user_id
        text = event.text.strip()

        if user_id not in user_data:
            handle_start(user_id)
            continue

        if "group_id" not in user_data[user_id]:
            handle_group(user_id, text)
            continue

        if text.replace(" ", "").isdigit():
            handle_custom_date(user_id, text)
        else:
            handle_buttons(user_id, text)