# 乒乓球遊戲 — 訓練資料規格與需求文件



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

- 動作回傳
MOVE_LEFT：將板子往左移
MOVE_RIGHT：將板子往右移
NONE：無動作

KNN演算法:
----------------------------------
- KNN的演算法步驟如下：
設定k值，亦即會在計算時找出距離x資料中最近的k筆資料：

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
<img width="1806" height="1146" alt="image" src="https://github.com/user-attachments/assets/26a0adfd-787f-45fc-ad58-26a4bb805a27" />


設計流程:
-----------------------------------
<img width="1121" height="786" alt="image" src="https://github.com/user-attachments/assets/e2da38c3-6109-463a-b499-5a20306fb910" />


架構圖:
-----------------------------------
<img width="2186" height="623" alt="image" src="https://github.com/user-attachments/assets/becbd777-5191-4407-8cef-39813f3a8690" />

<img width="1987" height="618" alt="image" src="https://github.com/user-attachments/assets/43fe647c-ff0b-43a3-953d-1c518990d326" />

驗收:
-----------------------------------
<img width="1094" height="633" alt="image" src="https://github.com/user-attachments/assets/210a7482-487a-4ec6-9d55-d7cf3a0605e3" />

API:
-----------------------------------


### `calculate_ball_landing`
#### 功能：
計算球的下一個落點（包括 X, Y 坐標），基於實時的速度、平台位置等變量進行邏輯運算。

#### 參數：
- **ball_x (int)**: 球的 X 座標。
- **ball_y (int)**: 球的 Y 座標。
- **ball_y_speed (int)**: Y 軸速度。
- **ball_x_speed (int)**: X 軸速度。
- **first_nonzero_frame (int, optional)**: 第一幀的時間 (非零幀)。
- **current_frame (int, optional)**: 當前幀的編號。
- **do_print (bool)**: 是否在過程中輸出調試訊息。
- **double_prediction (bool)**: 是否進行雙層預測 (適用於一些模擬情況)。

#### 回傳：
- **tuple**: 具體格式是 `(ball_x_final, ball_y_final, ball_y_speed_temp, ball_x_speed_temp, times)`。

---

### `double_calculate_ball_landing`
#### 功能：
基於 `calculate_ball_landing`，進一步模擬三種不同的物理情況並預測球的落點。

#### 參數：
與 `calculate_ball_landing` 相同，增加：
- **double_calculate**: 活動指令。

#### 回傳：
- **tuple**: `(res_normal, res_cut, res_accel, pre_frame_count)`

---

### `select_best_target`
#### 功能：
根據落點和當前球拍位置，選擇最佳目標位置以增加命中率。

#### 參數：
- **platform_x (int)**: 平台的 X 座標。
- **normal_x, cut_x, accel_x (int)**: 三個預測的 X 落點位置。
- **normal_frame, cut_frame, accel_frame (int)**: 衍生模擬所需幀。
- **pre_frame_count (int)**: 預測的前一幀計數。

#### 回傳：
- **int**: 最佳目標座標。

---

### `MLPlay` 類別
#### 功能：
主要進行遊戲邏輯決策的 AI 類別。
#### 初始方法：
- **`__init__(self, ai_name, *args, **kwargs)`**
  - 初始化特徵：
    - `side`: 決定輪到 1P 還是 2P。
    - 初始化模型 `knn_distance_only.pickle`。

- **方法**
  - **`update(self, scene_info, *args, **kwargs)`**
    - 判斷遊戲邏輯，根據當前場景資訊執行命令，包含以下狀態：
      - `GAME_ALIVE`: 運行時策略。
      - 移動策略：基於落點預測球拍 `MOVE_LEFT`、`MOVE_RIGHT`。

  - **`reset(self)`**
    - 清除遊戲中的緩存狀態。


# KNN 模型訓練報告

## 1. 資料分析

### 資料概況
- **資料總數：** 5,758 筆
- **特徵與標籤欄位：** 
  - `Distance`: 特徵
  - `Action`: 標籤


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

### 分類指標
| 類別   | Precision | Recall | F1-score | Support |
|--------|-----------|--------|----------|---------|
| -1 (`MOVE_LEFT`) | 1.00      | 1.00   | 1.00     | 221     |
| 0 (`NONE`)       | 1.00      | 1.00   | 1.00     | 674     |
| 1 (`MOVE_RIGHT`) | 1.00      | 1.00   | 1.00     | 257     |

- **總體準確率：** 1.00 (100%)

## 4. 決策邊界可視化
- **邊界邏輯：**
  - `NONE (0)` 範圍：-3 至 3 之間
  - `MOVE_LEFT (-1)` 範圍：Distance < -3
  - `MOVE_RIGHT (1)` 範圍：Distance > 3

決策邊界圖
<img width="3790" height="1653" alt="knn_decision_boundary_distance" src="https://github.com/user-attachments/assets/0f4da83a-d586-452f-896f-9856f9f66a7c" />

## 5. 結論
我整體還是以演算法為核心，只是利用把最佳落點與板子x距離的差當特徵求出向左向右不動。

最找特徵是兩個維度的(最佳落點跟板子位置)，但訓練效果還是差一點，所以改用他們的差值當特徵。
<img width="3488" height="1653" alt="image" src="https://github.com/user-attachments/assets/83743d3b-42d2-454d-a83b-ef989cba0c69" />

- **訓練集準確率：** 0.9922 (99.22%)
- **測試集大小：**   0.9905 (99.05%)


   
演算法遊玩
-----------------------------------

[![Watch the video](https://github.com/chjason123/Machine_Learning_final_project/blob/main/ping_pong/Snipaste_2026-01-05_21-50-58.png)](https://youtu.be/0yqKhdfs8F0)
