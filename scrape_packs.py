import requests
import os
import time
import re

def scrape_pack_images():
    """カードパック画像をスクレイピング"""
    print("カードパック画像のダウンロードを開始します")

    # imagesフォルダを作成
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"フォルダを作成しました: {images_dir}")

    # Sessionを使用してCookieを維持
    session = requests.Session()

    # ヘッダーを設定（Refererを追加して403エラーを回避）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }

    session.headers.update(headers)

    try:
        # URLからHTMLを取得（Cookieを取得するため）
        url = "https://game8.jp/pokemon-tcg-pocket/639702"
        print(f"HTMLを取得中: {url}")

        response = session.get(url)
        response.raise_for_status()
        html_content = response.text

        print(f"Cookies取得: {len(session.cookies)} 個")

        # 画像URLを抽出（img.game8.jpのパターン）
        pattern = r'img\.game8\.jp/\d+/[a-f0-9]+\.(png|jpg|webp)'
        matches = re.findall(pattern, html_content)

        # フルURLを構築して重複を除去
        image_urls = []
        seen = set()
        for match in re.finditer(pattern, html_content):
            img_url = 'https://' + match.group()
            if img_url not in seen:
                seen.add(img_url)
                image_urls.append(img_url)

        print(f"パック画像を {len(image_urls)} 枚見つけました")

        # 画像をダウンロード
        downloaded = 0
        for i, img_url in enumerate(image_urls):
            try:
                print(f"ダウンロード中 ({i+1}/{len(image_urls)}): {img_url}")

                # 画像リクエスト用のヘッダーを設定
                img_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
                    'Referer': 'https://game8.jp/pokemon-tcg-pocket/639702',
                    'Sec-Fetch-Dest': 'image',
                    'Sec-Fetch-Mode': 'no-cors',
                    'Sec-Fetch-Site': 'cross-site'
                }

                # 画像を取得（Sessionを使用）
                img_response = session.get(img_url, headers=img_headers, timeout=10)
                img_response.raise_for_status()

                # ファイル名を生成
                ext = '.png'
                if '.jpg' in img_url.lower():
                    ext = '.jpg'
                elif '.webp' in img_url.lower():
                    ext = '.webp'

                # URLからIDを抽出してファイル名に使用
                url_parts = img_url.split('/')
                if len(url_parts) >= 2:
                    img_id = url_parts[-2]
                else:
                    img_id = str(i+1)

                filename = f"pack_{i+1:03d}_{img_id}{ext}"
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

        print(f"\n完了: {downloaded} 枚のパック画像をダウンロードしました")
        return downloaded

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    scrape_pack_images()
