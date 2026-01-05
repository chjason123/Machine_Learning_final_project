GAME_WIDTH = 200
PLATFORM_DEFAULT_WIDTH = 40
PLATFORM_DEFAULT_HIGH = 10
PLATFORM_MARGIN_DEFAULT = 5  # 容錯範圍（像素）
PLATFORM_1P_Y = 420  # 1P 平台高度（y）
PLATFORM_2P_Y = 70   # 2P 平台高度（y）
BALL_SIZE_X = 10
BALL_SIZE_Y = 10

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
            print("ball_x_speed_temp:"+str(ball_x_speed_temp))
            print("ball_y_speed_temp:"+str(ball_y_speed_temp))

        if times /100 == 1:
            if do_print:
                print(times/100)
            times = 0
            ball_x_speed_temp = ball_x_speed_temp +max(-1, min(1, ball_x_speed_temp))
            ball_y_speed_temp = ball_y_speed_temp +max(-1, min(1, ball_y_speed_temp))

        
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
                
                if hit_wall==False:
                    #ball_x_final = ball_x_final + (PLATFORM_1P_Y - ball_high - ball_y_final) * max(-1, min(1, ball_x_speed_temp))
                    ball_x_final = ball_x_final + ball_x_speed_temp
                
                ball_y_final = PLATFORM_1P_Y - ball_high
                ball_y_speed_temp = -1 * ball_y_speed_temp
                if do_print:
                    print(f"times:{times} x:{ball_x_final} y:{ball_y_final} vx:{ball_x_speed_temp} vy:{ball_y_speed_temp} current_frame:{current_frame} first_nonzero_frame:{first_nonzero_frame} times:{times}")
                
                

                if double_prediction:
                    if do_print:
                        print(f"frame_counter: {frame_counter}")
                    return (ball_x_final, ball_y_final, ball_y_speed_temp, ball_x_speed_temp, times, frame_counter)
                else:
                    return (ball_x_final, ball_y_final, ball_y_speed_temp, ball_x_speed_temp, times)
            # 頂部撞擊 (2P)
            elif ball_y_final + ball_y_speed_temp <= PLATFORM_2P_Y + PLATFORM_DEFAULT_HIGH:
                if hit_wall==False:
                    #ball_x_final = ball_x_final + (ball_y_final - PLATFORM_2P_Y - PLATFORM_DEFAULT_HIGH) * max(-1, min(1, ball_x_speed_temp))
                    ball_x_final = ball_x_final + ball_x_speed_temp
                
                ball_y_final = PLATFORM_2P_Y + PLATFORM_DEFAULT_HIGH
                ball_y_speed_temp= -1 * ball_y_speed_temp
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
        
        if double_prediction:
                    if do_print:
                        print(f"frame_counter: {frame_counter}")
        
        frame_counter += 1  # 每次迴圈加一
        times += 1

#def calculate_ball_landing(ball_x, ball_y, ball_y_speed, ball_x_speed,first_nonzero_frame=None, current_frame=None, do_print=False):

def double_calculate_ball_landing(ball_x, ball_y, ball_y_speed, ball_x_speed,
                           first_nonzero_frame=None, current_frame=None, do_print=False):
    result = calculate_ball_landing(
        ball_x, ball_y, ball_y_speed, ball_x_speed,
        first_nonzero_frame, current_frame,
        do_print=do_print, double_prediction=True
    )
    # unpack
    next_ball_x, next_ball_y, next_ball_y_speed, next_ball_x_speed, times ,pre_frame_count = result

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


    return res_normal, res_cut, res_accel , pre_frame_count

# 將測試呼叫包在 main 判斷中
if __name__ == "__main__":
    #double_calculate_ball_landing(75, 80, 23, -23,150, 1839, do_print=True)
    calculate_ball_landing(75, 80, 25, 28,150, 1980, do_print=True)

# calculate_ball_landing(17,80 ,17 ,-17,0,
# filepath: e:\PAIA\pingpong4\collect\cal_v2.py

# calculate_ball_landing(106,80 ,21 ,-21,150, 1595, do_print=True)

# calculate_ball_landing(85,101 ,21 ,-21,150, 1596, do_print=True)