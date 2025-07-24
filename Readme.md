# keio.jpから休講情報をスクレイピングする
1. 依存関係をインストール
- pip install -r requirements.txt
2. chromedriverをインストール
- https://googlechromelabs.github.io/chrome-for-testing/
- Stable/Chromedriver、platformは環境に合わせて
- seleniumのリファレンス：　https://www.selenium.dev/ja/documentation/webdriver/troubleshooting/errors/driver_location/
3. 環境変数を設定
- KEIO_ID,KEIO_PWをそれぞれ直下の.envに