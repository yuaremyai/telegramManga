import telebot
import image_processing
from search_title import Search
from db_control import DataBase
from dotenv import dotenv_values

token = dotenv_values('.env')
bot = telebot.TeleBot(token=token["TOKEN"])
search = Search()
db = DataBase()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    db.init_user(message.chat.id)
    bot.send_message(message.chat.id, "Привет! Я Бот для чтения манги\n"
                                      "Чтобы выбрать что почитать используй команду /search название_манги\n"
                                      "Напиши /help чтобы посмотреть список всех команд ")


@bot.message_handler(commands=['help'])
def show_commands(message):
    bot.send_message(message.chat.id, "/help - Посмотреть все команды\n"
                                      "/search - Найти мангу по названию или сменить текущую\n"
                                      "/next - Следующая страница\n"
                                      "/move - Сменить том\n"
                                      "/chapter - Сменить главу\n"
                                      "/page - Сменить страницу\n"
                                      "/read - Отправляет текущую страницу")


@bot.message_handler(commands=['search'])
def ask_manga_title(message):
    sent_msg = bot.send_message(message.chat.id, "Введите название манги")
    bot.register_next_step_handler(sent_msg, get_manga_title)


def get_manga_title(message):
    title = message.text.strip()
    search_result = search.search_manga(title)
    if not search_result:
        sent_msg = bot.send_message(message.chat.id, "Ничего не найдено🙁 попробуй ещё")
        bot.register_next_step_handler(sent_msg, get_manga_title)
    else:
        formated_result = search.form_result(search_result)
        msg = formated_msg(formated_result)
        sent_msg = bot.send_message(message.chat.id, f"Выбери номер нужной манги\n{msg}")
        bot.register_next_step_handler(sent_msg, choose_title, formated_result)


def formated_msg(formated_search_result):
    msg = ""
    for i, val in enumerate(formated_search_result.keys(), 1):
        msg += f"/{i} {val}\n"
    return msg


def choose_title(message, formated_result):
    number = message.text.replace("/", "")
    try:
        number = int(number)
        if number > len(formated_result) or number < 1:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "Кажеться ты ввёл не число или оно за пределами списка. Попробуй ещё")
        bot.register_next_step_handler(message, choose_title, formated_result)
        return
    title = list(formated_result.values())[number-1].split("/")[-2]
    update_title(message.chat.id, title)
    bot.send_message(message.chat.id, "Отлично! Чтобы начать читать используй /read")


def update_title(chat_id, title):
    db.update_column(chat_id, "title", title)
    db.update_column(chat_id, "volume", 0)
    db.update_column(chat_id, "chapter", 0)
    db.update_column(chat_id, "page", 0)
    url = get_url(chat_id)
    update_max_values(chat_id)
    update_max_pages(chat_id, url)


@bot.message_handler(commands=['read'])
def get_current_page(message):
    url = get_url(message.chat.id)
    bot.send_message(message.chat.id, "Загружаю страницу")
    if search.is_long_images(url):
        read_long_image(message.chat.id, url)
    else:
        read_short_image(message.chat.id, url)


@bot.message_handler(commands=['next'])
def get_next_page(message):
    page = db.get_column(message.chat.id, "page") + 1  # Increment page
    max_page, chapter, max_chapter, volume, max_volume = db.get_multi_column(message.chat.id, ("max_page", "chapter",
                                                                                   "max_chapter", "volume", "max_volume"))
    if page + 1 > max_page:
        page = 0
        chapter += 1
    if chapter + 1 > max_chapter:
        chapter = 0
        volume += 1
    if volume + 1 > max_volume:
        bot.send_message(message.chat.id, "Поздравляю! Ты дочитал до конца\n"
                         "Если хочешь почитатать что-то ещё используй /search")
        return
    db.update_column(message.chat.id, "page", page)
    db.update_column(message.chat.id, "chapter", chapter)
    db.update_column(message.chat.id, "volume", volume)
    bot.send_message(message.chat.id, "Загружаю страницу")
    url = get_url(message.chat.id)
    update_max_values(message.chat.id)
    update_max_pages(message.chat.id, url)
    if search.is_long_images(url):
        read_long_image(message.chat.id, url)
    else:
        read_short_image(message.chat.id, url)


def get_url(chat_id):
    title, volume, chapter = db.get_multi_column(chat_id, ("title", "volume", "chapter"))
    links = search.get_groups(f"https://read.yagami.me/series/{title}")
    if not links:
        bot.send_message(chat_id, "Эта манга пустая. Выбери другую с помощью /search")
        return
    volume_links = links[volume]
    url = volume_links[list(volume_links.keys())[chapter]]
    return url


def update_max_pages(chat_id, url):
    if search.is_long_images(url):
        max_page = search.get_long_max_page(url)
    else:
        max_page = search.get_small_max_page(url)
    db.update_column(chat_id, "max_page", max_page)


def update_max_values(chat_id):
    title, volume, chapter = db.get_multi_column(chat_id, ("title", "volume", "chapter"))
    links = search.get_groups(f"https://read.yagami.me/series/{title}")
    db.update_column(chat_id, "max_volume", len(links))
    db.update_column(chat_id, "max_chapter", len(links[volume]))


def read_short_image(chat_id, url):
    page = db.get_column(chat_id, "page")
    img_url = search.get_small_image_link(f"{url}page/{page+1}")
    image = image_processing.get_image(img_url)
    bot.send_photo(chat_id, photo=image)


def read_long_image(chat_id, url):
    page = db.get_column(chat_id, "page")
    img_url = search.get_long_image_links(url)
    image = image_processing.get_image(img_url[page])
    parts = image_processing.cut_image(image)
    for part in parts:
        bot.send_photo(chat_id, photo=part)


@bot.message_handler(commands=['move'])
def set_volume(message):
    vol = db.get_column(message.chat.id, "max_volume")
    bot.send_message(message.chat.id, f"Напиши номер тома (сезона) на который хочешь перейти\n"
                                      f"Последний доступный том: {vol} ")
    bot.register_next_step_handler(message, confirm_volume, vol)


def confirm_volume(message, vol):
    try:
        number = int(message.text)
        if number > vol or number < 1:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "Кажеться ты ввёл не число или оно за пределами Доступного. Попробуй ещё")
        bot.register_next_step_handler(message, confirm_volume, vol)
        return
    else:
        db.update_column(message.chat.id, "volume", number-1)
        db.update_column(message.chat.id, "chapter", 0)
        db.update_column(message.chat.id, "page", 0)
        update_max_values(message.chat.id)
        update_max_pages(message.chat.id, url=get_url(message.chat.id))
        bot.send_message(message.chat.id, "Напиши /read чтобы получить продолжить читать")


@bot.message_handler(commands=["chapter"])
def set_chapter(message):
    chapter = db.get_column(message.chat.id, "max_chapter")
    bot.send_message(message.chat.id, f"Напиши номер тома (сезона) на который хочешь перейти\n"
                                      f"Последний доступная глава в сезоне: {chapter} ")
    bot.register_next_step_handler(message, confirm_chapter, chapter)


def confirm_chapter(message, chapter):
    try:
        number = int(message.text)
        if number > chapter or number < 1:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "Кажеться ты ввёл не число или оно за пределами Доступного. Попробуй ещё")
        bot.register_next_step_handler(message, confirm_chapter, chapter)
        return
    else:
        db.update_column(message.chat.id, "chapter", number-1)
        db.update_column(message.chat.id, "page", 0)
        update_max_values(message.chat.id)
        update_max_pages(message.chat.id, url=get_url(message.chat.id))
        bot.send_message(message.chat.id, "Напиши /read чтобы получить продолжить читать")


@bot.message_handler(commands=['page'])
def set_page(message):
    max_page = db.get_column(message.chat.id, "max_page")
    bot.send_message(message.chat.id, f"Напиши номер тома (сезона) на который хочешь перейти\n"
                                      f"Последний доступная страница в главе: {max_page} ")
    bot.register_next_step_handler(message, confirm_page, max_page)


def confirm_page(message, max_page):
    try:
        number = int(message.text)
        if number > max_page or number < 1:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "Кажеться ты ввёл не число или оно за пределами Доступного. Попробуй ещё")
        bot.register_next_step_handler(message, confirm_page, max_page)
        return
    else:
        db.update_column(message.chat.id, "page", number-1)
        bot.send_message(message.chat.id, "Напиши /read чтобы получить продолжить читать")


def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()
