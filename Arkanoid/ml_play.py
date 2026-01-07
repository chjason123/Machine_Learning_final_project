import os
import pickle
import csv
import random
import pygame
from sklearn import neighbors


class MLPlay:
    

    def load_data(self):
        """
        載入模型、特徵數據及目標數據
        """
        dir_path = os.path.dirname(__file__)

        # 載入模型
        model_path = os.path.join(dir_path, 'model.pickle')
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            print('Model loaded.')

        # 載入特徵數據
        features_path = os.path.join(dir_path, 'features.pickle')
        if os.path.exists(features_path):
            with open(features_path, 'rb') as f:
                self.features = pickle.load(f)

        # 載入目標數據
        targets_path = os.path.join(dir_path, 'targets.pickle')
        if os.path.exists(targets_path):
            with open(targets_path, 'rb') as f:
                self.targets = pickle.load(f)

    def save_training_data(self):
        """
        儲存訓練所需的特徵與目標數據
        """
        dir_path = os.path.dirname(__file__)
        with open(os.path.join(dir_path, 'features.pickle'), 'wb') as f:
            pickle.dump(self.features, f)
        with open(os.path.join(dir_path, 'targets.pickle'), 'wb') as f:
            pickle.dump(self.targets, f)
        with open(os.path.join(dir_path, 'model.pickle'), 'wb') as f:
            pickle.dump(self.model, f)

    def save_record(self):
        """
        儲存每一局的遊戲記錄
        """
        dir_path = os.path.dirname(__file__)
        with open(os.path.join(dir_path, 'record.csv'), 'w', newline='') as f:
            csv.writer(f, delimiter=',').writerows(self.record)

    def process_training_data(self):
        """
        處理遊戲記錄，提取可用於訓練的數據
        """
        self.record.reverse()
        target_index = None
        for i, data in enumerate(self.record):
            y = data[2]  # 小球的 y 座標
            if 395 - 7 <= y <= 395 + 7:
                target_index = i
                break

        if target_index is not None:
            target_x = self.record[target_index][1]
            for frame, x, y, dx, dy in self.record[target_index:]:
                if dy > 0:
                    self.features.append([x, y, dx, dy])
                    self.targets.append([target_x])
                else:
                    break

    def train_model(self):
        """
        使用 K 最近鄰演算法進行模型訓練
        """
        self.model = neighbors.KNeighborsRegressor(n_neighbors=5, weights='uniform')
        self.model.fit(self.features, self.targets)

    def __init__(self, *args, **kwargs):
        """
        機器學習遊戲代理初始化
        """
        self.model = None
        self.ball_served = False
        self.record = []  # 儲存每一幀的遊戲資訊
        self.features = []
        self.targets = []
        self.load_data()  # 載入模型及訓練數據
        
    def update(self, scene_info, keyboard=None, *args, **kwargs):
        """
        根據遊戲場景生成指令
        """
        if keyboard is None:
            keyboard = []

        # 判斷遊戲是否結束
        if scene_info["status"] in ("GAME_OVER", "GAME_PASS"):
            return "RESET"

        # 發球邏輯
        if not self.ball_served:
            self.ball_served = True
            return "SERVE_TO_RIGHT"

        # 平台操作
        if pygame.K_LEFT in keyboard:
            command = "MOVE_LEFT"
        elif pygame.K_RIGHT in keyboard:
            command = "MOVE_RIGHT"
        else:
            command = "NONE"

        # 擷取小球與平台資訊
        frame, (ball_x, ball_y) = scene_info['frame'], scene_info['ball']
        platform_x = scene_info['platform'][0]
        dx, dy = 0, 0

        # 計算小球速度
        if self.record:
            last_frame, last_x, last_y, last_dx, last_dy = self.record[-1][:5]
            if frame - last_frame == 1:
                dx, dy = ball_x - last_x, ball_y - last_y

        self.record.append([frame, ball_x, ball_y, dx, dy])

        # 模型預測
        if self.model and dy > 0 and ball_y < 395 + 7:
            target_x = self.model.predict([[ball_x, ball_y, dx, dy]])[0]
            if platform_x + 20 > target_x:
                command = "MOVE_LEFT"
            elif platform_x + 20 < target_x:
                command = "MOVE_RIGHT"

        # 隨機行為（小球接近平台時）
        if ball_y >= 395 - 7:
            command = random.choice(["MOVE_LEFT", "MOVE_RIGHT", "NONE"])

        return command

    def reset(self):
        """
        重置遊戲代理的狀態
        """
        self.save_record()
        self.process_training_data()
        self.train_model()
        self.save_training_data()
        self.ball_served = False
        self.record = []