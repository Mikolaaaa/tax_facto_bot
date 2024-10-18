from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp
import logging
import math
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Задай api_id, api_hash и токен бота
app = Client("my_bot", api_id=20038786, api_hash="8f9173e9b27beadd3dc35475ef1de1c2",
             bot_token="7840094271:AAEYvU6hieJoJOcPs3vUVmdaBMZGghGhnlI")

global_data = {}
global_data2 = {}
court_cases_global = []
court_cases_global2 = []
filter_values_global = []
filter_values_global2 = []
user_filters = {}
user_filters2 = {}

# Словарь для перевода фильтров
filter_translation = {
    "reasons": "ПРИЧИНЫ",
    "after_effect": "СЛЕДСТВИЯ",
    "qualification_note_references": "КВАЛИФИКАЦИЯ НО ДЕЙСТВИЙ НП",
    "circumstances_meeting": "ОБСТОЯТЕЛЬСТВА НП (СДЕЛКА)",
    "article_nk_rf_forfeit": "ШТРАФ (СТАТЬЯ)",
    "article_nk_rf_episode": "ЭПИЗОД (СТАТЬЯ)",
    "article_nk_rf_base": "СУДЕБНЫЙ АКТ (ОСНОВНАЯ СТАТЬЯ)",
    "theme_precedent": "ТЕМА ПРЕЦЕДЕНТА",
    "evidence":"ДОКАЗАТЕЛЬСТВА",
    "article": "НОРМА НК РФ",
    "table_violation": "ОПИСАНИЕ НАРУШЕНИЯ",
    "table_assessment_of_the_court": "ОЦЕНКА СУДА",
    "table_precendent": "ПРЕЦЕДЕНТ",
    "tax": "ПОШЛИНЫ"
}

# Максимальное количество кнопок на одной странице
BUTTONS_PER_PAGE = 10


@app.on_message(filters.command("precedent2"))
async def handle_message(client, message):
    user_id = message.from_user.id  # Получаем user_id
    logger.info(f"Получено сообщение от пользователя {message.from_user.id}: {message.text}")

    if user_id not in user_filters2:
        user_filters2[user_id] = {}

    async with aiohttp.ClientSession() as session:
        try:
            # Отправляем POST-запрос для получения фильтров
            async with session.post("http://195.19.40.209:8001/api/precedent-2/") as response:
                logger.info(f"Получен ответ от API с кодом: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    #print(data)
                    logger.debug(f"Ответ от API: {data}")

                    # Обрабатываем фильтры
                    filters_data = data.get('filters', {})
                    if filters_data:
                        print(f"filters: {filters_data}")
                        # Создаем кнопки для фильтров с пагинацией
                        filter_buttons = create_filter_buttons2(filters_data, user_id)
                        await message.reply("Выберите фильтр:", reply_markup=filter_buttons)
                    else:
                        await message.reply("Нет доступных фильтров.")
                        logger.warning("Нет доступных фильтров.")
                else:
                    pass
                    """await message.reply("Ошибка при запросе к API.")
                    logger.error(f"Ошибка при запросе к API: {response.status}")"""
        except Exception as e:
            logger.exception("Ошибка при выполнении запроса к API")
            await message.reply("Произошла ошибка при обращении к серверу.")


def create_filter_buttons2(filters_data, user_id, page=1):
    buttons = []
    start_index = (page - 1) * BUTTONS_PER_PAGE
    end_index = start_index + BUTTONS_PER_PAGE
    filter_items = list(filters_data.items())[start_index:end_index]
    #print(f"filter_items {filter_items}")
    #print(f"filters_data {filters_data}")
    #print(f"user_filters {user_filters}")

    for filter_key, filter_values in filter_items:
        #print(f"filter_key: {filter_key}")
        if filter_key in user_filters2[user_id]:
            pass
        else:
            translated_filter = filter_translation.get(filter_key, filter_key)
            buttons.append([InlineKeyboardButton(translated_filter + '2', callback_data=f"filter2_{filter_key}")])

    # Добавляем кнопки пагинации
    total_pages = math.ceil(len(filters_data) / BUTTONS_PER_PAGE)
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page2_{page - 1}"))
    if page < total_pages:
        pagination_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"page2_{page + 1}"))

    if pagination_buttons:
        buttons.append(pagination_buttons)

    if page == 1:    # Добавляем кнопку для сброса фильтров
        buttons.append([InlineKeyboardButton(text="Сбросить фильтры", callback_data="reset2_filters2")])

    return InlineKeyboardMarkup(buttons)


# Обработчик нажатия на фильтр
@app.on_callback_query(filters.regex(r"filter2_(.+)"))
async def on_filter_selected(client, callback_query):
    global filter_values_global2
    # Получаем все части после 'filter_' и объединяем их в строку
    filter_key = "_".join(callback_query.data.split("_")[1:])

    logger.info(f"Фильтр выбран: {filter_key}")

    user_id = callback_query.from_user.id
    print(f"user_id {user_id}")

    # Подготовка данных для POST-запроса
    filters_data = {
        "filters": user_filters[user_id]  # Используем все выбранные фильтры пользователя
    }
    print(f"filters_data {filters_data}")

    # Отправляем POST-запрос снова для получения данных фильтра
    async with aiohttp.ClientSession() as session:
        async with session.post("http://195.19.40.209:8001/api/precedent-2/", json=filters_data) as response:
            if response.status == 200:
                data = await response.json()
                # Удаляем предыдущее сообщение, если оно не "Выберите номер дела:"
                """if callback_query.message.text != "Выберите номер дела:":
                    await callback_query.message.delete()"""
                filters_data = data.get('filters', {})
                #print(filter_key)
                filter_values = filters_data.get(filter_key, [])
                filter_values_global2 = filter_values
                print(f"filter_values: {filter_values}")
                #print(f"filter_values {filter_values}")
                #print(f"filters_data {filters_data}")

                # Формируем сообщение с полным названием
                full_filter_name = filter_translation.get(filter_key, filter_key)

                # Удаляем предыдущее сообщение, если оно не "Выберите номер дела:"
                if callback_query.message.text != "Выберите номер дела:":
                    await callback_query.message.delete()

                # Создаем кнопки для значений фильтра
                value_buttons = await create_value_buttons2(filter_values, filter_key)
                await callback_query.message.reply_text(f"Выберите значение для {full_filter_name}:", reply_markup=value_buttons)



# Обработчик нажатий на пагинацию значений фильтра
@app.on_callback_query(filters.regex(r"value2_page2_(.+)"))
async def handle_pagination(client, callback_query):
    # Извлекаем информацию из callback_data
    #print(callback_query.data.split("_") )
    filter_key = "_".join(callback_query.data.split("_")[2:-1])
    new_page = callback_query.data.split("_")[-1]
    #print(f"filter_key: {filter_key}")
    #print(f"new_page: {new_page}")
    # _, filter_key, new_page = callback_query.data.split("_")
    new_page = int(new_page)

    # Получите текущие фильтры (например, из состояния пользователя или базы данных)
    # Предполагаем, что filter_values и filter_key доступны здесь
    filter_values = filter_values_global2

    # Создаем новые кнопки значений с текущей страницей
    new_buttons = await create_value_buttons2(filter_values, filter_key, page=new_page)

    # Обновляем сообщение с новыми кнопками
    await callback_query.message.edit_reply_markup(new_buttons)

    # Ответим пользователю, чтобы избежать сообщения об ошибке
    await callback_query.answer()



# Функция для создания кнопок значений фильтра с пагинацией
async def create_value_buttons2(filter_values, filter_key, page=1):
    buttons = []
    start_index = (page - 1) * BUTTONS_PER_PAGE
    end_index = start_index + BUTTONS_PER_PAGE
    filter_values_new = filter_values[start_index:end_index]

    for value in filter_values_new:
        name = value.get(f"{filter_key}__name", "Нет данных")
        id_value = value.get(f"{filter_key}__id", value.get(f"{filter_key}_id", 0))
        buttons.append([InlineKeyboardButton(name, callback_data=f"value2_{filter_key}_{id_value}")])

    total_pages = math.ceil(len(filter_values) / BUTTONS_PER_PAGE)
    pagination_buttons = []

    if page > 1:
        pagination_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"value2_page2_{filter_key}_{page - 1}"))

    if page < total_pages:
        print(222222222222222222222222222222222222222222222)
        pagination_buttons.append(
            InlineKeyboardButton("Вперед ➡️", callback_data=f"value2_page2_{filter_key}_{page + 1}"))

    if pagination_buttons:
        buttons.append(pagination_buttons)

    return InlineKeyboardMarkup(buttons)


# Обработчик для сброса фильтров
@app.on_callback_query(filters.regex(r"reset2_filters2"))
async def reset_filters(client, callback_query):
    global user_filters
    user_id = callback_query.from_user.id  # Получаем ID пользователя

    # Очищаем фильтры для текущего пользователя
    if user_id in user_filters2:
        user_filters2[user_id] = {}

    # Отправляем запрос на получение доступных фильтров с "пустыми" фильтрами
    filters_data = {
        "filters": {}  # Отправляем пустые фильтры, чтобы получить новые доступные
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("http://195.19.40.209:8001/api/precedent-2/", json=filters_data) as response:
                if response.status == 200:
                    data = await response.json()

                    # Удаляем предыдущее сообщение, если оно не "Выберите номер дела:"
                    if callback_query.message.text != "Выберите номер дела:":
                        await callback_query.message.delete()

                    # Отправляем обновленные фильтры пользователю
                    filters_data = data.get('filters', {})
                    if filters_data:
                        filter_buttons = create_filter_buttons2(filters_data, user_id)
                        await callback_query.message.reply("Фильтры сброшены. Выберите новый фильтр:",
                                                           reply_markup=filter_buttons)
                else:
                    await callback_query.message.reply("Ошибка при запросе к API.")
        except Exception as e:
            logger.exception("Ошибка при выполнении запроса к API")
            await callback_query.message.reply("Произошла ошибка при обращении к сервер.")


# Обработчик нажатия на значение фильтра
@app.on_callback_query(filters.regex(r"value2_(.+)"))
async def on_value_selected(client, callback_query):
    global global_data2, court_cases_global2, user_filters2
    data_parts = callback_query.data.split("_")
    filter_key = "_".join(data_parts[1:-1]) if len(data_parts) > 2 else data_parts[1]
    value_id = data_parts[-1]
    user_id = callback_query.from_user.id  # Получаем ID пользователя

    # Добавляем выбранное значение в словарь с фильтрами пользователя
    if user_id not in user_filters2:
        user_filters2[user_id] = {}

    # Добавляем новое значение фильтра к уже существующим
    if filter_key not in user_filters2[user_id]:
        user_filters2[user_id][filter_key] = []
    if value_id not in user_filters2[user_id][filter_key]:
        user_filters2[user_id][filter_key].append(value_id)

    # Подготовка данных для POST-запроса
    filters_data = {
        "filters": user_filters2[user_id]  # Используем все выбранные фильтры пользователя
    }

    #print(f"filters_data: {filters_data}")

    # Отправка POST-запроса с обновленными фильтрами
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("http://195.19.40.209:8001/api/precedent-2/", json=filters_data) as response:
                if response.status == 200:
                    data = await response.json()
                    global_data2 = data

                    # Удаляем предыдущее сообщение, если оно не "Выберите номер дела:"
                    if callback_query.message.text != "Выберите номер дела:":
                        await callback_query.message.delete()

                    # Обрабатываем список дел
                    table_violation = data.get('table_violation', [])
                    table_assessment_of_the_court = data.get('table_assessment_of_the_court', [])
                    table_precendent = data.get('table_precendent', [])

                    print(f"table_violation: {table_violation}")
                    print(f"table_assessment_of_the_court: {table_assessment_of_the_court}")
                    print(f"table_precendent: {table_precendent}")

                    # Создаем кнопки
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("Описание нарушения", callback_data="show_violation")],
                        [InlineKeyboardButton("Оценка суда", callback_data="show_assessment")],
                        [InlineKeyboardButton("Прецедент", callback_data="show_precendent")],
                    ])

                    # Удаляем предыдущее сообщение, если оно не "Выберите номер дела:"
                    if callback_query.message.text != "Выберите номер дела:":
                        await callback_query.message.delete()

                    #print(f"user_filters2: {user_filters2}")

                    filters_data_local = data.get('filters', {})

                    value_translation = {}

                    for filter_key, values in filters_data_local.items():
                        #print(f"filter_key: {filter_key}")
                        #print(f"values: {values}")
                        for value in values:
                            # print(f"value: {value}")
                            value_id = value[f'{filter_key}__id']
                            value_name = value[
                                f'{filter_key}__name']  # или другой ключ, в зависимости от вашей структуры
                            value_translation[value_id] = value_name

                    # Формируем строку с выбранными фильтрами
                    selected_filters_message = "Фильтры:\n"
                    for k, v in user_filters2[user_id].items():
                        filter_name = filter_translation.get(k, k)  # Получаем название фильтра по ключу
                        selected_values = [f"**{value_translation.get(int(value_id), value_id)}**" for value_id in v]
                        selected_filters_message += f"{filter_name}: {', '.join(selected_values)}\n"

                    await callback_query.message.reply(f"{selected_filters_message}Выберите информацию для отображения:", reply_markup=keyboard)

                    filters_data = data.get('filters', {})

                    filter_buttons = create_filter_buttons2(filters_data, user_id)
                    #print(filter_buttons)
                    await callback_query.message.reply(f"Если нужно, выберите еще фильтр:", reply_markup=filter_buttons)
                else:
                    await callback_query.message.reply("Ошибка при запросе к API.")
        except Exception as e:
            logger.exception("Ошибка при выполнении запроса к API")
            await callback_query.message.reply("Произошла ошибка при обращении к сервер.")





async def send_large_text(file_name, text, callback_query):
    # Если текст - это список, объединим его в строку
    if isinstance(text, list):
        text = "\n".join(text)  # Объединяем список в строку с разделителем \n

    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(text)

    await callback_query.message.reply_document(document=file_name)
    os.remove(file_name)  # Удаляем файл после отправки


@app.on_callback_query(filters.regex(r"show_violation"))
async def show_violation(client, callback_query):
    await callback_query.answer()  # Убираем "обработчик загрузки"
    violation_text = global_data2.get('table_violation', 'Нет данных')
    await send_large_text('violation.txt', violation_text, callback_query)


@app.on_callback_query(filters.regex(r"show_assessment"))
async def show_assessment(client, callback_query):
    await callback_query.answer()  # Убираем "обработчик загрузки"
    assessment_text = global_data2.get('table_assessment_of_the_court', 'Нет данных')
    await send_large_text('assessment.txt', assessment_text, callback_query)


@app.on_callback_query(filters.regex(r"show_precendent"))
async def show_precendent(client, callback_query):
    await callback_query.answer()  # Убираем "обработчик загрузки"
    precedent_text = global_data2.get('table_precendent', 'Нет данных')
    await send_large_text('precedent.txt', precedent_text, callback_query)


app.run()
