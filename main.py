import textwrap
import time

import requests
import telegram
from environs import Env


def send_message(bot, tg_chat_id, result):
    if result["is_negative"]:
        text = f"""Работа "{result["lesson_title"]}" проверена!\n\n
                В работе найдены ошибки\n\n
                Ссылка на работу {result["lesson_url"]}"""
    else:
        text = f"""Работа "{result["lesson_title"]}" проверена!\n\n
                Работа принята\n\n
                Ссылка на работу {result["lesson_url"]}"""
    bot.send_message(text=text, chat_id=tg_chat_id)


def main():
    env = Env()
    env.read_env()
    tg_bot_token = env.str("TG_BOT_TOKEN")
    tg_chat_id = env.str("TG_CHAT_ID")
    devman_token = env.str("DEVMAN_TOKEN")
    bot = telegram.Bot(token=tg_bot_token)

    url = "https://dvmn.org/api/long_polling/"
    header = {"Authorization": devman_token}
    params = {}
    while True:
        try:
            response = requests.get(url, headers=header, timeout=90, params=params)
            response.raise_for_status()
            response = response.json()

            if response["status"] == "found":
                for work in response["new_attempts"]:
                    send_message(bot, tg_chat_id, work)
            timestamp = response.get("last_attempt_timestamp")
            params.update({"timestamp": timestamp})

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(10)
            continue


if __name__ == "__main__":
    main()
