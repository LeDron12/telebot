import json
import sqlite3
import requests as rq
import time

def db_table_val(user_id: int, vk_public: str, twitter_public: str,
                 last_post_vk: str, last_post_twitter: str):
    conn = sqlite3.connect('telebot.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO all_users (user_id, vk_public, twitter_public, last_post_vk, last_post_twitter) VALUES (?, ?, ?, ?, ?)',
        (user_id, vk_public, twitter_public, last_post_vk, last_post_twitter))
    conn.commit()
    return True

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


def db_vk(id, domain, vk_client):
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

def auth_handler():
    key = input("Enter authentication code: ")
    remember_device = True

    return key, remember_device


def name_vk(domain, access_token):
    URL = f"https://api.vk.com/method/groups.getById?group_id={domain}&access_token={access_token}&v=5.131"
    data = rq.get(URL)
    time.sleep(0.5)
    name = json.loads(data.content)["response"][0]["name"]
    return name


def get_posts_vk(user_id, domain, vk_client, access_token):
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
    name = name_vk(domain, access_token)
    if len(last_posts_new) == 0:
        return descriptions, photo_urls, name, [last_id]
    else:
        return descriptions, photo_urls, name, last_posts_new