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
TIME_LIMIT = 45  # 制限時間（秒）

# ゲーム状態
STATE_SHOOTING = "shooting"
STATE_PACK_OPENING = "pack_opening"
STATE_RESULT = "result"


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
    pack_text = text_font.render("PACK", True, WHITE)
    pack_rect = pack_text.get_rect(center=(width // 2, height - 30))
    surface.blit(pack_text, pack_rect)
    return surface


def create_dummy_card_image(width, height, color, name):
    """ダミーのカード画像を生成"""
    surface = pygame.Surface((width, height))
    surface.fill(color)
    # 枠線
    pygame.draw.rect(surface, WHITE, (0, 0, width, height), 2)
    # カード名
    font = pygame.font.Font(None, 24)
    name_text = font.render(name, True, WHITE)
    name_rect = name_text.get_rect(center=(width // 2, height // 2))
    surface.blit(name_text, name_rect)
    return surface


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


class PackOpening:
    """パック開封シーンクラス"""
    def __init__(self, destroyed_packs_count):
        self.destroyed_packs_count = destroyed_packs_count
        self.current_pack_index = 0
        self.opening_progress = 0  # 0-100の開封進行度
        self.is_opened = False
        self.pack_width = 200
        self.pack_height = 280
        self.pack_x = SCREEN_WIDTH // 2 - self.pack_width // 2
        self.pack_y = SCREEN_HEIGHT // 2 - self.pack_height // 2

        # パック画像
        self.pack_image = create_dummy_pack_image(self.pack_width, self.pack_height)

        # ダミーカードデータ
        self.current_cards = self._generate_dummy_cards()

        # フォント
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def _generate_dummy_cards(self):
        """ダミーカードを生成"""
        colors = [RED, BLUE, GREEN, PURPLE, ORANGE]
        card_width = 80
        card_height = 120
        cards = []
        for i in range(CARDS_PER_PACK):
            name = f'Card {i+1}'
            color = colors[i % len(colors)]
            cards.append({
                'name': name,
                'color': color,
                'rarity': ['Common', 'Rare', 'Super Rare'][i % 3],
                'image': create_dummy_card_image(card_width, card_height, color, name)
            })
        return cards

    def handle_input(self, keys):
        """キー入力処理"""
        if not self.is_opened:
            # 矢印キーのいずれかが押されたら開封進行
            if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.opening_progress += 2
                if self.opening_progress >= 100:
                    self.opening_progress = 100
                    self.is_opened = True

    def draw(self, screen):
        """描画"""
        screen.fill(BLACK)

        if not self.is_opened:
            self._draw_pack_opening(screen)
        else:
            self._draw_opened_cards(screen)

    def _draw_pack_opening(self, screen):
        """パック開封中の描画"""
        # タイトル（何パック目か）
        title_text = self.font.render(f"Pack {self.current_pack_index + 1}/{self.destroyed_packs_count}", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title_text, title_rect)

        # 切り取られる上部の高さ
        cut_height = int(self.pack_height * 0.3 * (self.opening_progress / 100))

        # パック本体（下部）- 画像の下部分を描画
        pack_body_start_y = cut_height
        pack_body_height = self.pack_height - cut_height
        if pack_body_height > 0:
            # 画像の下部分を切り取って描画
            pack_body_area = pygame.Rect(0, pack_body_start_y, self.pack_width, pack_body_height)
            pack_body_surface = self.pack_image.subsurface(pack_body_area)
            screen.blit(pack_body_surface, (self.pack_x, self.pack_y + cut_height))

        # パック上部（切り取られる部分）- 画像の上部分を描画
        if self.opening_progress < 100:
            top_height = int(self.pack_height * 0.3 * (1 - self.opening_progress / 100))
            if top_height > 0:
                # 画像の上部分を切り取って描画（上に移動していく演出）
                top_area = pygame.Rect(0, 0, self.pack_width, top_height)
                top_surface = self.pack_image.subsurface(top_area)
                top_y = self.pack_y - (int(self.pack_height * 0.3) - top_height)
                screen.blit(top_surface, (self.pack_x, top_y))

        # 操作案内
        guide_text = self.small_font.render("Press Arrow Keys to Open!", True, WHITE)
        guide_rect = guide_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(guide_text, guide_rect)

        # 進行度バー
        bar_width = 300
        bar_height = 20
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = SCREEN_HEIGHT // 2 + self.pack_height // 2 + 50
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * self.opening_progress / 100), bar_height))

    def _draw_opened_cards(self, screen):
        """開封後のカード表示"""
        # タイトル
        title_text = self.font.render("Pack Opened!", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(title_text, title_rect)

        # カードを横並びに表示
        card_width = 80
        card_height = 120
        spacing = 20
        total_width = card_width * 5 + spacing * 4
        start_x = SCREEN_WIDTH // 2 - total_width // 2
        start_y = SCREEN_HEIGHT // 2 - card_height // 2

        for i, card in enumerate(self.current_cards):
            x = start_x + i * (card_width + spacing)
            # カード画像を描画
            screen.blit(card['image'], (x, start_y))

        # 次のパックまたは結果へ進む案内
        if self.current_pack_index < self.destroyed_packs_count - 1:
            next_text = self.small_font.render("Press SPACE for Next Pack", True, WHITE)
        else:
            next_text = self.small_font.render("Press SPACE to Continue", True, WHITE)
        next_rect = next_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(next_text, next_rect)

    def next_pack(self):
        """次のパックへ"""
        if self.current_pack_index < self.destroyed_packs_count - 1:
            self.current_pack_index += 1
            self.opening_progress = 0
            self.is_opened = False
            self.current_cards = self._generate_dummy_cards()
            return True
        return False

    def is_finished(self):
        """全パックの開封が完了したか"""
        return self.is_opened and self.current_pack_index >= self.destroyed_packs_count - 1


class Game:
    """メインゲームクラス"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PokePoke - Card Pack Sniper")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_SHOOTING

        # ゲーム要素の初期化
        self.crosshair = Crosshair()
        self.card_packs = []
        self.cards = []
        self.ammo = INITIAL_AMMO
        self.start_time = pygame.time.get_ticks()  # ゲーム開始時刻
        self.is_cleared = False  # クリアしたかどうか
        self.clear_time = 0  # クリアタイム

        # カードパックの配置 (左右に5個ずつ)
        self._setup_card_packs()

        # パック開封シーン
        self.pack_opening = None

        # フォント
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

    def _setup_card_packs(self):
        """カードパックをトランプの5のパターンで配置"""
        center_y = SCREEN_HEIGHT // 2
        offset_x = 120
        offset_y = 180

        # 左側と右側の中心X座標
        centers_x = [SCREEN_WIDTH // 4, SCREEN_WIDTH * 3 // 4]

        # 各中心点に対してトランプの5のパターンで配置
        for center_x in centers_x:
            positions = [
                (center_x - offset_x, center_y - offset_y),  # 左上
                (center_x + offset_x, center_y - offset_y),  # 右上
                (center_x, center_y),                        # 中央
                (center_x - offset_x, center_y + offset_y),  # 左下
                (center_x + offset_x, center_y + offset_y),  # 右下
            ]

            for x, y in positions:
                self.card_packs.append(CardPack(x, y))

    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == STATE_SHOOTING:
                    if event.key == pygame.K_SPACE:
                        self._fire()
                elif self.state == STATE_PACK_OPENING:
                    if event.key == pygame.K_SPACE and self.pack_opening.is_opened:
                        # 次のパックへ、または結果画面へ
                        if not self.pack_opening.next_pack():
                            self.state = STATE_RESULT
                elif self.state == STATE_RESULT:
                    if event.key == pygame.K_r:
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
        self.is_cleared = False
        self.clear_time = 0
        self.start_time = pygame.time.get_ticks()  # タイマーをリセット
        self.state = STATE_SHOOTING
        self.pack_opening = None
        self._setup_card_packs()

    def update(self):
        """ゲーム状態の更新"""
        keys = pygame.key.get_pressed()

        if self.state == STATE_SHOOTING:
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

        elif self.state == STATE_PACK_OPENING:
            if self.pack_opening:
                self.pack_opening.handle_input(keys)

    def _get_remaining_time(self):
        """残り時間を計算（秒）"""
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        remaining = TIME_LIMIT - elapsed_time
        return max(0, remaining)

    def _check_game_over(self):
        """ゲームオーバー条件をチェック"""
        shooting_ended = False

        # 全カードパック破壊（クリア）
        all_destroyed = all(pack.destroyed for pack in self.card_packs)
        if all_destroyed:
            self.is_cleared = True
            elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            self.clear_time = elapsed_time
            shooting_ended = True

        # 弾切れ
        if self.ammo == 0:
            shooting_ended = True

        # 制限時間切れ
        if self._get_remaining_time() <= 0:
            shooting_ended = True

        # シューティング終了時、パック開封シーンへ遷移
        if shooting_ended:
            destroyed_count = sum(1 for pack in self.card_packs if pack.destroyed)
            if destroyed_count > 0:
                self.pack_opening = PackOpening(destroyed_count)
                self.state = STATE_PACK_OPENING
            else:
                # パックを1つも破壊していない場合は結果画面へ
                self.state = STATE_RESULT

    def draw(self):
        """画面描画"""
        if self.state == STATE_SHOOTING:
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

        elif self.state == STATE_PACK_OPENING:
            if self.pack_opening:
                self.pack_opening.draw(self.screen)

        elif self.state == STATE_RESULT:
            self.screen.fill(BLACK)
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

        # 残り時間
        remaining_time = self._get_remaining_time()
        time_color = RED if remaining_time <= 10 else WHITE
        time_text = self.font.render(f"Time: {remaining_time:.1f}s", True, time_color)
        self.screen.blit(time_text, (10, 90))

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

        # タイトルテキスト（クリアか失敗か）
        if self.is_cleared:
            title_text = self.big_font.render("CLEAR!", True, GREEN)
        else:
            title_text = self.big_font.render("GAME OVER", True, RED)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(title_text, title_rect)

        # 結果
        destroyed = sum(1 for pack in self.card_packs if pack.destroyed)
        result_text = self.font.render(
            f"Packs Destroyed: {destroyed}/{CARD_PACKS_COUNT}",
            True, WHITE
        )
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(result_text, result_rect)

        # クリアタイム表示（クリアした場合のみ）
        if self.is_cleared:
            clear_time_text = self.font.render(
                f"Clear Time: {self.clear_time:.2f}s",
                True, YELLOW
            )
            clear_time_rect = clear_time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(clear_time_text, clear_time_rect)
            restart_y = SCREEN_HEIGHT // 2 + 110
        else:
            restart_y = SCREEN_HEIGHT // 2 + 70

        # リスタート案内
        restart_text = self.font.render("Press R to Restart", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, restart_y))
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
