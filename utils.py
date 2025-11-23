import pygame
import os
import glob
from constants import WHITE, BLUE, YELLOW


def get_japanese_font(size):
    """日本語対応フォントを取得"""
    # プロジェクト内のフォントを優先
    project_font = os.path.join(os.path.dirname(__file__), "fonts", "NotoSansCJKjp-Regular.otf")
    if os.path.exists(project_font):
        try:
            return pygame.font.Font(project_font, size)
        except:
            pass

    # 試すフォントファイルのパス
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf",
        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return pygame.font.Font(font_path, size)
            except:
                continue

    # フォールバック: システムフォントを試す
    font_names = [
        "notosanscjkjp",
        "notosansjp",
        "takaopgothic",
        "ipaexgothic",
        "ipagothic",
        "meiryo",
        "msgothic",
        "yugothic"
    ]

    for font_name in font_names:
        try:
            font = pygame.font.SysFont(font_name, size)
            if font.get_height() > 0:
                return font
        except:
            continue

    # フォールバック: デフォルトフォント
    return pygame.font.Font(None, size)


def load_images_from_dir(images_dir, patterns, label="画像"):
    """指定フォルダから画像を読み込む共通関数"""
    images = []

    if os.path.exists(images_dir):
        for pattern in patterns:
            files = glob.glob(os.path.join(images_dir, pattern))
            images.extend(files)
        images.sort()

    print(f"{len(images)} 枚の{label}を見つけました")
    return images


def load_card_images():
    """images/フォルダから全カード画像を読み込む"""
    patterns = ['rare_card_*.png', 'rare_card_*.jpg', 'rare_card_*.webp']
    return load_images_from_dir("images", patterns, "カード画像")


def load_pack_images():
    """pack_images/フォルダからパック画像を読み込む"""
    patterns = ['*.png', '*.jpg', '*.webp']
    return load_images_from_dir("pack_images", patterns, "パック画像")


def create_dummy_pack_image(width, height):
    """ダミーのパック画像を生成"""
    surface = pygame.Surface((width, height))
    surface.fill(BLUE)
    # 枠線
    pygame.draw.rect(surface, WHITE, (0, 0, width, height), 3)
    # ★マーク
    font = pygame.font.Font(None, 60)
    star = font.render("★", True, YELLOW)
    star_rect = star.get_rect(center=(width // 2, height // 2))
    surface.blit(star, star_rect)
    # PACK テキスト
    text_font = pygame.font.Font(None, 36)
    pack_text = text_font.render("パック", True, WHITE)
    pack_rect = pack_text.get_rect(center=(width // 2, height - 30))
    surface.blit(pack_text, pack_rect)
    return surface


def load_and_scale_card_image(image_path, width, height):
    """カード画像を読み込んでリサイズする"""
    try:
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (width, height))
        return image
    except Exception as e:
        print(f"画像読み込みエラー ({image_path}): {e}")
        return create_dummy_card_image_fallback(width, height)


def create_dummy_card_image_fallback(width, height):
    """フォールバック用のダミーカード画像"""
    surface = pygame.Surface((width, height))
    surface.fill((100, 100, 100))
    pygame.draw.rect(surface, WHITE, (0, 0, width, height), 2)
    font = pygame.font.Font(None, 24)
    text = font.render("?", True, WHITE)
    text_rect = text.get_rect(center=(width // 2, height // 2))
    surface.blit(text, text_rect)
    return surface


def create_dummy_card_image(width, height, color, name):
    """ダミーのカード画像を生成"""
    surface = pygame.Surface((width, height))
    surface.fill(color)
    # 枠線
    pygame.draw.rect(surface, WHITE, (0, 0, width, height), 2)

    # カード名（複数行対応）
    font = pygame.font.Font(None, 18)
    words = name.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " " if current_line else word
        test_surface = font.render(test_line, True, WHITE)
        if test_surface.get_width() <= width - 4:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())

    # 複数行を中央に配置
    line_height = 20
    total_height = len(lines) * line_height
    start_y = (height - total_height) // 2

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, WHITE)
        text_rect = text_surface.get_rect(center=(width // 2, start_y + i * line_height))
        surface.blit(text_surface, text_rect)

    return surface
