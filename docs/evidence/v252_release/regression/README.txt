完整回歸（v2.5.2 的 Release Gate）：commit fb7b6aa，固定在那個 commit 的乾淨 worktree，三份同時跑（$S/run_part.py WT P 3）。
開始 12:21:19 UTC，結束 13:14:10 UTC（53 分鐘）。
part 0/3: 120 passed, 0 failed, 0 known-open
part 1/3: 120 passed, 0 failed, 0 known-open
part 2/3: 119 passed, 0 failed, 0 known-open
合計 359/359。背景工作最後回報的結束碼 1 來自最後一行摘要指令（tail -2 不能同時讀三個檔），三份測試自己的結束碼都是 0。
