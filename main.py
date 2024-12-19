import telebot
import openai
import requests
from bs4 import BeautifulSoup as BS
from telebot.types import InputMediaPhoto

r = requests.get(f"https://stopgame.ru/games/action/popular?year_start=2014&year_end=2018&rating%5B%5D=pohvalno&rating%5B%5D=izumitelno")
r.raise_for_status()
html = BS(r.text, "lxml")
list_game = html.find("div", class_ = "_games-grid_198ms_320").find_next()
print(list_game.find('a').find("img").get('src'))
ans_list_game = []
bot = telebot.TeleBot("8115179561:AAGVIuipqg3mguFkFdSQ4qTCAAAhtlehMRM")
user_states = {}
WFG= "waiting_find_game"
WR= "waiting_recomendation"
ganr_l = {"Приключение":"adventure", "Экшн":"action","Файтинг":"fighting","Головоломка":"logic","Гонка":"racing","Симулятор":"simulator","Стратегия":"strategy"}
ganr_l1 = {"приключение":"adventure", "экшн":"action","файтинг":"fighting","головоломка":"logic","гонка":"racing","симулятор":"simulator","стратегия":"strategy"}
@bot .message_handler(commands=["start"])
def hi(mess):
    bot.send_message(mess.chat.id, "Привет!")
    bot.send_message(mess.chat.id, "Я бот и я умею выводить информацию по видеоиграм и рекомендовать лучшее")
    bot.send_message(mess.chat.id, "используй /help")

@bot .message_handler(commands=["help"])
def hlp(mess):
    bot.send_message(mess.chat.id, "найти игру - /find_game")
    bot.send_message(mess.chat.id, "лучшее в жанре - /top_list")



@bot.message_handler(commands=["find_game"])
def ret_command(message):
    user_id = message.from_user.id
    # Устанавливаем состояние ожидания сообщения
    user_states[user_id] = WFG
    bot.send_message(message.chat.id, "Введите название игры для поиска")

@bot.message_handler(commands=["top_list"])
def ret_command(message):
    user_id = message.from_user.id
    # Устанавливаем состояние ожидания сообщения
    user_states[user_id] = WR
    bot.send_message(message.chat.id,", ".join(map(str, ganr_l.keys())))
    bot.send_message(message.chat.id, "Введите жанр из списка доступных\nВведите с какого по какой год вышла игра\nОдним сообщением через пробел")
# Обработка текстового сообщения
@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_id = message.from_user.id

    if user_states.get(user_id) == WFG:
        user_message = message.text

        game = user_message.lower()
        r = requests.get(f"https://stopgame.ru/search?s={game}&where=games&sort=relevance")
        r.raise_for_status()
        html = BS(r.text, "lxml")
        try:
            game_titles = html.find("h2", class_="_title_1fjyn_173").text.strip()
            platform = html.find_all('div', class_="_info-grid__value_1fjyn_229")[0].text.strip()
            gnr = html.find_all('div', class_="_info-grid__value_1fjyn_229")[1].text.strip()
            dt = html.find_all('div', class_="_info-grid__value_1fjyn_229")[2].text.strip()
            mrk = html.find_all('span', class_="_users-rating__total_1fjyn_1")[0].text.strip()
            image_url = html.find("img").get('src')
            print(game_titles,image_url)
            bot.send_photo(message.chat.id, photo=image_url,
                           caption= f"Игра - {game_titles}\n" +
                                    f"{platform}\n" +
                                    f"Жанр - {gnr}\n" +
                                    f"Дата выхода - {dt}\n" +
                                    f"Оценка - {mrk}\n"
                           )
            mtext = html.find('div',class_ ="_info-grid__value_1fjyn_229")
            print(mtext)
        except AttributeError:
            bot.send_message(user_id, "Нету такой игры :(")
        user_states[user_id] = None

    elif user_states.get(user_id) == WR:
        user_message = message.text.split()
        user_message[0] = user_message[0].lower()
        if len(user_message)==3 and user_message[1].isdigit() and user_message[2].isdigit() and  int(user_message[1]) <= int(user_message[2]) and  int(user_message[1])>=1980 and int(user_message[2])<=2025:
            try:
                ans_list_game = []
                r = requests.get(f"https://stopgame.ru/games/{ganr_l1[user_message[0].lower()]}/popular?year_start={user_message[1]}&year_end={user_message[2]}&rating%5B%5D=pohvalno&rating%5B%5D=izumitelno")
                r.raise_for_status()
                html = BS(r.text, "lxml")
                list_game = html.find("div", class_="_games-grid_198ms_320").find_next()
                for i in range(5):
                    ans_list_game.append({"Name":list_game.find('a').get("title"),"Img":list_game.find('a').find("img").get('src')})
                    list_game = list_game.find_next_sibling()
                media = [
                    InputMediaPhoto(game["Img"], caption=game["Name"])
                    for game in ans_list_game
                ]

                bot.send_media_group(user_id, media)

            except AttributeError:
                bot.send_message(user_id, "Нету ничего что вам подходит :(")
            except KeyError:
                bot.send_message(user_id, "что то не то...   ╰（‵□′）╯")
        else:
            bot.send_message(message.chat.id,"Введите жанр из списка доступных\nВведите с какого по какой год вышла игра\nОдним сообщением через пробел")

        user_states[user_id] = None
    else:
        bot.send_message(user_id, "Пожалуйста, используйте команду /help перед отправкой сообщения.")


bot.polling(non_stop=True)