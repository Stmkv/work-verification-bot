import logging
import time

import requests
import telegram
from environs import Env

logger = logging.getLogger("work_verification")


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)




def send_message(bot, tg_chat_id, result):
    if result["is_negative"]:
        text = f"""Работа "{result["lesson_title"]}" проверена!\n\n
                В работе найдены ошибки\n\n
                Ссылка на работу {result["lesson_url"]}"""
    else:
        text = f"""Работа "{result["lesson_title"]}" проверена!\n\n
                Работа принята\n\n
                Ссылка на работу {result["lesson_url"]}"""
    bot.send_message(text = text, chat_id=tg_chat_id)




def main():
    env = Env()
    env.read_env()
    tg_bot_token = env.str("TG_BOT_TOKEN")
    tg_chat_id = env.str("TG_CHAT_ID")
    devman_token = env.str("DEVMAN_TOKEN")
    bot = telegram.Bot(token=tg_bot_token)

    FORMAT = "%(asctime)s : %(name)s : %(levelname)s : %(message)s"
    logging.basicConfig(
        level=logging.WARNING,
        format=FORMAT,
        handlers=[TelegramLogsHandler(bot, tg_chat_id)],
    )
    logger.info("Бот запущен")
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

        except requests.exceptions.ReadTimeout as err:
            logger.info(err, exc_info=True)
            time.sleep(1)
            continue
        except requests.exceptions.ConnectionError as err:
            logger.error(err, exc_info=True)
            time.sleep(10)
            continue


if __name__ == "__main__":
    main()
