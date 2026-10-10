Jill 摸貓（使用者 2026-10-10 §3）。同一個量法（docs/evidence/v24_rc8_5/sims/jill_pats.py）：新遊戲第 1 天、Jill 一個人顧店、
懶玩家（tests/run_tests.py LAZY_ACTOR），種子 1–20，數她開始摸貓的次數。

  jill_pats_main_fc0f5d8.txt          料理系統以前的 main：16 天有摸、29 次（使用者說的參考值）
  jill_pats_8298e18.txt               料理系統（第二輪之前）：10 天、13 次
  jill_pats_day1_d12a638.txt          第二輪前兩個機會（閒 0.8 秒、走回出菜口途中）：14 天、18 次
  jill_pats_day1_round2_final.txt     第二輪最後（加上「工作短暫空檔走過去摸」）：18 天、29 次
  where_she_meets_cats_day1_c50184d.txt / where_she_meets_cats.py
                                      第二輪前兩個機會時，休息中的貓在她 40 點內的時候她正在做什麼（種子 1–4）：
                                      多半是走去桌邊做事（walk_other）或去廚房（walk_kitchen）——那是工作，不停下來摸。

每晚的摸貓次數（前、中、後期）在 ../balance/ 的 evening_*.jsonl（cats.pats、cats.sofa_pets）。
