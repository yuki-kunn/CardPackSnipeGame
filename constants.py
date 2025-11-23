# 定数定義

# 画面設定
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
STATE_START = "start"
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
