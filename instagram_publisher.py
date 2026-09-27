"""
Instagram Publisher для блога о путешествиях
Публикация фото/карточек с подписью через instagrapi (эмуляция мобильного клиента)
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstagramPublisher:
    """Публикует посты в Instagram"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.client = Client()
        self.session_file = Path(f"sessions/{username}_session.json")
        self.posts_published = []

        Path("sessions").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)

    def login(self) -> bool:
        try:
            if self.session_file.exists():
                logger.info(f"Загружаю сессию из {self.session_file}")
                self.client.load_settings(self.session_file)
                self.client.login(self.username, self.password)
            else:
                logger.info(f"Логин в Instagram как {self.username}")
                self.client.login(self.username, self.password)

            self.client.dump_settings(self.session_file)
            logger.info("Успешный вход!")
            return True

        except LoginRequired:
            logger.error("Ошибка логина. Проверь username/password")
            return False
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")
            return False

    def publish_photo(self, photo_path: str, caption: str, hashtags: str = "") -> bool:
        try:
            if not os.path.exists(photo_path):
                logger.error(f"Фото не найдено: {photo_path}")
                return False

            full_caption = f"{caption}\n\n{hashtags}"
            logger.info(f"Публикую фото: {photo_path}")

            media = self.client.photo_upload(photo_path, full_caption)
            logger.info(f"Опубликовано! ID: {media.id}")

            self.posts_published.append({
                "date": datetime.now().isoformat(),
                "photo": photo_path,
                "caption": caption,
                "hashtags": hashtags,
                "media_id": media.id,
            })
            return True

        except Exception as e:
            logger.error(f"Ошибка при публикации: {str(e)}")
            return False

    def get_account_info(self) -> dict:
        try:
            user = self.client.account_info()
            return {
                "username": user.username,
                "full_name": user.full_name,
                "followers": user.follower_count,
                "following": user.following_count,
                "posts": user.media_count,
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации: {str(e)}")
            return {}

    def save_stats(self):
        stats_file = Path("logs") / f"published_{datetime.now().strftime('%Y%m%d')}.json"
        try:
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(self.posts_published, f, ensure_ascii=False, indent=2)
            logger.info(f"Статистика сохранена в {stats_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения: {str(e)}")
