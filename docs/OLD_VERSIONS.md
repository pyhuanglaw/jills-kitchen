# 舊版本：要查以前怎麼做的時候

每一個舊版本都在 `main` 的 git 歷史裡（2026-10-03 以前叫 `wip/lin` 的那條開發線，2026-10-04 起由 `main` 接手），不需要另外的
zip。2026-10-03 把 rc7.6 的 zip 匯入 GitHub 的那一個 commit 不在這條歷史裡，保存在 `archive/rc7.6-import-main`（d0947ea）。
要看某一版，就用那一版的 commit 開一個唯讀的 worktree：

```
git worktree add --detach ../jills-kitchen-old/v2.2.1 7dbcaff
git worktree add --detach ../jills-kitchen-old/v2.4-rc4 16f89ba
```

看完可以 `git worktree remove` 掉。不要在 worktree 裡 commit。

## 玩家 2026-10-03 給的兩個舊版

玩家說：「我給你早期的某個版本，你有時間可以專門設置一個舊版的這樣你要查什麼也比較好查」。逐檔比對過，玩家給的檔案就是
歷史裡的這兩個 commit：

| 版本 | commit | 本機 tag | 比對結果 |
|---|---|---|---|
| v2.2.1（Version 33） | `7dbcaff` | `v2.2.1` | 程式、測試、美術 200 個檔案完全一樣。`docs/V221_REPORT.md` 是之後的 `ab537c8` 版（發布後補的線上確認）；`docs/V23_BRIEF.md` 是之後補的 brief 版本。另外 37 個是測試跑出來的截圖（`tests/artifacts/`，git 不收）。單檔 `jills-kitchen-single-file.html` 也一樣。 |
| v2.4 rc4 | `16f89ba` | `v2.4-rc4` | 9 個 zip（source、saves、evidence、art 1–4、portrait cards 1–2）共 422 個檔案，跟 commit 完全一樣。 |

玩家傳檔時說「這九個檔案是2.3rc4」，但檔案名稱、店主手冊的戳記（`last: v2.4 rc4`）和 commit 都是 **v2.4 rc4**（2026-10-01 17:49）。
v2.3 的候選版是 `5350a5d`（tag `v2.3-rc1` 在原開發 session）。

`V221_REPORT.pdf` 是 `docs/V221_REPORT.md` 的 PDF 版，內容一樣。

## 其他版本怎麼找

- 每一版的發布報告（`docs/V2*_REPORT.md`、`docs/V24_RC*_REPORT.md`）開頭寫著它的 commit 或 tag。
- `git log --oneline --grep 'v2.4 rc5'` 這類搜尋找到那一版的 commit。
- 發布過的 tag（`v2.4-rc8`、`v2.4-rc8.1`、以後的版本）在本機；GitHub 上目前沒有 tag，只有 branch。
