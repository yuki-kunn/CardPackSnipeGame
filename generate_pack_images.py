import pygame
import os
import random

def generate_pack_images():
    """カードパック画像を生成する"""
    pygame.init()

    # imagesフォルダを作成
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"フォルダを作成しました: {images_dir}")

    # パックの種類と色を定義
    packs = [
        {"name": "charizard", "base_color": (255, 100, 50), "accent": (255, 200, 0), "label": "リザードン"},
        {"name": "pikachu", "base_color": (255, 220, 50), "accent": (255, 150, 50), "label": "ピカチュウ"},
        {"name": "mewtwo", "base_color": (180, 100, 255), "accent": (255, 100, 255), "label": "ミュウツー"},
        {"name": "mew", "base_color": (255, 150, 200), "accent": (255, 200, 230), "label": "ミュウ"},
        {"name": "gyarados", "base_color": (50, 100, 200), "accent": (100, 200, 255), "label": "ギャラドス"},
        {"name": "dragonite", "base_color": (255, 180, 100), "accent": (255, 220, 150), "label": "カイリュー"},
        {"name": "snorlax", "base_color": (100, 150, 180), "accent": (200, 230, 255), "label": "カビゴン"},
        {"name": "gengar", "base_color": (100, 50, 150), "accent": (180, 100, 255), "label": "ゲンガー"},
        {"name": "eevee", "base_color": (180, 150, 100), "accent": (230, 200, 150), "label": "イーブイ"},
        {"name": "lucario", "base_color": (50, 100, 180), "accent": (100, 180, 255), "label": "ルカリオ"},
    ]

    # パック画像のサイズ
    width = 200
    height = 280

    generated_count = 0

    for i, pack in enumerate(packs):
        # パック画像を作成
        surface = pygame.Surface((width, height))

        # 背景グラデーション
        base_color = pack["base_color"]
        for y in range(height):
            factor = y / height
            # グラデーション効果
            r = int(base_color[0] * (1 - factor * 0.3))
            g = int(base_color[1] * (1 - factor * 0.3))
            b = int(base_color[2] * (1 - factor * 0.3))
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

        # 外枠
        pygame.draw.rect(surface, (50, 50, 50), (0, 0, width, height), 4)

        # アクセントカラーの装飾
        accent = pack["accent"]

        # 上部の装飾バー
        pygame.draw.rect(surface, accent, (10, 10, width - 20, 30))
        pygame.draw.rect(surface, (255, 255, 255), (10, 10, width - 20, 30), 2)

        # 中央のダイヤモンド形状
        center_x = width // 2
        center_y = height // 2
        diamond_size = 60
        diamond_points = [
            (center_x, center_y - diamond_size),
            (center_x + diamond_size, center_y),
            (center_x, center_y + diamond_size),
            (center_x - diamond_size, center_y)
        ]
        pygame.draw.polygon(surface, accent, diamond_points)
        pygame.draw.polygon(surface, (255, 255, 255), diamond_points, 3)

        # 内側の光沢効果
        inner_diamond_size = 40
        inner_points = [
            (center_x, center_y - inner_diamond_size),
            (center_x + inner_diamond_size, center_y),
            (center_x, center_y + inner_diamond_size),
            (center_x - inner_diamond_size, center_y)
        ]
        highlight_color = (
            min(255, accent[0] + 50),
            min(255, accent[1] + 50),
            min(255, accent[2] + 50)
        )
        pygame.draw.polygon(surface, highlight_color, inner_points)

        # 下部の装飾バー
        pygame.draw.rect(surface, accent, (10, height - 40, width - 20, 30))
        pygame.draw.rect(surface, (255, 255, 255), (10, height - 40, width - 20, 30), 2)

        # 角の装飾
        corner_size = 15
        for corner_x, corner_y in [(10, 50), (width - 25, 50), (10, height - 65), (width - 25, height - 65)]:
            pygame.draw.rect(surface, (255, 255, 255, 128), (corner_x, corner_y, corner_size, corner_size), 2)

        # 光沢効果（斜めのライン）
        for offset in range(0, width + height, 30):
            start_x = offset
            start_y = 0
            end_x = offset - height
            end_y = height
            if start_x > width:
                start_y = start_x - width
                start_x = width
            if end_x < 0:
                end_y = height + end_x
                end_x = 0
            pygame.draw.line(surface, (255, 255, 255, 50), (start_x, start_y), (end_x, end_y), 1)

        # ファイル名を生成して保存
        filename = f"pack_{i+1:03d}_{pack['name']}.png"
        filepath = os.path.join(images_dir, filename)

        pygame.image.save(surface, filepath)
        generated_count += 1
        print(f"生成完了: {filepath} ({pack['label']})")

    # 追加のバリエーションを生成（異なるパターン）
    additional_packs = [
        {"name": "fire", "base_color": (200, 50, 30), "accent": (255, 150, 0)},
        {"name": "water", "base_color": (30, 100, 200), "accent": (100, 200, 255)},
        {"name": "grass", "base_color": (50, 150, 50), "accent": (150, 255, 100)},
        {"name": "electric", "base_color": (255, 200, 0), "accent": (255, 255, 100)},
        {"name": "psychic", "base_color": (200, 50, 150), "accent": (255, 150, 200)},
        {"name": "fighting", "base_color": (180, 100, 50), "accent": (255, 180, 100)},
        {"name": "dark", "base_color": (50, 50, 80), "accent": (100, 100, 150)},
        {"name": "steel", "base_color": (150, 150, 180), "accent": (200, 200, 230)},
        {"name": "dragon", "base_color": (100, 50, 200), "accent": (150, 100, 255)},
        {"name": "fairy", "base_color": (255, 150, 200), "accent": (255, 200, 230)},
    ]

    for i, pack in enumerate(additional_packs):
        surface = pygame.Surface((width, height))

        # 背景
        base_color = pack["base_color"]
        surface.fill(base_color)

        # 円形グラデーション効果
        for radius in range(min(width, height) // 2, 0, -5):
            factor = radius / (min(width, height) // 2)
            r = int(base_color[0] + (255 - base_color[0]) * (1 - factor) * 0.3)
            g = int(base_color[1] + (255 - base_color[1]) * (1 - factor) * 0.3)
            b = int(base_color[2] + (255 - base_color[2]) * (1 - factor) * 0.3)
            pygame.draw.circle(surface, (r, g, b), (width // 2, height // 2), radius)

        # 外枠
        pygame.draw.rect(surface, (30, 30, 30), (0, 0, width, height), 5)

        # 上部装飾
        accent = pack["accent"]
        pygame.draw.rect(surface, accent, (15, 15, width - 30, 25))

        # 中央の星形
        center_x = width // 2
        center_y = height // 2
        star_points = []
        for j in range(10):
            angle = j * 36 - 90
            if j % 2 == 0:
                r = 50
            else:
                r = 25
            import math
            x = center_x + r * math.cos(math.radians(angle))
            y = center_y + r * math.sin(math.radians(angle))
            star_points.append((x, y))
        pygame.draw.polygon(surface, accent, star_points)
        pygame.draw.polygon(surface, (255, 255, 255), star_points, 2)

        # 下部装飾
        pygame.draw.rect(surface, accent, (15, height - 40, width - 30, 25))

        # ファイル保存
        filename = f"pack_{len(packs) + i + 1:03d}_{pack['name']}.png"
        filepath = os.path.join(images_dir, filename)

        pygame.image.save(surface, filepath)
        generated_count += 1
        print(f"生成完了: {filepath}")

    pygame.quit()
    print(f"\n完了: {generated_count} 枚のパック画像を生成しました")
    return generated_count

if __name__ == "__main__":
    generate_pack_images()
