import telebot
import image_processing
import search_title
import t


bot = telebot.TeleBot(token=t.token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Я Бот для чтения манги\n"
                                      "Чтобы выбрать что почитать используй команду /search название_манги\n"
                                      "Напиши /help чтобы посмотреть список всех команд ")


@bot.message_handler(commands=['help'])
def show_commands(message):
    bot.send_message(message.chat.id, "/help - Посмотреть все команды\n"
                                      "/search - Найти мангу по названию или сменить текущую\n"
                                      "/move - Сменить главу\n"
                                      "/page - Сменить страницу")


@bot.message_handler(commands=['search'])
def ask_manga_title(message):
    sent_msg = bot.send_message(message.chat.id, "Введите название манги")
    bot.register_next_step_handler(sent_msg, get_manga_title)


def get_manga_title(message):
    title = message.text.strip()
    search_result = search_title.search_manga(title)
    if not search_result:
        sent_msg = bot.send_message(message.chat.id, "Ничего не найдено🙁 попробуй ещё")
        bot.register_next_step_handler(sent_msg, get_manga_title)
    else:
        formated_result = search_title.form_result(search_result)
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
        if number > len(formated_result):
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "Кажеться ты ввёл не число или оно за пределами списка. Попробуй ещё")
        bot.register_next_step_handler(message, choose_title, formated_result)
        return
    # data base Update user title
    pass


def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()