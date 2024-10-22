import time

import requests
import telegram
from environs import Env


def main():
    env = Env()
    env.read_env()
    TG_BOT_TOKEN = env.str("TG_BOT_TOKEN")
    TG_CHAT_ID = env.str("TG_CHAT_ID")
    bot = telegram.Bot(token=TG_BOT_TOKEN)

    url = "https://dvmn.org/api/long_polling/"
    header = {"Authorization": "Token 155a9451027aa13b5d65f3191859fb7ec1844dbe"}
    params = {}
    while True:
        try:
            response = requests.get(url, headers=header, timeout=90, params=params)
            response.raise_for_status()
            response = response.json()

            if response["status"] == "found":
                for work in response["new_attempts"]:
                    text = f"""Работа "{work["lesson_title"]}" проверена!\n\n"""
                    if work["is_negative"]:
                        text += "В работе найдены ошибки\n\n"
                    else:
                        text += "Работа принята\n\n"
                    text += f"Ссылка на работу {work["lesson_url"]}"
                    bot.send_message(text=text, chat_id=TG_CHAT_ID)

            timestamp = response.get("last_attempt_timestamp")
            params.update({"timestamp": timestamp})

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(10)
            continue


if __name__ == "__main__":
    main()
