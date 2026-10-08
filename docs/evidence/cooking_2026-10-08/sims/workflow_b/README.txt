Workflow B: the dirty dishes' numbers (2026-10-08 afternoon to evening). docs/cooking/WORKFLOW_B.md §9 reads these.
Each line of var*.jsonl is one evening (tools/sims/workflow_b_variant.py); the tables are tools/sims/workflow_b_table.py.
Builds: nodd = b8d0256 (no dirty dishes); cap10 = 2077498 (the private page's Version 7); the rest = the dish flow being tuned
(d52_cand/d30_cand: the machine's 20 and faster washing plus the nearest-table and no-room tries; final = d4bbb4b).
Variants patch the game after each day starts: capN = DD_CAP[0]=N; dw = washing in half the time; dw3 = a third;
idle = a cleaner washes whenever idle; nores = what is on its way does not hold room; waitclean/wclean = every waiter on 收桌;
hire = one more LV3 cleaner; machine = S.ops.dish=1; noNear/noBlk/noWb = the candidate without one of its changes.
Note: idlewash and cap20idle (the first round) patched window.ddWashNow, which the game never reads (its functions live in its
own scope): they are cap10 and cap20 again, line for line. The working version of that try is 'idle' (the second round).

== Day 52 save (tests/saves/player_day52.json: 21 tables, 4 LV5 waiters, 2 LV5 cleaners, the 商用洗碗機), seeds 7200 and 7000, three evenings each
variant           n guests  lost  revenue dirtyT blockT fullS washed wash@ | cleaner idle/clear/wash | waiter idle/serve/clear/wash
nodd              6   93.0  34.7    69342   0.40      0     0    0.0   0.0 |   0%   0%   0% |   0%   0%   0%   0%
cap20             6   84.5  41.7    60917   3.56    192     0  119.5   8.9 |  28%  36%  34% |  36%  31%   8%   0%
cap10             6   76.3  47.5    55640   5.48    821     4  106.7   7.7 |  29%  39%  30% |  37%  28%  12%   1%
waitclean         6   74.7  45.7    55196   5.01    949     4  110.8   7.5 |  30%  36%  31% |  28%  28%  20%   0%
cap30             6   86.8  38.5    62768   3.03    116     0  122.0   8.2 |  29%  36%  34% |  35%  32%   8%   0%
cap15             6   80.8  44.5    58995   4.25    356     0  120.5   8.7 |  28%  36%  34% |  36%  30%  10%   0%
cap20idle         6   84.5  41.7    60917   3.56    192     0  119.5   8.9 |  28%  36%  34% |  36%  31%   8%   0%
idlewash          6   76.3  47.5    55640   5.48    821     4  106.7   7.7 |  29%  39%  30% |  37%  28%  12%   1%
dw                6   80.5  44.5    57952   4.31    737     3  121.3   7.5 |  34%  47%  16% |  37%  30%   9%   0%
dw_idle_cap20     6   87.7  34.7    62667   2.23     39     0  156.0   6.5 |  32%  45%  20% |  34%  33%   7%   1%
idle              6   77.5  47.8    56372   5.34    802     4  113.3   5.8 |  25%  41%  31% |  37%  29%  10%   1%
dw_cap20          6   87.0  39.0    64434   2.17     45     0  151.7   9.4 |  34%  45%  19% |  36%  32%   7%   1%
nores             6   80.2  44.7    57826   4.66    477    24  115.2   8.0 |  29%  36%  32% |  37%  28%  13%   0%
dw_idle           6   83.8  39.3    63965   4.20    754     2  128.5   5.7 |  32%  48%  17% |  38%  31%   8%   0%
dw3               6   81.7  41.2    61010   4.27    817     2  127.2   7.6 |  35%  49%  13% |  38%  31%   8%   0%
dw3_idle_cap15    6   85.7  40.8    63269   2.54    138     0  145.7   6.4 |  35%  46%  15% |  35%  33%   7%   1%
d52_cand          6   85.8  39.2    62274   2.06     74     0  148.2   9.2 |  32%  42%  23% |  34%  32%   8%   2%
d52_nomachine     6   71.0  54.7    53036   6.05   1150     7  103.0   7.3 |  25%  46%  27% |  36%  29%  12%   1%
d52_fast          6   86.5  38.2    64290   2.15     53     0  156.3   9.1 |  34%  45%  17% |  34%  33%   8%   1%
d52_noWb          6   85.2  37.0    61570   2.49     50     1  141.3   8.8 |  33%  41%  24% |  35%  32%   7%   1%
d52_noNear        6   87.0  41.5    62670   2.46     96     2  147.3   8.4 |  32%  40%  24% |  34%  32%   9%   1%

== Day 30 save (tests/saves/player_day30.json: 12 tables, 4 waiters, 1 LV5 cleaner, no machine), seeds 3033 and 4044, three evenings each
variant           n guests  lost  revenue dirtyT blockT fullS washed wash@ | cleaner idle/clear/wash | waiter idle/serve/clear/wash
idle              6   58.8  31.2    35501   5.15    735    14   81.7   8.1 |  21%  39%  38% |  38%  22%  19%   4%
nodd              6   82.3  12.8    47812   0.41      0     0    0.0   0.0 |   0%   0%   0% |   0%   0%   0%   0%
cap10             6   59.7  30.3    34971   5.30    785    14   85.7   8.6 |  22%  34%  42% |  39%  22%  19%   3%
idle_cap15        6   69.7  23.2    40432   3.99    161     2  100.2   9.1 |  18%  27%  53% |  35%  24%  19%   2%
idle_cap20        6   68.5  21.7    40428   3.55     45     2  103.3   9.8 |  17%  26%  55% |  34%  24%  20%   2%
dw_idle_cap20     6   71.8  18.0    41629   2.68     39     2  117.0   9.4 |  22%  48%  27% |  35%  27%  15%   2%
d30_cand          6   54.3  34.8    32738   5.39    926    17   78.2   8.7 |  21%  39%  38% |  39%  23%  18%   3%
d30_fast          6   58.0  30.3    34303   4.99    835    19   82.7   8.7 |  23%  47%  27% |  38%  25%  16%   3%
d30_machine       6   69.0  20.7    39862   2.69     39     1  107.3  10.7 |  21%  41%  35% |  33%  26%  18%   3%
d30_hire          6   62.0  29.8    38711   4.57    782     4   96.5   7.2 |  23%  45%  31% |  39%  26%  16%   1%
d30_hire_machine  6   78.5  12.0    46708   1.32     17     0  133.3   9.0 |  30%  43%  25% |  37%  30%  11%   1%
d30_wclean        6   60.3  31.7    36234   4.84    983    18   92.0   8.3 |  23%  33%  42% |  29%  23%  25%   4%
d30_wwash         6   56.2  32.2    32539   5.45    906    20   77.8   6.7 |  23%  42%  33% |  33%  23%  18%   7%
d30_hire_cur      6   65.3  25.8    38422   4.54    717     3   99.2   7.3 |  24%  41%  34% |  40%  24%  18%   0%
d30_machine_wwash  6   69.0  20.7    39862   2.69     39     1  107.3  10.7 |  21%  41%  35% |  33%  26%  18%   3%
d30_noBlk         6   54.2  35.0    32669   5.43    938    18   77.8   8.8 |  21%  39%  38% |  39%  23%  18%   3%
d30_noNear        6   59.2  29.5    34041   5.29    825    16   83.7   8.4 |  23%  34%  41% |  37%  22%  20%   3%
d30_noWb          6   54.8  35.5    32045   5.65    958    17   73.2   8.7 |  22%  43%  34% |  40%  23%  16%   4%
d30_cap20         6   66.7  24.2    40857   3.74    135     3  103.8  11.8 |  18%  27%  53% |  33%  26%  20%   2%
final             6   60.5  31.0    34853   5.30    798    15   86.5   8.5 |  22%  35%  41% |  37%  22%  20%   3%
final_machine     6   71.3  20.3    42621   2.44     32     1  118.2  10.7 |  21%  41%  37% |  34%  26%  17%   3%
final_hire        6   66.2  25.3    39642   4.17    661     3   99.0   7.3 |  24%  41%  34% |  40%  25%  16%   0%
final_hire_machine  6   77.8  14.5    46814   1.63     40     0  134.0   9.1 |  31%  40%  27% |  37%  29%  12%   0%

== Stress tests A-D (tools/sims/workflow_b_stress.py): simb_old_* = b8d0256, simb_dev_* = the final dish flow (same code as d4bbb4b)
-- old_AB
perfect 1 {'guests': 14, 'lost': 0, 'rev': 1680} {'avg': 0, 'peak': 0, 'fulls': 0, 'full': 0, 'block': 0, 'in': 0, 'wash': 0, 'by': {}, 'washT': {}, 'starts': 0, 'startAvg': 0}
perfect 2 {'guests': 19, 'lost': 0, 'rev': 3180} {'avg': 0, 'peak': 0, 'fulls': 0, 'full': 0, 'block': 0, 'in': 0, 'wash': 0, 'by': {}, 'washT': {}, 'starts': 0, 'startAvg': 0}
perfect 3 {'guests': 4, 'lost': 0, 'rev': 420} {'avg': 0, 'peak': 0, 'fulls': 0, 'full': 0, 'block': 0, 'in': 0, 'wash': 0, 'by': {}, 'washT': {}, 'starts': 0, 'startAvg': 0}
lazy 1 {'guests': 14, 'lost': 0, 'rev': 1680} {'avg': 0, 'peak': 0, 'fulls': 0, 'full': 0, 'block': 0, 'in': 0, 'wash': 0, 'by': {}, 'washT': {}, 'starts': 0, 'startAvg': 0}
lazy 2 {'guests': 19, 'lost': 0, 'rev': 3180} {'avg': 0, 'peak': 0, 'fulls': 0, 'full': 0, 'block': 0, 'in': 0, 'wash': 0, 'by': {}, 'washT': {}, 'starts': 0, 'startAvg': 0}
lazy 3 {'guests': 4, 'lost': 0, 'rev': 420} {'avg': 0, 'peak': 0, 'fulls': 0, 'full': 0, 'block': 0, 'in': 0, 'wash': 0, 'by': {}, 'washT': {}, 'starts': 0, 'startAvg': 0}
-- dev_AB
perfect 1 {'guests': 15, 'lost': 0, 'rev': 1800} {'avg': 3.02, 'peak': 7, 'fulls': 0, 'full': 0, 'block': 0, 'in': 15, 'wash': 12, 'by': {'xq': 12}, 'washT': {'xq': 24.00000000000035}, 'starts': 3, 'startAvg': 6.3}
perfect 2 {'guests': 17, 'lost': 0, 'rev': 2640} {'avg': 5.25, 'peak': 10, 'fulls': 2, 'full': 8.8, 'block': 26, 'in': 22, 'wash': 14, 'by': {'jill': 14}, 'washT': {'jill': 25.6666666666671}, 'starts': 5, 'startAvg': 8.4}
perfect 3 {'guests': 7, 'lost': 0, 'rev': 1080} {'avg': 2.13, 'peak': 8, 'fulls': 0, 'full': 0, 'block': 0, 'in': 10, 'wash': 10, 'by': {'jill': 10}, 'washT': {'jill': 18.333333333333403}, 'starts': 2, 'startAvg': 8}
lazy 1 {'guests': 13, 'lost': 0, 'rev': 1560} {'avg': 3.37, 'peak': 7, 'fulls': 0, 'full': 0, 'block': 0, 'in': 11, 'wash': 6, 'by': {'xq': 6}, 'washT': {'xq': 11.999999999999968}, 'starts': 2, 'startAvg': 6.5}
lazy 2 {'guests': 19, 'lost': 2, 'rev': 3060} {'avg': 5.81, 'peak': 10, 'fulls': 2, 'full': 24.2, 'block': 32.5, 'in': 27, 'wash': 19, 'by': {'jill': 19}, 'washT': {'jill': 35.36666666666722}, 'starts': 6, 'startAvg': 9.3}
lazy 3 {'guests': 3, 'lost': 0, 'rev': 420} {'avg': 2.9, 'peak': 4, 'fulls': 0, 'full': 0, 'block': 0, 'in': 4, 'wash': 0, 'by': {}, 'washT': {}, 'starts': 0, 'startAvg': 0}
-- old_CD
C {'guests': 80, 'lost': 9, 'rev': 39470} {'avg': 0, 'peak': 0, 'fulls': 0, 'full': 0, 'block': 0, 'in': 0, 'wash': 0, 'by': {}, 'washT': {}, 'starts': 0, 'startAvg': 0} {'trips': 81, 'items': 124, 'max': 4, 'n': [0, 54, 16, 6, 5], 'multi': 13} {'avg': 1.54, 'peak': 8, 'full': 0.3, 'wait': 0, 'noW': 0}
D {'guests': 73, 'lost': 0, 'rev': 51710} {'avg': 0, 'peak': 0, 'fulls': 0, 'full': 0, 'block': 0, 'in': 0, 'wash': 0, 'by': {}, 'washT': {}, 'starts': 0, 'startAvg': 0} {'trips': 67, 'items': 104, 'max': 4, 'n': [0, 36, 26, 4, 1], 'multi': 5} {'avg': 0.7, 'peak': 4, 'full': 0, 'wait': 0, 'noW': 0}
D2 {'guests': 79, 'lost': 2, 'rev': 50170} {'avg': 0, 'peak': 0, 'fulls': 0, 'full': 0, 'block': 0, 'in': 0, 'wash': 0, 'by': {}, 'washT': {}, 'starts': 0, 'startAvg': 0} {'trips': 76, 'items': 104, 'max': 3, 'n': [0, 49, 26, 1, 0], 'multi': 6} {'avg': 0.73, 'peak': 4, 'full': 0, 'wait': 0, 'noW': 0}
-- dev_CD
C {'guests': 61, 'lost': 23, 'rev': 31295} {'avg': 5.15, 'peak': 10, 'fulls': 5, 'full': 13.8, 'block': 558.8, 'in': 84, 'wash': 77, 'by': {'cleaner': 65, 'waiter': 12}, 'washT': {'cleaner': 78.56666666666477, 'waiter': 19.200000000000113}, 'starts': 18, 'startAvg': 8.2} {'trips': 65, 'items': 99, 'max': 4, 'n': [0, 43, 12, 8, 2], 'multi': 9} {'avg': 1.12, 'peak': 7, 'full': 0, 'wait': 64.4, 'noW'
D {'guests': 68, 'lost': 8, 'rev': 56395} {'avg': 4.13, 'peak': 12, 'fulls': 0, 'full': 0, 'block': 0, 'in': 144, 'wash': 138, 'by': {'cleaner': 138}, 'washT': {'cleaner': 82.79999999999787}, 'starts': 12, 'startAvg': 7.2} {'trips': 79, 'items': 112, 'max': 3, 'n': [0, 50, 25, 4, 0], 'multi': 6} {'avg': 0.73, 'peak': 6, 'full': 0, 'wait': 18, 'noW': 4.8}
D2 {'guests': 71, 'lost': 0, 'rev': 54275} {'avg': 5.23, 'peak': 16, 'fulls': 0, 'full': 0, 'block': 3, 'in': 141, 'wash': 139, 'by': {'cleaner': 139}, 'washT': {'cleaner': 83.93333333333113}, 'starts': 8, 'startAvg': 8} {'trips': 75, 'items': 110, 'max': 4, 'n': [0, 43, 30, 1, 1], 'multi': 6} {'avg': 0.71, 'peak': 4, 'full': 0, 'wait': 18.5, 'noW': 2.5}
