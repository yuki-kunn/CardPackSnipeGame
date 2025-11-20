import os
import time
import requests
from playwright.sync_api import sync_playwright

def scrape_pack_images_with_playwright():
    """Playwrightを使用してカードパック画像をスクレイピング"""
    print("Playwrightでカードパック画像のダウンロードを開始します")

    # imagesフォルダを作成
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"フォルダを作成しました: {images_dir}")

    try:
        with sync_playwright() as p:
            # Chromiumを起動（ヘッドレスモード）
            print("ブラウザを起動中...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()

            # ページを読み込む
            url = "https://game8.jp/pokemon-tcg-pocket/639702"
            print(f"ページを読み込み中: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=60000)

            # ページが完全に読み込まれるまで待機
            page.wait_for_timeout(5000)

            # スクロールして遅延読み込み画像を表示させる
            print("ページをスクロールして画像を読み込み中...")
            for _ in range(10):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)

            # ページの最上部に戻る
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)

            # 全ての画像要素を取得
            print("画像要素を取得中...")
            img_elements = page.query_selector_all("img")
            print(f"合計 {len(img_elements)} 個の画像要素を見つけました")

            # パック画像のURLを抽出
            pack_image_urls = []
            seen_urls = set()

            for img in img_elements:
                try:
                    # src属性とdata-src属性を両方チェック
                    src = img.get_attribute("src")
                    data_src = img.get_attribute("data-src")

                    # 実際の画像URLを取得（data-srcを優先）
                    img_url = None
                    for url in [data_src, src]:
                        if url and "img.game8.jp" in url and "data:image" not in url:
                            img_url = url
                            break

                    if not img_url or img_url in seen_urls:
                        continue

                    # 画像のサイズを取得
                    bounding_box = img.bounding_box()
                    if bounding_box:
                        width = bounding_box.get('width', 0)
                        height = bounding_box.get('height', 0)
                        # ある程度の大きさがある画像のみ（30x30以上）
                        if width >= 30 and height >= 30:
                            seen_urls.add(img_url)
                            pack_image_urls.append(img_url)
                except Exception:
                    continue

            print(f"パック画像候補: {len(pack_image_urls)} 枚")

            # クッキーを取得
            cookies = context.cookies()

            # requestsセッションを作成
            session = requests.Session()
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', ''))

            # ヘッダーを設定
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': url,
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8'
            }

            # 画像をダウンロード
            downloaded = 0
            for i, img_url in enumerate(pack_image_urls):
                try:
                    print(f"ダウンロード中 ({i+1}/{len(pack_image_urls)}): {img_url[:80]}...")

                    # 画像を取得
                    response = session.get(img_url, headers=headers, timeout=10)
                    response.raise_for_status()

                    # ファイル名を生成
                    ext = '.png'
                    if '.jpg' in img_url.lower() or '.jpeg' in img_url.lower():
                        ext = '.jpg'
                    elif '.webp' in img_url.lower():
                        ext = '.webp'

                    # URLからIDを抽出
                    url_parts = img_url.split('/')
                    if len(url_parts) >= 2:
                        img_id = url_parts[-2]
                    else:
                        img_id = str(i+1)

                    filename = f"pack_{i+1:03d}_{img_id}{ext}"
                    filepath = os.path.join(images_dir, filename)

                    # 画像を保存
                    with open(filepath, 'wb') as f:
                        f.write(response.content)

                    downloaded += 1
                    print(f"保存完了: {filepath}")

                    # サーバーに負荷をかけないよう少し待つ
                    time.sleep(0.3)

                except Exception as e:
                    print(f"画像のダウンロードに失敗: {img_url[:50]}...")
                    print(f"エラー: {e}")

            print(f"\n完了: {downloaded} 枚のパック画像をダウンロードしました")

            # ブラウザを閉じる
            browser.close()
            return downloaded

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    scrape_pack_images_with_playwright()
