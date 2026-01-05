import pandas as pd
import pickle
import os
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import numpy as np
import matplotlib.pyplot as plt

# ===== 1. 讀取 CSV =====
feature_path = r'E:\PAIA\pingpong4\pingpong-knn-ai\logs\Distanc.csv'
label_path = r'E:\PAIA\pingpong4\pingpong-knn-ai\logs\Action.csv'
feature_df = pd.read_csv(feature_path)
label_df = pd.read_csv(label_path)

# 合併特徵和標籤資料
df = pd.concat([feature_df, label_df], axis=1)

print(f"✓ 已載入 {len(df)} 筆資料")
print(f"  欄位: {df.columns.tolist()}")
print(f"\n前 5 行:")
print(df.head())
print(f"\nDistance 範圍: [{df['Distance'].min():.1f}, {df['Distance'].max():.1f}]")
print(f"\nAction 分佈:")
print(df['Action'].value_counts())
print()

# ===== 2. 準備特徵和標籤 =====
X = df[['Distance']].values
y = df['Action'].values

print(f"✓ 特徵形狀: {X.shape}")
print(f"✓ 標籤形狀: {y.shape}\n")

# ===== 3. 分割訓練集和測試集 =====
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"✓ 訓練集大小: {len(X_train)}")
print(f"✓ 測試集大小:  {len(X_test)}\n")

# ===== 4. 訓練 KNN 模型 =====
# 使用 KNeighborsClassifier，設置 n_neighbors 為 5
model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train, y_train)
print("✓ 模型訓練完成\n")

# ===== 5. 評估模型 =====
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

train_accuracy = accuracy_score(y_train, y_pred_train)
test_accuracy = accuracy_score(y_test, y_pred_test)

print(f"✓ 訓練集準確度: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
print(f"✓ 測試集準確度:   {test_accuracy:.4f} ({test_accuracy*100:.2f}%)\n")

print("混淆矩陣:")
print(confusion_matrix(y_test, y_pred_test))
print("\n分類報告:")
print(classification_report(y_test, y_pred_test))

# ===== 6. 保存模型 =====
model_dir = os.path.dirname(feature_path)
model_path = os.path.join(model_dir, 'knn_distance_only.pickle')

with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print(f"✓ 模型已保存: {model_path}\n")

# ===== 7. 測試預測 =====
print("\n" + "=" * 50)
print("測試預測結果:")
print("=" * 50)

label_mapping = {-1: 'MOVE_LEFT', 0: 'NONE', 1: 'MOVE_RIGHT'}  # 類別映射
test_distances = [-50, -20, -10, -5, -3, 0, 3, 5, 10, 20, 50]
for distance in test_distances:
    prediction = model.predict([[distance]])[0]
    action_label = label_mapping.get(prediction, f"未知類別: {prediction}")
    print(f"Distance = {distance: 4d} → Action = {action_label}")

# ===== 8. 可視化決策邊界 =====
print("\n✓ 正在生成決策邊界圖...")

fig, ax = plt.subplots(figsize=(14, 6))

# 繪製原始資料
for action in sorted(df['Action'].unique()):
    mask = df['Action'] == action
    action_data = df[mask]['Distance'].values
    
    # 使用 Action 數值作為顯示 y 軸，無需抖動
    ax.scatter(action_data,
               [action] * len(action_data),  # y 軸使用 action 值
               label=f"Action: {action}",
               alpha=0.5,
               s=30)

# 繪製決策邊界
x_range = np.linspace(df['Distance'].min() - 10, df['Distance'].max() + 10, 500)
y_pred = model.predict(x_range.reshape(-1, 1))

# 定義顏色字典
colors = {
    -1: '#2ecc71',  # MOVE_LEFT
     0: '#f39c12',  # NONE
     1: '#3498db',  # MOVE_RIGHT
}

for i in range(len(x_range) - 1):
    pred_class = y_pred[i]
    if pred_class not in colors:
        print(f"警告: 類別 '{pred_class}' 的顏色未定義，將使用預設顏色。")
        color = '#000000'  # 預設為黑色
    else:
        color = colors[pred_class]

    # 繪製每一段橫向的顏色區間
    ax.axvspan(x_range[i], x_range[i+1], color=color, alpha=0.15)

# 添加參考線
ax.axvline(x=-3, color='red', linestyle='--', linewidth=2, label='Distance = -3 (left boundary)')
ax.axvline(x=3, color='red', linestyle='--', linewidth=2, label='Distance = +3 (right boundary)')

# 修改縱軸和標題
ax.set_yticks([-1, 0, 1])  # 設定縱軸為 Action 標籤值
ax.set_yticklabels(['MOVE_LEFT (-1)', 'NONE (0)', 'MOVE_RIGHT (1)'], fontsize=11)
ax.set_xlabel('Distance (Target_X - Platform_X)', fontsize=12, fontweight='bold')
ax.set_ylabel('Action', fontsize=12, fontweight='bold')
ax.set_title('Decision Boundary Analysis (Distance Feature)', fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=11)
ax.grid(True, alpha=0.3)

boundary_path = os.path.join(model_dir, 'knn_decision_boundary_distance.png')
plt.savefig(boundary_path, dpi=300, bbox_inches='tight')
print(f"✓ 決策邊界圖已保存: {boundary_path}")
plt.close()