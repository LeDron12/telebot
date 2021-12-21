import telebot
import vk_api
import json
import warnings
import sqlite3
import urllib
import requests as rq
import time
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    # Data base
    def db_table_val(user_id: int, vk_public: str, twitter_public: str,
                     last_post_vk: str, last_post_twitter: str):
        conn = sqlite3.connect('telebot.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO all_users (user_id, vk_public, twitter_public, last_post_vk, last_post_twitter) VALUES (?, ?, ?, ?, ?)',
            (user_id, vk_public, twitter_public, last_post_vk, last_post_twitter))
        conn.commit()


    def db_check(id):
        conn = sqlite3.connect('telebot.db')
        cursor = conn.cursor()
        sql_select_query = """select * from all_users where user_id = ?"""
        cursor.execute(sql_select_query, (id,))
        records = cursor.fetchall()
        if (len(records)) == 0:
            conn.commit()
            return True
        else:
            conn.commit()
            return False


    def db_vk(id, domain):
        try:
            wall_posts = vk_client.wall.get(
                domain=domain,
                count=1,
            )['items']
        except:
            return False
        conn = sqlite3.connect('telebot.db')
        cursor = conn.cursor()
        sql_select_query = """select * from all_users where user_id = ?"""
        cursor.execute(sql_select_query, (id,))
        records = cursor.fetchall()
        all_vk_domain = set()
        if len(records):
            all_vk_domain = set(records[0][2].split())
        if len(all_vk_domain) == 15:
            return False
        all_vk_domain.add(domain)
        all_vk_domain = " ".join(all_vk_domain)
        sql_update_query = """Update all_users set vk_public = ? where user_id = ?"""
        cursor.execute(sql_update_query, (all_vk_domain, id,))
        conn.commit()
        return True


    def db_vk_delete(id, domain):
        conn = sqlite3.connect('telebot.db')
        cursor = conn.cursor()
        sql_select_query = """select * from all_users where user_id = ?"""
        cursor.execute(sql_select_query, (id,))
        records = cursor.fetchall()
        all_vk_domain = set()
        if (len(records)):
            all_vk_domain = set(records[0][2].split())
        try:
            all_vk_domain.remove(domain)
            all_vk_domain = " ".join(all_vk_domain)
            sql_update_query = """Update all_users set vk_public = ? where user_id = ?"""
            cursor.execute(sql_update_query, (all_vk_domain, id,))
            conn.commit()
        except KeyError as e:
            pass
            conn.commit()


    def get_domains_vk(id):
        conn = sqlite3.connect('telebot.db')
        cursor = conn.cursor()
        sql_select_query = """select * from all_users where user_id = ?"""
        cursor.execute(sql_select_query, (id,))
        records = cursor.fetchall()
        all_domains = []
        if len(records):
            all_domains = records[0][2].split()
        conn.commit()
        return all_domains


    def db_vk_last(id):
        conn = sqlite3.connect('telebot.db')
        cursor = conn.cursor()
        sql_select_query = """select * from all_users where user_id = ?"""
        cursor.execute(sql_select_query, (id,))
        records = cursor.fetchall()
        all_last_posts = list(map(int, str(records[0][4]).split()))
        conn.commit()
        return all_last_posts


    def db_vk_last_change(id, last_posts_new_all):
        conn = sqlite3.connect('telebot.db')
        cursor = conn.cursor()
        last_posts_new_all = " ".join(map(str, last_posts_new_all))
        sql_update_query = """Update all_users set last_post_vk = ? where user_id = ?"""
        cursor.execute(sql_update_query, (last_posts_new_all, id,))
        conn.commit()


    #

    warnings.filterwarnings('ignore')
    with open('access_token.txt') as f:
        access_token = f.read()


    # VK_api
    def auth_handler():
        key = input("Enter authentication code: ")
        remember_device = True

        return key, remember_device


    with open('api_key.txt') as f:
        google_token = f.read()
    with open('vk_data.json', 'r') as json_file:
        client = json.load(json_file)

    vk_session = vk_api.VkApi(
        client['email_or_phone_number'],
        client['password'],
        auth_handler=auth_handler
    )
    try:
        vk_session.auth()
    except vk_api.exceptions.Captcha as captcha:
        captcha.sid
        captcha.get_url()
        captcha.get_image()
    vk_client = vk_session.get_api()


    def name_vk(domain):
        URL = f"https://api.vk.com/method/groups.getById?group_id={domain}&access_token={access_token}&v=5.131"
        data = rq.get(URL)
        time.sleep(0.5)
        name = json.loads(data.content)["response"][0]["name"]
        return name


    def get_posts_vk(user_id, domain):
        wall_posts = vk_client.wall.get(
            domain=domain,
            count=5,
        )['items']
        last_posts = db_vk_last(user_id)
        last_posts_new = []
        photo_urls = []
        descriptions = []
        last_id = ""
        for wall_post in wall_posts:
            if wall_post["id"] not in last_posts:
                if "attachments" in wall_post:
                    # print(wall_post, '\n', '\n')
                    descriptions.append(wall_post["text"])
                    photo_urls.append([])
                    if "attachments" in wall_post:
                        for elem in wall_post["attachments"]:
                            photo = elem.get('photo')
                            if photo:
                                for photo_item in photo["sizes"]:
                                    if photo_item["width"] >= 350:
                                        photo_urls[-1].append(photo_item["url"])
                                        break
                        last_posts_new.append(wall_post["id"])
                elif len(wall_post["text"]) != 0:
                    descriptions.append(wall_post["text"])
                    photo_urls.append([])
                    photo_urls[-1].append(
                        "https://sun9-30.userapi.com/impf/c834202/v834202747/242f8/CS8oRxwfjos.jpg?size=1197x801&quality=96&sign=691d41fd9b022093980e3b6140cb4737&type=album")
                    last_posts_new.append(wall_post["id"])
            else:
                last_id = wall_post["id"]
                break
        name = name_vk(domain)
        if len(last_posts_new) == 0:
            return descriptions, photo_urls, name, [last_id]
        else:
            return descriptions, photo_urls, name, last_posts_new


    def get_groups_vk(user_id):
        URL = f"https://api.vk.com/method/groups.get?user_id={user_id}&extended={1}&access_token={access_token}&v=5.131"
        domains = []
        try:
            data = rq.get(URL)
            data = json.loads(data.content)
            for item in data["response"]["items"]:
                domains.append(item["screen_name"])
            return domains
        except:
            return domains


    def get_user_id(user_domain):
        URL = f"https://api.vk.com/method/users.get?user_ids={user_domain}&access_token={access_token}&v=5.131"
        data = rq.get(URL)
        data = json.loads(data.content)
        user_id = data["response"][0]["id"]
        return user_id


    #

    # BOT
    with open('bot_token.txt') as f:
        bot_token = f.read()
    bot = telebot.TeleBot(bot_token)


    @bot.message_handler(commands=['start'])
    def hello(message):
        if db_check(message.from_user.id):
            bot.send_message(message.chat.id,
                             "Добрый день! Этот бот является альтернативой ленты в Вк. Напиши /help, если хочешь узнать больше!")
            us_id = message.from_user.id
            db_table_val(
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
            if db_vk(message.from_user.id, domain):
                bot.send_message(message.chat.id, "Паблик успешно добавлен!")
            else:
                bot.send_message(message.chat.id, "Невозможно добавить группу " + domain)
        else:
            bot.send_message(message.chat.id, "Неверно введен адрес")


    @bot.message_handler(commands=['add_twitter'])
    def add_twitter(message):
        data = message.text.split('/')
        domain = data[-1]
        if data[-2] == "twitter.com":
            db_twitter(message.from_user.id, domain)
            bot.send_message(message.chat.id, "Успешно подписались!")
        else:
            bot.send_message(message.chat.id, "Неверно введен адрес")


    @bot.message_handler(commands=['delete_vk'])
    def delete_vk(message):
        data = message.text.split('/')
        domain = data[-1]
        if data[-2] == "vk.com":
            db_vk_delete(message.from_user.id, domain)
            bot.send_message(message.chat.id, "Паблик успешно удален!")
        else:
            bot.send_message(message.chat.id, "Неверно введен адрес")


    @bot.message_handler(commands=['delete_twitter'])
    def delete_twitter(message):
        data = message.text.split('/')
        domain = data[-1]
        if data[-2] == "twitter.com":
            db_twitter_delete(message.from_user.id, domain)
            bot.send_message(message.chat.id, "Успешно отписались!")
        else:
            bot.send_message(message.chat.id, "Неверно введен адрес")


    @bot.message_handler(commands=['refresh'])
    def refresh(message):
        bot.send_message(message.chat.id, "Ищем новые записи...")
        were_new = False
        all_domains = get_domains_vk(message.from_user.id)
        last_posts_new_all = []
        for domain in all_domains:
            descriptions, photo_urls, name, last_posts_new = get_posts_vk(message.from_user.id, domain)
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
        db_vk_last_change(message.from_user.id, last_posts_new_all)
        if not were_new:
            bot.send_message(message.chat.id, "Новых записей пока что нет")


    @bot.message_handler(commands=['my_vk'])
    def my_vk(message):
        my_domains_vk = get_domains_vk(message.from_user.id)
        answer = " "
        for domain in my_domains_vk:
            answer += name_vk(domain) + " - " + f"https://vk.com/{domain}" + '\n'
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


    """@bot.message_handler(commands=['import'])
    def import_all(message):
        data = message.text.split('/')
        domain = data[-1]
        user_id = get_user_id(domain)
        domains = get_groups_vk(user_id)
        if len(domains) == 0:
            bot.send_message(message.chat.id, "Невозможно импортировать группы пользователя")
        else:
            for domain in domains:
                db_vk(message.from_user.id, domain)
        bot.send_message(message.chat.id, "Все группы, кроме закрытых, успешно импортированы")"""

    bot.polling(none_stop=True)
    #
