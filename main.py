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
        self.y = SCREEN_HEIGHT // 2
        self.size = 20
        self.speed = 5

    def get_rect(self):
        """衝突判定用の矩形を返す"""
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2,
                          self.size, self.size)

    def update(self, keys):
        """矢印キーで照準を移動"""
        if keys[pygame.K_LEFT] and self.x > self.size:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.size:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > self.size:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.size:
            self.y += self.speed

    def draw(self, screen):
        """照準を描画"""
        # 十字の照準
        pygame.draw.line(screen, RED, (self.x - self.size, self.y),
                        (self.x + self.size, self.y), 3)
        pygame.draw.line(screen, RED, (self.x, self.y - self.size),
                        (self.x, self.y + self.size), 3)
        pygame.draw.circle(screen, RED, (self.x, self.y), self.size, 2)


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
        self.initial_x = x  # 初期位置を記憶
        self.width = 60
        self.height = 80
        self.destroyed = False
        self.color = BLUE

        # ランダムな左右移動
        self.speed = random.uniform(1, 3)  # ランダムな速度
        self.direction = random.choice([-1, 1])  # ランダムな初期方向
        self.move_range = random.randint(30, 80)  # 移動範囲

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
        self.card_packs = []
        self.cards = []
        self.ammo = INITIAL_AMMO

        # カードパックの配置 (左右に5個ずつ)
        self._setup_card_packs()

        # フォント
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

    def _setup_card_packs(self):
        """カードパックをトランプの5のパターンで配置"""
        # 左側エリアの中心座標
        left_center_x = SCREEN_WIDTH // 4
        center_y = SCREEN_HEIGHT // 2

        # 右側エリアの中心座標
        right_center_x = SCREEN_WIDTH * 3 // 4

        # オフセット（4隅からの距離）
        offset_x = 120
        offset_y = 180

        # 左側に5個（トランプの5のパターン）
        left_positions = [
            (left_center_x - offset_x, center_y - offset_y),  # 左上
            (left_center_x + offset_x, center_y - offset_y),  # 右上
            (left_center_x, center_y),                        # 中央
            (left_center_x - offset_x, center_y + offset_y),  # 左下
            (left_center_x + offset_x, center_y + offset_y),  # 右下
        ]

        for x, y in left_positions:
            self.card_packs.append(CardPack(x, y))

        # 右側に5個（トランプの5のパターン）
        right_positions = [
            (right_center_x - offset_x, center_y - offset_y),  # 左上
            (right_center_x + offset_x, center_y - offset_y),  # 右上
            (right_center_x, center_y),                        # 中央
            (right_center_x - offset_x, center_y + offset_y),  # 左下
            (right_center_x + offset_x, center_y + offset_y),  # 右下
        ]

        for x, y in right_positions:
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
        """照準位置でヒット判定"""
        if self.ammo > 0:
            self.ammo -= 1
            crosshair_rect = self.crosshair.get_rect()

            # 照準とカードパックの衝突判定
            for pack in self.card_packs:
                if pack.destroyed:
                    continue

                if crosshair_rect.colliderect(pack.get_rect()):
                    # ヒット！
                    new_cards = pack.destroy()
                    self.cards.extend(new_cards)
                    break

    def _restart(self):
        """ゲームを再開"""
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

        # カードパックの更新（左右移動）
        for pack in self.card_packs:
            pack.update()

        # カードの更新
        for card in self.cards[:]:
            card.update()
            if not card.active:
                self.cards.remove(card)

        # ゲームオーバー判定
        self._check_game_over()

    def _check_game_over(self):
        """ゲームオーバー条件をチェック"""
        # 弾切れ
        if self.ammo == 0:
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
