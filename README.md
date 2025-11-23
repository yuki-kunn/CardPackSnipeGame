# カードパックをうちおとせ！

カードパックを狙い撃ちして、ゲットしたパックを開封するシューティングゲームです。
小学生でも遊べるように、ひらがな表示に対応しています。

## 遊び方

1. **スタート画面**でスペースキーを押してゲーム開始
2. **矢印キー**で照準を動かす
3. **スペースキー**で弾を発射
4. 動いているパックに当てるとゲット！
5. ゲットしたパックを開封してカードをもらおう

### ルール
- 弾数: 10発
- 制限時間: 45秒
- パック数: 10個

## 必要な環境

- Python 3.x
- Pygame

```bash
pip install pygame
```

## ファイル構成

```
CardPackSnipeGame/
├── main.py          # ゲーム起動ファイル
├── game.py          # メインゲームロジック
├── constants.py     # 定数定義
├── utils.py         # ユーティリティ関数
├── crosshair.py     # 照準クラス
├── hit_effect.py    # エフェクトクラス
├── card_pack.py     # カードパッククラス
├── pack_opening.py  # パック開封クラス
├── fonts/           # フォントファイル
│   └── NotoSansCJKjp-Regular.otf
├── images/          # カード画像
│   ├── rare_card_*.png/jpg/webp
│   └── card_ura.jpg (カード裏面)
└── pack_images/     # パック画像
    └── *.png/jpg/webp
```

## セットアップ

### 1. 仮想環境の作成（推奨）

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. フォントのダウンロード

日本語表示に必要なフォントをダウンロードしてください：

```bash
mkdir -p fonts
cd fonts
wget https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf
```

または、以下のリンクから直接ダウンロード：
- [NotoSansCJKjp-Regular.otf](https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf)

### 3. 画像ファイルの配置

#### カード画像（images/）
- ファイル名: `rare_card_*.png`、`rare_card_*.jpg`、`rare_card_*.webp`
- カード裏面: `card_ura.jpg`
- 画像がない場合はダミー表示で動作します

#### パック画像（pack_images/）
- ファイル名: `*.png`、`*.jpg`、`*.webp`
- 画像がない場合はダミー表示で動作します

## 実行方法

```bash
python main.py
```

## 操作方法

| キー | 動作 |
|------|------|
| 矢印キー | 照準を移動 |
| スペース | 弾を発射 / 決定 |
| クリック | カードをめくる |

## 終了条件

- 弾切れ
- 制限時間切れ
- または全カードパック破壊（クリア）

## ライセンス

このゲームは個人利用を目的としています。
