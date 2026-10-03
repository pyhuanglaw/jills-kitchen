# 部署成 iPhone 主畫面 App（PWA）

專案已經是可安裝的 PWA：`manifest.webmanifest`、`icons/`、`sw.js`（離線快取 app shell）、iOS 的 `apple-mobile-web-app-*` meta、`viewport-fit=cover` 與 safe-area 內距都在 `index.html` 裡。存檔仍在瀏覽器的 localStorage／IndexedDB，備份／恢復照舊。

**剩下唯一的外部步驟：把整個資料夾放到任何 HTTPS 靜態主機。** 例如 GitHub Pages：

1. 把 `index.html`、`css/`、`js/`、`icons/`、`manifest.webmanifest`、`sw.js` 推到一個 repo，開啟 Pages。
2. 在 iPhone 的 Safari 打開網址 → 分享 → 「加入主畫面」。
3. 之後從主畫面開啟：全螢幕、沒有 Safari 的網址列，離線也能開（第一次開過之後）。

注意：
- Service worker 只在 http(s) 且不是單檔版時註冊；`jills-kitchen-single-file.html`（artifact 用）不會註冊。
- 換版本時把 `sw.js` 裡的 `CACHE` 名稱改掉，舊快取會在下次開啟時清掉。
- 這個環境沒有 iPhone，「加入主畫面」與離線啟動沒有實機驗證；manifest／SW 只在 Chromium 驗過可安裝性檢查（見 V18_1_CHANGES.md）。
