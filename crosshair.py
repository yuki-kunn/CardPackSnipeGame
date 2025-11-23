import pygame
from constants import DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT, RED


class Crosshair:
    """照準クラス"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = screen_width // 2
        self.y = screen_height // 2
        # 画面サイズに応じてサイズをスケーリング
        scale = min(screen_width / DEFAULT_SCREEN_WIDTH, screen_height / DEFAULT_SCREEN_HEIGHT)
        self.size = int(20 * scale)
        self.speed = max(3, int(5 * scale))

    def get_rect(self):
        """衝突判定用の矩形を返す"""
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2,
                          self.size, self.size)

    def update(self, keys):
        """矢印キーで照準を移動"""
        if keys[pygame.K_LEFT] and self.x > self.size:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < self.screen_width - self.size:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > self.size:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < self.screen_height - self.size:
            self.y += self.speed

    def update_screen_size(self, screen_width, screen_height):
        """画面サイズ更新時に照準位置を調整"""
        self.screen_width = screen_width
        self.screen_height = screen_height
        # サイズをスケーリング
        scale = min(screen_width / DEFAULT_SCREEN_WIDTH, screen_height / DEFAULT_SCREEN_HEIGHT)
        self.size = int(20 * scale)
        self.speed = max(3, int(5 * scale))
        # 照準が画面外に出ないように調整
        self.x = min(self.x, screen_width - self.size)
        self.y = min(self.y, screen_height - self.size)

    def draw(self, screen):
        """照準を描画"""
        # 十字の照準
        pygame.draw.line(screen, RED, (self.x - self.size, self.y),
                        (self.x + self.size, self.y), 3)
        pygame.draw.line(screen, RED, (self.x, self.y - self.size),
                        (self.x, self.y + self.size), 3)
        pygame.draw.circle(screen, RED, (self.x, self.y), self.size, 2)
