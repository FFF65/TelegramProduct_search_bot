import time

import telebot
from selenium import webdriver
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
import config
from telebot import types

bot = telebot.TeleBot(config.TOKEN)

keyb = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1 = types.KeyboardButton('Найти среднюю цену товара')
keyb.add(button1)
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,'Доброго времени суток, ' + message.from_user.first_name + '. '
                                      'Этот бот предназначен для поиска средней цены товара на Авито',reply_markup=keyb)

@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == 'Найти среднюю цену товара':
        bot.send_message(message.chat.id,'Введите название',reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message,search)


def search(message):
    bot.send_message(message.chat.id,'Выполняю поиск')
    driver = webdriver.Edge(EdgeChromiumDriverManager().install())
    driver.get(config.AVITO_SEARCH + message.text)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source,'html.parser')
    products = soup.find_all('meta',attrs={'itemprop':'price'})
    driver.get(config.AVITO_SEARCH2 + message.text)
    products2 = soup.find_all('meta', attrs={'itemprop': 'price'})
    sum = 0
    for product in products2:
        sum += int(product.get('content'))
    for product in products:
        sum+=int(product.get('content'))
    avg = round(sum/(len(products)+len(products2)),2)
    bot.send_message(message.chat.id,'Средняя стоимость ' + message.text + ' : ' + str(avg) + '₽',reply_markup=keyb)

















if __name__ == '__main__':
    bot.polling()
