import os
import time
import random
import sys
import pickle
import sys
import numpy
import sklearn
#print(sklearn.__version__)
# 如果系統找不到 numpy._core，就手動指向 numpy
if not hasattr(numpy, "_core"):
    sys.modules["numpy._core"] = numpy
# 常數定義（來自 pong_ball_simulation.py）
GAME_WIDTH = 200
PLATFORM_DEFAULT_WIDTH = 40
PLATFORM_DEFAULT_HIGH = 10
PLATFORM_MARGIN_DEFAULT = 5  # 容錯範圍（像素）
PLATFORM_1P_Y = 420  # 1P 平台高度（y）
PLATFORM_2P_Y = 70   # 2P 平台高度（y）
BALL_SIZE_X = 10
BALL_SIZE_Y = 10

# 全局變數（來自 pong_ball_simulation.py）
ball_x_final = 0
ball_x_old = 0
ball_y_final = 0
ball_y_old = 0
ball_y_speed_temp = 0
ball_x_speed_temp = 0
ball_high = 0
ball_width = 0
times = 0
player_temp = 0


def calculate_ball_landing(ball_x, ball_y, ball_y_speed, ball_x_speed,
                           first_nonzero_frame=None, current_frame=None, do_print=False, double_prediction=False):
    """計算球的落點位置"""
    global player_temp, ball_x_final, ball_x_old, ball_y_final, ball_y_old
    global ball_y_speed_temp, ball_x_speed_temp, ball_high, ball_width, times

    ball_x_final = ball_x
    ball_x_old = ball_x
    ball_y_final = ball_y
    ball_y_old = ball_y
    ball_y_speed_temp = ball_y_speed
    ball_x_speed_temp = ball_x_speed
    ball_high = BALL_SIZE_Y
    ball_width = BALL_SIZE_X

    frame_counter = 0  # 新增 frame_counter

    try:
        if first_nonzero_frame is not None and current_frame is not None: 
            times = (int(current_frame) - int(first_nonzero_frame)) % 100 + 1
            if do_print:
                print("initial times:" + str(times))
        else:
            times = 0
    except Exception: 
        times = 0

    if (int(current_frame) - int(first_nonzero_frame)) % 100 == 0 and (int(current_frame) - int(first_nonzero_frame)) / 100 != 0:
        ball_x_speed_temp = ball_x_speed_temp + max(-1, min(1, ball_x_speed_temp))
        ball_y_speed_temp = ball_y_speed_temp + max(-1, min(1, ball_y_speed_temp))
    
    # 判斷接觸用的 y 值（微調避免邊界誤判）
    contact_y_1P = PLATFORM_1P_Y - BALL_SIZE_Y - 1
    contact_y_2P = PLATFORM_2P_Y + BALL_SIZE_Y + 1

    max_iters = 1000
    while True:
        # --- 每個模擬步計算是否需要套用 speed increments ---
        
        if do_print:
            print("ball_x_speed_temp: "+str(ball_x_speed_temp))
            print("ball_y_speed_temp:"+str(ball_y_speed_temp))

        if times /100 == 1:
            if do_print:
                print(times/100)
            times = 0
            ball_x_speed_temp = ball_x_speed_temp + max(-1, min(1, ball_x_speed_temp))
            ball_y_speed_temp = ball_y_speed_temp + max(-1, min(1, ball_y_speed_temp))

        
        # 底部撞擊 (1P)
        if (ball_high + ball_y_final) + ball_y_speed_temp >= PLATFORM_1P_Y or (ball_y_final + ball_y_speed_temp <= PLATFORM_2P_Y + PLATFORM_DEFAULT_HIGH) or ((ball_x_final + ball_width) + ball_x_speed_temp >= GAME_WIDTH) or (ball_x_final + ball_x_speed_temp <= 0):
            
            hit_wall = False
            # 模擬一步（含左右牆反彈）
            
            if (ball_x_final + ball_width) + ball_x_speed_temp >= GAME_WIDTH: 
                ball_x_final = GAME_WIDTH - ball_width
                ball_x_speed_temp = -1 * ball_x_speed_temp
                hit_wall = True   
            elif ball_x_final + ball_x_speed_temp <= 0:
                ball_x_final = 0
                ball_x_speed_temp = -1 * ball_x_speed_temp
                hit_wall = True


            if (ball_high + ball_y_final) + ball_y_speed_temp >= PLATFORM_1P_Y: 
                
                if hit_wall == False:
                    ball_x_final = ball_x_final + ball_x_speed_temp
                
                ball_y_final = PLATFORM_1P_Y - ball_high
                ball_y_speed_temp = -1 * ball_y_speed_temp
                if do_print:
                    print(f"times:{times} x:{ball_x_final} y:{ball_y_final} vx:{ball_x_speed_temp} vy:{ball_y_speed_temp} current_frame:{current_frame} first_nonzero_frame:{first_nonzero_frame} times:{times}")
                
                if double_prediction:
                    if do_print:
                        print(f"frame_counter:  {frame_counter}")
                    return (ball_x_final, ball_y_final, ball_y_speed_temp, ball_x_speed_temp, times, frame_counter)
                else: 
                    return (ball_x_final, ball_y_final, ball_y_speed_temp, ball_x_speed_temp, times)
            
            # 頂部撞擊 (2P)
            elif ball_y_final + ball_y_speed_temp <= PLATFORM_2P_Y + PLATFORM_DEFAULT_HIGH: 
                if hit_wall == False:
                    ball_x_final = ball_x_final + ball_x_speed_temp
                
                ball_y_final = PLATFORM_2P_Y + PLATFORM_DEFAULT_HIGH
                ball_y_speed_temp = -1 * ball_y_speed_temp
                if do_print:
                    print(f"times:{times} x:{ball_x_final} y:{ball_y_final} vx:{ball_x_speed_temp} vy:{ball_y_speed_temp} current_frame:{current_frame} first_nonzero_frame:{first_nonzero_frame} times:{times}")

                if double_prediction:
                    if do_print:
                        print(f"frame_counter: {frame_counter}")
                    return (ball_x_final, ball_y_final, ball_y_speed_temp, ball_x_speed_temp, times, frame_counter)
                else:
                    return (ball_x_final, ball_y_final, ball_y_speed_temp, ball_x_speed_temp, times)
            else:
                ball_y_final = ball_y_final + ball_y_speed_temp
        else:
            ball_x_final = ball_x_final + ball_x_speed_temp
            ball_y_final = ball_y_final + ball_y_speed_temp

        
        if do_print:
            print(f"times:{times} x:{ball_x_final} y:{ball_y_final} vx:{ball_x_speed_temp} vy:{ball_y_speed_temp} current_frame:{current_frame} first_nonzero_frame:{first_nonzero_frame} times:{times}")
        
        frame_counter += 1  # 每次迴圈加一
        times += 1


def double_calculate_ball_landing(ball_x, ball_y, ball_y_speed, ball_x_speed,
                           first_nonzero_frame=None, current_frame=None, do_print=False):
    """預測三種不同情況下的球落點"""
    result = calculate_ball_landing(
        ball_x, ball_y, ball_y_speed, ball_x_speed,
        first_nonzero_frame, current_frame,
        do_print=do_print, double_prediction=True
    )
    # unpack
    next_ball_x, next_ball_y, next_ball_y_speed, next_ball_x_speed, times, pre_frame_count = result

    # 預測三種落點
    res_normal = calculate_ball_landing(
        next_ball_x, next_ball_y, next_ball_y_speed, next_ball_x_speed,
        first_nonzero_frame=0, current_frame=times, 
        do_print=do_print, double_prediction=True
    )
    vx_cut = -1 * next_ball_x_speed
    res_cut = calculate_ball_landing(
        next_ball_x, next_ball_y, next_ball_y_speed, vx_cut,
        first_nonzero_frame=0, current_frame=times, 
        do_print=do_print, double_prediction=True
    )
    if next_ball_x_speed > 0:
        vx_accel = next_ball_x_speed + 3
    elif next_ball_x_speed < 0:
        vx_accel = next_ball_x_speed - 3
    else:
        vx_accel = 3
    res_accel = calculate_ball_landing(
        next_ball_x, next_ball_y, next_ball_y_speed, vx_accel,
        first_nonzero_frame=0, current_frame=times, 
        do_print=do_print, double_prediction=True
    )

    return res_normal, res_cut, res_accel, pre_frame_count


def select_best_target(platform_x, normal_x, cut_x, accel_x, normal_frame, cut_frame, accel_frame, pre_frame_count):
    """選擇最佳目標位置"""
    GAME_WIDTH = 200
    PLATFORM_ERROR = 6  # 球拍誤差 6
    PLATFORM_DEFAULT_WIDTH = 20
    max_move = pre_frame_count * 5
    min_x = max(platform_x - max_move, 0)
    max_x = min(platform_x + max_move, GAME_WIDTH - PLATFORM_DEFAULT_WIDTH)

    # 從min_x到max_x之間，找出能覆蓋最多落點的x座標
    candidates = []
    # 球拍每次只能動5格，所以在可移動範圍內每5格取一個點來評估
    for target_x in range(int(min_x), int(max_x) + 5, 5):
        count = 0
        is_cover_normal = False
        sum_dist = 0
        for idx, (pred_x, frame) in enumerate([(normal_x, normal_frame), (cut_x, cut_frame), (accel_x, accel_frame)]):
            if pred_x is not None and frame is not None:
                move_range = frame * 5
                # 板子可移動範圍 + 板子寬度
                if (abs(target_x - pred_x) <= move_range or
                    (pred_x >= target_x and pred_x <= target_x + move_range + PLATFORM_ERROR-1) or
                    (pred_x <= target_x and pred_x >= target_x - move_range - PLATFORM_ERROR+1)):
                    count += 1
                    sum_dist += abs(target_x - pred_x)
                    if idx == 0:
                        is_cover_normal = True
        # 若沒覆蓋任何點，sum_dist 設為極大值，避免被選到
        if count == 0:
            sum_dist = float('inf')
        candidates.append((count, sum_dist, is_cover_normal, target_x))

    # 排序：
    # 1. 覆蓋最多點（count, 降冪）
    # 2. 距離總和最小（sum_dist, 升冪）
    # 3. 若覆蓋點數 < 3，優先覆蓋 normal_x（is_cover_normal, 降冪）
    max_count = max([c[0] for c in candidates]) if candidates else 0
    if max_count < 3:
        # 覆蓋點數較少時，優先覆蓋 normal_x
        candidates. sort(key=lambda x: (-x[0], -x[2], x[1]))
    else:
        # 覆蓋最多點時，優先距離總和最小
        candidates.sort(key=lambda x: (-x[0], x[1]))
    best_target = candidates[0][3] if candidates else platform_x

    return best_target


class MLPlay:
    """主要 AI 控制類"""
    def __init__(self, ai_name, *args, **kwargs):
        self.side = ai_name

        # 確定模型檔案的路徑，使用程式執行檔案所在目錄
        model_path = os.path.join(os.path.dirname(__file__), "knn_distance_only.pickle")
        
        # 確保模型檔案存在
        if not os.path.exists(model_path):  # 檢查路徑是否存在
            raise FileNotFoundError(f"模型檔案不存在: {model_path}")
        
        # 讀取模型
        with open(model_path, 'rb') as f:
            self.AI_Model = pickle.load(f)
        self.time = int(time.time())
        self.cached_prediction = None
        self.first_nonzero_frame = None  # 初始化變數

        # 發球相關
        self.serve_target_x = None  # 以「平台中心座標」為參考
        self.serve_command = None
        #test_input = [[-20], [0], [20]]
        #prediction = self.AI_Model.predict(test_input)
        #print(prediction)  # 假設模型做回歸，可能輸出為: [-19.5, 0.0, 20.5]
        #print(type(prediction))  # <class 'numpy.ndarray'>
    
    def update(self, scene_info, *args, **kwargs):
        # 當遊戲非進行中時，直接回傳 RESET（reset() 會被呼叫來清除狀態）
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"

        # 預設三種落點為 None，避免 UnboundLocalError
        p_norm, p_cut, p_accel = None, None, None
        pre_frame_count = 0

        current_frame = scene_info["frame"]
        ball_x = scene_info["ball"][0]
        ball_y = scene_info["ball"][1]
        speed_x = scene_info["ball_speed"][0]
        speed_y = scene_info["ball_speed"][1]

        # 判斷發球幀 (first_nonzero_frame)
        if speed_y == 0:
            self.first_nonzero_frame = None
        elif self.first_nonzero_frame is None:
            self.first_nonzero_frame = current_frame

        # 常數（與 select_best_target 保持一致）
        GAME_WIDTH = 200
        PLATFORM_DEFAULT_WIDTH = 20
        PLATFORM_CENTER_OFFSET = PLATFORM_DEFAULT_WIDTH // 2  # 20//2 = 10

        if self.side == "1P":
            raw_platform_x = scene_info["platform_1P"][0]
        else:
            raw_platform_x = scene_info["platform_2P"][0]

        # 使用平台「中心」作為 my_platform_x（確保與 target_x 的參考系一致）
        my_platform_x = raw_platform_x + PLATFORM_CENTER_OFFSET

        if self.side == "1P": 
            is_ball_coming = speed_y > 0
        else:
            is_ball_coming = speed_y < 0

        command = "NONE"
        target_x = 100

        if speed_y == 0:
            # 發球/靜止狀態：使用隨機位置發球邏輯
            # 若還沒有選擇發球目標，則隨機選擇一個位置與方向
            if self.serve_target_x is None:
                # 先選平台左邊可放範圍，再轉成「平台中心」座標
                left_x = random.randint(0, GAME_WIDTH - PLATFORM_DEFAULT_WIDTH)
                self.serve_target_x = left_x + PLATFORM_CENTER_OFFSET
                # 隨機選發球方向（game engine 接受的指令）
                self.serve_command = random.choice(["SERVE_TO_LEFT", "SERVE_TO_RIGHT"])

            movement_command = self.AI_Model.predict([[self.serve_target_x-my_platform_x]])   # 計算預測

            if movement_command ==  -1:
                return "MOVE_LEFT"
            elif movement_command == 1:
                return "MOVE_RIGHT"
            else:
                return self.serve_command


        elif is_ball_coming:
            # 球朝我方來，清除 cached prediction（下一輪由對手打過來）
            self.cached_prediction = None
            start_frame = self.first_nonzero_frame if self.first_nonzero_frame is not None else current_frame
            res = calculate_ball_landing(ball_x, ball_y, speed_y, speed_x, start_frame, current_frame)
            if res:
                target_x = res[0]
            else:
                target_x = 100

            # 移動指令（在球來時也可移動靠近預測落點）
            #print(str(target_x-my_platform_x))
            movement_command = self.AI_Model.predict([[target_x-my_platform_x]])   # 計算預測
            #print(movement_command)
            if movement_command ==  -1:
                return "MOVE_LEFT"
            elif movement_command == 1:
                return "MOVE_RIGHT"
            else:
                return "NONE"

        else:
            # 球離開我方（飛向對手）時，嘗試使用 cached prediction 或 double calculate
            if self.cached_prediction is None:
                start_frame = self.first_nonzero_frame if self.first_nonzero_frame is not None else current_frame
                res = double_calculate_ball_landing(ball_x, ball_y, speed_y, speed_x, start_frame, current_frame)
                if res:
                    res_normal, res_cut, res_accel, pre_frame_count = res
                    self.cached_prediction = (res_normal, res_cut, res_accel, pre_frame_count + 1)
                else: 
                    self.cached_prediction = (None, None, None, 0)
            p_norm, p_cut, p_accel, pre_frame_count = self. cached_prediction

            # 計算三種落點與目前球拍距離
            candidates = []
            for pred in [p_norm, p_cut, p_accel]:
                if pred: 
                    pred_x = pred[0]
                    dist = abs(my_platform_x - pred_x)
                    candidates.append((dist, pred_x, pred))
            target_x = select_best_target(
                my_platform_x,
                p_norm[0] if p_norm else None,
                p_cut[0] if p_cut else None,
                p_accel[0] if p_accel else None,
                p_norm[-1] if p_norm else None,
                p_cut[-1] if p_cut else None,
                p_accel[-1] if p_accel else None,
                pre_frame_count
            )
            # 讓 pre_frame_count 隨球移動逐幀遞減，最小為 0
            if pre_frame_count > 0:
                pre_frame_count -= 1
            # 更新 cached_prediction 以便下次使用
            self.cached_prediction = (p_norm, p_cut, p_accel, pre_frame_count)
            movement_command = self.AI_Model.predict([[target_x-my_platform_x]])   # 計算預測
            

            if movement_command ==  -1:
                return "MOVE_LEFT"
            elif movement_command == 1:
                return "MOVE_RIGHT"
            else:
                return "NONE"

    def reset(self):
        """清除暫存狀態與緩存（為下一回合準備）"""
        self.cached_prediction = None
        self. first_nonzero_frame = None
        self.serve_target_x = None
        self.serve_command = None
        return


