完整回歸（v2.5.3 的 Release Gate）：commit 0d41d8e，固定在那個 commit 的乾淨 worktree，三份同時跑（scratchpad 的 run_part.py WT P 3）。
開始 13:33:32 UTC，結束 14:33:45 UTC（60 分鐘；中間同時跑了正常玩家模擬，所以比平常慢一點）。
part 0/3: 121 passed, 0 failed, 0 known-open
part 1/3: 120 passed, 0 failed, 0 known-open
part 2/3: 120 passed, 0 failed, 0 known-open
合計 361/361（比 v2.5.2 多兩個新測試：staff_every_list_has_a_name_for_every_place、stock_one_tap_restock_leaves_no_dish_of_tonight_empty）。
