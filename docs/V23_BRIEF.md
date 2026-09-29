Jill’s Kitchen v2.3 — Stories of Jill’s Kitchen
完整開發 Brief：故事事件、人物記憶、評論 2.0、社群、宣傳、酒水服務與餐廳歷史
請在 v2.2.1 已完成、Version 33 已發布、v2.2.1 tag 已建立且 QA 完成之後，才開始本版本。
不要把這份需求插入尚未完成的 v2.2.1。
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
20. STORY ARC 13：品酒師 Ken × Monsieur 杜
《餐廳是不是少了什麼？》
這條應該正式解鎖一整個輕量酒水服務。
Stage 1
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

只種伏筆。
Stage 2：Monsieur 杜
Ken：
「這一道如果配——」

Monsieur 杜：
「不要。」

Ken：
「我還沒講。」

「我知道你要講什麼。」

Jill：
「你們兩個可以先讓我把餐廳開完嗎？」

Stage 3：酒水企劃
成熟餐廳 + Ken 多次來訪 + 前置故事完成後：
打烊後出現：
新企劃：酒水服務
玩家可以：
開始規劃

或：
之後再說

拒絕不能永久 miss。
21. 酒水系統架構
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
第一版可以有幾個 style：
- 清爽白酒；
- 飽滿白酒；
- 輕盈紅酒；
- 濃郁紅酒；
- 氣泡酒。
可以有遊戲內虛構酒名，但不必過度 SKU 化。
酒水基礎設施
成為新的成熟期 money sink：
- 小型溫控酒櫃；
- 專業恆溫酒櫃；
- 杯具／服務設備；
- 後續高階展示。
設備必須真的畫在餐廳裡。
不要只在 upgrade menu 顯示 Lv.2。
Pairing
部分料理可以有推薦 pairing。
客人：
- 不喝；
- 單點；
- 接受 pairing。
平常由 staff 自動服務。
不要增加大量 active task。
First Tasting Night
酒水正式推出前／推出時：
Ken 參與。
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

😂
Monsieur 杜可以加入。
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
- Ken-triggered wine service；
- Life Album / Records integration。
品質優先於事件數量。
53. 開發順序
不要一次同時改全部。
建議依以下順序：
Phase A — Foundation
先做：
- fact / memory extension；
- story state；
- event arbiter；
- migration；
- idempotent consequences；
- debug/evidence tooling。
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
Phase E — Wine
做 Ken story → investment → equipment → wine list → pairing → guest behavior → reviews/social。
不要先做複雜 wine inventory。
Phase F — Remaining story arcs
架構穩定後再加入其他 NPC stories。
故事內容應主要 data-driven，不要每加一條就修改 simulation 核心。
Phase G — Crossovers
最後才大量加入：
- Sophie × Momo；
- Ken × Monsieur 杜；
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
完成這份 architecture report 後再開始 Phase A。
不要重新設計已穩定的 v2.2.1 系統，不要為了 v2.3 建立不必要的大型 framework，也不要把 presentation 問題升級成 infrastructure project。