import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_pack_images_with_selenium():
    """Seleniumを使用してカードパック画像をスクレイピング"""
    print("Seleniumでカードパック画像のダウンロードを開始します")

    # imagesフォルダを作成
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
        print(f"フォルダを作成しました: {images_dir}")

    # Chrome オプションを設定
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # ヘッドレスモード
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        # WebDriverを初期化
        print("ChromeDriverを初期化中...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # ページを読み込む
        url = "https://game8.jp/pokemon-tcg-pocket/639702"
        print(f"ページを読み込み中: {url}")
        driver.get(url)

        # ページが完全に読み込まれるまで待機
        time.sleep(5)

        # スクロールして遅延読み込み画像を表示させる
        print("ページをスクロールして画像を読み込み中...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        max_scrolls = 10

        while scroll_count < max_scrolls:
            # ページの最下部までスクロール
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # 画像が読み込まれるまで待機

            # 新しい高さを取得
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_count += 1

        # ページの最上部に戻る
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        # 全ての画像要素を取得
        print("画像要素を取得中...")
        img_elements = driver.find_elements(By.TAG_NAME, "img")
        print(f"合計 {len(img_elements)} 個の画像要素を見つけました")

        # パック画像のURLを抽出
        pack_image_urls = []
        seen_urls = set()

        for img in img_elements:
            try:
                # src属性を取得
                src = img.get_attribute("src")
                if not src:
                    continue

                # img.game8.jpのURLをフィルタリング
                if "img.game8.jp" in src and src not in seen_urls:
                    # 小さすぎる画像は除外（アイコンなど）
                    width = img.get_attribute("width")
                    height = img.get_attribute("height")

                    # naturalWidthとnaturalHeightを取得
                    natural_width = driver.execute_script("return arguments[0].naturalWidth", img)
                    natural_height = driver.execute_script("return arguments[0].naturalHeight", img)

                    # ある程度の大きさがある画像のみ
                    if natural_width and natural_height:
                        if natural_width >= 50 and natural_height >= 50:
                            seen_urls.add(src)
                            pack_image_urls.append(src)

            except Exception as e:
                continue

        print(f"パック画像候補: {len(pack_image_urls)} 枚")

        # クッキーを取得してrequestsセッションに設定
        cookies = driver.get_cookies()
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

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

        # ドライバを閉じる
        driver.quit()
        return downloaded

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    scrape_pack_images_with_selenium()
