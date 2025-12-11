# Arkanoid 打磚塊 — 訓練資料規格與需求文件
版本：v1.0  
日期：2025-11-26  



功能:
-----------------------------------
- 球拍左移右移。
- 發球方向。
- 預測球的反彈軌跡。
- 通關Lv1~Lv20。

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
        elif (ball_high + ball_y_final) + ball_y_speed_temp >= PLATFORM_1P_Y:
            ball_x_final = ball_x_final + ball_x_speed_temp
            ball_y_final = PLATFORM_1P_Y - ball_high 
            print(''.join([str(x) for x in ['times :', times, '  x:', ball_x_final, 'y:', ball_y_final, '  x_speed:', ball_x_speed_temp, '  y_speed:', ball_y_speed_temp]]))
            return (ball_x_final, ball_y_final)
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

分析(BreakDown):
-----------------------------------
<img width="1567" height="940" alt="image" src="https://github.com/user-attachments/assets/2f47529c-7e8f-4959-934b-e3e9e28293a0" />


設計流程:
-----------------------------------
<img width="1123" height="598" alt="image" src="https://github.com/user-attachments/assets/27e57981-f56e-4c4f-9b18-f9d5c334e18e" />



架構圖:
-----------------------------------
<img width="1951" height="723" alt="image" src="https://github.com/user-attachments/assets/89f4def0-ea5f-4671-b855-d525219e49e5" />




