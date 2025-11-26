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
    global player_temp, ball_x_final, ball_x_old, ball_y_final, ball_y_old, ball_y_speed_temp, ball_x_speed_temp, ball_high, ball_width
    ball_x_final = ball_x
    ball_x_old = ball_x
    ball_y_final = ball_y
    ball_y_old = ball_y
    ball_y_speed_temp = ball_y_speed
    ball_x_speed_temp = ball_x_speed
    ball_high = BALL_SIZE_Y
    ball_width = BALL_SIZE_X

    # 調整接觸判斷：避免球「剛好落在板子範圍」造成誤判
    contact_y_1P = PLATFORM_1P_Y - BALL_SIZE_Y - 1
    contact_y_2P = PLATFORM_2P_Y + BALL_SIZE_Y + 1

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
        elif (ball_high + ball_y_final) + ball_y_speed_temp > PLATFORM_1P_Y:
            ball_x_final = ball_x_final + min(max(ball_x_speed_temp, -1), 1) * (PLATFORM_1P_Y -1 - (ball_high + ball_y_final))
            ball_y_final = PLATFORM_1P_Y - ball_high - 1
        # 頂部撞擊 (2P)
        elif ball_y_final + ball_y_speed_temp <= PLATFORM_2P_Y + BALL_SIZE_Y:
            ball_x_final = ball_x_final + min(max(ball_x_speed_temp, -1), 1) * (ball_y_final - (PLATFORM_2P_Y + BALL_SIZE_Y + 1))
            ball_y_final = PLATFORM_2P_Y + BALL_SIZE_Y + 1
        else:
            ball_x_final = ball_x_final + ball_x_speed_temp
            ball_y_final = ball_y_final + ball_y_speed_temp


        # 停止條件：碰到任一平台接觸 y（使用調整後的 contact_y）
        if ball_y_final == contact_y_1P or ball_y_final == contact_y_2P:
            return (ball_x_final, ball_y_final)
```
---

- 模型回傳動作指令

MOVE_LEFT：將板子往左移
MOVE_RIGHT：將板子往右移
NONE：無動作



