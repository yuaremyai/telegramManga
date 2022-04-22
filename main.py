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
                                      "/search название_манги - Найти мангу по названию\n"
                                      "/help - Посмотреть все команды\n")


@bot.message_handler(commands=['search'])
def select_manga(message):
    bot.send_message(message.chat.id, message.text)


def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()