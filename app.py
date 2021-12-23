import telebot
import vk_api
import json
import warnings
import urllib
import time
import methods as m

warnings.filterwarnings('ignore')
with open('access_token.txt') as f:
    access_token = f.read()

with open('api_key.txt') as f:
    google_token = f.read()

with open('vk_data.json', 'r') as json_file:
    client = json.load(json_file)

vk_session = vk_api.VkApi(
    client['email_or_phone_number'],
    client['password'],
    auth_handler=m.auth_handler,
    app_id=2685278
)

try:
    vk_session.auth(token_only=True)
except vk_api.exceptions.Captcha as captcha:
    captcha.sid
    captcha.get_url()
    captcha.get_image()
vk_client = vk_session.get_api()

with open('bot_token.txt') as f:
    bot_token = f.read()
bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def hello(message):
    if m.db_check(message.from_user.id):
        bot.send_message(message.chat.id,
                         "Добрый день! Этот бот является альтернативой ленты в Вк. Напиши /help, если хочешь узнать больше!")
        us_id = message.from_user.id
        m.db_table_val(
            user_id=us_id,
            vk_public="",
            twitter_public="",
            last_post_vk="",
            last_post_twitter="",
        )


@bot.message_handler(commands=['add_vk'])
def add_vk(message):
    data = message.text.split('/')
    domain = data[-1]
    if data[-2] == "vk.com":
        if m.db_vk(message.from_user.id, domain, vk_client):
            bot.send_message(message.chat.id, "Паблик успешно добавлен!")
        else:
            bot.send_message(message.chat.id, "Невозможно добавить группу " + domain)
    else:
        bot.send_message(message.chat.id, "Неверно введен адрес")


@bot.message_handler(commands=['delete_vk'])
def delete_vk(message):
    data = message.text.split('/')
    domain = data[-1]
    if data[-2] == "vk.com":
        m.db_vk_delete(message.from_user.id, domain)
        bot.send_message(message.chat.id, "Паблик успешно удален!")
    else:
        bot.send_message(message.chat.id, "Неверно введен адрес")


@bot.message_handler(commands=['refresh'])
def refresh(message):
    bot.send_message(message.chat.id, "Ищем новые записи...")
    were_new = False
    all_domains = m.get_domains_vk(message.from_user.id)
    last_posts_new_all = []
    for domain in all_domains:
        descriptions, photo_urls, name, last_posts_new = m.get_posts_vk(message.from_user.id, domain, vk_client, access_token)
        last_posts_new_all += last_posts_new
        for i in range(len(descriptions)):
            try:
                if len(photo_urls[i]) != 0:
                    were_new = True
                    bot.send_message(message.chat.id, "⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️")
                    bot.send_message(message.chat.id, name)
                    if len(descriptions[i]) > 0:
                        bot.send_message(message.chat.id, descriptions[i])
                    for photo_url in photo_urls[i]:
                        f = open('out.jpg', 'wb')
                        f.write(urllib.request.urlopen(photo_url).read())
                        f.close()
                        img = open('out.jpg', 'rb')
                        bot.send_photo(message.chat.id, img)
                        img.close()
            except:
                bot.send_message(message.chat.id, "Текст поста слишком длинный")
        time.sleep(1.5)
    m.db_vk_last_change(message.from_user.id, last_posts_new_all)
    if not were_new:
        bot.send_message(message.chat.id, "Новых записей пока что нет")


@bot.message_handler(commands=['my_vk'])
def my_vk(message):
    my_domains_vk = m.get_domains_vk(message.from_user.id)
    answer = " "
    for domain in my_domains_vk:
        answer += m.name_vk(domain, access_token) + " - " + f"https://vk.com/{domain}" + '\n'
    if (answer == ' '):
        answer = "У вас нет пабликов"
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Список команд 👇")
    bot.send_message(message.chat.id,
                     "Добавить паблик VK: /add_vk 'ссылка на паблик' (пабликов можно добавить не больше 15, паблик не должен быть закрытым)" + '\n' +
                     "Удалить паблик VK: /delete_vk 'ссылка на паблик'" + '\n' +
                     "Обновить ленту: /refresh" + '\n' +
                     "Узнать список своих пабликов VK: /my_vk" + '\n')


bot.polling(none_stop=True)
#
