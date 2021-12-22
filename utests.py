import unittest
import app
import telebot
import vk_api
import json
import warnings
import sqlite3
import urllib
import requests as rq
import time

class AllTests(unittest.TestCase):
    def auth(self):
        with open('api_key.txt') as f:
            google_token = f.read()
        with open('vk_data.json', 'r') as json_file:
            client = json.load(json_file)

        vk_session = vk_api.VkApi(
            client['email_or_phone_number'],
            client['password'],
            auth_handler=app.auth_handler,
            app_id=2685278
        )
        try:
            vk_session.auth(token_only=True)
        except vk_api.exceptions.Captcha as captcha:
            captcha.sid
            captcha.get_url()
            captcha.get_image()
        vk_client = vk_session.get_api()


    def test_name_domain(self):
        self.auth()
        domain = "sasambainc"
        self.assertEqual(app.name_vk(domain), "Сасамба", 'Хуйня')
        return True


if __name__ == '__main__':
    unittest.main()
