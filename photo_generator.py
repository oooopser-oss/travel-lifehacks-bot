"""
Photo Generator for Travel & Lifehacks posts
Генерирует карточки-советы с градиентом и текстом (для постов типа lifehack)
"""

import os
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class TravelPhotoGenerator:
    """Генерирует карточки-советы для блога о путешествиях"""

    TEAL = (0, 121, 140)      # глубокий бирюзовый
    SAND = (237, 201, 175)    # песочный
    SKY = (135, 206, 235)     # небесно-голубой
    SUNSET = (255, 138, 101)  # закатный оранжевый
    WHITE = (255, 255, 255)

    PALETTES = {
        "lifehack": (TEAL, SKY),
        "packing": (SUNSET, SAND),
        "budget": (TEAL, SAND),
        "safety": (SUNSET, TEAL),
    }

    EMOJIS = {
        "lifehack": "💡",
        "packing": "🧳",
        "budget": "💰",
        "safety": "🛡️",
    }

    def __init__(self, output_dir: str = "generated_photos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def create_gradient_image(self, width=1080, height=1080, color1=None, color2=None) -> Image.Image:
        color1 = color1 or self.TEAL
        color2 = color2 or self.SKY

        img = Image.new('RGB', (width, height))
        pixels = img.load()
        for y in range(height):
            r = int(color1[0] + (color2[0] - color1[0]) * y / height)
            g = int(color1[1] + (color2[1] - color1[1]) * y / height)
            b = int(color1[2] + (color2[2] - color1[2]) * y / height)
            for x in range(width):
                pixels[x, y] = (r, g, b)
        return img

    def add_text_to_image(self, img: Image.Image, title="", subtitle="", emoji="💡") -> Image.Image:
        draw = ImageDraw.Draw(img)
        width, height = img.size

        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
        except Exception:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()

        try:
            emoji_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
            emoji_supports_color = True
        except Exception:
            emoji_font = title_font
            emoji_supports_color = False

        if emoji:
            emoji_bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
            emoji_width = emoji_bbox[2] - emoji_bbox[0]
            emoji_x = (width - emoji_width) // 2
            if emoji_supports_color:
                draw.text((emoji_x, 150), emoji, font=emoji_font, embedded_color=True)
            else:
                draw.text((emoji_x, 150), emoji, fill=self.WHITE, font=emoji_font)

        if title:
            wrapped_title = "\n".join(textwrap.wrap(title, width=16))
            title_bbox = draw.textbbox((0, 0), wrapped_title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            title_x = (width - title_width) // 2
            title_y = (height - title_height) // 2 - 50
            draw.text((title_x, title_y), wrapped_title, fill=self.WHITE, font=title_font)

        if subtitle:
            wrapped_subtitle = "\n".join(textwrap.wrap(subtitle, width=32))
            subtitle_bbox = draw.textbbox((0, 0), wrapped_subtitle, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (width - subtitle_width) // 2
            subtitle_y = height - 280
            draw.text((subtitle_x, subtitle_y), wrapped_subtitle, fill=self.WHITE, font=subtitle_font)

        return img

    def generate_card(self, card_type: str, title: str, subtitle: str, filename: str) -> str:
        color1, color2 = self.PALETTES.get(card_type, (self.TEAL, self.SKY))
        emoji = self.EMOJIS.get(card_type, "💡")

        img = self.create_gradient_image(color1=color1, color2=color2)
        img = self.add_text_to_image(img, title=title, subtitle=subtitle, emoji=emoji)

        output_path = self.output_dir / filename
        img.save(output_path, quality=95)
        return str(output_path)


if __name__ == "__main__":
    generator = TravelPhotoGenerator()
    path = generator.generate_card(
        card_type="packing",
        title="Правило одной сумки",
        subtitle="Как путешествовать неделю с одним рюкзаком",
        filename="test_card.jpg"
    )
    print(f"Готово: {path}")
