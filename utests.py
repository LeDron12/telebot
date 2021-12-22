import unittest
import methods
import telebot
import vk_api
import json
import warnings
import sqlite3
import urllib
import requests as rq
import time

class TestAllTests(unittest.TestCase):
    def test_name_domain(self):
        with open('access_token.txt') as f:
            access_token = f.read()
        with open('api_key.txt') as f:
            google_token = f.read()
        with open('vk_data.json', 'r') as json_file:
            client = json.load(json_file)

        vk_session = vk_api.VkApi(
            client['email_or_phone_number'],
            client['password'],
            auth_handler=methods.auth_handler,
            app_id=2685278
        )
        try:
            vk_session.auth(token_only=True)
        except vk_api.exceptions.Captcha as captcha:
            captcha.sid
            captcha.get_url()
            captcha.get_image()
        vk_client = vk_session.get_api()
        domain = "sasambainc"
        self.assertEqual(methods.name_vk(domain, access_token), "Сасамба", 'False')

    def test_insert_delete_db(self):
        self.assertEqual(methods.db_table_val(1, '1', '1', '1', '1'), True, 'False')
        conn = sqlite3.connect('telebot.db')
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM table1 WHERE user_id = ?',
            (1, ))
        conn.commit()


if __name__ == '__main__':
    unittest.main()
