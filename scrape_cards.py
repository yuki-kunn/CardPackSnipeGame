import requests
import os
import time
import json

def scrape_card_images_from_json():
    """JSONファイルからカード画像をダウンロード"""
    print("カード画像のダウンロードを開始します")

    # imagesフォルダを作成
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"フォルダを作成しました: {images_dir}")

    # ヘッダーを設定（ブラウザのように振る舞う）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # JSONファイルを取得
        json_url = "https://assets.game8.jp/tools/script_template/pokemon_card.json"
        print(f"JSONデータを取得中: {json_url}")

        response = requests.get(json_url, headers=headers)
        response.raise_for_status()

        # JSONをパース
        categories = response.json()
        print(f"カテゴリデータを取得しました: {len(categories)} 件")

        # 画像URLを抽出（ネストされた構造を処理）
        # レアカード（exカード）のみをフィルタリング
        image_urls = []
        total_cards = 0
        for category in categories:
            if 'db_data' in category:
                for card in category['db_data']:
                    total_cards += 1
                    # col_19に"ex"が含まれるカードのみ（レアカード）
                    col_19 = card.get('col_19', '') or ''
                    col_19 = col_19.strip() if col_19 else ''
                    if col_19 and 'ex' in col_19.lower():
                        if 'image_url' in card and card['image_url']:
                            # /show を /original に置き換えて高解像度版を取得
                            img_url = card['image_url'].replace('/show', '/original')

                            # HTTPSに統一
                            if img_url.startswith('//'):
                                img_url = 'https:' + img_url
                            elif not img_url.startswith('http'):
                                img_url = 'https://' + img_url

                            image_urls.append({
                                'url': img_url,
                                'name': card.get('title', 'Unknown'),
                                'id': card.get('id', 'unknown'),
                                'rarity': col_19
                            })

        print(f"全カード数: {total_cards} 件")

        print(f"カード画像を {len(image_urls)} 枚見つけました")

        # 画像をダウンロード
        downloaded = 0
        for i, card_info in enumerate(image_urls):
            try:
                img_url = card_info['url']
                card_name = card_info['name']
                print(f"ダウンロード中 ({i+1}/{len(image_urls)}): {card_name}")

                # 画像を取得
                img_response = requests.get(img_url, headers=headers, timeout=10)
                img_response.raise_for_status()

                # ファイル名を生成（レアカードのみ）
                card_id = card_info['id']
                rarity = card_info.get('rarity', 'rare')

                # 拡張子を判定
                ext = '.jpg'
                if '.png' in img_url.lower():
                    ext = '.png'
                elif '.webp' in img_url.lower():
                    ext = '.webp'

                filename = f"rare_card_{i+1:03d}_{card_id}{ext}"
                filepath = os.path.join(images_dir, filename)

                # 画像を保存
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)

                downloaded += 1
                print(f"保存完了: {filepath}")

                # サーバーに負荷をかけないよう少し待つ
                time.sleep(0.3)

            except Exception as e:
                print(f"画像のダウンロードに失敗: {img_url}")
                print(f"エラー: {e}")

        print(f"\n完了: {downloaded} 枚の画像をダウンロードしました")
        return downloaded

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    scrape_card_images_from_json()
