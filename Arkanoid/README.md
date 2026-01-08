# Arkanoid 打磚塊(KNN 回歸)




功能:
-----------------------------------
- 球拍左移右移。
- 預測球落點。
- 通關關卡。

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
| 板子| 40 * 10 |
| 球 | 10 * 10 |
| 磚塊、硬磚塊   | 25 * 10 |

初始位置
| 物件名稱 | 初始位置 |
|---|---|
| 板子 | [80, 400] |
| 球 | [95, 390] |

移動速度（每幀像素）
| 物件名稱 | 移動速度 [每幀(像素)] |
|---|---:|
| 板子 | 5 |
| 球（初始） | 7 |

註：位址皆已左上角 (0,0) 為原點。




介面:
-----------------------------------



- 遊戲資訊 scene_info 的資料格式如下
```
{
  "frame": 0,
  "status": "GAME_ALIVE",
  "ball": [ 93, 395],
  "ball_served": false,
  "platform": [ 75, 400],
  "bricks": [
    [ 50, 60],
    ...,
    [125, 80]
  ],
  "hard_bricks": [
    [ 35, 50],
    ...,
    [135, 90]
  ]
}
```
- frame：遊戲畫面更新的編號
- ball：(x, y) tuple。球的位置。
- ball_served：true or false 布林值 boolean。表示是否已經發球。
- platform：(x, y) tuple。平台的位置。
- bricks：為一個 list，裡面每個元素皆為 (x, y) tuple。剩餘的普通磚塊的位置，包含被打過一次的硬磚塊。
- hard_bricks：為一個 list，裡面每個元素皆為 (x, y) tuple。剩餘的硬磚塊位置。
- status： 目前遊戲的狀態
- - GAME_ALIVE：遊戲進行中
- - GAME_PASS：所有磚塊都被破壞
- - GAME_OVER：平台無法接到球

---
模型 K 最近鄰回歸（K Nearest Neighbors Regressor, KNN 回歸）:
-----------------------------------
```
self.model = neighbors.KNeighborsRegressor(n_neighbors=5, weights='uniform')
```
監督式機器學習
在 KNN 回歸中，當需要對一個新的樣本進行預測時，模型會：
找出與該樣本「特徵距離最近」的 K 個鄰居；
使用這些鄰居的目標值（如上例中表達的 targetX）來進行「平均值預測」（或基於其他權重計算的加權平均）。
參數說明

### n_neighbors=5
含義：K 最近鄰中的 K 值，用於決定將從訓練集中選擇「最近的 5 個鄰居」作為預測基礎。
選擇 5 的原因：
K 值過小（如 1 或 2）：容易受噪聲影響，模型可能過擬合。
K 值過大：可能會納入來自很遠的鄰居，導致模型的預測平滑化，減少靈敏度，甚至可能受干擾。
選擇 5 作為預設，表示取 5 個鄰居，使模型在「平滑性」與「靈敏度」之間取得平衡。

### weights='uniform'
含義：「影響預測值的每個鄰居的權重」。
選項：
uniform：均等權重，所有鄰居對預測值的貢獻相同，每個鄰居的目標值被平均計算。
distance：基於距離加權，鄰近的樣本會有更高的權重，遠近樣本影響力遞減。
為什麼選擇 uniform？
目前的特徵（小球的座標和速度）在數據分布上具有一致性，因此採用均等權重。

## 特徵與目標

過濾有效的樣本：
從 record 中篩選出關鍵幀，這些幀包含小球接近並到達平台的路徑數據。

### 目標（targetX）
當小球的高度 (y) 位於距離平台範圍（395 - 7 <= y <= 395 + 7）時：
找出這個瞬間小球的 x 座標作為目標（targetX）。
### 特徵（Features）
跟蹤小球在該幀之前的運動軌跡，提取其位置與速度（x, y, dx, dy）。
僅當小球正在下降（dy > 0）時，將這些數據作為訓練樣本。

設計流程:
-----------------------------------
<img width="1076" height="532" alt="image" src="https://github.com/user-attachments/assets/492090d0-c41b-4571-b15f-e903e51055f4" />



分析(BreakDown):
-----------------------------------
<img width="1873" height="740" alt="image" src="https://github.com/user-attachments/assets/19a77976-0999-4493-a9ee-6a7dbd20d4ee" />



架構圖:
-----------------------------------
<img width="2164" height="458" alt="image" src="https://github.com/user-attachments/assets/39593da3-68a1-40cd-939d-8af6dc5228da" />

程式:
<img width="2164" height="458" alt="image" src="https://github.com/user-attachments/assets/9510b435-430b-4b42-bf50-dcad90ccbec4" />


API:
----
| 函數名稱                       | 輸入                      | 輸出                  | 功能說明                                         |
|--------------------------------|---------------------------|-----------------------|------------------------------------------------|
| `load_data()`              | `features.pickle`、`targets.pickle`、`model.pickle`  | 無                    | 載入模型、訓練數據（features.pickle、targets.pickle）。   |
| `save_training_data()`     | 已訓練數據：features、targets | `features.pickle`、`targets.pickle`、`model.pickle` | 儲存特徵數據、目標數據，以及模型。                   |
| `save_record()`            | `record`                | `record.csv`         | 保存遊戲記錄到 CSV 檔案中。                          |
| `process_training_data()`  | `record`                | `features` 和 `targets` | 處理記錄以提取特徵和目標數據，用於模型訓練。                 |
| `train_model()`            | `features` 和 `targets` | 已訓練的模型           | 使用 K 最近鄰演算法建立機器學習模型。                      |

特徵分布圖:
----
座標 : 球的 x左標，與y做標 ，以及x方向速度
<img width="899" height="795" alt="image" src="https://github.com/user-attachments/assets/066cc05c-1fee-45b4-acb6-0b662eb93148" />

### 結論:
----

1. **模型的現有表現**：
   - 該模型能夠完成基本的任務，例如判斷小球的運動軌跡，並準確接到球。
   - 然而，模型並未對遊戲中的磚塊位置進行判斷，因此無法基於磚塊的分佈採取策略性行動。

2. **不足之處**：
   - 有時模型可能會卡在場地邊緣，導致操作失誤。
   - 當發球時，模型並未考慮到磚塊的位置，較大程度上缺少策略性，這直接影響了通關效率。

3. **提升空間**：
   - **訓練發球模型**：可以針對發球進行專門訓練，讓模型能根據磚塊的位置選擇發球方向，從而增加擊中更多磚塊的概率。
   - **考慮磚塊狀況**：將磚塊的位置、數量等資訊加入特徵數據，讓模型能根據當前局面的不同進行策略調整。

4. **發球策略的重要性**：
   - 發球策略對通關結果的影響很大。如果能根據磚塊的位置進行精確發球，則可顯著提高遊戲效率與成功率。

### 影片:
----
#### 卡牆角:
https://github.com/user-attachments/assets/2c709be5-bc71-48eb-92ef-9d3e6decbda7



#### 通關:


https://github.com/user-attachments/assets/e2ebd865-4509-43b3-bed5-46f4bf65373f




https://github.com/user-attachments/assets/9562781c-3dd7-4e42-a475-f9d6175ab469


