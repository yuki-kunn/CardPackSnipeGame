import pygame
import random
import os
from constants import (
    DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT,
    BLACK, WHITE, BLUE, GREEN, YELLOW,
    CARDS_PER_PACK, CARD_MASTER_DATA
)
from utils import (
    get_japanese_font, create_dummy_pack_image,
    load_and_scale_card_image, create_dummy_card_image
)


class PackOpening:
    """パック開封シーンクラス"""
    def __init__(self, destroyed_packs_count, screen_width, screen_height, card_image_files, pack_image_files=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.destroyed_packs_count = destroyed_packs_count
        self.current_pack_index = 0
        self.opening_progress = 0
        self.is_opened = False
        self.card_image_files = card_image_files
        self.pack_image_files = pack_image_files or []

        # スケール計算
        scale = min(screen_width / DEFAULT_SCREEN_WIDTH, screen_height / DEFAULT_SCREEN_HEIGHT)
        self.pack_width = int(200 * scale)
        self.pack_height = int(280 * scale)
        self.pack_x = screen_width // 2 - self.pack_width // 2
        self.pack_y = screen_height // 2 - self.pack_height // 2

        # パック画像
        self.pack_image = self._load_random_pack_image()

        # カードサイズ
        self.card_height = int(self.screen_height * 0.35)
        self.card_width = int(self.card_height * 2 / 3)

        # カード裏面画像
        self.card_back_image = self._load_card_back_image()

        self.current_cards = self._generate_cards()
        self.all_cards = []

        # フォント
        self.font = get_japanese_font(int(28 * scale))
        self.small_font = get_japanese_font(int(18 * scale))

    def _load_card_back_image(self):
        """カード裏面画像を読み込む"""
        try:
            back_image_path = os.path.join("images", "card_ura.jpg")
            if os.path.exists(back_image_path):
                img = pygame.image.load(back_image_path)
                return pygame.transform.scale(img, (self.card_width, self.card_height))
        except Exception as e:
            print(f"カード裏面画像読み込みエラー: {e}")

        # フォールバック
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
        return create_dummy_pack_image(self.pack_width, self.pack_height)

    def _generate_cards(self):
        """ランダムにカードを生成"""
        cards = []

        if self.card_image_files and len(self.card_image_files) >= CARDS_PER_PACK:
            selected_images = random.sample(self.card_image_files, CARDS_PER_PACK)

            for i, image_path in enumerate(selected_images):
                card_image = load_and_scale_card_image(image_path, self.card_width, self.card_height)
                cards.append({
                    'id': i + 1,
                    'name': os.path.basename(image_path),
                    'image': card_image,
                    'image_path': image_path,
                    'flipped': False
                })
        else:
            selected_cards = random.sample(CARD_MASTER_DATA, min(CARDS_PER_PACK, len(CARD_MASTER_DATA)))
            for card_data in selected_cards:
                cards.append({
                    'id': card_data['id'],
                    'name': card_data['name'],
                    'color': card_data['color'],
                    'rarity': card_data['rarity'],
                    'image': create_dummy_card_image(self.card_width, self.card_height, card_data['color'], card_data['name']),
                    'flipped': False
                })

        return cards

    def handle_input(self, keys):
        """キー入力処理"""
        if not self.is_opened:
            if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.opening_progress += 2
                if self.opening_progress >= 100:
                    self.opening_progress = 100
                    self.is_opened = True
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

        # タイトル
        title_text = self.font.render(f"Pack {self.current_pack_index + 1}/{self.destroyed_packs_count}", True, WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, int(30 * scale)))
        screen.blit(title_text, title_rect)

        # パック描画
        cut_height = int(self.pack_height * 0.3 * (self.opening_progress / 100))

        pack_body_start_y = cut_height
        pack_body_height = self.pack_height - cut_height
        if pack_body_height > 0:
            pack_body_area = pygame.Rect(0, pack_body_start_y, self.pack_width, pack_body_height)
            pack_body_surface = self.pack_image.subsurface(pack_body_area)
            screen.blit(pack_body_surface, (self.pack_x, self.pack_y + cut_height))

        if self.opening_progress < 100:
            top_height = int(self.pack_height * 0.3 * (1 - self.opening_progress / 100))
            if top_height > 0:
                top_area = pygame.Rect(0, 0, self.pack_width, top_height)
                top_surface = self.pack_image.subsurface(top_area)
                top_y = self.pack_y - (int(self.pack_height * 0.3) - top_height)
                screen.blit(top_surface, (self.pack_x, top_y))

        # 操作案内
        guide_text = self.small_font.render("やじるしキーでひらこう！", True, WHITE)
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
        title_text = self.font.render("パックがあいたよ！", True, YELLOW)
        scale = min(self.screen_width / DEFAULT_SCREEN_WIDTH, self.screen_height / DEFAULT_SCREEN_HEIGHT)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, int(50 * scale)))
        screen.blit(title_text, title_rect)

        # カードを横並びに表示
        spacing = int(20 * scale)
        total_width = self.card_width * 5 + spacing * 4
        start_x = self.screen_width // 2 - total_width // 2
        start_y = self.screen_height // 2 - self.card_height // 2

        self.card_positions = []

        for i, card in enumerate(self.current_cards):
            x = start_x + i * (self.card_width + spacing)
            self.card_positions.append((x, start_y, self.card_width, self.card_height))

            if card.get('flipped', False):
                screen.blit(card['image'], (x, start_y))
            else:
                screen.blit(self.card_back_image, (x, start_y))

        all_flipped = self.all_cards_flipped()

        if not all_flipped:
            click_text = self.small_font.render("カードをクリックしてめくろう！", True, YELLOW)
            click_rect = click_text.get_rect(center=(self.screen_width // 2, int(80 * scale)))
            screen.blit(click_text, click_rect)
        else:
            if self.current_pack_index < self.destroyed_packs_count - 1:
                next_text = self.small_font.render("スペースキーでつぎのパック", True, GREEN)
            else:
                next_text = self.small_font.render("スペースキーでけっかをみる", True, GREEN)
            next_rect = next_text.get_rect(center=(self.screen_width // 2, self.screen_height - int(50 * scale)))
            screen.blit(next_text, next_rect)

    def handle_mouse_click(self, mouse_pos):
        """マウスクリック処理"""
        if not self.is_opened:
            return

        if not hasattr(self, 'card_positions'):
            return

        for i, (x, y, w, h) in enumerate(self.card_positions):
            if x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h:
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
        title_text = self.font.render("ゲットしたカード！", True, YELLOW)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, int(30 * scale)))
        screen.blit(title_text, title_rect)

        # カード総数
        total_text = self.small_font.render(f"ぜんぶで {len(self.all_cards)}まい", True, WHITE)
        total_rect = total_text.get_rect(center=(self.screen_width // 2, int(70 * scale)))
        screen.blit(total_text, total_rect)

        if len(self.all_cards) == 0:
            return

        # レイアウト計算
        header_height = int(90 * scale)
        footer_height = int(50 * scale)
        available_height = self.screen_height - header_height - footer_height
        available_width = self.screen_width - int(30 * scale)

        card_count = len(self.all_cards)
        card_aspect_ratio = 2 / 3

        best_card_height = 0
        best_cards_per_row = 1
        best_spacing = 10

        for test_cards_per_row in range(1, card_count + 1):
            rows = (card_count + test_cards_per_row - 1) // test_cards_per_row
            spacing = int(10 * scale)

            max_width_per_card = (available_width - spacing * (test_cards_per_row - 1)) / test_cards_per_row
            height_from_width = max_width_per_card / card_aspect_ratio
            max_height_per_card = (available_height - spacing * (rows - 1)) / rows
            card_height = min(height_from_width, max_height_per_card)

            if card_height > best_card_height:
                best_card_height = card_height
                best_cards_per_row = test_cards_per_row
                best_spacing = spacing

        display_card_height = int(best_card_height)
        display_card_width = int(display_card_height * card_aspect_ratio)
        spacing = best_spacing
        cards_per_row = best_cards_per_row

        min_card_height = int(60 * scale)
        if display_card_height < min_card_height:
            display_card_height = min_card_height
            display_card_width = int(display_card_height * card_aspect_ratio)

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

            scaled_image = pygame.transform.scale(card['image'], (display_card_width, display_card_height))
            screen.blit(scaled_image, (x, y))

        # 案内
        next_text = self.small_font.render("スペースキーでスタートにもどる", True, WHITE)
        next_rect = next_text.get_rect(center=(self.screen_width // 2, self.screen_height - int(25 * scale)))
        screen.blit(next_text, next_rect)
