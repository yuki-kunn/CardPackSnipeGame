import pygame
from constants import YELLOW
from utils import get_japanese_font


class HitEffect:
    """GET!表示エフェクトクラス"""
    def __init__(self, x, y, scale=1.0):
        self.x = x
        self.y = y
        self.scale = scale
        self.lifetime = 60  # フレーム数
        self.age = 0
        self.font_size = int(48 * scale)
        self.font = get_japanese_font(self.font_size)
        self.active = True

    def update(self):
        """エフェクトを更新"""
        self.age += 1
        self.y -= 2 * self.scale  # 上に浮かぶ

        if self.age >= self.lifetime:
            self.active = False

    def draw(self, screen):
        """エフェクトを描画"""
        if not self.active:
            return

        # フェードアウト効果
        alpha = max(0, 255 - int(255 * self.age / self.lifetime))

        # テキストを描画
        text_surface = self.font.render("ゲット！", True, YELLOW)
        text_surface.set_alpha(alpha)

        # 中央に配置
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)
