import pygame
import random
import sys

# 初期化
pygame.init()

# 定数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 200)
ORANGE = (255, 165, 0)

# ゲーム設定
INITIAL_AMMO = 10
CARD_PACKS_COUNT = 10
CARDS_PER_PACK = 5


class Crosshair:
    """照準クラス"""
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 50
        self.size = 20
        self.speed = 5

    def update(self, keys):
        """矢印キーで照準を移動"""
        if keys[pygame.K_LEFT] and self.x > self.size:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.size:
            self.x += self.speed

    def draw(self, screen):
        """照準を描画"""
        # 十字の照準
        pygame.draw.line(screen, RED, (self.x - self.size, self.y),
                        (self.x + self.size, self.y), 3)
        pygame.draw.line(screen, RED, (self.x, self.y - self.size),
                        (self.x, self.y + self.size), 3)
        pygame.draw.circle(screen, RED, (self.x, self.y), self.size, 2)


class Bullet:
    """弾丸クラス"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = 10
        self.active = True

    def update(self):
        """弾丸を上に移動"""
        self.y -= self.speed
        if self.y < 0:
            self.active = False

    def draw(self, screen):
        """弾丸を描画"""
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)

    def get_rect(self):
        """衝突判定用の矩形を返す"""
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                          self.radius * 2, self.radius * 2)


class Card:
    """カードクラス"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.speed = 3
        self.color = random.choice([RED, BLUE, GREEN, PURPLE, ORANGE])
        self.active = True

    def update(self):
        """カードを下に落とす"""
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.active = False

    def draw(self, screen):
        """カードを描画"""
        pygame.draw.rect(screen, self.color,
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE,
                        (self.x, self.y, self.width, self.height), 2)


class CardPack:
    """カードパッククラス"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 80
        self.destroyed = False
        self.color = BLUE

    def draw(self, screen):
        """カードパックを描画"""
        if not self.destroyed:
            pygame.draw.rect(screen, self.color,
                           (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, WHITE,
                           (self.x, self.y, self.width, self.height), 3)
            # パックの中央に★マーク
            font = pygame.font.Font(None, 40)
            star = font.render("★", True, YELLOW)
            screen.blit(star, (self.x + 15, self.y + 20))

    def get_rect(self):
        """衝突判定用の矩形を返す"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def destroy(self):
        """カードパックを破壊してカードを生成"""
        self.destroyed = True
        cards = []
        for i in range(CARDS_PER_PACK):
            # パックの位置からランダムな方向にカードを散らす
            offset_x = random.randint(-30, 30)
            card = Card(self.x + self.width // 2 + offset_x, self.y)
            cards.append(card)
        return cards


class Game:
    """メインゲームクラス"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PokePoke - Card Pack Sniper")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False

        # ゲーム要素の初期化
        self.crosshair = Crosshair()
        self.bullets = []
        self.card_packs = []
        self.cards = []
        self.ammo = INITIAL_AMMO

        # カードパックの配置 (左右に5個ずつ)
        self._setup_card_packs()

        # フォント
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

    def _setup_card_packs(self):
        """カードパックを左右に配置"""
        # 左側に5個
        for i in range(5):
            x = 50
            y = 80 + i * 100
            self.card_packs.append(CardPack(x, y))

        # 右側に5個
        for i in range(5):
            x = SCREEN_WIDTH - 110
            y = 80 + i * 100
            self.card_packs.append(CardPack(x, y))

    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self._fire()
                elif event.key == pygame.K_r and self.game_over:
                    self._restart()

    def _fire(self):
        """弾丸を発射"""
        if self.ammo > 0:
            bullet = Bullet(self.crosshair.x, self.crosshair.y)
            self.bullets.append(bullet)
            self.ammo -= 1

    def _restart(self):
        """ゲームを再開"""
        self.bullets.clear()
        self.card_packs.clear()
        self.cards.clear()
        self.ammo = INITIAL_AMMO
        self.game_over = False
        self._setup_card_packs()

    def update(self):
        """ゲーム状態の更新"""
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.crosshair.update(keys)

        # 弾丸の更新
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)

        # カードの更新
        for card in self.cards[:]:
            card.update()
            if not card.active:
                self.cards.remove(card)

        # 衝突判定
        self._check_collisions()

        # ゲームオーバー判定
        self._check_game_over()

    def _check_collisions(self):
        """弾丸とカードパックの衝突判定"""
        for bullet in self.bullets[:]:
            if not bullet.active:
                continue
            bullet_rect = bullet.get_rect()

            for pack in self.card_packs:
                if pack.destroyed:
                    continue

                if bullet_rect.colliderect(pack.get_rect()):
                    # ヒット！
                    bullet.active = False
                    self.bullets.remove(bullet)
                    new_cards = pack.destroy()
                    self.cards.extend(new_cards)
                    break

    def _check_game_over(self):
        """ゲームオーバー条件をチェック"""
        # 弾切れ
        if self.ammo == 0 and len(self.bullets) == 0:
            self.game_over = True

        # 全カードパック破壊
        all_destroyed = all(pack.destroyed for pack in self.card_packs)
        if all_destroyed:
            self.game_over = True

    def draw(self):
        """画面描画"""
        self.screen.fill(BLACK)

        # カードパックを描画
        for pack in self.card_packs:
            pack.draw(self.screen)

        # カードを描画
        for card in self.cards:
            card.draw(self.screen)

        # 弾丸を描画
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # 照準を描画
        self.crosshair.draw(self.screen)

        # UI描画
        self._draw_ui()

        # ゲームオーバー画面
        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_ui(self):
        """UI要素を描画"""
        # 残弾数
        ammo_text = self.font.render(f"Ammo: {self.ammo}", True, WHITE)
        self.screen.blit(ammo_text, (10, 10))

        # 破壊したパック数
        destroyed = sum(1 for pack in self.card_packs if pack.destroyed)
        packs_text = self.font.render(f"Packs: {destroyed}/{CARD_PACKS_COUNT}", True, WHITE)
        self.screen.blit(packs_text, (10, 50))

        # 獲得カード数
        cards_text = self.font.render(f"Cards: {len(self.cards)}", True, WHITE)
        self.screen.blit(cards_text, (SCREEN_WIDTH - 150, 10))

    def _draw_game_over(self):
        """ゲームオーバー画面を描画"""
        # 半透明の黒背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # GAME OVER テキスト
        game_over_text = self.big_font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)

        # 結果
        destroyed = sum(1 for pack in self.card_packs if pack.destroyed)
        result_text = self.font.render(
            f"Packs Destroyed: {destroyed}/{CARD_PACKS_COUNT}",
            True, WHITE
        )
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(result_text, result_rect)

        # リスタート案内
        restart_text = self.font.render("Press R to Restart", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        """メインゲームループ"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
