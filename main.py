import pygame
import random
import sys
import os
import glob

# 初期化
pygame.init()

# 定数
DEFAULT_SCREEN_WIDTH = 800
DEFAULT_SCREEN_HEIGHT = 600
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
STATE_CARD_COLLECTION = "card_collection"
STATE_RESULT = "result"

# カードマスターデータ（20種類）
CARD_MASTER_DATA = [
    {"id": 1, "name": "Fire Dragon", "color": RED, "rarity": "Super Rare"},
    {"id": 2, "name": "Water Spirit", "color": BLUE, "rarity": "Rare"},
    {"id": 3, "name": "Earth Golem", "color": GREEN, "rarity": "Common"},
    {"id": 4, "name": "Thunder Bird", "color": YELLOW, "rarity": "Rare"},
    {"id": 5, "name": "Dark Knight", "color": PURPLE, "rarity": "Super Rare"},
    {"id": 6, "name": "Light Angel", "color": WHITE, "rarity": "Super Rare"},
    {"id": 7, "name": "Ice Phoenix", "color": BLUE, "rarity": "Rare"},
    {"id": 8, "name": "Forest Elf", "color": GREEN, "rarity": "Common"},
    {"id": 9, "name": "Flame Wizard", "color": ORANGE, "rarity": "Rare"},
    {"id": 10, "name": "Wind Fairy", "color": (173, 216, 230), "rarity": "Common"},
    {"id": 11, "name": "Rock Giant", "color": (139, 69, 19), "rarity": "Common"},
    {"id": 12, "name": "Storm Dragon", "color": YELLOW, "rarity": "Super Rare"},
    {"id": 13, "name": "Shadow Assassin", "color": (64, 64, 64), "rarity": "Rare"},
    {"id": 14, "name": "Crystal Guardian", "color": (147, 112, 219), "rarity": "Rare"},
    {"id": 15, "name": "Magma Titan", "color": ORANGE, "rarity": "Super Rare"},
    {"id": 16, "name": "Ocean Leviathan", "color": BLUE, "rarity": "Super Rare"},
    {"id": 17, "name": "Sky Pegasus", "color": (135, 206, 250), "rarity": "Common"},
    {"id": 18, "name": "Jungle Tiger", "color": GREEN, "rarity": "Common"},
    {"id": 19, "name": "Desert Sphinx", "color": (210, 180, 140), "rarity": "Rare"},
    {"id": 20, "name": "Mystic Unicorn", "color": PURPLE, "rarity": "Rare"},
]


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


class HitEffect:
    """GET!表示エフェクトクラス"""
    def __init__(self, x, y, scale=1.0):
        self.x = x
        self.y = y
        self.scale = scale
        self.lifetime = 60  # フレーム数
        self.age = 0
        self.font_size = int(48 * scale)
        self.font = pygame.font.Font(None, self.font_size)
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
        text_surface = self.font.render("GET!", True, YELLOW)
        text_surface.set_alpha(alpha)

        # 中央に配置
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)


def load_card_images():
    """images/フォルダから全カード画像を読み込む"""
    images_dir = "images"
    card_images = []

    if os.path.exists(images_dir):
        # rare_card_*.png/jpg/webp のパターンで画像を検索
        patterns = ['rare_card_*.png', 'rare_card_*.jpg', 'rare_card_*.webp']
        for pattern in patterns:
            files = glob.glob(os.path.join(images_dir, pattern))
            card_images.extend(files)

        # ファイル名でソート
        card_images.sort()

    print(f"{len(card_images)} 枚のカード画像を見つけました")
    return card_images


def load_pack_images():
    """pack_images/フォルダからパック画像を読み込む"""
    # ダミーデータを使用（空のリストを返す）
    print("パック画像: ダミーデータを使用")
    return []


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


def load_and_scale_card_image(image_path, width, height):
    """カード画像を読み込んでリサイズする"""
    try:
        image = pygame.image.load(image_path)
        # カードのサイズに合わせてスケーリング
        image = pygame.transform.scale(image, (width, height))
        return image
    except Exception as e:
        print(f"画像読み込みエラー ({image_path}): {e}")
        # エラー時はダミー画像を返す
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

    # テキストを適切に分割
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
        self.speed = random.uniform(1, 3) * scale  # ランダムな速度
        self.direction = random.choice([-1, 1])  # ランダムな初期方向
        self.move_range = random.randint(int(30 * scale), int(80 * scale))  # 移動範囲

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
                # パック画像を描画
                screen.blit(self.pack_image, (self.x, self.y))
            else:
                # フォールバック: ダミー描画
                pygame.draw.rect(screen, self.color,
                               (self.x, self.y, self.width, self.height))
                pygame.draw.rect(screen, WHITE,
                               (self.x, self.y, self.width, self.height), int(3 * self.scale))
                # パックの中央に★マーク（スケールに応じて調整）
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


class PackOpening:
    """パック開封シーンクラス"""
    def __init__(self, destroyed_packs_count, screen_width, screen_height, card_image_files, pack_image_files=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.destroyed_packs_count = destroyed_packs_count
        self.current_pack_index = 0
        self.opening_progress = 0  # 0-100の開封進行度
        self.is_opened = False
        self.card_image_files = card_image_files  # 利用可能な画像ファイルのリスト
        self.pack_image_files = pack_image_files or []  # パック画像ファイルのリスト

        # スケール計算
        scale = min(screen_width / DEFAULT_SCREEN_WIDTH, screen_height / DEFAULT_SCREEN_HEIGHT)
        self.pack_width = int(200 * scale)
        self.pack_height = int(280 * scale)
        self.pack_x = screen_width // 2 - self.pack_width // 2
        self.pack_y = screen_height // 2 - self.pack_height // 2

        # パック画像（ランダムに選択）
        self.pack_image = self._load_random_pack_image()

        # カードデータ（画面サイズに応じて動的にサイズ調整）
        # 画面の高さの約30%をカードの高さとする
        self.card_height = int(self.screen_height * 0.35)
        # アスペクト比を2:3に保つ
        self.card_width = int(self.card_height * 2 / 3)

        # カード裏面画像を読み込む
        self.card_back_image = self._load_card_back_image()

        self.current_cards = self._generate_cards()
        self.all_cards = []  # 獲得した全カードを保存

        # フォント
        self.font = pygame.font.Font(None, int(36 * scale))
        self.small_font = pygame.font.Font(None, int(24 * scale))

    def _load_card_back_image(self):
        """カード裏面画像を読み込む"""
        try:
            back_image_path = os.path.join("images", "card_ura.jpg")
            if os.path.exists(back_image_path):
                img = pygame.image.load(back_image_path)
                return pygame.transform.scale(img, (self.card_width, self.card_height))
        except Exception as e:
            print(f"カード裏面画像読み込みエラー: {e}")

        # フォールバック: 青い裏面を生成
        surface = pygame.Surface((self.card_width, self.card_height))
        surface.fill(BLUE)
        pygame.draw.rect(surface, WHITE, (0, 0, self.card_width, self.card_height), 3)
        return surface

    def _load_random_pack_image(self):
        """ランダムにパック画像を読み込む"""
        if self.pack_image_files:
            try:
                pack_path = random.choice(self.pack_image_files)
                img = pygame.image.load(pack_path)
                return pygame.transform.scale(img, (self.pack_width, self.pack_height))
            except Exception as e:
                print(f"パック画像読み込みエラー: {e}")
        # フォールバック
        return create_dummy_pack_image(self.pack_width, self.pack_height)

    def _generate_cards(self):
        """ランダムにカードを生成（実際の画像を使用）"""
        cards = []

        # 画像ファイルが利用可能な場合はランダムに選択
        if self.card_image_files and len(self.card_image_files) >= CARDS_PER_PACK:
            # 重複なしで5枚選択
            selected_images = random.sample(self.card_image_files, CARDS_PER_PACK)

            for i, image_path in enumerate(selected_images):
                # 画像を読み込んでスケーリング
                card_image = load_and_scale_card_image(image_path, self.card_width, self.card_height)

                cards.append({
                    'id': i + 1,
                    'name': os.path.basename(image_path),  # ファイル名を使用
                    'image': card_image,
                    'image_path': image_path,
                    'flipped': False  # 裏面から開始
                })
        else:
            # 画像が足りない場合はダミーを使用
            selected_cards = random.sample(CARD_MASTER_DATA, min(CARDS_PER_PACK, len(CARD_MASTER_DATA)))
            for card_data in selected_cards:
                cards.append({
                    'id': card_data['id'],
                    'name': card_data['name'],
                    'color': card_data['color'],
                    'rarity': card_data['rarity'],
                    'image': create_dummy_card_image(self.card_width, self.card_height, card_data['color'], card_data['name']),
                    'flipped': False  # 裏面から開始
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
                    # 開封完了時、獲得カードを全カードリストに追加
                    self.all_cards.extend(self.current_cards)

    def draw(self, screen):
        """描画"""
        screen.fill(BLACK)

        if not self.is_opened:
            self._draw_pack_opening(screen)
        else:
            self._draw_opened_cards(screen)

    def _draw_pack_opening(self, screen):
        """パック開封中の描画"""
        scale = min(self.screen_width / DEFAULT_SCREEN_WIDTH, self.screen_height / DEFAULT_SCREEN_HEIGHT)

        # タイトル（何パック目か）
        title_text = self.font.render(f"Pack {self.current_pack_index + 1}/{self.destroyed_packs_count}", True, WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, int(30 * scale)))
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
        guide_rect = guide_text.get_rect(center=(self.screen_width // 2, self.screen_height - int(50 * scale)))
        screen.blit(guide_text, guide_rect)

        # 進行度バー
        bar_width = int(300 * scale)
        bar_height = int(20 * scale)
        bar_x = self.screen_width // 2 - bar_width // 2
        bar_y = self.screen_height // 2 + self.pack_height // 2 + int(50 * scale)
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), max(1, int(2 * scale)))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * self.opening_progress / 100), bar_height))

    def _draw_opened_cards(self, screen):
        """開封後のカード表示"""
        # タイトル
        title_text = self.font.render("Pack Opened!", True, YELLOW)
        scale = min(self.screen_width / DEFAULT_SCREEN_WIDTH, self.screen_height / DEFAULT_SCREEN_HEIGHT)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, int(50 * scale)))
        screen.blit(title_text, title_rect)

        # カードを横並びに表示
        spacing = int(20 * scale)
        total_width = self.card_width * 5 + spacing * 4
        start_x = self.screen_width // 2 - total_width // 2
        start_y = self.screen_height // 2 - self.card_height // 2

        # カード位置を保存（クリック判定用）
        self.card_positions = []

        for i, card in enumerate(self.current_cards):
            x = start_x + i * (self.card_width + spacing)
            self.card_positions.append((x, start_y, self.card_width, self.card_height))

            # 裏面か表面かを判定して描画
            if card.get('flipped', False):
                # 表面を表示
                screen.blit(card['image'], (x, start_y))
            else:
                # 裏面を表示
                screen.blit(self.card_back_image, (x, start_y))

        # すべてのカードがめくられたかチェック
        all_flipped = self.all_cards_flipped()

        if not all_flipped:
            # まだめくっていないカードがある場合
            click_text = self.small_font.render("Click cards to flip!", True, YELLOW)
            click_rect = click_text.get_rect(center=(self.screen_width // 2, int(80 * scale)))
            screen.blit(click_text, click_rect)
        else:
            # すべてめくった場合
            if self.current_pack_index < self.destroyed_packs_count - 1:
                next_text = self.small_font.render("Press SPACE for Next Pack", True, GREEN)
            else:
                next_text = self.small_font.render("Press SPACE to Restart", True, GREEN)
            next_rect = next_text.get_rect(center=(self.screen_width // 2, self.screen_height - int(50 * scale)))
            screen.blit(next_text, next_rect)

    def handle_mouse_click(self, mouse_pos):
        """マウスクリック処理"""
        if not self.is_opened:
            return

        # カード位置が設定されていない場合は何もしない
        if not hasattr(self, 'card_positions'):
            return

        # クリックされたカードを探す
        for i, (x, y, w, h) in enumerate(self.card_positions):
            if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
                # カードをめくる
                self.current_cards[i]['flipped'] = True
                break

    def all_cards_flipped(self):
        """すべてのカードがめくられたかチェック"""
        return all(card.get('flipped', False) for card in self.current_cards)

    def next_pack(self):
        """次のパックへ"""
        if self.current_pack_index < self.destroyed_packs_count - 1:
            self.current_pack_index += 1
            self.opening_progress = 0
            self.is_opened = False
            self.current_cards = self._generate_cards()
            # 次のパック用に新しい画像を読み込む
            self.pack_image = self._load_random_pack_image()
            return True
        return False

    def is_finished(self):
        """全パックの開封が完了したか"""
        return self.is_opened and self.current_pack_index >= self.destroyed_packs_count - 1

    def draw_card_collection(self, screen):
        """獲得カード一覧を描画"""
        screen.fill(BLACK)

        scale = min(self.screen_width / DEFAULT_SCREEN_WIDTH, self.screen_height / DEFAULT_SCREEN_HEIGHT)

        # タイトル
        title_text = self.font.render("All Cards Collected!", True, YELLOW)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, int(30 * scale)))
        screen.blit(title_text, title_rect)

        # カード総数表示
        total_text = self.small_font.render(f"Total: {len(self.all_cards)} cards", True, WHITE)
        total_rect = total_text.get_rect(center=(self.screen_width // 2, int(70 * scale)))
        screen.blit(total_text, total_rect)

        if len(self.all_cards) == 0:
            return

        # 利用可能な画面領域を計算
        header_height = int(90 * scale)
        footer_height = int(50 * scale)
        available_height = self.screen_height - header_height - footer_height
        available_width = self.screen_width - int(30 * scale)

        # カード枚数から最適なサイズを計算
        card_count = len(self.all_cards)
        card_aspect_ratio = 2 / 3  # 幅 / 高さ

        # 最適なレイアウトを探索（カードサイズを最大化）
        best_card_height = 0
        best_cards_per_row = 1
        best_spacing = 10

        for test_cards_per_row in range(1, card_count + 1):
            rows = (card_count + test_cards_per_row - 1) // test_cards_per_row

            # このレイアウトでの最大カードサイズを計算
            spacing = int(10 * scale)

            # 幅から計算
            max_width_per_card = (available_width - spacing * (test_cards_per_row - 1)) / test_cards_per_row
            height_from_width = max_width_per_card / card_aspect_ratio

            # 高さから計算
            max_height_per_card = (available_height - spacing * (rows - 1)) / rows

            # 小さい方を採用
            card_height = min(height_from_width, max_height_per_card)

            if card_height > best_card_height:
                best_card_height = card_height
                best_cards_per_row = test_cards_per_row
                best_spacing = spacing

        # 最適なサイズを適用
        display_card_height = int(best_card_height)
        display_card_width = int(display_card_height * card_aspect_ratio)
        spacing = best_spacing
        cards_per_row = best_cards_per_row

        # 最小サイズの制限
        min_card_height = int(60 * scale)
        if display_card_height < min_card_height:
            display_card_height = min_card_height
            display_card_width = int(display_card_height * card_aspect_ratio)

        # グリッド描画の開始位置を計算
        total_rows = (card_count + cards_per_row - 1) // cards_per_row
        actual_row_width = cards_per_row * display_card_width + (cards_per_row - 1) * spacing
        actual_col_height = total_rows * display_card_height + (total_rows - 1) * spacing
        start_x = (self.screen_width - actual_row_width) // 2
        start_y = header_height + (available_height - actual_col_height) // 2

        for i, card in enumerate(self.all_cards):
            row = i // cards_per_row
            col = i % cards_per_row
            x = start_x + col * (display_card_width + spacing)
            y = start_y + row * (display_card_height + spacing)

            # カード画像をスケーリングして描画
            scaled_image = pygame.transform.scale(card['image'], (display_card_width, display_card_height))
            screen.blit(scaled_image, (x, y))

        # 次へ進む案内
        next_text = self.small_font.render("Press SPACE to Restart", True, WHITE)
        next_rect = next_text.get_rect(center=(self.screen_width // 2, self.screen_height - int(25 * scale)))
        screen.blit(next_text, next_rect)


class Game:
    """メインゲームクラス"""
    def __init__(self):
        self.screen_width = DEFAULT_SCREEN_WIDTH
        self.screen_height = DEFAULT_SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("PokePoke - Card Pack Sniper")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_SHOOTING

        # カード画像ファイルを読み込む
        self.card_image_files = load_card_images()

        # パック画像ファイルを読み込む
        self.pack_image_files = load_pack_images()

        # ゲーム要素の初期化
        self.crosshair = Crosshair(self.screen_width, self.screen_height)
        self.card_packs = []
        self.hit_effects = []  # GET!エフェクト
        self.ammo = INITIAL_AMMO
        self.start_time = pygame.time.get_ticks()  # ゲーム開始時刻
        self.is_cleared = False  # クリアしたかどうか
        self.clear_time = 0  # クリアタイム

        # カードパックの配置 (左右に5個ずつ)
        self._setup_card_packs()

        # パック開封シーン
        self.pack_opening = None

        # フォント（スケール対応）
        scale = min(self.screen_width / DEFAULT_SCREEN_WIDTH, self.screen_height / DEFAULT_SCREEN_HEIGHT)
        self.font = pygame.font.Font(None, int(36 * scale))
        self.big_font = pygame.font.Font(None, int(72 * scale))

    def _setup_card_packs(self):
        """カードパックをトランプの5のパターンで配置（レスポンシブ）"""
        center_y = self.screen_height // 2
        # スケール計算
        scale = min(self.screen_width / DEFAULT_SCREEN_WIDTH, self.screen_height / DEFAULT_SCREEN_HEIGHT)
        # 画面サイズに応じてオフセットを調整
        offset_x = int(120 * scale)
        offset_y = int(180 * scale)

        # 左側と右側の中心X座標
        centers_x = [self.screen_width // 4, self.screen_width * 3 // 4]

        # パック画像をランダムに選択するためのリストを作成
        selected_pack_images = []
        if self.pack_image_files:
            # 10個のパック用に画像をランダムに選択（重複許可）
            for _ in range(CARD_PACKS_COUNT):
                selected_pack_images.append(random.choice(self.pack_image_files))
        else:
            selected_pack_images = [None] * CARD_PACKS_COUNT

        pack_index = 0
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
                pack_image = selected_pack_images[pack_index] if pack_index < len(selected_pack_images) else None
                self.card_packs.append(CardPack(x, y, scale, pack_image))
                pack_index += 1

    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # ウィンドウリサイズ処理
                self.screen_width = event.w
                self.screen_height = event.h
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
                scale = min(self.screen_width / DEFAULT_SCREEN_WIDTH, self.screen_height / DEFAULT_SCREEN_HEIGHT)

                # フォントを更新
                self.font = pygame.font.Font(None, int(36 * scale))
                self.big_font = pygame.font.Font(None, int(72 * scale))

                # 照準の画面サイズを更新
                self.crosshair.update_screen_size(self.screen_width, self.screen_height)
                # カードパックの位置を再計算
                self.card_packs.clear()
                self._setup_card_packs()
                # パック開封シーンの画面サイズを更新
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
                    self.pack_opening.font = pygame.font.Font(None, int(36 * scale))
                    self.pack_opening.small_font = pygame.font.Font(None, int(24 * scale))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左クリック
                    if self.state == STATE_PACK_OPENING and self.pack_opening:
                        self.pack_opening.handle_mouse_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if self.state == STATE_SHOOTING:
                    if event.key == pygame.K_SPACE:
                        self._fire()
                elif self.state == STATE_PACK_OPENING:
                    if event.key == pygame.K_SPACE and self.pack_opening.is_opened:
                        # すべてのカードがめくられている場合のみ次へ進める
                        if self.pack_opening.all_cards_flipped():
                            # 次のパックへ、または獲得カード一覧へ
                            if not self.pack_opening.next_pack():
                                self.state = STATE_CARD_COLLECTION
                elif self.state == STATE_CARD_COLLECTION:
                    if event.key == pygame.K_SPACE:
                        self._restart()  # カード一覧から直接リスタート

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
                    pack.destroy()

                    # GET!エフェクトを生成
                    scale = min(self.screen_width / DEFAULT_SCREEN_WIDTH, self.screen_height / DEFAULT_SCREEN_HEIGHT)
                    effect_x = pack.x + pack.width // 2
                    effect_y = pack.y + pack.height // 2
                    self.hit_effects.append(HitEffect(effect_x, effect_y, scale))
                    break

    def _restart(self):
        """ゲームを再開"""
        self.card_packs.clear()
        self.hit_effects.clear()
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

            # エフェクトの更新
            for effect in self.hit_effects[:]:
                effect.update()
                if not effect.active:
                    self.hit_effects.remove(effect)

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
                self.pack_opening = PackOpening(destroyed_count, self.screen_width, self.screen_height, self.card_image_files, self.pack_image_files)
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

            # GET!エフェクトを描画
            for effect in self.hit_effects:
                effect.draw(self.screen)

            # 照準を描画
            self.crosshair.draw(self.screen)

            # UI描画
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

    def _draw_game_over(self):
        """ゲームオーバー画面を描画"""
        # 半透明の黒背景
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # タイトルテキスト（クリアか失敗か）
        if self.is_cleared:
            title_text = self.big_font.render("CLEAR!", True, GREEN)
        else:
            title_text = self.big_font.render("GAME OVER", True, RED)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(title_text, title_rect)

        # 結果
        destroyed = sum(1 for pack in self.card_packs if pack.destroyed)
        result_text = self.font.render(
            f"Packs Destroyed: {destroyed}/{CARD_PACKS_COUNT}",
            True, WHITE
        )
        result_rect = result_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        self.screen.blit(result_text, result_rect)

        # クリアタイム表示（クリアした場合のみ）
        if self.is_cleared:
            clear_time_text = self.font.render(
                f"Clear Time: {self.clear_time:.2f}s",
                True, YELLOW
            )
            clear_time_rect = clear_time_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 60))
            self.screen.blit(clear_time_text, clear_time_rect)
            restart_y = self.screen_height // 2 + 110
        else:
            restart_y = self.screen_height // 2 + 70

        # リスタート案内
        restart_text = self.font.render("Press R to Restart", True, YELLOW)
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
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
