import pygame
import random
from constants import BLUE, WHITE, YELLOW


class CardPack:
    """カードパッククラス"""
    def __init__(self, x, y, scale=1.0, pack_image_path=None):
        self.x = x
        self.y = y
        self.initial_x = x  # 初期位置を記憶
        self.scale = scale
        self.destroyed = False
        self.color = BLUE
        self.pack_image_path = pack_image_path
        self.pack_image = None

        # デフォルトサイズ
        self.width = int(60 * scale)
        self.height = int(80 * scale)

        # パック画像を読み込み（元の縦横比を維持）
        if pack_image_path:
            try:
                img = pygame.image.load(pack_image_path)
                original_width = img.get_width()
                original_height = img.get_height()

                # 基準の高さに合わせてスケーリング（縦横比を維持）
                target_height = int(80 * scale)
                aspect_ratio = original_width / original_height
                target_width = int(target_height * aspect_ratio)

                self.width = target_width
                self.height = target_height
                self.pack_image = pygame.transform.scale(img, (self.width, self.height))
            except Exception as e:
                print(f"パック画像読み込みエラー: {e}")
                self.pack_image = None

        # ランダムな左右移動（スケールに応じて調整）
        self.speed = random.uniform(1, 3) * scale
        self.direction = random.choice([-1, 1])
        self.move_range = random.randint(int(30 * scale), int(80 * scale))

    def update(self):
        """カードパックを左右に動かす"""
        if not self.destroyed:
            self.x += self.speed * self.direction

            # 初期位置から一定範囲を超えたら方向転換
            if abs(self.x - self.initial_x) > self.move_range:
                self.direction *= -1

    def draw(self, screen):
        """カードパックを描画"""
        if not self.destroyed:
            if self.pack_image:
                screen.blit(self.pack_image, (self.x, self.y))
            else:
                # フォールバック: ダミー描画
                pygame.draw.rect(screen, self.color,
                               (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, WHITE,
                               (self.x, self.y, self.width, self.height), int(3 * self.scale))
                # パックの中央に★マーク
                font_size = int(40 * self.scale)
                font = pygame.font.Font(None, font_size)
                star = font.render("★", True, YELLOW)
                star_rect = star.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
                screen.blit(star, star_rect)

    def get_rect(self):
        """衝突判定用の矩形を返す"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def destroy(self):
        """カードパックを破壊"""
        self.destroyed = True
