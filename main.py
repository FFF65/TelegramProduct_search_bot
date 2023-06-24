import time
import telebot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import config
from telebot import types


bot = telebot.TeleBot(config.TOKEN)

keyb = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1 = types.KeyboardButton('Найти среднюю цену товара')
button2 = types.KeyboardButton('Поиск видео')
keyb.add(button1, button2)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Доброго времени суток, ' + message.from_user.first_name + '. '
                        'Этот бот предназначен для поиска средней цены товара на Авито',
                     reply_markup=keyb)


@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == 'Найти среднюю цену товара':
        bot.send_message(message.chat.id, 'Введите название', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, search)
    if message.text == 'Поиск видео':
        bot.send_message(message.chat.id, 'Введите название\n'
                                          'Примечание: Данный бот выводит только первые пять видео',
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, movie_search)


def search(message):
    bot.send_message(message.chat.id, 'Выполняю поиск')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(config.AVITO_SEARCH + message.text)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    products = soup.find_all('meta', attrs={'itemprop': 'price'})
    driver.get(config.AVITO_SEARCH2 + message.text)
    products2 = soup.find_all('meta', attrs={'itemprop': 'price'})
    sum = 0
    for product in products2:
        sum += int(product.get('content'))
    for product in products:
        sum += int(product.get('content'))
    avg = round(sum / (len(products) + len(products2)), 2)
    bot.send_message(message.chat.id, 'Средняя стоимость ' + message.text + ' : ' + str(avg) + ' ₽', reply_markup=keyb)


def movie_search(message):
    bot.send_message(message.chat.id, 'Идет поиск')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(config.MOVIE_SEARCH + message.text)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    movies = soup.find_all(name='a', attrs={'id': 'video-title'})
    time.sleep(4)
    counter = 0
    for movie in movies:
        if counter == 5: break
        bot.send_message(message.chat.id,'https://www.youtube.com/' + movie.get('href'),
                         reply_markup=keyb)
        counter += 1

    bot.send_message(message.chat.id,'Поиск закончен')

if __name__ == '__main__':
    bot.polling()
