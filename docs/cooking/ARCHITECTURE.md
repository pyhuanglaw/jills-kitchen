# 料理系統（Cooking Gameplay）— 架構與工作紀錄

規格（產品 canon，逐字）：

- `docs/v24/cooking_gameplay_spec_2026-10-07.txt`：整體規格。
- `docs/v24/cooking_workflow_canon_2026-10-07.txt`：31 道菜的流程，以及「玩家永遠不用背下一步」。
- `docs/v24/cooking_station_capacity_2026-10-07.txt`：工作站容量。
- `docs/v24/cooking_overnight_orders_2026-10-07.txt`：開發順序與防災條款。

這份文件記錄怎麼把規格做進現在的遊戲：程式結構、做到哪裡、遇到的技術衝突，以及要使用者決定的事。
它不重新設計規格；規格跟程式衝突時，以規格為準，衝突寫在最後兩段。

## 一句話

一道菜（或同一道菜的一批）是一個「工作」（work node）。它照自己的流程（例如 熱區 → 裝盤）一站一站走；每一站是廚房裡本來就有的位置，
有容量限制；Jill 和廚師用同一套規則接手。

## 名詞

| 遊戲裡的說法 | 程式 | 廚房裡的實際位置 |
|---|---|---|
| 備料 PREP | `prep` | 冷盤台的砧板（現有 `prep` slots） |
| 熱區 HOT | `hot` | 爐台的爐口（現有 `stove` slots，2 → 6 口） |
| 烤箱 OVEN | `oven` | 烤箱（現有 `oven` slots，1 → 2） |
| 飲料 DRINK | `drink` | 咖啡機（現有 `bar` slots，1 → 2 → 4） |
| 披薩烤爐 | `pizza` | 披薩烤爐（現有 `pizza` slot，固定 1） |
| 裝盤 PLATING | `plate` | 出菜口廚房側（新的 `pass` slots，1 → 2 → 3，用出菜口現有的盤位） |
| 出杯 SERVE | `serve` | 飲料放上出菜口取餐側；不占容量 |

水槽、冰箱、冷藏室不是流程的一站；角色可以在動畫裡走過去。

## 工作（work node）

```
{ id, d: 菜, n: 份數, its: [ticket items], fam: 流程, si: 第幾站,
  st: 'wait' | 'go' | 'work' | 'cook' | 'ready',
  slot: 占用的位置, who: 'jill' | 廚師 id | null, act / pas: 這一站剩下的手作／自己煮的時間 }
```

- `wait`：還沒開始這一站，在等位置或等人。
- `go`：已經有人接，人在走過去（位置先保留）。
- `work`：人在那一站做（手作的部分）。
- `cook`：自己在煮（爐上、烤箱裡），不需要人站著。
- `ready`：這一站做完了，菜留在原地，等送去下一站。不會壞、不會焦，也不會變差。

一個工作從開始做到被送去下一站，一直占著那一站的一個位置。一批（例如 炒飯 ×3）只占一個位置。

## 流程（規格 F，只有這幾種）

| family | 流程 |
|---|---|
| `hot2` | 熱區 → 裝盤 |
| `cold2` | 備料 → 裝盤 |
| `drink2` | 飲料 → 出杯 |
| `oven2` | 烤箱 → 裝盤 |
| `hot3` | 備料 → 熱區 → 裝盤 |
| `oven3` | 備料 → 烤箱 → 裝盤 |
| `pizza3` | 備料 → 披薩烤爐 → 裝盤 |

每道菜屬於哪一種，照 `cooking_workflow_canon_2026-10-07.txt` 的表；Special 跟原本的菜一樣；招牌主菜 `hot3`，招牌甜點 `cold2`。

## 做到哪裡

（逐步更新）
