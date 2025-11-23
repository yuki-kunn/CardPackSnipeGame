import pygame
import random
from constants import (
    DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT, FPS,
    BLACK, WHITE, RED, GREEN, YELLOW,
    INITIAL_AMMO, CARD_PACKS_COUNT, TIME_LIMIT,
    STATE_START, STATE_SHOOTING, STATE_PACK_OPENING,
    STATE_CARD_COLLECTION, STATE_RESULT
)
from utils import get_japanese_font, load_card_images, load_pack_images
from crosshair import Crosshair
from hit_effect import HitEffect
from card_pack import CardPack
from pack_opening import PackOpening


class Game:
    """メインゲームクラス"""
    def __init__(self):
        self.screen_width = DEFAULT_SCREEN_WIDTH
        self.screen_height = DEFAULT_SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("カードパックをうちおとせ！")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_START

        # 画像ファイルを読み込む
        self.card_image_files = load_card_images()
        self.pack_image_files = load_pack_images()

        # ゲーム要素の初期化
        self.crosshair = Crosshair(self.screen_width, self.screen_height)
        self.card_packs = []
        self.hit_effects = []
        self.ammo = INITIAL_AMMO
        self.start_time = pygame.time.get_ticks()
        self.is_cleared = False
        self.clear_time = 0

        # カードパックの配置
        self._setup_card_packs()

        # パック開封シーン
        self.pack_opening = None

    def _get_scale(self):
        """画面スケールを計算"""
        return min(self.screen_width / DEFAULT_SCREEN_WIDTH, self.screen_height / DEFAULT_SCREEN_HEIGHT)

    def _setup_card_packs(self):
        """カードパックをトランプの5のパターンで配置"""
        center_y = self.screen_height // 2
        scale = self._get_scale()
        offset_x = int(120 * scale)
        offset_y = int(180 * scale)

        centers_x = [self.screen_width // 4, self.screen_width * 3 // 4]

        selected_pack_images = []
        if self.pack_image_files:
            for _ in range(CARD_PACKS_COUNT):
                selected_pack_images.append(random.choice(self.pack_image_files))
        else:
            selected_pack_images = [None] * CARD_PACKS_COUNT

        pack_index = 0
        for center_x in centers_x:
            positions = [
                (center_x - offset_x, center_y - offset_y),
                (center_x + offset_x, center_y - offset_y),
                (center_x, center_y),
                (center_x - offset_x, center_y + offset_y),
                (center_x + offset_x, center_y + offset_y),
            ]

            for x, y in positions:
                pack_image = selected_pack_images[pack_index] if pack_index < len(selected_pack_images) else None
                self.card_packs.append(CardPack(x, y, scale, pack_image))
                pack_index += 1

    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen_width = event.w
                self.screen_height = event.h
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
                scale = self._get_scale()

                self.crosshair.update_screen_size(self.screen_width, self.screen_height)
                self.card_packs.clear()
                self._setup_card_packs()

                if self.pack_opening:
                    self.pack_opening.screen_width = self.screen_width
                    self.pack_opening.screen_height = self.screen_height
                    self.pack_opening.pack_width = int(200 * scale)
                    self.pack_opening.pack_height = int(280 * scale)
                    self.pack_opening.pack_x = self.screen_width // 2 - self.pack_opening.pack_width // 2
                    self.pack_opening.pack_y = self.screen_height // 2 - self.pack_opening.pack_height // 2
                    self.pack_opening.pack_image = self.pack_opening._load_random_pack_image()
                    self.pack_opening.card_width = int(80 * scale)
                    self.pack_opening.card_height = int(120 * scale)
                    self.pack_opening.font = get_japanese_font(int(28 * scale))
                    self.pack_opening.small_font = get_japanese_font(int(18 * scale))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.state == STATE_PACK_OPENING and self.pack_opening:
                        self.pack_opening.handle_mouse_click(event.pos)

            elif event.type == pygame.KEYDOWN:
                if self.state == STATE_START:
                    if event.key == pygame.K_SPACE:
                        self._start_game()
                elif self.state == STATE_SHOOTING:
                    if event.key == pygame.K_SPACE:
                        self._fire()
                elif self.state == STATE_PACK_OPENING:
                    if event.key == pygame.K_SPACE and self.pack_opening.is_opened:
                        if self.pack_opening.all_cards_flipped():
                            if not self.pack_opening.next_pack():
                                self.state = STATE_CARD_COLLECTION
                elif self.state == STATE_CARD_COLLECTION:
                    if event.key == pygame.K_SPACE:
                        self._back_to_start()

    def _start_game(self):
        """ゲームを開始"""
        self.state = STATE_SHOOTING
        self.start_time = pygame.time.get_ticks()

    def _reset_game(self):
        """ゲーム状態をリセット"""
        self.card_packs.clear()
        self.hit_effects.clear()
        self.ammo = INITIAL_AMMO
        self.is_cleared = False
        self.clear_time = 0
        self.pack_opening = None
        self._setup_card_packs()

    def _back_to_start(self):
        """スタート画面に戻る"""
        self._reset_game()
        self.state = STATE_START

    def _fire(self):
        """照準位置でヒット判定"""
        if self.ammo > 0:
            self.ammo -= 1
            crosshair_rect = self.crosshair.get_rect()

            for pack in self.card_packs:
                if pack.destroyed:
                    continue

                if crosshair_rect.colliderect(pack.get_rect()):
                    pack.destroy()
                    scale = self._get_scale()
                    effect_x = pack.x + pack.width // 2
                    effect_y = pack.y + pack.height // 2
                    self.hit_effects.append(HitEffect(effect_x, effect_y, scale))
                    break

    def _restart(self):
        """ゲームを再開"""
        self._reset_game()
        self.start_time = pygame.time.get_ticks()
        self.state = STATE_SHOOTING

    def update(self):
        """ゲーム状態の更新"""
        keys = pygame.key.get_pressed()

        if self.state == STATE_SHOOTING:
            self.crosshair.update(keys)

            for pack in self.card_packs:
                pack.update()

            for effect in self.hit_effects[:]:
                effect.update()
                if not effect.active:
                    self.hit_effects.remove(effect)

            self._check_game_over()

        elif self.state == STATE_PACK_OPENING:
            if self.pack_opening:
                self.pack_opening.handle_input(keys)

    def _get_remaining_time(self):
        """残り時間を計算"""
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        remaining = TIME_LIMIT - elapsed_time
        return max(0, remaining)

    def _check_game_over(self):
        """ゲームオーバー条件をチェック"""
        shooting_ended = False

        all_destroyed = all(pack.destroyed for pack in self.card_packs)
        if all_destroyed:
            self.is_cleared = True
            elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            self.clear_time = elapsed_time
            shooting_ended = True

        if self.ammo == 0:
            shooting_ended = True

        if self._get_remaining_time() <= 0:
            shooting_ended = True

        if shooting_ended:
            destroyed_count = sum(1 for pack in self.card_packs if pack.destroyed)
            if destroyed_count > 0:
                self.pack_opening = PackOpening(
                    destroyed_count, self.screen_width, self.screen_height,
                    self.card_image_files, self.pack_image_files
                )
                self.state = STATE_PACK_OPENING
            else:
                self.state = STATE_RESULT

    def draw(self):
        """画面描画"""
        if self.state == STATE_START:
            self._draw_start()

        elif self.state == STATE_SHOOTING:
            self.screen.fill(BLACK)

            for pack in self.card_packs:
                pack.draw(self.screen)

            for effect in self.hit_effects:
                effect.draw(self.screen)

            self.crosshair.draw(self.screen)
            self._draw_ui()

        elif self.state == STATE_PACK_OPENING:
            if self.pack_opening:
                self.pack_opening.draw(self.screen)

        elif self.state == STATE_CARD_COLLECTION:
            if self.pack_opening:
                self.pack_opening.draw_card_collection(self.screen)

        elif self.state == STATE_RESULT:
            self.screen.fill(BLACK)
            self._draw_game_over()

        pygame.display.flip()

    def _draw_start(self):
        """スタート画面を描画"""
        self.screen.fill(BLACK)
        scale = self._get_scale()

        # タイトル
        title_font = get_japanese_font(int(40 * scale))
        title_text = title_font.render("カードパックをうちおとせ！", True, YELLOW)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, int(80 * scale)))
        self.screen.blit(title_text, title_rect)

        # 遊び方説明
        rule_font = get_japanese_font(int(18 * scale))
        rules = [
            "【あそびかた】",
            "",
            "やじるしキー: まとをうごかす",
            "スペースキー: たまをうつ",
            "",
            "うごいているパックをねらってうとう！",
            "あてたパックのカードがもらえるよ",
            "",
            f"たまは {INITIAL_AMMO}こ、じかんは {TIME_LIMIT}びょう",
            f"ぜんぶで {CARD_PACKS_COUNT}このパックがあるよ",
        ]

        start_y = int(150 * scale)
        line_height = int(28 * scale)
        for i, rule in enumerate(rules):
            if rule == "【あそびかた】":
                color = GREEN
            elif rule == "":
                continue
            else:
                color = WHITE
            rule_text = rule_font.render(rule, True, color)
            rule_rect = rule_text.get_rect(center=(self.screen_width // 2, start_y + i * line_height))
            self.screen.blit(rule_text, rule_rect)

        # スタート案内
        start_font = get_japanese_font(int(24 * scale))
        start_text = start_font.render("スペースキーでスタート！", True, GREEN)
        start_rect = start_text.get_rect(center=(self.screen_width // 2, self.screen_height - int(60 * scale)))
        self.screen.blit(start_text, start_rect)

    def _draw_ui(self):
        """UI要素を描画"""
        scale = self._get_scale()
        jp_font = get_japanese_font(int(22 * scale))
        line_height = int(30 * scale)

        # 残弾数
        ammo_text = jp_font.render(f"のこりのたま: {self.ammo}", True, WHITE)
        self.screen.blit(ammo_text, (10, 10))

        # 破壊したパック数
        destroyed = sum(1 for pack in self.card_packs if pack.destroyed)
        packs_text = jp_font.render(f"ゲットしたパック: {destroyed}/{CARD_PACKS_COUNT}", True, WHITE)
        self.screen.blit(packs_text, (10, 10 + line_height))

        # 残り時間
        remaining_time = self._get_remaining_time()
        time_color = RED if remaining_time <= 10 else WHITE
        time_text = jp_font.render(f"のこりじかん: {remaining_time:.1f}びょう", True, time_color)
        self.screen.blit(time_text, (10, 10 + line_height * 2))

        # 操作説明
        help_font = get_japanese_font(int(18 * scale))
        help_text = help_font.render("やじるしキー: うごく  スペース: うつ", True, YELLOW)
        help_rect = help_text.get_rect(center=(self.screen_width // 2, self.screen_height - int(20 * scale)))
        self.screen.blit(help_text, help_rect)

    def _draw_game_over(self):
        """ゲームオーバー画面を描画"""
        scale = self._get_scale()
        jp_font = get_japanese_font(int(22 * scale))
        jp_big_font = get_japanese_font(int(36 * scale))

        # 半透明の黒背景
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # タイトル
        if self.is_cleared:
            title_text = jp_big_font.render("クリア！やったね！", True, GREEN)
        else:
            title_text = jp_big_font.render("ざんねん！", True, RED)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(title_text, title_rect)

        # 結果
        destroyed = sum(1 for pack in self.card_packs if pack.destroyed)
        result_text = jp_font.render(
            f"ゲットしたパック: {destroyed}こ / {CARD_PACKS_COUNT}こ",
            True, WHITE
        )
        result_rect = result_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        self.screen.blit(result_text, result_rect)

        # クリアタイム
        if self.is_cleared:
            clear_time_text = jp_font.render(
                f"クリアタイム: {self.clear_time:.2f}びょう",
                True, YELLOW
            )
            clear_time_rect = clear_time_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 60))
            self.screen.blit(clear_time_text, clear_time_rect)
            restart_y = self.screen_height // 2 + 110
        else:
            restart_y = self.screen_height // 2 + 70

        # リスタート案内
        restart_text = jp_font.render("Rキーでもういちどあそぶ", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(self.screen_width // 2, restart_y))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        """メインゲームループ"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
