"""
Автономный Instagram-бот: блог про путешествия и лайфхаки.
Публикует 14 постов по одному в день: реальные фото направлений (Adobe Stock,
лицензированы заранее) чередуются с автоматически сгенерированными карточками-советами.
"""

import os
import logging
from datetime import datetime, time, timedelta
from pathlib import Path
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from instagram_publisher import InstagramPublisher
from photo_generator import TravelPhotoGenerator
from content_calendar import POSTS_SCHEDULE

load_dotenv()
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/bot.log'), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class TravelAutonomousBot:
    """Автономный бот для блога про путешествия и лайфхаки"""

    def __init__(self, username: str, password: str):
        self.publisher = InstagramPublisher(username, password)
        self.generator = TravelPhotoGenerator()
        self.scheduler = BackgroundScheduler()

    def login(self) -> bool:
        return self.publisher.login()

    def resolve_photo_path(self, post_data: dict) -> str:
        """Возвращает путь к фото поста: готовое stock-фото или сгенерированная карточка"""
        if post_data["content_type"] == "photo":
            return post_data["photo_file"]

        return self.generator.generate_card(
            card_type=post_data["card_type"],
            title=post_data["title"],
            subtitle=post_data["subtitle"],
            filename=f"day_{post_data['day']}.jpg",
        )

    def generate_and_publish_post(self, post_data: dict) -> bool:
        try:
            photo_path = self.resolve_photo_path(post_data)
            logger.info(f"Публикую пост дня {post_data['day']}: {photo_path}")

            success = self.publisher.publish_photo(
                photo_path=photo_path,
                caption=post_data["caption"],
                hashtags=post_data["hashtags"],
            )

            if success:
                logger.info("Пост успешно опубликован!")
            else:
                logger.error("Ошибка публикации поста")
            return success

        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")
            return False

    def schedule_posts(self, start_date: datetime = None):
        """
        Планирует посты по одному на каждый день, начиная с start_date.
        Время публикации чередуется между 3 оптимальными слотами.
        """
        publish_times = [
            {"hour": 9, "minute": 0},
            {"hour": 14, "minute": 0},
            {"hour": 19, "minute": 0},
        ]

        if start_date is None:
            start_date = datetime.now() + timedelta(days=1)

        for index, post_data in enumerate(POSTS_SCHEDULE):
            time_config = publish_times[index % len(publish_times)]
            post_date = (start_date + timedelta(days=index)).date()
            run_date = datetime.combine(post_date, time(hour=time_config["hour"], minute=time_config["minute"]))

            self.scheduler.add_job(
                self.generate_and_publish_post,
                'date',
                run_date=run_date,
                args=[post_data],
                id=f"post_day_{post_data['day']}",
            )
            logger.info(f"Пост дня {post_data['day']} запланирован на {run_date.strftime('%Y-%m-%d %H:%M')}")

    def start(self):
        logger.info("Запускаю Travel Autonomous Bot...")

        if not self.login():
            logger.error("Не удалось войти в Instagram")
            return False

        self.schedule_posts()
        self.scheduler.start()
        logger.info("Бот запущен! Посты будут публиковаться автоматически.")

        try:
            import time as time_module
            while True:
                time_module.sleep(1)
        except KeyboardInterrupt:
            logger.info("Бот остановлен")
            self.scheduler.shutdown()

    def get_account_info(self):
        return self.publisher.get_account_info()


if __name__ == "__main__":
    USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
    PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")

    if not USERNAME or not PASSWORD:
        logger.error("Установи INSTAGRAM_USERNAME и INSTAGRAM_PASSWORD в .env файле!")
        exit(1)

    bot = TravelAutonomousBot(USERNAME, PASSWORD)
    bot.start()
