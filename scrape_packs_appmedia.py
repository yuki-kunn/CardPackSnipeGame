import os
import time
import requests
from playwright.sync_api import sync_playwright

def scrape_pack_images_from_appmedia():
    """appmedia.jpからカードパック画像をスクレイピング"""
    print("appmedia.jpからカードパック画像のダウンロードを開始します")

    # pack_imagesフォルダを作成
    images_dir = "pack_images"
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
            url = "https://appmedia.jp/pokepocke/78759029"
            print(f"ページを読み込み中: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=60000)

            # ページが完全に読み込まれるまで待機
            page.wait_for_timeout(5000)

            # スクロールして遅延読み込み画像を表示させる
            print("ページをスクロールして画像を読み込み中...")
            for _ in range(20):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(800)

            # ページの最上部に戻る
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)

            # 「パック一覧とおすすめポイント」セクションを探す
            print("「パック一覧とおすすめポイント」セクションを探しています...")

            # パック画像のURLを抽出
            pack_image_urls = []
            seen_urls = set()

            # JavaScriptでセクション内の画像のみを抽出
            pack_images_data = page.evaluate('''() => {
                const results = [];

                // 「パック一覧」を含むヘッダーを探す
                const headings = document.querySelectorAll('h2, h3, h4');
                let targetSection = null;
                let targetIndex = -1;

                for (let i = 0; i < headings.length; i++) {
                    const text = headings[i].innerText || headings[i].textContent;
                    if (text.includes('パック一覧')) {
                        targetSection = headings[i];
                        targetIndex = i;
                        break;
                    }
                }

                if (!targetSection) {
                    return { found: false, images: [] };
                }

                // セクションの位置を取得
                const sectionTop = targetSection.getBoundingClientRect().top + window.scrollY;

                // 次のh2を探す
                let sectionBottom = document.body.scrollHeight;
                for (let i = targetIndex + 1; i < headings.length; i++) {
                    if (headings[i].tagName === 'H2') {
                        sectionBottom = headings[i].getBoundingClientRect().top + window.scrollY;
                        break;
                    }
                }

                // 全ての画像をチェック
                const allImages = document.querySelectorAll('img');

                for (const img of allImages) {
                    const rect = img.getBoundingClientRect();
                    const imgTop = rect.top + window.scrollY;

                    // セクション内にある画像のみ
                    if (imgTop >= sectionTop && imgTop < sectionBottom) {
                        let imgUrl = img.getAttribute('data-src') || img.getAttribute('src');
                        const alt = img.getAttribute('alt') || '';

                        if (!imgUrl || imgUrl.includes('data:image')) continue;

                        // 相対URLを絶対URLに変換
                        if (imgUrl.startsWith('/')) {
                            imgUrl = 'https://appmedia.jp' + imgUrl;
                        }

                        // パック画像の条件:
                        // 1. alt属性に「ポケポケ_」が含まれている
                        // 2. または wp-content/uploads のURLで縦長の画像

                        const isPackImage = alt.includes('ポケポケ_');

                        if (!isPackImage) continue;

                        // 外部CDN（mzstatic.com等）は除外
                        if (imgUrl.includes('mzstatic.com')) continue;

                        // 画像サイズをチェック
                        const width = rect.width;
                        const height = rect.height;

                        // 縦長の画像のみ（パック画像の特徴）
                        if (height <= width) continue;

                        // 極端に小さい画像を除外
                        if (width < 30 || height < 50) continue;

                        results.push({
                            url: imgUrl,
                            alt: alt,
                            width: width,
                            height: height
                        });
                    }
                }

                return { found: true, images: results };
            }''')

            if not pack_images_data['found']:
                print("「パック一覧とおすすめポイント」セクションが見つかりませんでした")
                browser.close()
                return 0

            print(f"セクション内で {len(pack_images_data['images'])} 枚の画像候補を発見")

            # 重複を除去
            for img_info in pack_images_data['images']:
                img_url = img_info['url']
                if img_url not in seen_urls:
                    seen_urls.add(img_url)
                    pack_image_urls.append(img_info)

            print(f"重複除去後: {len(pack_image_urls)} 枚")

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
            for i, img_info in enumerate(pack_image_urls):
                try:
                    img_url = img_info['url']
                    alt = img_info['alt']

                    print(f"ダウンロード中 ({i+1}/{len(pack_image_urls)}): {alt or img_url[-50:]}...")

                    # 画像を取得
                    response = session.get(img_url, headers=headers, timeout=15)
                    response.raise_for_status()

                    # Content-Typeをチェック
                    content_type = response.headers.get('Content-Type', '')
                    if 'image' not in content_type and len(response.content) < 1000:
                        print(f"スキップ (画像ではない): {img_url[-50:]}")
                        continue

                    # ファイル名を生成
                    ext = '.png'
                    if '.jpg' in img_url.lower() or '.jpeg' in img_url.lower():
                        ext = '.jpg'
                    elif '.webp' in img_url.lower():
                        ext = '.webp'
                    elif 'image/jpeg' in content_type:
                        ext = '.jpg'
                    elif 'image/webp' in content_type:
                        ext = '.webp'

                    # ファイル名を生成（alt属性から安全な文字のみ抽出）
                    safe_alt = "".join(c for c in alt if c.isalnum() or c in ('_', '-', 'パ', 'ッ', 'ク'))[:40] if alt else ""
                    filename = f"pack_{i+1:03d}_{safe_alt}{ext}" if safe_alt else f"pack_{i+1:03d}{ext}"
                    filepath = os.path.join(images_dir, filename)

                    # 画像を保存
                    with open(filepath, 'wb') as f:
                        f.write(response.content)

                    downloaded += 1
                    print(f"保存完了: {filename}")

                    # サーバーに負荷をかけないよう少し待つ
                    time.sleep(0.3)

                except Exception as e:
                    print(f"画像のダウンロードに失敗: {img_url[-50:]}...")
                    print(f"エラー: {e}")

            print(f"\n完了: {downloaded} 枚のパック画像をダウンロードしました")
            print(f"保存先: {os.path.abspath(images_dir)}")

            # ブラウザを閉じる
            browser.close()
            return downloaded

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    scrape_pack_images_from_appmedia()
