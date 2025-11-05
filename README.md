# PokePoke - Card Pack Sniper Game

射的形式でカードパックを撃ち落とし、カードを獲得するゲームです。

## ゲーム仕様

- **エンジン**: Pygame
- **カードパック数**: 10個 (左右に5個ずつ)
- **初期弾数**: 10発
- **各パックのカード数**: 5枚

## 操作方法

- **照準移動**: 矢印キー
- **発射**: スペースキー

## セットアップ

### 1. python3-venvのインストール（初回のみ）
```bash
sudo apt install python3.12-venv
```

### 2. 仮想環境の作成と起動
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存関係のインストールと実行
```bash
pip install -r requirements.txt
python main.py
```

### 終了後
仮想環境から抜けるには:
```bash
deactivate
```

## 終了条件

- 弾切れ
- または全カードパック破壊
