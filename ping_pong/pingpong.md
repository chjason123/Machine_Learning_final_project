# 乒乓球遊戲 — 訓練資料規格與需求文件
版本：v1.0  
日期：2025-11-26  



功能:
-----------------------------------
- 球拍左移右移。
- 發球方向。
- 預測球的反彈軌跡。

限制:
-----------------------------------
- 語言:
Python(AI訓練)
- 環境版本:
Python 3.11.5
- 模組:
Mlgame
- 遊戲介面:

物件大小（寬*高）
| 物件名稱 | 大小 [寬*高(像素)] |
|---|---:|
| 遊戲視窗 | 200 * 500 |
| 板子1、板子2 | 40 * 10 |
| 球 | 10 * 10 |
| 障礙物(困難模式)  | 30 * 20 |

初始位置
| 物件名稱 | 初始位置 |
|---|---|
| 板子1 | [80, 420] |
| 板子2 | [80, 70] |
| 球 | [95, 410] |

移動速度（每幀像素）
| 物件名稱 | 移動速度 [每幀(像素)] |
|---|---:|
| 板子 | 5 |
| 障礙物 | 5 |
| 球（初始） | 7(發球後每 100 影格增加 1) |

註：位址皆已左上角 (0,0) 為原點。

![side1](https://github.com/user-attachments/assets/290241b9-3483-425f-9bc0-6bf84ff2ac7b)



切球機制

1.板子與球的移動方向相同，球的 X軸 速度會增加

2.板子與球的移動方向相反，球會被打回反方向，速度不變

3.板子不動，球依照反彈原理反彈，速度不變

![side2](https://github.com/user-attachments/assets/902028eb-19e9-4bac-bdf2-84d49a82374f)

介面:
-----------------------------------



- 遊戲資訊 scene_info 的資料格式如下
```
{
  "frame": 24,
  "status": "GAME_ALIVE",
  "ball": [
    63,
    241
  ],
  "ball_speed": [
    7,
    7
  ],
  "ball_served": true,
  "serving_side": "2P",
  "platform_1P": [
    0,
    420
  ],
  "platform_2P": [
    0,
    70
  ],
  "blocker": [
    140,
    240
  ]
}
```
- frame：遊戲畫面更新的編號
- status：字串。目前的遊戲狀態，會是以下的值其中之一：
- GAME_ALIVE：遊戲正在進行中
- GAME_1P_WIN：這回合 1P 獲勝
- GAME_2P_WIN：這回合 2P 獲勝
- GAME_DRAW：這回合平手
- ball (x, y) tuple。球的位置。
- ball_speed：(x, y) tuple。目前的球速。
- ball_served：true or false 布林值 boolean。表示是否已經發球。
- serving_side：1P or 2P 字串 string。表示發球方。
- platform_1P：(x, y) tuple。1P 板子的位置。
- platform_2P：(x, y) tuple。2P 板子的位置。
- blocker：(x, y) tuple。障礙物的位置。如果選擇的難度不是 HARD，則其值為 None。

- 其他特徵(球落點):
利用球的位置與球速，當對方打回時可計算出球的落點
```
def calculate_ball_landing(ball_x, ball_y, ball_y_speed, ball_x_speed):
    while True:
        # 左右牆反彈
        if (ball_x_final + ball_width) + ball_x_speed_temp > GAME_WIDTH:
            ball_y_final = ball_y_final + ball_y_speed_temp
            ball_x_final = GAME_WIDTH - ball_width
            ball_x_speed_temp = -1 * ball_x_speed_temp
        elif ball_x_final + ball_x_speed_temp < 0:
            ball_y_final = ball_y_final + ball_y_speed_temp
            ball_x_final = 0
            ball_x_speed_temp = -1 * ball_x_speed_temp
        # 底部撞擊 (1P)
        elif (ball_high + ball_y_final) + ball_y_speed_temp >= PLATFORM_1P_Y:
            ball_x_final = ball_x_final + ball_x_speed_temp
            ball_y_final = PLATFORM_1P_Y - ball_high 
            print(''.join([str(x) for x in ['times :', times, '  x:', ball_x_final, 'y:', ball_y_final, '  x_speed:', ball_x_speed_temp, '  y_speed:', ball_y_speed_temp]]))
            return (ball_x_final, ball_y_final)
        # 頂部撞擊 (2P)
        elif ball_y_final + ball_y_speed_temp <= PLATFORM_2P_Y + BALL_SIZE_Y:
            ball_x_final = ball_x_final + ball_x_speed_temp
            ball_y_final = PLATFORM_2P_Y + BALL_SIZE_Y 
            print(''.join([str(x) for x in ['times :', times, '  x:', ball_x_final, 'y:', ball_y_final, '  x_speed:', ball_x_speed_temp, '  y_speed:', ball_y_speed_temp]]))
            return (ball_x_final, ball_y_final)
        else:
            ball_x_final = ball_x_final + ball_x_speed_temp
            ball_y_final = ball_y_final + ball_y_speed_temp
```
---


- 模型回傳動作指令

MOVE_LEFT：將板子往左移
MOVE_RIGHT：將板子往右移
NONE：無動作

KNN演算法:
----------------------------------
- KNN的演算法步驟如下：
設定k值，亦即會在計算時找出距離x資料中最近的k筆資料，距離計算方式如下幾種：

使用距離計算方式：

- 歐幾里德距離(Euclidean distance)

<img width="200" height="113" alt="image" src="https://github.com/user-attachments/assets/b879468a-892f-4842-8e2d-3e63bf542538" />

### 優點:
最符合日常幾何直覺（直線距離）。

對於「少數幾個維度差距很重要」的情境能放大這些差別。

### 缺點:
對離群值敏感：偏大的座標差異會被平方放大。
在高維空間容易遇到「距離集中」（distance concentration）問題，導致最近鄰區分度降低。
需做特徵縮放（標準化、正規化），否則尺度大的特徵會主導。

### 使用情況:
特徵已被適當標準化、且差異以空間直線距離衡量合理

資料維度不極高、或重要信號集中在少數維度。

計算距離後，找出k筆資料，並以投票的方式計算k點中的類別，並以投票數量最高的那個類別作為x的類別


分析:
-----------------------------------
<img width="1659" height="1110" alt="image" src="https://github.com/user-attachments/assets/09f501aa-5868-40d2-9abe-8668c7c86d5b" />



設計流程:
-----------------------------------
<img width="1121" height="786" alt="image" src="https://github.com/user-attachments/assets/1012f269-1722-4528-9a9c-14b060d0a4b8" />


架構圖:
-----------------------------------
<img width="1951" height="723" alt="image" src="https://github.com/user-attachments/assets/c9df2755-ac9e-4c4e-b799-e238d5fedf4e" />

驗收:
-----------------------------------
<img width="1094" height="633" alt="image" src="https://github.com/user-attachments/assets/210a7482-487a-4ec6-9d55-d7cf3a0605e3" />

# KNN 模型訓練報告

## 1. 資料分析

### 資料概況
- **資料總數：** 5,758 筆
- **特徵與標籤欄位：** 
  - `Distance`: 特徵
  - `Action`: 標籤

### 前 5 筆資料
| Distance | Action |
|----------|--------|
| 45       | 1      |
| 40       | 1      |
| 35       | 1      |
| 30       | 1      |
| 25       | 1      |



### 標籤分佈（Action）
| 標籤   | 頻率 | 百分比    |
|--------|------|-----------|
| 0 (`NONE`) | 3,367 | 58.5%     |
| 1 (`MOVE_RIGHT`) | 1,287 | 22.4%     |
| -1 (`MOVE_LEFT`) | 1,104 | 19.2%     |

---

## 2. 訓練與測試概要

### 資料切分
- **訓練集大小：** 4,606 筆 (80%)
- **測試集大小：** 1,152 筆 (20%)

---

## 3. 模型訓練與評估

### 訓練與測試準確率
- **訓練集準確率：** 100%
- **測試集準確率：** 100%

### 混淆矩陣
| **預測\實際** | -1 (`MOVE_LEFT`) | 0 (`NONE`) | 1 (`MOVE_RIGHT`) |
|---------------|-----------------|-----------|------------------|
| **-1**        | 221             | 0         | 0                |
| **0**         | 0               | 674       | 0                |
| **1**         | 0               | 0         | 257              |

### 分類指標
| 類別   | Precision | Recall | F1-score | Support |
|--------|-----------|--------|----------|---------|
| -1 (`MOVE_LEFT`) | 1.00      | 1.00   | 1.00     | 221     |
| 0 (`NONE`)       | 1.00      | 1.00   | 1.00     | 674     |
| 1 (`MOVE_RIGHT`) | 1.00      | 1.00   | 1.00     | 257     |

- **總體準確率：** 1.00 (100%)
- **宏平均（Macro Avg）：** Precision = 1.00, Recall = 1.00, F1 = 1.00
- **加權平均（Weighted Avg）：** Precision = 1.00, Recall = 1.00, F1 = 1.00

---

## 4. 測試預測結果
以下顯示一些測試資料的預測結果：

| Distance | 預測標籤 | 動作            |
|----------|----------|-----------------|
| -50      | -1       | MOVE_LEFT       |
| -20      | -1       | MOVE_LEFT       |
| -10      | -1       | MOVE_LEFT       |
| -5       | -1       | MOVE_LEFT       |
| -3       | 0        | NONE            |
| 0        | 0        | NONE            |
| 3        | 0        | NONE            |
| 5        | 1        | MOVE_RIGHT      |
| 10       | 1        | MOVE_RIGHT      |
| 20       | 1        | MOVE_RIGHT      |
| 50       | 1        | MOVE_RIGHT      |

---

## 5. 決策邊界可視化
- **邊界邏輯：**
  - `NONE (0)` 範圍：-3 至 3 之間
  - `MOVE_LEFT (-1)` 範圍：Distance < -3
  - `MOVE_RIGHT (1)` 範圍：Distance > 3

   
演算法遊玩
-----------------------------------
https://youtu.be/vgyHdUP6mEA
