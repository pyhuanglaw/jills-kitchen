Jill’s Kitchen v2.3 — Stories of Jill’s Kitchen
完整開發 Brief：故事事件、人物記憶、評論 2.0、社群、宣傳、酒水服務與餐廳歷史
請在 v2.2.1 已完成、Version 33 已發布、v2.2.1 tag 已建立且 QA 完成之後，才開始本版本。
不要把這份需求插入尚未完成的 v2.2.1。
【整合紀錄 2026-09-30】本文件已整合兩份 addendum（原文存於 docs/v23/）：
- 《LOUNGE EXPANSION + STAFF GROWTH + RELATIONSHIP SPACE》→ 第二部（L1–L45）。
- 《LOUNGE ORIGIN ARC — 餐廳是不是少了什麼？》→ 第 20 節（Ken × Monsieur 杜 現在是 Lounge 的敘事起源）。
- 四位新員工的核心概念圖（approved concept direction）→ docs/v23/lounge_cast_concept.png，文字轉錄在 L12a。
- 《LOUNGE STORYLINES & RELATIONSHIP CONTENT》（第三份，同日稍後）→ 第三部（S1–S22）；Sophie × Mia 的角色設定圖
  → docs/v23/sophie_mia_concept.png，文字轉錄在 S6a。與既有章節重疊的人（Sophie、Mia、Dylan、王家、Ken × 杜）只加交叉
  引用，不改既有內容。
被 addendum 明確取代的部分，只在文件層面調整字句：第 20 節（Stage 3「酒水企劃」→ Lounge 企劃）、第 21 節（酒水基礎設施
不再是主廳裡的酒櫃，而是 Lounge 的吧台／酒藏；First Tasting Night = 起源線 Beat 4 的一次性實驗）、第 52 節（Ken-triggered
wine service → Ken → wine → Lounge 起源線）、第 53 節（Phase E「Wine」→ Phase E–I 的 Lounge 分期）、「開始方式」的稽核清單
（加入 addendum Phase 0 的報告項目）。其餘既有的故事／關係／Reviews／Social／Marketing／酒水／貓／Dylan／熟客要求全部保留。
本文件與 addendum 的存在都不構成開始 v2.3 的授權：v2.3（含 architecture audit）要等到明確授權才開始。
v2.3 的核心不是再增加大量獨立功能，而是讓目前已經存在的 Jill、Dylan、五隻貓、熟客、特殊客人、員工、料理、Life Album、Restaurant Records、Reviews、店鋪升級與 simulation 開始彼此記得、彼此影響，形成真正的餐廳歷史。
0. 最重要的產品目標
目前 Jill’s Kitchen 已經有足夠的經營骨架。
v2.3 不應主要追求：
- 更多房間；
- 更多無關 NPC；
- 更多純裝飾家具；
- 更多獨立小系統；
- 更多單次隨機事件；
- 更複雜的數值管理。
v2.3 要解決的是：
Day 50 不應只是比 Day 20 更有錢、更大、更忙。

玩家應該感覺：
「這些人已經在這間店一起生活五十天了。」

核心設計原則：
Randomness = 今天抽到什麼。
History = 因為以前真的發生過這件事，所以今天才發生這件事。

玩家不應每天重新抽一個沒有歷史的事件池。
餐廳應該逐漸形成自己的故事。
1. 開發前：先做現況稽核，不要直接重寫
開始 coding 前，先完整閱讀目前 v2.2.1 source 與相關資料結構。
請先確認並列出目前以下系統實際存在的位置與資料流：
- regular / named guest history；
- World Memory；
- Dylan progression；
- 王先生／王太太 persistent identity；
- guest visit history；
- speech log；
- Reviews；
- Restaurant Records；
- Life Album；
- achievements / milestones；
- daily event system；
- weather / special day；
- customer ordering model；
- menu / recipes / Signature progression；
- staff persistent state；
- cat autonomous behavior；
- furniture / upgrade persistence；
- save/load/migration；
- RNG；
- daily settlement；
- current social-like or blogger mechanics, if any.
先 reuse，再新增。
不要因為這份 brief 使用「Story」「Memory」「Social」等名詞，就直接建立數套新的平行 state。
如果既有系統已經能承擔資料，應優先擴充。
2. 架構原則：一個歷史來源，不要六套互相打架的記憶
2.1 建議概念架構
不要照名稱機械建立 class；請依現有程式架構最小化整合。
但邏輯上應有四層：
A. FACT / MEMORY
只記錄真的發生過的事。
例如：
- Sophie 看過寶寶；
- Sophie 曾抱怨寶寶靠近包包；
- Sophie 曾主動問寶寶在哪；
- Sophie 已送貓用品；
- Momo 親眼看到寶寶使用該用品；
- Ken 曾吃某料理；
- 某 NPC 親歷某次停電；
- Mia 在 Side Hall 建成前就來過；
- 某員工在某 milestone 發生時已受僱；
- 某客人吃過某道 Signature 第一版；
- 某客人曾遇到售罄；
- 某客人曾等待超過某時間；
- 某客人曾坐 Side Hall；
- 某 NPC 曾在 Dylan reveal 前看過 Dylan/Jill 特殊互動。
Fact 必須來源於真實 simulation。
不要讓 NPC 全知。
B. STORY STATE
只記：
- 哪條 arc 到哪個 stage；
- 上一次 beat 何時發生；
- 是否完成；
- 是否有 pending beat；
- 必要的少量 story-specific flags。
不要把完整 simulation 複製進 story state。
例如 Sophie 不需要：
likesCats = 0.72
只需要類似：
- metBaoBao
- complainedAboutBag
- askedAboutBaoBao
- giftGiven
實際命名依現有 coding convention。
C. CONSEQUENCE
Story beat 發生後，可以對世界留下效果：
- persistent decor；
- cat furniture；
- NPC preference；
- seat preference；
- recipe unlock；
- wine service unlock；
- temporary demand；
- social topic；
- new review behavior；
- future dialogue pool；
- Album opportunity；
- Restaurant Record；
- future event eligibility。
所有 consequence 必須 idempotent。
同一 story beat 因 reload / retry / save restore 再跑，不可以：
- 重複送家具；
- 重複扣錢；
- 重複解鎖料理；
- 重複發同一篇重要貼文；
- 重複寫 milestone；
- 重複新增同一 NPC。
D. PRESENTATION
最後才是：
- dialogue；
- speech bubble；
- small animation；
- social post；
- review；
- Album photo；
- notification；
- settlement card。
Presentation 不能反過來成為真實狀態來源。
例如：
不要因為生成了一句「Sophie 看著寶寶」就假定寶寶真的在現場。
先確認世界狀態成立，再演出。
3. 建立輕量 Story Event Arbiter，而不是大型 RPG Story Engine
需要一個很小的事件仲裁機制，避免同一天：
- Dylan reveal；
- Sophie 送禮；
- Ken 解鎖酒水；
- 神秘評論家揭露；
- 員工故事；
- Pairing Night；
- milestone；
全部一起爆炸。
每天根據 eligible candidates 選擇少量事件。
建議密度
Major beat
通常一天最多 1 個。
例如：
- Sophie 送貓用品；
- 酒水企劃正式提出；
- 神秘評論家文章揭露；
- Signature 試作夜；
- 四人打烊晚餐。
Minor callback
一天可以 0–2 個。
例如：
- 「最近沒停電了吧？」
- Sophie 看一下寶寶；
- 周董問布丁；
- 小林固定飲料；
- 老員工知道東西在哪；
- NPC 評論 Side Hall。
Ambient interaction
仍可正常大量存在。
例如：
- 貓走動；
- staff idle；
- ordinary guest speech；
- Jill idle；
- regular normal visit。
正常營業日仍然是遊戲主體。
目標大約：
80% 正常餐廳生活，20% 值得記住的事情。

不要把 Jill’s Kitchen 做成每一天都有人宣布人生重大轉折。
4. Event eligibility 必須 declarative / data-driven
不要把 20 條故事全部散落成：
if(day>25 && sophie...)
if(day>28 && ken...)
散在 render loop、customer loop、settlement loop 裡。
每個 story beat 至少概念上應有：
- stable unique ID；
- arc ID；
- stage；
- prerequisites；
- blockers；
- minimum day if necessary；
- required present characters；
- optional present characters；
- required restaurant state；
- cooldown；
- priority；
- major/minor classification；
- trigger window（opening / service / after close / settlement）；
- effect / consequence；
- fallback；
- Album eligibility；
- social eligibility；
- callback unlocks。
具體資料格式請依現有 codebase 決定。
不要為了符合這份文字硬建一個龐大 framework。
5. 不准把故事綁死在「第幾天」
Day 可以作最低成熟度條件，但不要：
Day 27 Sophie 固定送禮。
Day 31 Ken 固定解鎖酒。
Day 35 評論家固定出現。

應該由：
餐廳狀態 + NPC 歷史 + 真實遭遇 + cooldown + 一點 RNG
共同決定。
因此不同存檔的故事順序可以不同。
6. NPC 只能知道自己合理知道的事
這是 v2.3 的 HARD RULE。
例如：
某次 Day 18 停電。
當時：
- Sophie 在；
- Mia 不在。
之後電力升級。
Sophie 可以：
「最近沒再停電了吧？」

Mia 不可以。
同理：
- 沒看過舊 Side Hall 的 NPC 不能說「以前這裡還沒有側廳」；
- 沒吃過第一版 Signature 的 NPC 不應比較第一版；
- 新員工不能回憶自己入職前的 staff meal；
- 沒親眼看到某隻貓的 NPC 不應突然說自己很熟牠；
- 沒看過 Dylan/Jill 互動的人不能提供相關 clue。
7. 不做 RPG 好感度 UI
不要新增：
- ❤️ 73；
- Friendship Level；
- Story 3/5；
- Relationship XP；
- 任務驚嘆號；
- Quest Complete；
- Story Reward。
可以內部有 progression state，但玩家從行為理解關係。
例如：
玩家知道 Sophie 開始喜歡寶寶，不是因為：
Sophie ❤️ BaoBao +10

而是因為：
第一次：
「可以不要讓牠靠我的包嗎？」

後來：
「今天那隻呢？」

再後來：
「看到就買了。」

最後她送的貓用品真的永久放在店裡。
8. STORY ARC 01：Sophie × 寶寶
【2026-09-30】這條線在 Lounge 之後仍獨立繼續（S7）；Sophie × Mia（S6）是另一條線，可以自然交會，不取代這條。
《我沒有特別喜歡貓》
這是 v2.3 的代表故事之一，請優先做好。
Stage 1：保持距離
Sophie 來店，而且寶寶真的靠近她／她的包。
Sophie：
「可以不要讓牠靠我的包嗎？」

Jill：
「寶寶，過來。」

寶寶依自己的 AI 行為離開或待在附近。
不要 teleport。
Stage 2：開始注意
至少隔數次 Sophie visit。
某次寶寶沒有在她附近。
Sophie 看一下：
「今天那隻呢？」

Jill：
「哪隻？」

Sophie：
「……算了。」

Stage 3：寶寶主動靠近
必須是寶寶真的處於合理可互動位置。
寶寶自主坐在 Sophie 附近。
Sophie 不需要立刻摸牠。
她只是低頭看。
Album candidate：
只是坐一下

Stage 4：Sophie 帶東西
再隔一段時間。
Sophie 某次來店手上有小紙袋。
吃完後：
Jill：
「這什麼？」

Sophie：
「看到就買了。」

Jill 打開。
是一件小型、符合目前餐廳美術風格的貓用品。
Jill：
「給寶寶的？」

Sophie：
「給你們店裡的。」

Jill：
「妳不是不喜歡貓？」

Sophie：
「我沒有說不喜歡。」

Jill：
「妳第一次來叫她不要靠妳的包。」

Sophie：
「那是兩件事。」

Permanent consequence
該貓用品永久出現在餐廳。
不是商店購買物。
物件資訊可以淡淡寫：
Sophie 帶來的。

寶寶有較高使用 preference。
其他貓仍可使用。
Sophie 以後如果看到寶寶正在使用，可以：
- 停一下；
- 看一眼；
- 不一定講話。
不要把每個情緒都用 dialogue 解釋。
Album
可捕捉：
她說只是剛好看到

或：
Sophie 說她沒有特別喜歡貓

Social crossover
如果 Momo 日後真的看到寶寶正在使用該物件，可以產生一篇社群貼文：
聽說這個不是店裡買的。
某位嘴硬的熟客送的。

Sophie 下次來：
「那篇是誰發的？」

Jill：
「哪篇？」

Sophie：
「算了。」

這就是本版想要的 story → world object → another NPC → social → callback。
9. STORY ARC 02：老饕李先生 × 第二道 Signature
《兩道走天下》
注意 v2.2.1 已新增／可能已新增第二道 Signature Dessert。
因此 v2.3 必須兼容：
新存檔
可以讓這條 story arc 成為第二 Signature 的自然 origin / progression。
v2.2.1 成熟舊存檔
絕對不能重新鎖住玩家已經擁有的料理。
Migration 應辨識已解鎖狀態。
成熟舊檔可以：
- 將 origin 視為 historical；
- 從後續 callback / recognition 開始；
- 或用一次不破壞既有 unlock 的回顧型小事件承接。
不要因為 v2.3 story system 導致玩家失去已解鎖料理。
新 progression 的故事方向
老饕：
「所以妳就打算靠這一道走天下？」

Jill：
「不行嗎？」

老饕：
「行啊。」

停一下。
「就是有點浪費。」

Sophie 後續：
「主菜已經知道自己是誰了。甜點還沒有。」

打烊後 Jill 試作。
可有一次輕量方向選擇：
- 清爽；
- 濃郁；
- Jill 自己想做的。
不是數值正解。
之後：
《還沒有名字的甜點》
特殊試作夜。
老饕 / Sophie / Momo 至少一位提高來訪機率。
Album：
還沒有名字的甜點

最終老饕：
「現在可以了。」

Jill：
「什麼？」

「兩道走天下。」

之後其他 NPC 可以記得這道 Signature 的出現。
10. STORY ARC 03：Madame Lin
《她什麼都看得到》
Madame Lin 的特色不是單純 VIP。
她非常注意空間與 hospitality 細節。
她應讀取真實餐廳狀態：
- 空調；
- 主燈；
- Side Hall；
- 戶外座位；
- 桌椅；
- 洗碗機／可見設備；
- 空間改裝。
例如真的升級冷氣後：
「冷氣換過了？」

Jill：
「妳怎麼知道？」

沒有升：
「還沒換啊。」

Gift event
她實際見證過數次餐廳改善後，某次帶來一個符合美術風格的小型植物／decor。
Jill：
「今天怎麼帶東西？」

Madame Lin：
「那個角落空很久了。」

Jill：
「……妳每次到底都在看哪裡？」

Permanent consequence：
物件永久存在。
說明：
Madame Lin 帶來的。

11. STORY ARC 04：周董
《都可以》
不要把周董做成炫富 caricature。
他的笑點：
每次都說「隨便／都可以」，其實習慣非常固定。

逐漸形成：
- preferred seating；
- ordering pattern；
- 一個非常普通的甜點偏好，例如布丁。
Seat event
習慣位置被普通客人占用。
不要趕普通客人。
員工：
「周董，平常的位置今天有人。」

周董：
「那就別的位置啊。」

第一次坐 Side Hall。
之後永久增加 Side Hall preference。
Pudding callback
正式聚餐後：
「布丁還有嗎？」

若售罄：
Jill：
「今天沒有了。」

「喔。」

Jill：
「你不是都隨便？」

周董：
「……那明天再來。」

隔天 appearance probability 提高。
12. STORY ARC 05：神秘美食評論家
《戴帽子的客人》
第一次來：
名字只能顯示：
戴帽子的客人

不要：
- 評論家 icon；
- 特殊光圈；
- VIP priority；
- 玩家警告；
- 特殊服務 bonus。
正常排隊。
正常等待。
正常點餐。
2–5 天後
Restaurant Records：
有人寫了 Jill’s Kitchen。

此時才 reveal identity / portrait。
評論內容必須根據當天真實 experience：
- 吃什麼；
- 等多久；
- 是否售罄；
- 是否 rush；
- 是否停電；
- Jill 是否服務；
- 坐哪區；
- 是否看到貓；
- 當時餐廳環境。
如果那天很亂，不准 magically 寫完美評論。
Later return
Jill：
「今天還戴帽子？」

評論家：
「比較安靜。」

Jill：
「你上次害我三天都有人問同一道菜。」

之後成為低頻 recurring named guest。
13. STORY ARC 06：衛生檢查員
《今天不是來檢查》
前幾次照正常 inspection。
後來某晚穿便服來。
員工：
「……他來了。」

Jill：
「誰？」

「那個。」

Jill：
「他今天沒有夾板。」

檢查員：
「我今天只是來吃飯。」

當天：
完全不是 inspection。
真的坐下、點餐、付款。
之後加入極低頻普通客人池。
14. STORY ARC 07：王先生 × 王太太
《今天只有一個人》
玩家習慣他們一起來。
某天只有王先生。
不解釋。
隔一段時間只有王太太。
也不解釋。
後來一起來：
王太太：
「他上次自己跑來吃。」

王先生：
「妳前天不也來了？」

「我是經過。」

「我也是經過。」

之後永久允許：
- couple visit；
- Mr. Wang solo；
- Mrs. Wang solo。
他們是兩個人，不是 Couple NPC object。
15. STORY ARC 08：王先生／王太太 × Dylan／Jill
【2026-09-30】「十一年了」指的只有 Jill 與 Dylan 自己的關係（S11）；Dylan 不是「觀察別人的戀情十一年」，也不會對新關係全知。
《還在追喔？》
Dylan reveal 前：
王太太：
「還在追喔？」

Dylan：
「很難追。」

Jill：
「你可以放棄。」

Dylan：
「不行。」

不要解釋。
這是 clue。
Reveal 後：
王太太：
「追到了沒？」

Dylan：
「還在努力。」

Jill：
「十一年了。」

Rare after-close event
四人真的都在場且條件適合：
打烊後坐同桌。
貓照自己的 AI 活動。
Album：
打烊以後

16. STORY ARC 09：Mia
【2026-09-30】Mia 也是 Sophie × Mia（S6，primary slow-burn）的一半；這裡的聚餐線與那條線各自獨立，Mia 永遠是獨立 NPC。
《我以前來的時候》
只有真的在早期餐廳來過的 Mia 才能說：
「我以前來的時候這邊還沒有側廳。」

後續：
Mia 的聚餐
帶 3–4 位朋友。
真正形成多人 ticket。
- 點較多種類；
- 停留較久；
- 有合照 opportunity；
- Album 可記錄。
其中一位朋友日後極低機率成為 ordinary return customer。
17. STORY ARC 10：小林
《我還沒點》
逐漸形成固定飲料 preference。
某天剛坐：
Jill 已經放上飲料。
小林：
「我還沒點。」

Jill：
「你哪次不是這個？」

「……也是。」

之後可以提前準備。
偶爾某天：
「今天不要那個。」

Jill：
「你怎麼了？」

小故事即可，不要硬做大事件。
18. STORY ARC 11：Leo
《終於都在》
Leo 可以幫 Jill 拍五隻貓。
HARD RULE：
只有五隻真的都在合理可拍範圍時才可觸發。
不要 staged teleport。
不要再出現：
五隻貓同框

照片實際三隻。
Album：
終於都在

19. STORY ARC 12：吃貨小琪 × Momo
《是不是那一道？》
兩人的功能必須不同。
小琪
Food-driven。
她喜歡某道菜後：
- 社群提到；
- 2–3 天該料理 demand 上升；
- 客人真的說：「是不是那一道？」
Momo
Presentation / venue / trend-driven。
她比較可能帶來：
- first-time visitors；
- Side Hall interest；
- Signature presentation interest；
- cats / atmosphere interest。
不要把兩個角色做成同一個「Influencer +20%」。
20. STORY ARC 13：品酒師 Ken × Monsieur 杜 — 《餐廳是不是少了什麼？》＝ Lounge 的起源
【2026-09-30 reconciled】這條線原本「正式解鎖一整個輕量酒水服務」；現在它的後果變大：它是 Lounge（第二部）的敘事起源。
敘事素材保留，Stage 3 的「酒水企劃」改為「Lounge 企劃」。不要把先前設計的 wine-trigger story 換成單純的 construction unlock；
玩家不可以只因為營收／天數／評分達標就突然在 upgrade menu 看到「Build Lounge」。Lounge 要先以一個「想法」存在於餐廳的故事裡。
結構：
KEN’S QUESTION → WINE / PAIRING CONVERSATIONS → JILL BEGINS CONSIDERING IT → SMALL REAL-WORLD EXPERIMENT / TASTING
→ AFTER-CLOSE LOUNGE PROJECT DISCUSSION → PLAYER MAY START OR DEFER PROJECT → BUILD LOUNGE I → PERMANENT WINE / BAR SERVICE BEGINS
The Lounge therefore has an authored origin. It is not an upgrade that appears from nowhere.

BEAT 1 — KEN NOTICES THE ABSENCE（原 Stage 1）
After Ken has genuinely visited Jill’s Kitchen enough to know the food, and has actually eaten suitable dishes:
Ken：
「Jill，我一直想問一件事。」

Jill：
「什麼？」

「妳真的完全不賣酒？」

「目前沒有。」

Ken：
「難怪。」

Jill：
「難怪什麼？」

「有幾道菜，每次吃到一半，都覺得旁邊少了一個東西。」

（addendum 版的收尾，可擇一或合用）
Jill：
「你是來吃飯還是來找工作？」

Ken：
「吃飯。」

只種伏筆。This creates a real fact such as kenRaisedWineQuestion = true. Do not expose the flag to the player. Do not trigger
solely from calendar day. Ken must have real restaurant history.

BEAT 2 — MONSIEUR 杜 DISAGREES（原 Stage 2）
Ideal presentation: Ken and Monsieur 杜 are genuinely co-present later. Ken begins discussing what he would pair with a dish.
Ken：
「這一道如果配——」

Monsieur 杜：
「不要。」

Ken：
「我還沒講。」

「我知道你要講什麼。」

Jill：
「你們兩個可以先讓我把餐廳開完嗎？」

This begins their wine disagreement and establishes their relationship.
IMPORTANT DEADLOCK PROTECTION: Monsieur 杜 co-presence should NOT be an absolute prerequisite for the entire Lounge system.
If repeated natural opportunities fail to produce Ken × 杜 co-presence, Ken’s wine discussion may continue through another
valid presentation. Monsieur 杜 can enter the arc later and react to it. Therefore: Ken is the structural origin; Ken ×
Monsieur 杜 is the preferred authored enrichment. Do not allow unlucky scheduling to permanently block Lounge construction.

BEAT 3 — THE IDEA KEEPS RETURNING
Do NOT immediately unlock construction after one dialogue. Over subsequent REAL visits, the idea should recur lightly:
Ken notices another dish that would pair well; Jill sees someone ordering dinner and lingering afterward; a customer asks
whether there is somewhere to have one more drink; a suitable existing regular remains after dinner. These should be sparse
callbacks, not repetitive prompts. The restaurant gradually develops a reason for a Lounge. The player should feel
「好像真的可以做。」 not 「系統叫我升級了。」

BEAT 4 — SMALL TASTING / PROOF OF CONCEPT（原第 21 節的 First Tasting Night）
Before permanent Lounge construction, allow ONE authored experimental evening. This is NOT permanent wine service yet.
Possible framing: Ken helps Jill prepare a very small tasting selection. No bottle inventory system. No permanent wine menu.
No new daily management. The event uses a limited number of actual guests.
Jill：
「你自己開的頭。」

Ken：
「我只是問妳為什麼沒有。」

Jill：
「現在有了。」

Ken：
「……那我要負責？」

Jill：
「要。」

Monsieur 杜 may attend if naturally eligible; if present, he and Ken can disagree over pairing. The player may make one or
two meaningful high-level choices about pairing direction; there is no objectively correct answer. The purpose of this
event is: 1. narrative; 2. prove that wine fits Jill’s Kitchen; 3. introduce wine visually; 4. create Album / Review /
Social history; 5. make Jill seriously consider a permanent space. It is NOT a hidden tutorial for a giant wine simulator.
Album：「Ken 自己開的頭」或「他們還是沒有同意」。

BEAT 5 — AFTER CLOSING: THE LOUNGE IDEA（原 Stage 3）
After the tasting / sufficient wine-origin facts, trigger a quiet after-close moment. Jill looks at the restaurant after service.
Jill：
「如果真的要做，我不想只是放一個酒櫃。」

Ken：
「那妳想怎樣？」

Jill：
「讓人吃完飯以後，還有地方可以坐。」

This is the conceptual birth of the Lounge. The project is then revealed to the PLAYER:
新企劃：Jill’s Kitchen — Lounge
玩家可以：
開始規劃

或：
之後再說

「之後再說」NEVER permanently loses the Lounge. The project can be revisited later through Restaurant Records / project UI /
another natural reminder. Do not repeatedly nag the player.

BEAT 6 — PROJECT, NOT INSTANT PURCHASE
Once the player chooses to pursue it, the Lounge becomes a visible expansion project. It should require: appropriate
restaurant maturity; physical expansion availability; substantial money investment. Exact balance must be audited.
Do NOT require arbitrary story grind after Jill has already decided to build it. Do NOT require friendship meters. Do NOT
require Monsieur 杜 to appear again. The player is now making a restaurant-development decision.

BEAT 7 — CONSTRUCTION COMPLETES
When Lounge I is completed, the physical restaurant changes. This is the moment permanent Lounge service becomes available.
At minimum: bar counter; initial seating; wine storage/display; glassware; Lounge assignment destination; Bar Food
eligibility; bartender staffing requirement. Permanent alcohol service begins here. Do NOT permanently sell the full wine
menu in Main Hall before Lounge I exists. The earlier tasting was an authored experiment, not normal daily service. After
Lounge opens, Main/Side guests may eventually order eligible wine with dinner, but the Lounge remains the operational and
narrative home of the wine program.

BEAT 8 — FIRST REAL LOUNGE NIGHT
The first night should NOT be a giant scripted cutscene. Let normal service occur, but use restrained authored callbacks.
Ken should have elevated likelihood to appear if naturally valid. If Monsieur 杜 appears:
Ken：
「你不是說不要？」

杜：
「我說的是你的搭配。」

Ken：
「所以你還是來了。」

杜：
「我來吃飯。」

Jill：
「你現在坐在酒吧。」

Do not require this exact wording. The important thing is continuity: these people remember why this room exists.

LONG-TERM CONSEQUENCE
After Lounge opens: Ken does NOT become staff. Monsieur 杜 does NOT become staff. They remain paying customers. They may
gradually become Lounge regulars. Evan / 晴 may later learn their habits through REAL service history. This creates a new
relationship chain: Ken ↔ Monsieur 杜, Ken ↔ Evan, Monsieur 杜 ↔ Evan, Ken ↔ 晴, Jill ↔ Lounge history. The origin event
therefore continues generating story instead of ending after unlock.
Late callback（S4）：much later, after Evan has naturally learned the history of the Lounge —
Evan：「聽說這裡是你害的。」 Ken：「誰跟你講的？」 Jill（從別處）：「我。」 Only if Evan has reasonably learned the origin story.

TRIGGER ARCHITECTURE / DEADLOCK SAFETY
Do NOT implement this as Day 35 → Ken line / Day 38 → 杜 line / Day 40 → tasting / Day 42 → Lounge, and do NOT implement
it as one fragile linear stage chain. Represent important historical facts separately. Conceptually: Ken has enough real
visit history; Ken has eaten relevant food; Ken raised wine question; Ken discussed pairing; Monsieur 杜 participated in
wine disagreement (optional enrichment); experimental tasting occurred; Jill considered permanent wine service; Lounge
project revealed; player deferred / accepted; Lounge construction started; Lounge completed; first Lounge service occurred.
Only true logical requirements are HARD. Use eligibility windows / weighted selection / overdue priority for presentation.
Most importantly, the system must distinguish STRUCTURAL PROGRESSION (Ken raises question → Jill experiments → Lounge
project becomes possible) from OPTIONAL CHARACTER ENRICHMENT (Monsieur 杜 happened to argue with Ken; Momo posted about
tasting; 老饕 commented on pairing; Sophie attended tasting; etc.). Optional enrichment must NEVER deadlock structural
progression.

MATURE-SAVE SAFETY
Do not assume the player reaches this arc in one exact restaurant-development order. The player may already have: Side
Hall; mature staff; high revenue; Signature dishes; infrastructure upgrades; long Ken history. Eligibility should recognize
existing valid history where available. Do not replay logically obsolete introductory material merely because a new field
was added. At the same time: never fabricate that an event occurred if the save has no evidence for it. Use safe migration
defaults and allow the next natural visit to begin the missing story.

NARRATIVE PRINCIPLE
The player should eventually be able to remember: 「這個酒吧是 Ken 當初一直嫌 Jill 的餐廳沒有酒，後來才真的弄出來的。」
The Lounge must have provenance. It should feel like something that happened in Jill’s Kitchen history, not a feature that
appeared in a patch.
21. 酒水系統架構
【2026-09-30 reconciled】酒水服務現在主要透過可擴建的 Lounge 發展（第二部 L4、L7–L11）；本節保留「輕量」原則，把設備與
時序對齊到 Lounge：永久酒水服務從 Lounge I 完工開始（第 20 節 Beat 7），之前只有一次 authored tasting（Beat 4）。
保持輕量。
不要做：
- 30 種真實酒莊 SKU；
- 酒類進貨 micro-management；
- 酒窖濕度；
- 酒杯清洗小遊戲；
- 每桌手動倒酒；
- Sommelier Skill Tree；
- 酒類期貨市場。
😂
第一版可以有幾個 style（與 L10 相同的五種）：
- 氣泡酒；
- 清爽白酒；
- 飽滿白酒；
- 輕盈紅酒；
- 濃郁紅酒。
可以有遊戲內虛構酒名，但不必過度 SKU 化。v2.3 不要求玩家逐瓶補貨；酒的成本以 cost-of-goods 表現，不是另一套每日庫存。
酒水基礎設施
不再是主廳裡的一個酒櫃，而是 Lounge 本身的一部分（吧台、酒藏／展示、杯具；Lounge II／III 再升級）。它仍然是成熟期的
money sink，而且設備必須真的畫在餐廳裡，不要只在 upgrade menu 顯示 Lv.2。
Pairing
部分料理可以有推薦 pairing。
客人：
- 不喝；
- 單點；
- 接受 pairing。
平常由 staff 自動服務（L11：never「每桌跳視窗選酒」）。玩家的決定在高價值時刻：提供哪些酒款／style、Lounge 投資、tasting
night、authored pairing 選擇、menu/pairing 策略、員工分配。80% flow，20% hand-feel。
Main Hall / Side Hall 在 Lounge I 之前不永久販售完整酒單；Lounge 開幕後主廳／側廳客人可以逐漸點合適的酒配晚餐，但 Lounge
是酒水的營運與敘事中心。
First Tasting Night
就是第 20 節的 Beat 4：一次 authored 的實驗之夜，Ken 參與、Monsieur 杜可加入、玩家做一兩個高階選擇；不是每日營運。
Album：
Ken 自己開的頭

或：
他們還是沒有同意
22. 評論系統 2.0
Reviews 不要只是一顆星數 generator。
每篇重要評論應根據 guest 真實 experience。
至少考慮：
- dishes eaten；
- waiting time；
- sell-outs；
- service；
- room；
- cats encountered；
- hospitality；
- wine；
- special event；
- atmosphere；
- staff / Jill interaction；
- repeat visit context。
Review topics
內部可以維護 topics，例如：
- food；
- signature；
- dessert；
- wine；
- service；
- waiting；
- cats；
- atmosphere；
- Side Hall；
- outdoor；
- comfort；
- value；
- staff。
但 UI 不要直接 dump engineering tags。
玩家看到：
最近大家在說
🐈 貓咪
🍽️ Jill’s Signature
✨ 側廳氣氛
⏱️ 最近幾篇提到等待時間
23. 負評不是 reputation punishment button
例如：
★★★☆☆
「東西很好吃，但想點的兩道都賣完了。」

不要直接：
Reputation -20

如果同一客人日後回來，而且真的改善：
★★★★★
「第二次來順很多，而且終於吃到上次賣完的那一道。」

這是服務恢復故事。
24. 社群系統
Jill’s Kitchen 社群頁
社群不是另一個需要每天 grind 的 dashboard。
主要有：
A. 客人自己發
自動產生，但只能根據真的發生的事情。
例如 Momo 真的看到柔柔：
今天本來是來吃飯的，但有人一直在桌子下面監督我。

照片必須真的有柔柔。
B. Jill’s Kitchen 自己發
不要要求玩家寫文案。
每隔合理時間，系統可以從最近真的發生過的內容提供最多 3 個候選。
例如：
🍽️ 新料理
第二道 Signature。
🐈 店裡的一天
Life Album 的自然貓照片。
✨ 新側廳
真的完成的 Side Hall。
🍷 新酒單
酒水正式開始。
玩家選擇一個。
遊戲自動產生符合 Jill’s Kitchen 語氣的短貼文。
25. 社群不是 Followers Clicker
不要把核心變成：
Followers 12,394
+500
+300
Social Lv.8

可以顯示自然的互動數字作 flavour，但不要讓它變主要 progression currency。
真正 gameplay effect 應該來自：
大家正在談什麼。

26. Social topic → real demand
例如分享料理：
未來幾天：
- food-driven guests 稍增；
- 該料理 ordering weight 上升。
分享貓：
- 愛貓新客稍增；
- 拍照行為稍增。
但：
五隻貓不因此變成員工。
不要把貓抓到指定位置營業。
分享 Side Hall：
- date / group guests 對 Side Hall preference 上升。
分享酒單：
- dinner / pairing interest 上升。
27. 宣傳／廣告系統
廣告不是：
$10,000 → Customers +20%

玩家應該選：
「現在希望什麼樣的人知道 Jill’s Kitchen？」

Campaign A：在地宣傳
較低成本。
增加：
- nearby first-time guests；
- families；
- solo diners；
- future regular conversion opportunities。
Campaign B：料理／Signature 宣傳
宣傳一個實際 menu item。
提高：
- 該菜需求；
- food-driven visitors。
如果備料不足：
真的可能售罄。
客人甚至可以：
「不是說有那個甜點嗎？」

這是玩家自己宣傳造成的 demand。
不要偷偷替玩家補無限庫存。
Campaign C：Side Hall／聚餐
提高：
- group parties；
- Side Hall demand；
- longer table stays；
- larger tickets。
讓 Side Hall 真正有商業用途。
Campaign D：店貓／生活感
提高：
- first-time curiosity；
- cat-interested guests；
- photo behavior。
但不能強迫貓互動。
Campaign E：晚餐／酒單
酒水解鎖後：
- dinner demand；
- pairing；
- wine orders；
- mature dining guests。
28. 廣告不是直接買熟客
HARD RULE：
Paid reach ≠ regular conversion.

廣告能把人第一次帶進來。
能不能回來取決於：
- food；
- wait；
- sell-out；
- service；
- atmosphere；
- experience。
因此：
花錢 → 新客 → 真實體驗 → 有些人才成為回頭客。

不要：
花錢 → Regular +12。

29. Campaign result 必須是真資料
Campaign 結束後可以顯示：
42 位客人第一次來
18 桌點了 Signature Dessert
7 位提到是在社群看到
3 位後來再次來店
最常被提到：甜點、貓咪、側廳

數字必須從 simulation telemetry 得出。
不能生成假的 flavour metrics。
30. Social / Review / Ads 的共同 topic model
這三個系統不要各做一套互不相干的 tags。
應盡量共享一個輕量 topic vocabulary。
例如：
signature
可以同時被：
- review 提到；
- Momo 發文；
- Jill 宣傳；
- ordinary guests 因此點單；
- Restaurant Records 記錄；
- future NPC callback 使用。
避免：
ReviewSystem 用 dessert_good
SocialSystem 用 sweetTrend
Ads 用 campaignFood2
最後彼此對不起來。
31. 社群只能「放大」真實故事
HARD RULE：
Social media cannot invent history.

不能憑空發：
「五隻貓今天一起睡！」

除非真的發生。
不能發：
「新 Signature 大受歡迎！」

除非真的有足夠 sales / reactions。
不能發：
「Sophie 帶了貓用品！」

除非她真的完成該事件。
社群的功能是：
放大世界裡真的發生的事情。

32. Life Album / Reviews / Social / Records 的角色分工
不要四套都顯示同樣內容。
Life Album
私人記憶。
那天長什麼樣。

Reviews
客人的記憶。
那頓飯感覺如何。

Social
公共談論。
最近大家在談什麼。

Restaurant Records
店的歷史。
Jill’s Kitchen 發生過什麼重要事情。

四者應該可以引用同一個真實 event/fact，但呈現不同角度。
33. 員工故事
《第一天》
新員工不要第一天就像做十年。
前幾班可以有：
- 找錯工作站；
- 問東西在哪；
- 老員工指路；
- staff meal 被叫過去。
幾天後自然消失。
沒有 veteran staff 時由 Jill 帶。
不要造成效率嚴重懲罰。
主要是生活感。
34. 資深員工
《第二層左邊》
資深員工除了 level 之外，也應有生活上的成熟感。
例如 Jill rush 中找東西。
阿珠姐：
「第二層左邊。」

甚至不用回頭。
之後可形成非常小的 veteran bonus。
不是新的 skill tree。
是：
她真的在這裡做久了。

35. 員工餐變成故事載體
既有 staff meal 可以產生 character-specific fragments。
例如 Nina：
「你今天是不是把我的甜點吃掉了？」

Hugo：
「沒有。」

「盒子上寫 Nina。」

「我以為是口味。」

😂
很多天後如果兩人仍在職：
桌上出現兩份。
不用解釋。
36. 員工故事必須容忍解雇
不要寫：
Nina Chapter 3 必須 Hugo 在職

然後 Hugo 被解雇就永遠卡死。
每條需要多人故事的 beat 必須：
- 可以延後；
- 可以 timeout；
- 可以換成 fallback；
- 或根本只是 optional。
玩家管理員工的自由優先。
37. 五隻貓：家具自己長出故事
玩家買新貓家具後：
不要只是：
Cat Comfort +5

接下來數日讓五隻自己探索。
例如：
- 包包先睡；
- 小齁聞；
- 柔柔研究；
- 樾樾遠遠看；
- 寶寶暫時不理。
根據真實使用次數形成 preference。
於是某張床最後可能自然變成：
包包最常睡的地方。

不是 script 預先指定。
38. NPC × Cat familiarity
不要 meter。
至少實作幾組：
Sophie × 寶寶
完整 arc。
陳伯伯 × 樾樾
因為樾樾謹慎，必須慢。
第一次願意靠近：
「今天比較近喔。」

之後樾樾對陳伯伯稍微降低避讓。
Momo × 柔柔
容易拍到柔柔的自然怪行為。
周董 × 包包
包包睡他附近。
周董本來要走，卻繼續坐。
Jill：
「你不是有事？」

周董：
「牠在睡。」

39. 餐廳 upgrade 也必須進入歷史
如果 NPC 親歷：
- 停電；
- 舊空調；
- 舊 Side Hall；
- 舊燈；
- 擴建前；
- 戶外區之前；
之後 upgrade，可以有 callback。
例如真正經歷停電的人：
「最近沒再停電了吧？」

Jill：
「不要講。」

讓 upgrade 從數值變成餐廳歷史。
40. Milestone
《好像真的開起來了》
重要 revenue / restaurant maturity milestone 不要只有 achievement。
打烊後。
如果 Dylan 合理在場：
Jill：
「欸。」

Dylan：
「嗯？」

「你看。」

Dylan 看帳。
「……妳以前第一天賺多少？」

Jill：
「不要問。」

如果 Dylan 不在：
可以由實際在職最久員工使用另一版本。
Album 不拍帳目。
拍：
打烊後還亮著燈的餐廳。

標題：
好像真的開起來了

41. Dylan HARD RULES
【2026-09-30】S11：Jill × Dylan 是關係生態裡的「長期的愛」對照組；reveal 後他可以偶爾注意到別人的關係（「她們是不是——」／「不要管人家。」），
但不全知、不介入、不替別人的關係當旁白。
Dylan 從 Day 1 就是 Jill 的丈夫。
不是陌生人。
不是 dating candidate。
玩家早期不知道而已。
Reveal 前：
「這個客人怎麼熟得不太正常？」

Reveal：
Jill：
「老公，走了。」

Dylan：
「好。」

Reveal 後：
Dylan 仍然會：
- 來店；
- 追 Jill；
- 撩 Jill；
- 被 Jill 拒絕／吐槽；
- 跟熟客互動；
- 被貓當家人。
不要：
- affection meter；
- dating；
- confession quest；
- Dylan 變員工；
- reveal 後降低存在感。
核心：
Dylan 沒有假裝愛 Jill。
他假裝的只有自己還沒追到她。

42. Story crossover 是重點，不要做平行鐵路
不要：
Sophie Story
Ken Story
Momo Story
老饕 Story
彼此完全不碰。
應該：
Sophie 評甜點
→ 老饕注意
→ Jill 試作
→ Momo 發文
→ 新客來點
→ 評論家後來也吃
→ 社群開始談 Signature
→ 玩家選擇是否宣傳
→ demand 真的變化。
同一件事情可以在不同人的人生裡留下不同痕跡。
43. 故事與經營必須雙向
不是只有：
Story → gameplay。

也要：
Gameplay → story。

例如玩家自己投 Signature campaign：
→ demand 增加
→ 備料不足
→ 售罄
→ 某客人沒吃到
→ 留評論
→ 下次真的吃到
→ review recovery。
這不是預先寫好的固定故事。
是 simulation 自己產生故事。
44. Save / migration 是 P0
v2.2.1 已經抓到過真實存檔 migration exception 導致 Day 35 變 Day 1 的嚴重問題。
v2.3 不准重演。
所有新增 story/social/wine/marketing state：
- 必須有 defaults；
- missing fields safe；
- legacy saves safe；
- malformed optional state safe；
- migration idempotent；
- migration 不得在核心 load 完成前因 optional story data crash；
- 不得 reset day/money/staff/menu/album/regulars。
45. 用真實成熟存檔測 migration
不要只測 synthetic fixture。
至少測：
- fresh game；
- early game；
- mid game；
- Day 30 real save；
- Day 35 real save；
- v2.2.1 mature save。
驗證：
load → play → save → reload。
核心 state 必須一致。
46. RNG / deterministic testing
Story eligibility 可以使用 RNG，但測試不能因此完全不可重現。
沿用目前 seeded/manual simulation 架構。
需要能回答：
為什麼這一天這個事件 eligible？
為什麼沒發生？
哪個 major event 被選中？
哪個因 cooldown 被擋？

但不要把 debug UI 放給一般玩家。
47. 不要讓測試誤把「有呼叫函式」當成「玩家真的看到」
沿用 I / T / O distinction。
I
Implemented。
T
Targeted automated/simulated verification。
O
Observed in normal real play。
Claude/Fable 不得把 headless / simulated touch / seeded test 寫成 O。
真 iPhone 項目保留給玩家實測。
48. Story regression tests
至少覆蓋：
- story beat 不重複 consequence；
- save/reload 不重送禮；
- Sophie gift 只出現一次；
- BaoBao 不在場時不演她在場；
- 五貓照片必須五貓；
- NPC 不知道未親歷事件；
- solo Wang 不破壞 couple history；
- Dylan reveal state 不被 story engine reset；
- dismissed employee 不造成 story crash；
- social post 不引用不存在照片；
- review 不引用未吃料理；
- campaign demand 正確開始／結束；
- expired trend 不永久污染 demand；
- wine unlock 不重複扣錢；
- legacy Signature 不被 relock；
- old saves load；
- Album references valid entities；
- story major-event arbitration 正常；
- same story 不因 reload 同日重播。
49. 不要過度測試 presentation pixel
需要更新 golden 的地方可以更新。
但不要再次把大量時間花在：
- 1px brightness；
- hair alpha；
- insignificant antialiasing；
- 完全不影響 gameplay 的 pixel diff。
優先測：
state correctness > story correctness > save correctness > gameplay consequence > readable UI > pixel perfection
50. UI 原則
不要新增五個永久大按鈕把主畫面塞爆。
Social / Reviews / Marketing 可以合理整合到既有：
- Journal；
- Records；
- management；
- phone-like panel；
- settlement；
- planning UI。
請先稽核目前 navigation。
不要因為新增三個系統就新增三個永遠佔空間的大 tab。
手機 390px 實際可讀性優先。
51. 玩家操作量
這版新增很多「內容」，但不應新增很多「工作」。
不要要求玩家：
- 每天發社群；
- 每桌選 pairing；
- 每杯倒酒；
- 每篇評論回覆；
- 每天調廣告；
- 管 followers；
- 管 NPC 關係；
- 管貓好感；
- 管 story quest。
玩家仍然主要經營餐廳。
故事與社群大部分是：
觀察、選擇、偶爾介入。

52. v2.3 第一階段內容量
第一版不要追求 300 events。
目標：
- 約 15–20 條真正有 progression 的 story arcs；
- 約 30–50 個 minor callback / crossover；
- 至少 5 個永久世界痕跡；
- 至少 5 個會改變某天營業的 story event；
- 至少 5 組 NPC ↔ NPC relationships；
- 至少 5 組 NPC ↔ cat familiarity；
- Reviews 2.0；
- Social；
- lightweight Marketing；
- Ken → wine → Lounge 起源線（Class A；Lounge 本身依第 53 節 Phase E–F）；
- Life Album / Records integration。
品質優先於事件數量。
53. 開發順序
【2026-09-30 reconciled】Phase A–D 不變；原 Phase E「Wine」由 Lounge 分期（addendum L41）取代；原 Phase F「Remaining story
arcs」與 Phase G「Crossovers」併入下面的 G 與 I。這個順序可以在 architecture audit 之後調整，但不得從 brief 直接跳到「build
complete Lounge」。
不要一次同時改全部。
Phase 0 — Architecture audit only（見「開始方式」；NO CODE until the audit is reviewed）。
Phase A — Foundation
先做：
- fact / memory extension；
- story state；
- event arbiter；
- migration；
- idempotent consequences；
- debug/evidence tooling；
- generic familiarity behavior（L19）。
先不要大量寫故事。
用 2 條 vertical slice 驗證架構：
1. Sophie × 寶寶；
2. 一個簡單 infrastructure callback。
確認：
story → save → reload → future callback → Album / object
整條正常。
Phase B — Reviews 2.0
先讓 review 真正基於 guest experience。
不要先做 social。
確認：
experience → review topic → repeat visit callback
成立。
Phase C — Social
讓 Social 消費：
- real events；
- real photos；
- review topics；
- real dishes。
確認不 invent history。
Phase D — Marketing
Marketing 只改：
- arrival composition；
- ordering weights；
- seating/group tendencies；
- temporary topic interest。
不要直接生成 revenue。
確認：
campaign → real guests → real experience → real reviews
完整閉環。
Phase E — Lounge foundation
- room shell；
- room transition；
- staffing destination；
- bartender role；
- shared kitchen Bar Food routing；
- minimal drinks；
- save migration；
- NO giant story pack yet。
Phase F — Lounge I playable vertical slice
- Evan；
- one existing FOH supporting；
- small Lounge；
- waiting transition；
- small Bar Food menu；
- Ken / Monsieur 杜 interaction（第 20 節 Beat 8）；
- Dylan / Evan small interaction；
- staff familiarity；
- real-save smoke。
Phase G — Lounge expansion / staff，以及其餘 story arcs
- 晴；
- 安安；
- Lounge II；
- broader existing-staff familiarity；
- relationship events；
- 架構穩定後再加入其他 NPC stories（原 Phase F）：故事內容應主要 data-driven，不要每加一條就修改 simulation 核心。
Phase H — Optional Bar Food specialization
- 阿拓；
- kitchen load consequences；
- optional Bar Pantry / Fry Station；
- Lounge III if justified。
Phase I — Crossovers / romance-authorized arcs / long-delay callbacks / polish
最後才大量加入：
- Sophie × Momo；
- Ken × Monsieur 杜（Lounge 常客化）；
- 王先生王太太 × Dylan/Jill；
- Momo × cats；
- regular × infrastructure；
- staff × staff；
- review × social；
- campaign × review。
這樣比較不容易一開始就 spaghetti。
54. Commit / checkpoint 策略
不要一個 8 小時巨大 commit。
至少按 phase 留可回退 checkpoint。
每一階段：
1. implementation；
2. targeted tests；
3. save/load；
4. short smoke；
5. commit；
6. 再進下一 phase。
任何新 phase 發生重大 regression，可以回退到上一個乾淨 checkpoint。
不得動 v2.2.1 tag。
55. 不要重寫目前 simulation
HARD RULE。
除非先提出具體 root cause，否則不要：
- 重寫 customer engine；
- 重寫 cat AI；
- 重寫 staff engine；
- 重寫 save format；
- 重寫 menu system；
- 重寫 Life Album；
- 重寫 Dylan；
- 重寫 regular history。
v2.3 應該像：
在現在這間活著的餐廳上建立記憶。

不是拆掉餐廳重蓋。
56. Performance
Story eligibility 不應每 frame 掃描所有 story arcs。
Story evaluation 應主要發生在合理節點：
- day start；
- guest arrival；
- seating；
- meal completion；
- special interaction；
- closing；
- settlement；
- upgrade completion；
- campaign completion。
不要每 animation frame evaluate 50 條故事。
57. 玩家看不到的 debug evidence
開發時可以保留結構化 evidence，例如：
某日：
- eligible major events；
- selected event；
- rejected reason；
- required NPC presence；
- memory facts；
- consequence；
- social topic；
- campaign source；
- review source facts。
這是為 QA。
不要讓玩家正常 UI 看到：
storyArc=sophieCat stage=3 eligibility=.82
😂
58. 成功標準
v2.3 完成後，玩家玩到 Day 50–100 應該能自然回答：
Sophie 是怎樣的人？
她跟哪隻貓有特別關係？
那個貓用品哪裡來的？
周董其實喜歡吃什麼？
王先生王太太是不是永遠一起來？
Ken 為什麼跟酒單有關？
Jill’s Kitchen 為什麼開始賣酒？
第二道 Signature 怎麼變成這間店的招牌？
哪個員工待最久？
哪個客人親歷過以前那次停電？
最近大家為什麼突然一直點某道菜？
那篇評論為什麼讓店裡突然多很多新客？
那張「打烊以後」照片是什麼時候拍的？
Dylan 為什麼還在追自己的老婆？

玩家應該知道答案。
但不是因為他讀過 Character Encyclopedia。
而是：
他真的在 Jill’s Kitchen 裡看過這些事情發生。

59. 最終產品感受
這個版本最重要的不是讓玩家說：
「哇，事件好多。」

而是：
「欸，Sophie 今天居然在找寶寶。」

「幹，小琪那篇害我布丁真的賣完。」

「周董不是說隨便嗎？」

「這個檢查員今天居然真的只是來吃飯。」

「原來那盆植物是 Madame Lin 以前送的。」

「Ken 當初只是嫌沒有酒，結果現在真的有一整個酒櫃。」

「這個員工居然已經在這裡這麼久了。」

「以前這邊真的沒有側廳。」

這才是 v2.3。
60. 最後一條最高優先原則
Do not write stories that merely happen in Jill’s Kitchen.
Write stories that become part of Jill’s Kitchen.

故事發生過以後，最好能留下：
一件東西、一道菜、一個習慣、一段關係、一篇評論、一張照片、一個座位偏好、一種客群、一個未來 callback，或者一個只有這個存檔才有的歷史。
最後每個玩家的 Jill’s Kitchen 都應該有一點不同。
不是因為 RNG 給了不同家具。
而是因為：
他們的餐廳真的經歷過不同的日子。

開始方式
收到這份 brief 後：
不要立刻修改 source。
先：
1. audit v2.2.1 現有 architecture；
2. 指出哪些既有系統可以直接 reuse；
3. 提出最小新增 state；
4. 列出 migration strategy；
5. 列出 event arbitration strategy；
6. 列出 Sophie × 寶寶 vertical slice 的完整資料流；
7. 列出 Reviews → Social → Marketing 的共享 topic/data flow；
8. 說明如何避免 duplicate consequence / reload replay / omniscient NPC；
9. 提出分 phase implementation plan；
10. 指出你認為這份 brief 中任何會與目前 codebase 衝突或造成高 regression risk 的地方。
11. （addendum Phase 0）report the current room model、customer location/state model、ticket identity model、staff
    assignment model、kitchen/ticket routing、event scheduler、Regular History / World Memory、save schema/migration、
    Album capture architecture、review/social architecture；
12. how the Lounge can be added with minimum duplication（一間餐廳，不是兩個遊戲：L2）、likely regression risks、
    recommended implementation boundaries；
13. 提出 station familiarity / wine familiarity 的最小表示與 UI 命名（L15–L17），以及 event lanes / overdue bonus 的
    arbiter 參數位置（L20–L22）。
14. （S21）說明現有系統如何安全支撐：persistent Relationship Facts、familiarity、authored romantic eligibility、staff
    employment dependencies、event weighting、overdue catch-up、room transitions、story event budget、special Life Album
    illustration unlocks、save migration、mature-save compatibility。不建 generic romance engine／dating simulator／N×N romance matrix。

第二部：Lounge 擴建、員工成長與關係空間（Addendum 2026-09-30，原文 docs/v23/addendum_2026-09-30_lounge_expansion.txt）
本部是 docs/V23_BRIEF.md 的 DESIGN / ARCHITECTURE ADDENDUM。DO NOT IMPLEMENT THIS NOW；v2.3 仍以 architecture audit 開始（Phase 0），
且要等明確授權。The Lounge is now a major v2.3 direction, but it must be integrated into the existing Jill’s Kitchen
simulation rather than becoming a second independent game. 與第 20 節（起源線）一起讀。

L1. PRODUCT VISION
Jill’s Kitchen eventually grows beyond a restaurant with additional dining rooms.

It develops a connected evening Lounge / wine bar.

The conceptual distinction is:

Main Hall:
“吃飯”
high service density / primary dining / turnover

Side Hall:
“聚餐”
groups / comfort / longer meals

Lounge:
“留下來”
lower turnover / higher average spend / higher social density / relationship development

The Lounge should feel like Jill’s Kitchen growing another layer of life at night.

It is NOT:
- a nightclub
- a sports bar
- a separate business
- a second restaurant simulation
- a cocktail minigame
- a wine inventory simulator
- a dating simulator
- a new F2P management layer
- an excuse to replace existing characters with new characters

Core fantasy:

During dinner, Jill runs a restaurant.

Later in the evening, some people do not immediately leave.

They move to the Lounge.
They sit longer.
People who used to merely recognize one another begin talking.
Staff begin remembering customers.
Customers begin remembering staff.
Separate regulars slowly become part of one another’s lives.

The Lounge is a physical place where the existing v2.3 relationship-memory system becomes visible.

Core line:

「主廳是吃飯，側廳是聚餐，酒吧是留下來。」

And:

「這些人本來不是一群朋友，是這間餐廳讓他們慢慢認識。」

L2. HARD ARCHITECTURAL RULE: ONE RESTAURANT, NOT TWO GAMES
The Lounge MUST remain inside the existing Jill’s Kitchen restaurant simulation.

Do NOT create:
- a second game loop
- a separate save
- a separate customer universe
- a duplicate staff system
- a duplicate relationship system
- a duplicate review system
- a duplicate event scheduler
- a duplicate economy
- a duplicate inventory system
- a duplicate clock
- a duplicate customer AI framework

Reuse the existing systems whenever safe:

- restaurant clock
- customer identity
- regular history
- World Memory
- Relationship Facts
- staff roster
- staff assignment board
- kitchen
- tickets
- economy
- Reviews 2.0
- Social
- Marketing
- Life Album
- Restaurant Records
- Story Event Arbiter

The Lounge is primarily:

NEW SPACE
+ NEW SERVICE TYPE
+ NEW STAFF SPECIALTY
+ NEW MENU CATEGORY
+ NEW SEATING BEHAVIOR
+ NEW SOCIAL/RELATIONSHIP OPPORTUNITIES

It is NOT a parallel simulation.

Conceptually a guest may have:

location = MAIN / SIDE / LOUNGE / WAITING / LEAVING

and can transition safely between spaces.

Do not implement this exact enum if current architecture suggests a safer representation.
Audit first.

L3. VISUAL DIRECTION
Working identity:

Jill’s Kitchen — Lounge

The Lounge must visually belong to the same restaurant.

It should NOT suddenly become:
- black nightclub walls
- neon purple LEDs
- loud nightclub design
- generic American pub
- sports-bar TVs
- overly masculine whiskey den
- wall-to-wall alcohol bottles
- casino-like luxury
- another copy of Main Hall

Visual direction:

warm contemporary Taipei hospitality
+
quiet wine lounge
+
residential warmth

Palette should extend the mature Jill’s Kitchen palette:

- ivory
- cream
- oatmeal
- beige
- greige
- taupe
- natural warm wood
- warm stone
- restrained charcoal
- small brass details
- plant green
- warm amber lighting

Lighting:
lower and warmer than Main Hall,
but NEVER so dark that NPC faces, food, cats, or social interactions become hard to read on phone.

The player must still be able to visually understand:
- who is sitting with whom
- who is waiting for someone
- which staff member is serving
- where Jill is
- where Dylan is
- which cat entered the Lounge
- what social event is occurring

Do not sacrifice gameplay readability for mood.

The Lounge should communicate:

“It is still Jill’s restaurant. It is simply later now.”

L4. EXPANDABLE LOUNGE
Do not give the player the final Lounge immediately.

It should physically grow with the restaurant.

Exact prices and capacities must be balance-audited before implementation.
The following numbers are design targets, not immutable constants.

------------------------------
LOUNGE I — SMALL BAR
------------------------------

A mature restaurant story unlock introduces the possibility.

Approximate spatial identity:
- real bar counter
- ~6 bar seats
- ~2–3 small lounge tables
- compact wine storage
- basic glassware
- warm lighting
- small Bar Food menu

This should feel like Jill has opened a small new evening space.

Minimum viable staffing:
- 1 trained bartender
- 1 FOH support person
- shared Main Kitchen

No second kitchen.

------------------------------
LOUNGE II — BAR LOUNGE
------------------------------

Physical expansion:
- longer bar
- more seating
- ~5–6 table/lounge groups depending on actual layout
- improved wine display/storage
- better lighting
- some sofa/lounge seating
- stronger evening identity
- increased social event eligibility

Staffing naturally grows:
- 1–2 bartenders
- 1–2 Lounge-capable FOH
- Main Kitchen still shared

This is where the Lounge begins to feel like a real second social environment inside the same restaurant.

------------------------------
LOUNGE III — MATURE LOUNGE
------------------------------

Late-game money sink and spatial transformation.

Possible physical elements:
- mature bar counter
- richer wine display
- premium seating
- sofa grouping
- quiet conversation corner
- better glassware/service equipment
- atmospheric lighting
- optional Bar Pantry / Fry Station

IMPORTANT:

Lounge III must not simply increase table count.

Different seating areas should support different social behavior.

BAR COUNTER:
strangers / regulars / bartender conversations

SMALL TABLE:
friends / couples / quiet conversations

SOFA / GROUP AREA:
small social clusters

QUIET CORNER:
low-frequency intimate or reflective story moments

Space itself should help tell stories.

L5. THE LOUNGE IS ALSO A WAITING SPACE
One practical gameplay benefit:

When Main Hall / Side Hall is full, some eligible guests may choose:

“先到 Lounge 等桌”

instead of standing in a normal queue.

They may:
- sit at the bar
- order a drink
- wait naturally
- move to Main/Side when their table becomes available

This must NOT create duplicate customers or duplicate tickets.

The SAME guest entity transitions spaces.

Potential flow:

ARRIVE
→ WAITING
→ LOUNGE
→ MAIN/SIDE
→ optional LOUNGE after dinner
→ LEAVE

But do not force every guest through this.

Some guests:
- do not drink
- do not want to wait
- prefer direct dining
- may leave normally

The Lounge should improve restaurant flow without becoming mandatory.

L6. EVENING FLOW
The Lounge should create a visible change in restaurant rhythm.

Approximate conceptual flow:

early dinner:
Main/Side dominant

later dinner:
Lounge becomes increasingly active

late evening:
Main Hall gradually empties
while a smaller number of guests remain in Lounge

Do NOT hard-code rigid time behavior without auditing the current service clock.

The desired player feeling is:

“The restaurant has a second half of the night.”

This allows relationship scenes that would feel unnatural during peak table turnover.

L7. BAR FOOD
The Lounge gets a SHORT dedicated Bar Food menu.

Do NOT copy the full restaurant menu.

Possible categories:

- truffle fries
- fried chicken / seasoned chicken bites
- fried seafood
- croquette
- mushrooms / warm small plate
- cheese / charcuterie-style small plate
- simple dessert
- one Jill’s Kitchen Signature Bar Bite

Exact dishes should fit existing ingredient/art architecture.

Bar Food is primarily:
- shareable
- quick
- suited to drinks
- visually distinct from full dinner plates

L8. HARD RULE: SHARED KITCHEN FIRST
Bar I and Bar II MUST use the existing Main Kitchen.

Example Lounge ticket:

LOUNGE TABLE 3
Sparkling ×2
Truffle Fries ×1
Fried Chicken ×1

Drinks:
→ Bartender workflow

Food:
→ existing Main Kitchen ticket workflow

Completed food:
→ Lounge Server / Runner delivers to Lounge

Do NOT create a second full kitchen.

Do NOT create a second ingredient inventory.

Do NOT create a second prep system.

Do NOT create a second refrigerator economy.

Reuse existing ingredients whenever sensible.

The interesting consequence is:

A successful Lounge increases Main Kitchen demand.

This creates a real management tradeoff.

The player may respond by:
1. assigning more existing kitchen staff
2. improving staff familiarity with Bar Food
3. later hiring a specialist
4. eventually purchasing a small Bar Pantry/Fry Station

L9. OPTIONAL LATE-GAME BAR PANTRY
Only after Lounge demand becomes substantial should the player be offered:

Bar Pantry / Fry Station

This is NOT a second kitchen.

It can finish only limited Bar Food such as:
- fries
- fried chicken
- croquette
- cold plates
- simple dessert finishing

It cannot produce:
- full restaurant entrées
- Signature main dishes
- complex Main Kitchen recipes

Purpose:
- reduce Main Kitchen pressure
- provide visible late-game infrastructure
- create a meaningful money sink
- make a Bar Food specialist valuable

It should be optional.

The player should first FEEL the operational reason before being asked to buy it.

L10. WINE / DRINK ARCHITECTURE
Do not turn wine into a 25-SKU inventory simulator.

Initial conceptual wine styles:

- sparkling
- crisp white
- fuller white
- light red
- full red

Individual fictional wine names may be used for presentation.

Underlying gameplay should rely on a small stable style vocabulary.

Do NOT require the player to restock every bottle manually in v2.3.

Drink cost can be represented operationally through cost-of-goods rather than another daily inventory burden.

The Lounge should increase:
- average spend
- pairing possibilities
- evening identity
- character interactions
- story possibilities

It should NOT increase repetitive clicking.

L11. NO PER-TABLE WINE MICROMANAGEMENT
Never require:

guest orders dish
→ popup asks player to choose wine
→ repeat 50 times

Normal wine service should be largely automated through staff and guest preference.

Player decisions should occur at higher-value moments:

- which wines/styles to offer
- Lounge investment
- special tasting night
- authored pairing story choices
- menu/pairing strategy
- staff assignment

80% flow.
20% hand-feel.

L12. CORE NEW STAFF
New staff exist only because the restaurant has developed new professional needs.

Do NOT generate a large new roster.

Existing staff remain important.

Approved new core characters:

--------------------------------
EVAN 林奕文 — 32
HEAD BARTENDER
--------------------------------

Role:
Lounge’s first major bartender / eventual Head Bartender.

Personality:
- quiet
- stable
- observant
- dry humor
- professionally mature
- remembers people extremely well
- does not expose people merely because he understands them

Core character principle:

「記得很多，但不會因為知道很多就一直講。」

Background:
Previously worked in a more formal hotel/bar environment.

He became interested in Jill’s Kitchen because it is a place where:
- customers know Jill
- customers know the cats
- regulars recognize one another
- people have history

He prefers this human continuity to treating customers like anonymous table numbers.

Possible interview:

Jill:
「我們現在其實還沒有很多酒。」

Evan:
「我有看到。」

Jill:
「那你還來？」

Evan:
「所以才有工作。」

Long-term role:
He gradually becomes one of the witnesses to the Lounge’s social history.

He may know:
- Ken and Monsieur Du’s habits
- Zhou’s fake “隨便”
- Sophie’s preferred quiet seating
- Dylan’s tendency to wait for Jill
- which regulars used to arrive separately but now sit together

HARD MEMORY RULE:
Evan does NOT know events from before he was hired unless he later learns them through a valid event.

No omniscience.

Visual:
Use the approved concept direction.
He must be visually very distinct from 阿拓.
Do not let male NPC procedural art converge into the same face.

--------------------------------
沈晴 — 27
BARTENDER
--------------------------------

Role:
Second bartender, primarily needed as Lounge expands.

Personality:
- professional
- quick
- perceptive
- verbally fast
- playful but not childish
- good at handling customers who do not know what they want

Contrast:

Evan:
understands and often says nothing.

晴:
understands and may say one sentence too much.

Possible interaction:

周董:
「隨便。」

晴:
「不行。」

周董:
「？」

晴:
「你看起來就不是可以隨便的人。」

She should develop relationships with:
- 小琪
- Momo
- Mia
- Zhou
- existing staff
- eventually other Lounge regulars

Do NOT write her as:
- ditzy
- loud
- gossip machine
- generic cute bartender

She is competent.

Visual:
Use approved concept direction.
She must be immediately distinguishable from 安安.

--------------------------------
阿拓 — 29
BAR FOOD / KITCHEN SPECIALIST
--------------------------------

IMPORTANT:
He is NOT required when Lounge first opens.

He becomes an optional hire when Lounge food demand becomes high enough that Main Kitchen pressure is noticeable.

Character concept:

He takes “food that people think is only a snack” extremely seriously.

Possible Jill exchange:

Jill:
「就薯條啊。」

阿拓:
「妳再說一次。」

Jill:
「……松露薯條。」

阿拓:
「好多了。」

Strengths:
- frying
- Bar Food
- timing
- small plates
- consistency

He is not a separate “Bar Chef class” requiring a new kitchen system.

Initially he works through the same kitchen architecture.

Potential relationship:
阿拓 × Hugo / existing kitchen staff

Early:
Hugo:
「看起來好了。」

阿拓:
「看起來跟好了是兩回事。」

Much later:
Hugo:
「再二十秒？」

阿拓:
「十八。」

Their work history should visibly develop.

Potential regular relationship:
老饕李先生

老饕:
「這個炸雞誰做的？」

Jill:
「阿拓。」

老饕:
「叫他不要改。」

Later:

阿拓:
「今天炸雞有。」

老饕:
「我又沒問。」

--------------------------------
安安 — 26
LOUNGE SERVER / HOST
--------------------------------

Role:
Dedicated Lounge floor specialist as Lounge grows.

She is NOT a wine expert.

Her strength is spatial/social awareness.

She becomes good at remembering:
- seating
- who is waiting
- who prefers which area
- which table will transfer to Main Hall
- which guests tend to sit together
- who is probably waiting for someone

Early:

Ken:
「杜來了嗎？」

安安:
「杜先生？」

Ken:
「……算了。」

Much later:

Ken enters.

安安:
「他還沒來。」

Ken:
「我又沒問。」

安安:
「你每次都問。」

Gameplay role:
- Lounge seating
- table transition
- waiting guests
- bar-food delivery
- regular familiarity

Visual:
Use approved concept direction.
She must remain visually distinct from 晴.

L13. CHARACTER ART RULE
The approved concept direction intentionally makes the four new characters visually distinct.

Do NOT regress toward procedural lookalikes.

Particularly:

EVAN and 阿拓 must not share the same facial structure/hair silhouette.

晴 and 安安 must not look like sisters or palette-swapped versions of the same portrait.

Preserve:
- different silhouettes
- different face shapes
- different hair
- different body language
- different expression language
- different work posture

When integrating actual assets, use deterministic mapping by character ID.

Never assign portraits by array order if that could reproduce the previous Sophie/小林 mapping bug.

Named character → stable explicit portrait mapping.

L12a. 角色設定卡（approved concept direction）
圖：docs/v23/lounge_cast_concept.png（2026-09-30 收到；四張卡＋Lounge 場景）。以下是卡上的文字，作為角色與美術的依據；
整合真實 portrait 時依角色 ID 做 deterministic mapping（L13），不得按陣列順序。
Evan 林奕文 32 — 首席 Bartender
「我比較擅長記得人，而不是讓人過來忘記自己。」
背景：曾在國際飯店酒吧工作，喜歡真正認識客人的地方。
個性：安靜、觀察力強、乾幽默。
專長：調酒、熟客記憶、氣氛掌握。
關係：從觀察開始，慢慢成為這間店不可或缺的一部分。
場景句：「今天還是一樣？」「只是今天比較需要。」／「要不要先喝完再吵？」
晴 沈晴 27 — Bartender
「隨便？不行。你看起來就不是可以隨便的人。」
背景：在台北多間酒吧工作過，喜歡熱鬧，也喜歡觀察人。
個性：直率、反應快、很會接話、嘴快。
專長：調酒、應對新客、記住客人喜好。
關係：一開始覺得這群熟客很特別，後來發現自己也很喜歡這裡。
場景句：「你真的都可以？」／「好；那我真的隨便。」
阿拓 黃柘 29 — Bar Food 料理員
「炸物不是配角，是讓大家留下來的理由。」
背景：原本在餐酒館與小食專門店工作，對「一口就會記得的東西」有執念。
個性：認真、龜毛、但其實很好相處。
專長：炸物、小食、出餐 timing、簡單甜點。
關係：希望讓酒吧的小食有和主餐一樣的水準，也和廚房團隊建立了很好的默契。
場景句：「看起來好了？再二十秒。」／「薯條而已？」「妳再說一次。」
安安 26 — Lounge 服務生 / Host
「位置我幫你想好。主餐等一下，先喝一杯吧。」
背景：曾在精品酒店與餐廳服務，喜歡觀察人和安排空間。
個性：親切、細心、觀察力強、記性好。
專長：座位安排、熟客照顧、轉場服務。
關係：很快熟悉每個人的習慣，是酒吧不可或缺的節奏管理者。
場景句：「主廳還要十五分鐘，要不要先坐吧台？」／「他還沒來。」「我又沒問。」「你每次都問。」
場景圖（下方）：「Jill’s Kitchen Lounge」霓虹字、弧形吧台與高腳椅、小圓桌與沙發、植栽、暖琥珀光、一隻貓在沙發上；
標語 “Same people. New stories. A bigger table.” — 這就是 L3 視覺方向的參照：still Jill’s restaurant, simply later.

L14. EXISTING STAFF MUST NOT BECOME OBSOLETE
Opening the Lounge must NOT make existing staff useless.

Existing employees should be able to SUPPORT the Lounge where their existing skills logically transfer.

Examples:

existing FOH:
- can deliver food
- clear tables
- serve Lounge tables
- assist waiting/table transitions
- gradually learn basic wine service

existing kitchen:
- makes Bar Food
- gradually becomes familiar with Bar Food
- can be assigned additional capacity when Lounge demand is high

existing runner:
- can move food between Kitchen and Lounge

existing dishwasher infrastructure:
- remains shared where architecturally appropriate

BUT:

A general FOH employee should not instantly become a full bartender.

Bartending remains a meaningful specialty.

L15. STAFF GROWTH / STATION FAMILIARITY
Do NOT build a giant RPG skill tree.

Add only a lightweight concept of:

STATION FAMILIARITY

Conceptual examples:

MAIN
SIDE
LOUNGE
KITCHEN

Possible hidden/simple levels:

NEW
FAMILIAR
EXPERIENCED

Exact naming/UI should be proposed during architecture audit.

Important principle:

Existing general competence TRANSFERS.

An experienced Main Hall server entering Lounge for the first time does NOT become incompetent.

They already know:
- carrying
- service
- guest interaction
- clearing
- restaurant rhythm

They initially lack:
- Lounge layout knowledge
- wine location
- Lounge table numbers
- bar workflow
- regular drink habits
- Lounge-specific transitions

Therefore:

first Lounge shifts:
slightly slower / needs occasional help

after repeated real shifts:
becomes comfortable

later:
can train/help newer staff

Example:

First Lounge shift:

阿哲:
「這杯是哪桌？」

Evan:
「三號。」

阿哲 walks away, returns.

「三號是哪邊？」

Much later:

new employee:
「三號在哪？」

阿哲:
「靠牆第二桌。」

This is the desired feeling.

L16. WINE FAMILIARITY
A similarly lightweight transferable competency may exist:

NONE
BASIC
COMFORTABLE

Do NOT expose it as an RPG XP grind unless necessary.

Basic:
- correctly delivers drinks
- understands basic wine styles
- fewer simple service mistakes

Comfortable:
- can answer simple guest questions
- remembers familiar customers’ usual drinks
- can handle basic wine-table service without bartender intervention

BUT:

FOH staff should never completely replace a trained bartender.

Bartender specialty remains valuable.

Likewise:

Bartenders may gradually learn Main/Side Hall service if assigned there.

People can learn.

They are not immutable job cards.

L17. LONG-TERM STAFF VALUE
The desired late-game feeling:

A staff member who joined early may eventually be useful in several spaces.

The player should naturally think:

「這個人哪裡都能頂。」

That creates attachment to veteran employees.

Do NOT reduce this to:

STR +7
DEX +4

Represent it through:
- reliable behavior
- station familiarity
- remembered customers
- contextual dialogue
- service autonomy
- veteran/new employee interactions

Possible staff card history:

阿哲
在店 47 天
熟悉：主廳、側廳
正在熟悉：Lounge

Nina
在店 62 天
熟悉：主廳、Lounge
remembers Momo’s presentation habits

Hugo
在店 80 天
Kitchen veteran
Bar Food: experienced

Do not implement these exact labels without UI audit.
The concept matters more than literal text.

L18. RELATIONSHIP ARCHITECTURE IN THE LOUNGE
The Lounge MUST use the same Relationship Facts architecture described elsewhere in v2.3.

Do NOT create:

LoungeRelationshipManager

Do NOT create a second friendship graph.

Use shared facts such as:

met
recognizes
knowsName
repeatedCoPresence
hasSpoken
sharedTable
sharedDrink
sharedFood
sharedEvent
recognizesHabit
comfortableSittingTogether
noticesAbsence
knowsStaffRole
remembersPastService
usualSeat
usualDrink

Facts must come from REAL events.

No omniscience.

No progression solely because the calendar advanced.

L19. RELATIONSHIP PROGRESSION MUST NOT DEADLOCK
CRITICAL ARCHITECTURAL RULE.

Do NOT build long prerequisite chains such as:

met 4 times
→ greeting
→ shared table
→ event X
→ event Y
→ only then relationship progresses

This is highly vulnerable to deadlock.

Instead:

FACTS
→ coarse familiarity state
→ unlock broader behavior pools
→ authored story beats become eligible

Conceptual hidden familiarity:

0 stranger
1 recognize
2 familiar
3 comfortable

Do NOT show a relationship meter to the player.

Facts may promote familiarity.

Example:

repeated co-presence
→ recognize

meaningful interaction
→ familiar

shared table / repeated shared events
→ comfortable

Familiarity should generally unlock BEHAVIOR, not a single mandatory “next chapter.”

Example:

Sophie × Mia at recognize:
- glance
- greeting
- acknowledge departure

familiar:
- short conversation
- knows name
- comments on usual order
- accepts shared seating

comfortable:
- voluntarily sits nearby/together
- notices absence
- introduces to another person
- participates in multi-character story beats

No single behavior should become a mandatory progression key unless absolutely narratively required.

L20. ELIGIBILITY WEIGHTS, NOT GIANT PREREQUISITE CHAINS
Use HARD requirements only for things that must logically be true.

Examples:
- required characters are actually present
- required staff still employed
- required cat is actually in a reasonable location
- post-reveal Dylan dialogue only after reveal
- a character cannot remember an event they never witnessed

Other conditions should generally influence event WEIGHT.

Conceptual example:

Sophie × Mia Lounge conversation

base weight
+ repeated co-presence
+ knows name
+ shared seating history
+ long time since last interaction
+ same room
- heavy rush
- another major event

Do not copy these literal numbers.
Use the architecture audit to propose safe implementation.

L21. SOFT CATCH-UP / OVERDUE BONUS
Important authored relationships must not remain frozen forever because RNG was unlucky.

If an event has been valid repeatedly but not selected, gradually increase its priority/weight.

Conceptually:

eligible 1–2 times:
normal

eligible repeatedly:
increasing weight

long-overdue important beat:
high priority when a natural window exists

This must NOT force absurd scenes.

It simply prevents:

Day100 and Ken/Monsieur Du still behave like strangers despite 20 genuine co-presences.

Critical arcs may use stronger catch-up windows.

Emergent moments do NOT need guaranteed catch-up.

L22. THREE EVENT LANES
Do not let every tiny greeting compete with a major story beat.

Use the SAME Story Event Arbiter but distinguish conceptual event weight/budget:

MAJOR
0–1/day normally

Examples:
- major Lounge opening
- Signature story beat
- tasting night
- meaningful relationship turning point
- major reviewer/social event

MINOR
limited small number/day

Examples:
- notices absence
- first meaningful conversation
- bartender/customer callback
- shared food interaction

AMBIENT
lightweight behavior

Examples:
- greeting
- glance
- sitting nearby
- bartender places usual glass
- customer moves bag to free a familiar seat
- staff recognizes usual order

Ambient behavior must not block a major story.

Do not create:

“Sophie said hello, therefore Dylan reveal was postponed.”

L23. PRESENTATION FALLBACKS
Story meaning should not depend on one fragile physical condition.

Example:

A relationship needs a meaningful interaction.

Ideal presentation:
restaurant crowded → Jill asks two regulars to share a table.

But if the player runs a spacious restaurant and crowding never occurs, their relationship must not freeze forever.

Alternative presentation:
one character stops at the other’s table for a conversation.

Same meaningful relationship fact.
Different presentation.

Rule:

STORY MEANING MAY BE STABLE.
PRESENTATION MAY HAVE SAFE FALLBACKS.

Do not fake character presence.

Do not teleport characters merely to satisfy a story.

Delay when required.
Fallback when equivalent.
Skip optional crossover when neither is natural.

L24. THE LOUNGE ACCELERATES SOCIAL OPPORTUNITY IT DOES NOT GENERATE FRIENDSHIP AUTOMATICALLY
Being in the Lounge may increase probability of:
- longer conversation
- shared seating
- sharing Bar Food
- bartender interaction
- noticing familiar people
- remaining after dinner

But:

Lounge presence ≠ friendship.

Repeated actual history is still required.

L25. AUTHORED LOUNGE RELATIONSHIP EXAMPLES
【2026-09-30】第三部把其中幾組寫深：Sophie × Mia（S6，八個 phase）、Ken × 杜（S5，deep friendship，不是戀愛）、Evan（S4）、
晴 × 阿拓（S9，新的 optional 員工線）、Jill × Dylan 與王家作為對照（S11、S12）。
These are tone/content targets.
Do not hard-code every scene into a linear quest chain.

--------------------------------
SOPHIE × MIA
--------------------------------

Their familiarity may begin in the restaurant.

Later both independently use Lounge.

Mia:
「這裡有人嗎？」

Sophie:
「現在有了。」

Early:
they merely sit near one another.

Later:
they share fries or another small plate.

Much later:

Sophie arrives first.
Her bag is on the adjacent chair.

Mia enters.

Without dialogue, Sophie removes the bag.

This action is more valuable than a Friendship Level popup.

--------------------------------
KEN × MONSIEUR 杜
--------------------------------

They naturally become strong Lounge regulars.

They continue disagreeing about wine.

Over time they may develop preferred seats.

One night only Ken arrives.

Evan casually prepares two coasters.

Ken:
「他今天沒來。」

Evan:
「我沒問。」

Their relationship becomes meaningful when absence is noticed.

--------------------------------
老饕李先生 × 小琪
--------------------------------

小琪 orders fried chicken.

老饕:
「妳來這裡還吃這個？」

小琪:
「炸雞怎麼了？」

老饕:
「沒怎麼。」

Later he takes one.

小琪:
「你不是嫌？」

老饕:
「我沒有嫌。」

This can connect to their existing social/food-history relationship.

--------------------------------
DYLAN × EVAN
--------------------------------

Pre-reveal:

Dylan:
「Jill 今天有喝什麼嗎？」

Evan:
「你可以直接問她。」

Dylan:
「這樣就沒有參考價值了。」

Evan may gradually realize something is unusual.

Do NOT let Evan reveal the marriage.

After Dylan reveal, Evan does not necessarily need a huge shocked reaction.

A funny possibility is that the player realizes Evan had already suspected something.

--------------------------------
晴 × 周董
--------------------------------

周董:
「隨便。」

晴:
「不行。」

周董:
「？」

晴:
「你看起來就不是可以隨便的人。」

Later she learns what his “隨便” actually means.

--------------------------------
安安 × KEN
--------------------------------

Early:

Ken:
「杜來了嗎？」

安安:
「杜先生？」

Ken:
「……算了。」

Later:

Ken enters.

安安:
「他還沒來。」

Ken:
「我又沒問。」

安安:
「你每次都問。」

This demonstrates staff growth through remembered human behavior.

--------------------------------
阿拓 × HUGO
--------------------------------

Early:
professional disagreement about Bar Food timing.

Later:
wordless or near-wordless kitchen coordination.

Their relationship is created through work, not generic friendship dialogue.

L26. FRIENDSHIP AND ROMANCE
【2026-09-30】whitelist 見 S13：PRIMARY Sophie × Mia；SECONDARY / OPTIONAL 晴 × 阿拓；Ken × Monsieur 杜 永遠是友情。
eligibility 架構見 S14–S15；milestone 插圖見 S8、S10、S16–S17。
The Lounge may support friendship and a SMALL number of romantic developments.

HARD RULE:

GENERIC RELATIONSHIP SYSTEM MUST NEVER GENERATE ROMANCE AUTOMATICALLY.

No:

affinity > 80
→ dating

No generic matchmaking.

No automatic pairing of male/female characters.

No visible:
- heart meters
- dating meters
- confession quests
- matchmaking UI

Generic relationship architecture may produce:
- recognition
- familiarity
- friendship
- comfort
- shared habits
- shared seating
- noticing absence

Romance is allowed ONLY for explicitly authored/whitelisted adult character pairs.

Even an eligible pair does not need to become romantic in every save unless specifically authored that way.

Possible progression should remain subtle:

independent visits
→ repeated encounters
→ longer conversations
→ voluntarily sitting together
→ one waits for the other
→ occasionally arriving together

No giant:

“THEY ARE NOW DATING ❤️”

popup.

The player should often notice before the UI says anything.

Example:

One person arrives first.

Bartender:
「今天一個人？」

Character:
「……先一個。」

Much later they enter together.

The player should think:

「幹？？？你們兩個？？？」

That is the desired emotional response.

Friendship must remain equally valuable.

Some relationships that LOOK romantic may simply become close friendships.

Do not make every meaningful relationship romantic.

L27. CUSTOMER × STAFF RELATIONSHIPS
The Lounge naturally increases customer/staff familiarity.

This should be used heavily.

Examples:

bartender remembers usual drink

server knows preferred seat

customer notices a staff member’s day off

staff member knows a regular is waiting for someone

customer remembers a server from their first week

veteran staff recognizes an old habit

But customer/staff romance should be extremely rare and authored only if ever used.

Do NOT create workplace matchmaking mechanics.

L28. SEATS CAN HAVE HISTORY
Lounge seating should not only represent capacity.

Certain recurring characters may gradually develop soft preferences.

Examples:
- Ken often chooses a particular bar seat
- Sophie prefers a quieter area
- Dylan may choose a position where Jill is visible
- a pair that became familiar may begin choosing adjacent seats

Do not reserve seats permanently.

Normal guests may occupy them.

That itself can create natural variation.

Example:

Ken’s usual seat is occupied.

He sits beside Monsieur Du instead.

No one is displaced.

This may create a different interaction.

Seat preference is a WEIGHT, not ownership.

L29. CATS IN THE LOUNGE
All existing cat canon remains.

HARD:
cats NEVER go outside the restaurant.

The Lounge is indoors, therefore cats may autonomously visit if physically/pathing appropriate.

Do NOT turn cats into Lounge attractions or management tasks.

Possible natural behavior:
- 包包 sleeps near a Lounge chair
- 寶寶 chooses a visible elegant spot
- 樾樾 cautiously approaches a familiar person
- 柔柔 creates odd little moments
- 小齁 follows Jill or competes for proximity

Their presence may create real relationship callbacks.

Example:
周董 delays leaving because 包包 is sleeping nearby.

Do not teleport a cat to create an event.

The cat must actually be there.

L30. REVIEWS / SOCIAL / LOUNGE
The Lounge must integrate with the previously specified shared topic vocabulary.

Possible topics:
- wine
- atmosphere
- late-night
- Bar Food
- staff
- comfort
- social
- Signature
- waiting experience

Real Lounge events may generate:
- reviews
- social posts
- Album photos
- Records entries

Social must amplify REAL events.

It cannot invent:
- a relationship
- a dish
- a cat interaction
- a party
- a crowded night

that did not occur.

L31. LIFE ALBUM
【2026-09-30】新增：authored relationship milestone illustrations（S8、S10、S16、S17）— 真正發生後才解鎖的專屬插圖，
不是隨機截圖；Album 不能變成 CG 收集館。
Lounge stories may become some of the strongest Life Album material.

Examples:

「只是再坐一下」
「他今天沒來」
「打烊以後」
「第一次坐在一起」
「Ken 自己開的頭」
「他們還是沒有同意」
「今天晚一點」

But all Album images must match reality.

No fake staged photos.

If title implies two characters:
both must actually be present.

If a cat is referenced:
that cat must actually be in the captured scene.

Do not reproduce the old “五隻同框 but only three cats visible” problem.

L32. OPERATING CONSEQUENCES
The Lounge should create interesting management consequences without punitive busywork.

Possible consequences:

+ higher evening revenue
+ higher average spend
+ additional waiting capacity
+ more relationship opportunities
+ more late-game money sinks
+ more staff specialization
+ more use of existing kitchen

Tradeoffs:

- more kitchen load
- more FOH staffing demand
- bartender specialization needed
- longer-staying customers occupy Lounge seats

Do NOT add:
- taxes
- arbitrary maintenance punishment
- alcohol spoilage micromanagement
- daily bottle ordering
- mandatory manual pouring
- constant glasswashing clicks

L33. STAFF ASSIGNMENT INTEGRATION
Reuse the new v2.2.1 “工作分配” architecture.

Do NOT recreate the old unclear “換工作站” cycling behavior.

Lounge should appear naturally as another assignment destination once unlocked.

Player should be able to understand:

WHO
is assigned to
WHAT AREA / ROLE

without cycling random employees.

Potential conceptual assignments:

Main Hall
Side Hall
Lounge
Kitchen
Bartender

Exact representation depends on architecture audit.

Do not assume every staff member is eligible for every assignment.

L34. STAFFING GROWTH TARGET
Current mature saves already have substantial staff.

A mature restaurant with full Lounge may naturally reach approximately 13–15 total employees, but this is NOT a required fixed number.

Do not require all staff to work simultaneously.

The player should gradually feel:

“今晚 Lounge 比較忙，我要多放一個人過去。”

or:

“今天 Side Hall 有聚餐，我把強的 FOH 留那邊。”

This is the desired staffing decision.

Not:

“15 people require constant micromanagement.”

L35. NO NEW NPC EXPLOSION
Do NOT create many new customers simply because Lounge exists.

The PRIMARY Lounge cast should be existing Jill’s Kitchen characters:

- 陳伯伯
- Mia
- 小林
- Leo
- Sophie
- 王先生
- 王太太
- Dylan
- 周董
- Madame Lin
- Mr. Hart
- 老饕李先生
- Monsieur 杜
- 品酒師 Ken
- 神秘美食評論家
- 小琪
- Momo
- existing staff
- existing cats

The point is to deepen the existing social world.

New permanent NPCs should be added only when they provide a role the existing cast cannot naturally provide.

Currently approved core new staff are:

- Evan 林奕文
- 沈晴
- 阿拓
- 安安

Do NOT spontaneously generate 10 more named Lounge regulars.

L36. STORY SYSTEM PRIORITIES
The Lounge is not a quest hub.

No:
- exclamation marks
- “Sophie Story 3/5”
- friendship progress bars
- collect reward buttons
- romance meters

Story should emerge through:

- arrivals
- seating
- food/drink orders
- shared food
- conversation
- remembered habits
- staff familiarity
- absence
- waiting
- moving between rooms
- after-dinner lingering
- after-close moments
- Reviews
- Social
- Album
- Records

The player should feel like they noticed something happening.

Not like they completed a quest.

L37. SAVE / MIGRATION SAFETY
This is P0.

v2.2.1 mature saves MUST load safely into v2.3.

Do not repeat the Day35 migration regression.

Before implementation:
audit current save schema and migration order.

Requirements:

- old saves without Lounge fields load safely
- Lounge defaults locked/unbuilt
- existing staff retain current roles/levels/history
- new station familiarity initializes safely
- no existing employee loses competence
- no regular history resets
- no Dylan progression resets
- no Album/Reviews/Records loss
- no existing Signature unlock relocks
- no new character mapping collision
- no duplicate customer IDs
- no duplicate staff IDs

Migration must be:
idempotent
version-aware
tested on real mature saves

Use at least:
- fresh/new save
- Day30 fixture
- current Day35+ real mature save

Reload migrated saves more than once to prove idempotence.

L38. EVENT / SIMULATION SAFETY
Avoid adding per-frame relationship scans.

Relationship/story evaluation should happen at meaningful boundaries such as:

- character arrival
- seating
- order creation
- food/drink delivery
- room transition
- another named character arrival
- service completion
- closing
- specific event resolution

Do NOT compute all NPC × NPC relationships every frame.

Do NOT build a full N×N matrix unless architecture audit proves a compelling reason.

Create/update relationship facts only for relevant entities that genuinely interacted or shared meaningful context.

L39. TICKET SAFETY
A guest moving:

Lounge → Main Hall

or:

Main Hall → Lounge

must remain the SAME guest.

Do not:
- duplicate their ticket
- duplicate payment
- duplicate review eligibility
- duplicate visit count
- duplicate relationship co-presence
- duplicate Album eligibility

A single visit may have multiple phases.

Audit ticket identity before implementation.

L40. STORY IMPORTANCE CLASSES
Not every story needs guaranteed completion.

Class A — CRITICAL / STRUCTURAL
Should reliably occur when conditions mature.

Examples:
- Lounge unlock
- wine-service origin
- important restaurant milestone
- Dylan core progression
- second Signature progression

Use strong catch-up windows.

Class B — CHARACTER ARC
Expected to occur reasonably often but can vary.

Examples:
- Sophie × 寶寶
- Ken × Monsieur Du
- customer/staff familiarity
- 王先生 × 王太太

Use soft catch-up.

Class C — EMERGENT MOMENT
Never guaranteed.

Examples:
Sophie + Mia + Momo + Nina + 寶寶 happen to combine into one beautiful evening scene.

These should remain rare and special.

Do NOT force them merely to “show content.”

L41. V2.3 IMPLEMENTATION PHASING — UPDATE
Do NOT implement all of this at once.

After v2.2.1 release:

PHASE 0
ARCHITECTURE AUDIT ONLY

Report:
- current room model
- customer location/state model
- ticket identity model
- staff assignment model
- kitchen/ticket routing
- event scheduler
- Regular History / World Memory
- save schema/migration
- Album capture architecture
- review/social architecture
- how Lounge can be added with minimum duplication
- likely regression risks
- recommended implementation boundaries

NO CODE until audit is reviewed.

Then proposed staged implementation:

PHASE A
Story/Relationship foundation already specified in main v2.3 brief
+ Sophie/BaoBao vertical slice
+ generic familiarity behavior

PHASE B
Reviews 2.0 / shared topic vocabulary

PHASE C
Social layer

PHASE D
Marketing layer

PHASE E
Lounge foundation:
- room shell
- room transition
- staffing destination
- bartender role
- shared kitchen Bar Food routing
- minimal drinks
- save migration
- NO giant story pack yet

PHASE F
Lounge I playable vertical slice:
- Evan
- one existing FOH supporting
- small Lounge
- waiting transition
- small Bar Food menu
- Ken/Monsieur Du interaction
- Dylan/Evan small interaction
- staff familiarity
- real-save smoke

PHASE G
Lounge expansion / staff:
- 晴
- 安安
- Lounge II
- broader existing-staff familiarity
- relationship events

PHASE H
Optional Bar Food specialization:
- 阿拓
- kitchen load consequences
- optional Bar Pantry/Fry Station
- Lounge III if justified

PHASE I
Crossovers / romance-authorized arcs / long-delay callbacks / polish

This exact ordering may be adjusted after architecture audit if current code suggests a safer dependency order.

But do NOT jump directly from brief to “build complete Lounge.”

L42. TESTING PHILOSOPHY
Test SYSTEM TRUTHS, not every dialogue line.

Important invariants:

- no duplicate guest after room transition
- no duplicate ticket
- no duplicate payment
- no duplicate visit count
- no impossible omniscient memory
- no relationship progression without real co-presence/interaction where required
- dismissed staff never appear in staff story beats
- cats are never teleported outside
- Lounge food routes to valid kitchen
- bartender-only actions respect staff eligibility
- old saves migrate safely
- station familiarity persists
- veteran staff do not lose old competence
- event budgets work
- ambient events do not block major stories
- overdue bonus cannot bypass hard requirements
- no portrait ID collisions
- no Album title/content mismatch

Use deterministic seeded tests where useful.

Avoid building another enormous brittle golden-test laboratory.

Visual golden tests only where they protect real layout regressions.

Real mature-save smoke remains mandatory.

L43. I / T / O DISCIPLINE
Continue current definitions:

I = Implemented
T = Targeted / automated test
O = Observed in normal play

Never promote T to O.

For Lounge especially:

Automated test proving:
“Sophie and Mia can share seating”

is T.

It becomes O only when normal play actually produces a coherent scene and it looks/feels correct.

Phone-scale real play remains the final authority for:
- room readability
- seating density
- staff visibility
- story perceptibility
- whether Lounge feels alive
- whether kitchen load is annoying
- whether staffing is understandable
- whether interactions are noticeable during actual service

L44. PERFORMANCE / SCOPE GUARDRAIL
Do not turn this into a simulation research project.

Before creating any new subsystem ask:

Can existing:
- customer state
- staff assignment
- event arbiter
- World Memory
- relationship facts
- kitchen routing
- save system

represent this safely?

Prefer extension over replacement.

Do not rewrite stable systems merely because a cleaner theoretical architecture exists.

Do not build:
- full social graph simulator
- generic dating AI
- bartender physics
- realistic alcohol chemistry
- bottle-by-bottle cellar simulation
- second pathfinding engine
- second kitchen
- separate Lounge economy

The goal is:

MORE LIFE VISIBLE TO THE PLAYER.

Not:

MORE ARCHITECTURE INVISIBLE TO THE PLAYER.

L45. FINAL ACCEPTANCE TARGET
By mature play (roughly Day50–100 depending on save history), the player should be able to notice:

- Jill’s Kitchen physically grew a real evening Lounge
- the Lounge looks related to the restaurant but has its own identity
- Main Hall, Side Hall and Lounge feel functionally different
- existing staff learned new spaces instead of becoming obsolete
- veteran employees feel valuable
- bartender is a real specialty
- Bar Food uses the restaurant kitchen naturally
- Lounge success creates manageable kitchen/staffing consequences
- the player has meaningful late-game investments
- some customers wait in Lounge instead of queueing mechanically
- some dinner guests move to Lounge afterward
- existing regulars recognize one another
- some independently arriving people now sit together
- staff know customer habits
- customers notice staff
- someone occasionally notices another person’s absence
- some friendships have clearly grown over time
- a very small number of authored relationships may hint at or develop romance
- the player notices relationship changes without meters or quest UI
- cats remain autonomous indoor family members
- Album / Reviews / Social / Records preserve actual history
- the restaurant feels different because things happened there before

The ultimate target scene is NOT a scripted cutscene.

It is something like:

Main Hall is winding down.

Ken and Monsieur Du are still arguing at the bar.

Evan already knows where their glasses go.

Sophie arrives and sees Mia in the Lounge.
She quietly moves her bag off the adjacent chair.

Momo notices BaoBao nearby but remembers not to photograph Sophie.

Nina brings food and already knows how Momo likes the plate positioned.

Dylan sits where he can still see Jill finishing work.

A veteran employee helps a newer Lounge server without being asked.

One of the cats falls asleep under a chair.

Nothing announces:

STORY EVENT COMPLETE.

The player simply realizes:

“These people know each other now.”

That is v2.3.


第三部：Lounge 故事線與關係內容（Addendum 2026-09-30 #2，原文 docs/v23/addendum_2026-09-30_lounge_storylines.txt）
STORY / CONTENT specification for the future v2.3 Lounge — future scope；DO NOT IMPLEMENT before v2.2.1 Version 33 is completely
released and the v2.3 architecture audit has been reviewed（S22）。與第 20 節（起源線）、第二部 L18–L28、L31 一起讀。

The Lounge is not valuable merely because it sells wine.

Its real narrative purpose is:

People who previously came to Jill’s Kitchen separately begin spending enough time in the same place to recognize one another.

Some become friends.
Some become part of each other’s routines.
A very small number may slowly become romantic.
Staff become part of customers’ histories.
Customers become part of staff members’ working lives.

The player should gradually realize:

「這些人以前根本不認識。」


S1. STORY PHILOSOPHY
The Lounge must NOT become a quest hub.

Never show:

Sophie Romance 3/5
Friendship +10
Relationship Level Up
❤️ 78%
Dating unlocked
Talk to Mia (!)

The player observes relationships through behavior.

Important relationship development should be expressed through things such as:

- choosing to sit near someone
- greeting someone without introduction
- knowing their name
- sharing food
- remembering their drink
- waiting for someone
- noticing someone is absent
- leaving together
- arriving together
- staff preparing something before being asked
- moving a bag off the adjacent chair
- keeping a seat available without formally reserving it
- changing one's normal behavior because another person is present

The central rule is:

RELATIONSHIPS ARE OBSERVED THROUGH CHANGED BEHAVIOR.

Not through meters.

S2. THE LOUNGE MUST HAVE AN ORIGIN STORY
The Lounge does NOT appear merely because the player reached a revenue threshold.

Ken is the narrative origin.

The structural arc is:

KEN NOTICES THE RESTAURANT DOES NOT SELL WINE
→ repeated real food/pairing conversations
→ Monsieur 杜 may join and disagree
→ small experimental tasting evening
→ Jill realizes she does not merely want a wine cabinet
→ Jill wants somewhere guests can remain after dinner
→ Lounge project becomes available
→ player may build now or defer
→ Lounge I construction
→ first real Lounge service

Ken remains a CUSTOMER.

Monsieur 杜 remains a CUSTOMER.

Neither becomes free staff.

--------------------------------------------------
KEN — FIRST QUESTION
--------------------------------------------------

Only after Ken has genuine visit history and has eaten suitable food.

Ken:
「妳真的完全不賣酒？」

Jill:
「目前沒有。」

Ken:
「有幾道菜，我每次吃到一半，都覺得旁邊少了一個東西。」

Jill:
「你是來吃飯還是來找工作？」

Ken:
「吃飯。」

Do not immediately unlock Lounge construction.

The idea must first become part of restaurant history.

--------------------------------------------------
MONSIEUR 杜
--------------------------------------------------

Preferred later event if Ken and 杜 are genuinely co-present:

Ken:
「這一道如果配——」

杜:
「不要。」

Ken:
「我還沒講。」

杜:
「我知道你要講什麼。」

Their disagreement becomes a recurring relationship motif.

IMPORTANT:

Monsieur 杜 participation is CHARACTER ENRICHMENT.

It must NOT become a hard blocker for Lounge structural progression.

If RNG repeatedly prevents natural co-presence, Ken's structural arc continues.

杜 can join later.

--------------------------------------------------
EXPERIMENTAL TASTING
--------------------------------------------------

Eventually Jill tries ONE small tasting evening.

This is not permanent wine service.

No permanent bottle inventory.
No wine micromanagement.
No giant tutorial.

It exists to prove:

“Wine actually belongs here.”

It may create:
- real Reviews
- Social discussion
- Life Album photo
- character memories
- Ken/杜 disagreement

After sufficient real history:

Jill:
「如果真的要做，我不想只是放一個酒櫃。」

Ken:
「那妳想怎樣？」

Jill:
「讓人吃完飯以後，還有地方可以坐。」

NEW PROJECT:
Jill’s Kitchen — Lounge

Player may choose:

[開始規劃]
[之後再說]

Deferring NEVER permanently loses the Lounge.

S3. AFTER THE LOUNGE OPENS
Do NOT treat the opening as the end of the story.

It is the beginning of a new social environment.

The first nights should primarily use EXISTING characters.

The player should see familiar people behaving differently because there is now somewhere to stay.

Possible behaviors:

Dinner → Lounge

Lounge → Dinner

Wait for dining table in Lounge

Come specifically for Lounge

Stay after another regular leaves

Wait for another person

Join someone already seated

Move from bar counter to shared table

Share Bar Food

Talk to bartender

Leave together

The SAME customer identity must persist through room transitions.

S4. EVAN — THE PERSON WHO STARTS REMEMBERING EVERYONE
Evan begins with no magical knowledge of restaurant history.

He learns through actual employment.

Early:

Ken:
「杜來了嗎？」

Evan:
「還沒看到。」

Later, after enough real history:

Ken walks in.

Evan places one coaster down.

Then pauses.

Places a second coaster nearby.

Ken:
「他今天沒來。」

Evan:
「我沒問。」

Evan gradually learns:
- regular drinks
- preferred seating
- who tends to wait for whom
- who argues about what
- who comes alone
- who increasingly arrives together

But he NEVER exposes private information simply because he knows it.

His personality is:

「記得很多，但不會因為知道很多就一直講。」

--------------------------------------------------
LATE CALLBACK TO LOUNGE ORIGIN
--------------------------------------------------

Much later, after Evan has naturally learned the history of the Lounge:

Evan:
「聽說這裡是你害的。」

Ken:
「誰跟你講的？」

Jill, from elsewhere:
「我。」

This should only occur if Evan has reasonably learned the origin story.

S5. KEN × MONSIEUR 杜 DEEP FRIENDSHIP — NOT ROMANCE
This relationship is intentionally capable of fooling the player.

They may:

- argue constantly
- know each other's wine preferences
- sit together
- save an adjacent seat
- notice absence
- wait for one another
- order food together
- arrive independently but spend the evening together

BUT:

They are NOT a romantic pair.

This is important.

The relationship system must establish:

INTIMACY ≠ ROMANCE.

Example:

晴:
「你今天不等杜先生？」

Ken:
「我為什麼要等他？」

pause

Ken:
「他有說幾點嗎？」

Do not turn this into a romantic reveal later.

Their friendship itself is valuable.

S6. SOPHIE × MIA PRIMARY SLOW-BURN ROMANTIC ARC
This is the strongest candidate for the major new romantic relationship.

It must take a LONG time.

The first half of their development should be indistinguishable from ordinary friendship.

Do NOT internally begin with:

SophieLikesMia = true

Use ordinary Relationship Facts first.

Possible facts:

recognizes
knowsName
repeatedCoPresence
sharedTable
sharedFood
choosesNearbySeat
waitedFor
noticedAbsence
leftTogether
arrivedTogether

Only an explicitly authored whitelist may later interpret enough qualitative history as:

romanticEligible

Even then:

romanticEligible ≠ dating.

--------------------------------------------------
PHASE A — RECOGNITION
--------------------------------------------------

They repeatedly encounter one another naturally.

Mia:
「妳也常來？」

Sophie:
「……妳不是也一樣。」

Nothing romantic.

--------------------------------------------------
PHASE B — FIRST SHARED SPACE
--------------------------------------------------

A crowded restaurant or Lounge may naturally cause them to share seating.

But shared seating must NOT be a hard progression requirement.

If crowding never happens, an equivalent meaningful conversation can occur naturally.

Story meaning fixed.
Presentation may fallback.

--------------------------------------------------
PHASE C — ACTIVE CHOICE
--------------------------------------------------

This is more important than repeated co-presence.

Mia is already in Lounge.

Sophie enters.

Other seats exist.

Sophie chooses to sit nearby.

Later:

Mia:
「妳今天不是坐那邊？」

Sophie:
「這邊也可以。」

This is the first moment where an observant player may suspect something.

--------------------------------------------------
PHASE D — MAKING SPACE
--------------------------------------------------

Sophie arrives first.

Her bag is on the adjacent chair.

Mia enters.

Sophie notices her.

Without dialogue:

Sophie moves the bag.

This should count as more meaningful relationship evidence than another generic conversation.

--------------------------------------------------
PHASE E — SHARED FOOD
--------------------------------------------------

Mia:
「要不要吃這個？」

Sophie:
「不要。」

Later Sophie is eating it.

No relationship popup.

--------------------------------------------------
PHASE F — WAITING
--------------------------------------------------

Sophie has finished.

Normally she would leave.

Evan:
「還要什麼嗎？」

Sophie:
「不用。」

She stays.

Later Mia arrives.

Evan notices.

He says nothing.

This may create a qualitative fact:

waitedFor(Mia)

Waiting should matter more than simple co-presence.

--------------------------------------------------
PHASE G — LEAVING TOGETHER
--------------------------------------------------

Near closing:

Mia:
「走嗎？」

Sophie:
「嗯。」

They leave together.

Potential Life Album title:

《今天一起走》

NOT:

《第一次約會》

The player interprets the moment.

--------------------------------------------------
PHASE H — ARRIVING TOGETHER
--------------------------------------------------

Much later, after sufficient real history:

They enter Jill’s Kitchen together.

Jill:
「今天一起？」

Mia:
「嗯。」

Sophie:
「……怎樣？」

Jill:
「沒有啊。」

From this point:

arrivesTogether becomes occasionally eligible.

They still remain two independent NPCs.

Never merge them into a Couple entity.

They may still:
- visit separately
- have separate preferences
- have separate stories
- interact with different people
- arrive alone

A relationship must ADD identity, not erase it.

S6a. Sophie × Mia 角色設定（canonical appearances）
圖：docs/v23/sophie_mia_concept.png（2026-09-30 收到）。這是 S8 milestone 插圖與任何新表情藝術的外觀依據；v2.2.1 遊戲內既有的
sophie / mia 肖像（assets/portraits/web/sophie.webp、mia.webp）仍是目前的 canon，整合新藝術時依角色 ID 對應（L13），不得按順序。
Sophie：色票 近黑／暖棕／灰米／砂色。深色長捲髮（另有盤髮變化），黑西裝外套＋黑上衣、灰寬褲、黑色托特包、腕錶、小耳環，手邊常有
一杯紅酒；表情：沉思、側看、托腮、微笑、戴眼鏡看書。氣質安靜、內斂、有距離感。
Mia：色票 深棕／駝色／乾燥玫瑰／米白。高馬尾＋瀏海，米白襯衫（圖中配深色圍裙）、耳環，手邊是加薄荷的飲料；表情：大笑、托腮、
瞇眼笑、驚訝、吃東西、趴桌笑。氣質明亮、外放、活潑。
兩人的對比（安靜 × 明亮）就是 S6 八個 phase 要靠「行為改變」讓玩家自己看出來的東西；插圖要低調（S8：一起坐、一起走、分食、自然
靠近），不要婚禮、誇張親吻、大愛心、告白畫面或畫面內文字。

S7. SOPHIE × 寶寶 CONTINUES
Sophie’s relationship with 寶寶 must continue independently.

Romance does NOT replace earlier character stories.

Instead, story threads may cross naturally.

Example:

寶寶 approaches Sophie.

Sophie pets her naturally.

Mia watches.

Sophie:
「幹嘛？」

Mia:
「沒有。」

Sophie:
「妳有。」

Mia:
「我真的沒有。」

If Mia eventually learns about the item Sophie brought for 寶寶, she may reference it.

But only after she has actually witnessed or learned that fact.

No omniscience.

S8. SOPHIE × MIA ROMANTIC MILESTONE IMAGE
IMPORTANT NEW REQUIREMENT:

When an authored relationship genuinely crosses the confirmed romantic milestone, generate/unlock ONE dedicated relationship illustration for Life Album.

This is NOT merely a random screenshot.

It is a special authored milestone image.

However:

The image may unlock ONLY after the underlying relationship event actually occurred.

Do not fabricate relationship history merely to unlock artwork.

For Sophie × Mia:

after their relationship has genuinely become romantic through real history,
unlock a dedicated Sophie × Mia illustration.

The illustration should use their canonical character appearances.

It may depict an understated moment such as:
- sitting together in Lounge
- leaving together
- quiet shared food/drink
- one leaning naturally toward the other

Avoid:
- wedding imagery
- exaggerated kissing
- giant hearts
- visual-novel confession framing
- text saying “COUPLE UNLOCKED”

Life Album title should remain understated.

Examples:

《今天一起來》
《留到很晚》
《她的位置》
《兩個人的晚上》

This artwork becomes a permanent piece of restaurant history.

S9. 晴 × 阿拓 OPTIONAL STAFF SLOW-BURN
This is a SECONDARY authored romantic possibility.

It begins as professional chemistry.

Do NOT start romantically.

Early:

晴:
「炸雞好了沒？」

阿拓:
「沒有。」

晴:
「看起來好了。」

阿拓:
「妳跟 Hugo 講一樣的話。」

晴:
「那代表我們兩個都正常。」

Their first relationship is WORK.

Over time they learn each other's timing.

Eventually 晴 can recognize when food is nearly ready without asking.

阿拓 learns which Lounge tables actually need speed.

--------------------------------------------------
SMALL PERSONAL CHANGE
--------------------------------------------------

After closing:

晴 is still working at the bar.

阿拓 places a small plate beside her.

晴:
「什麼？」

阿拓:
「多的。」

She tastes it.

晴:
「你明明就是特別做的。」

阿拓:
「多的。」

Do not label this romantic.

Repeat variations rarely.

--------------------------------------------------
ABSENCE
--------------------------------------------------

One day 阿拓 is not working.

晴:
「今天炸物怎麼怪怪的？」

Hugo:
「一樣的做法。」

晴:
「喔。」

pause

晴:
「阿拓今天沒來？」

Hugo:
「妳不是在問炸物？」

This is where the player may begin suspecting something.

--------------------------------------------------
EMPLOYMENT SAFETY
--------------------------------------------------

This arc MUST tolerate firing / staff absence.

If 晴 or 阿拓 is no longer employed:

Do not teleport them back.

Do not freeze unrelated systems.

Do not punish the player.

Do not leave a permanent broken StoryStage waiting for them.

The romantic arc simply becomes inactive unless the game later has a legitimate former-employee return mechanism.

This is an OPTIONAL character arc.

It must never block restaurant progression.

S10. 晴 × 阿拓 MILESTONE IMAGE
If and only if their authored romantic relationship genuinely develops far enough:

unlock a dedicated relationship illustration.

Possible understated image:

After closing,
Lounge mostly empty,
晴 sitting at bar,
阿拓 beside her with the small plate he claims was “extra.”

Again:

No giant romance UI.
No hearts.
No confession screen.

The player should recognize the history represented by the image.

S11. JILL × DYLAN LONG-TERM LOVE AS CONTRAST
Jill and Dylan are already married and have been together for approximately eleven years.

Dylan is NOT “observing a romance for eleven years.”

The eleven years refers ONLY to Jill and Dylan’s own long-term relationship.

Their role in the relationship ecosystem is different:

Sophie × Mia:
a relationship beginning.

晴 × 阿拓:
work familiarity becoming personal.

Jill × Dylan:
a long-established marriage where Dylan still enjoys acting like he is pursuing his wife.

王先生 × 王太太:
an established married couple with ordinary independent lives.

Ken × Monsieur 杜:
deep friendship without romance.

This contrast is important.

--------------------------------------------------
JILL / DYLAN OBSERVING NEW RELATIONSHIPS
--------------------------------------------------

After Dylan’s marriage reveal, he may occasionally notice other relationships developing.

But do NOT make him omniscient.

Example:

Dylan:
「她們是不是——」

Jill:
「不要管人家。」

Dylan:
「我只是觀察。」

Jill:
「你很閒是不是？」

This is enough.

Do NOT say he has been observing them for eleven years.

--------------------------------------------------
JILL / DYLAN THEMATIC CALLBACK
--------------------------------------------------

A new relationship may occasionally remind the player that Jill/Dylan have their own long history.

For example:

Dylan watches two people awkwardly choose seats near each other.

Dylan:
「以前我也——」

Jill:
「你現在也一樣。」

Dylan:
「也是。」

This preserves Dylan’s core joke:

He never stopped pursuing Jill.

S12. 王先生 × 王太太 ESTABLISHED COUPLE
They should demonstrate that being married does not mean functioning as one NPC.

Sometimes:
- arrive together
- arrive separately
- one waits
- one leaves earlier
- one sits with another regular
- they tease each other
- they know one another’s habits

Their relationship should feel comfortable and ordinary.

This provides another contrast to new romance.

S13. RELATIONSHIP NETWORK — NOT PAIRING TABLE
Do NOT turn all characters into romantic candidates.

Most relationships should remain:

friendship
professional familiarity
regular/staff familiarity
shared-interest relationship
friendly rivalry
customer/restaurant history

Romance is rare.

Currently approved romantic authored candidates:

PRIMARY:
Sophie × Mia

SECONDARY / OPTIONAL:
晴 × 阿拓

Do NOT spontaneously create additional romantic pairs without approval.

Especially:

Ken × Monsieur 杜 remains friendship.

Do not automatically pair opposite-sex NPCs.

Do not assume repeated co-presence means attraction.

S14. ROMANTIC ELIGIBILITY ARCHITECTURE
Do NOT use:

coPresenceCount >= 10
→ romance

Romantic progression requires qualitative facts.

Examples:

choosesNearbySeat
waitedFor
changedDepartureBehavior
sharedFoodVoluntarily
noticedAbsence
arrivedTogether
leftTogether
repeatedActiveChoice

The authored pair must first develop through normal relationship architecture.

Conceptually:

FACTS
→ FAMILIARITY
→ COMFORT
→ QUALITATIVE RELATIONSHIP HISTORY
→ romanticEligible
→ authored romantic beats
→ confirmed relationship state

The player sees NONE of these technical states.

S15. DO NOT DEADLOCK ROMANCE
Do not require one exact physical event.

Example:

Sophie/Mia romance should not permanently fail because:

“they never happened to share Table 4.”

Use meaningful equivalent presentation.

But do NOT fake core facts.

If Mia never actually arrived:
Sophie cannot wait for Mia and then somehow record waitedFor(Mia).

If Sophie left before Mia arrived:
do not claim they left together.

Presentation can fallback.

History cannot lie.

S16. RELATIONSHIP ART ARCHITECTURE
Dedicated relationship illustrations are authored rewards for genuine long-term history.

They are NOT random screenshots.

They should be treated similarly to special Life Album assets.

Requirements:

- canonical faces
- stable character mapping
- correct outfits/era where relevant
- correct relationship
- no unrelated character accidentally appearing
- no portrait identity swap
- no impossible cat
- no event depicted before it occurred

If an illustration includes a cat:
that inclusion must be appropriate to the actual authored milestone.

Do not use generated text inside the artwork if avoidable.

Use game UI for title/caption.

This avoids typography artifacts and keeps localization safe.

S17. OTHER RELATIONSHIP MILESTONE IMAGES
Romance is NOT the only relationship worthy of special artwork.

Potentially, extremely important non-romantic history may also earn one.

Examples:

Ken × Monsieur 杜:
their established Lounge friendship / argument

Dylan × Jill:
rare post-reveal long-term-marriage moment

Staff ensemble:
late-night staff meal

But keep these rare.

Life Album should not become a collectible CG gallery.

Special illustrations should feel exceptional.

S18. EVENT DENSITY
Do not turn Lounge into nonstop scripted dialogue.

Normal night:
mostly restaurant simulation.

Typical:
0–1 major authored story beat
0–2 minor callbacks
ambient interactions as appropriate

Some nights:
nothing important happens.

That silence is necessary.

Without ordinary nights, special nights do not feel special.

S19. CROSSOVER EXAMPLES
As history grows, relationships may cross.

Examples:

Mia knows Sophie likes 寶寶.

Evan knows Ken waits for 杜.

晴 knows 周董’s “隨便” is not actually random.

安安 recognizes who is waiting for whom.

王太太 notices Sophie/Mia before they formally arrive together.

Dylan suspects something but Jill tells him not to interfere.

Hugo notices 晴 asking about 阿拓.

These are BONUS callbacks.

They must NEVER become mandatory prerequisites for the underlying relationship.

S20. LONG-TERM TARGET
By Day80–100 in a sufficiently mature save, a player might witness something like:

Ken and Monsieur 杜 are already arguing at their usual part of the bar.

Evan barely needs to ask what they want.

Sophie arrives first.

She sits down.

Her bag is on the next chair.

Mia enters later.

Sophie removes the bag without saying anything.

Nearby, 晴 asks Kitchen whether 阿拓 is working tonight, then immediately pretends the question was about food.

Dylan notices Sophie and Mia.

He looks toward Jill.

Jill sees his face before he says anything.

Jill:
「不要。」

Dylan:
「我還沒講。」

One of the cats is asleep nearby.

Nothing announces:

RELATIONSHIP EVENT COMPLETE.

The player understands all of it because they remember what these people used to be like.

That is the target.

S21. IMPLEMENTATION GUARDRAIL
Before coding any of these stories:

architecture audit must explain how current systems safely support:

- persistent Relationship Facts
- familiarity
- authored romantic eligibility
- staff employment dependencies
- event weighting
- overdue catch-up
- room transitions
- story event budget
- special Life Album illustration unlocks
- save migration
- mature-save compatibility

Do NOT build a generic romance engine.

Do NOT build a dating simulator.

Do NOT create an N×N romance matrix.

Do NOT create romance AI.

Implement only the small number of authored relationships we actually need.

The system should be generic enough for relationship facts,
but ROMANCE itself remains authored.

S22. CURRENT EXECUTION STATUS
DOCUMENTATION ONLY FOR NOW.

Do not implement this before v2.2.1 Version33 is complete.

When eventually authorized for v2.3:

implement relationship infrastructure first,
prove it with a small vertical slice,
then add Lounge relationship content gradually.

Do not attempt every storyline in one commit.

完成這份 architecture report 後再開始 Phase A。
不要重新設計已穩定的 v2.2.1 系統，不要為了 v2.3 建立不必要的大型 framework，也不要把 presentation 問題升級成 infrastructure project。