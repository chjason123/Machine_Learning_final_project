import pandas as pd
import os

# ===== 1. 讀取原始訓練資料 =====
csv_path = r'E:\PAIA\pingpong4\pingpong-knn-ai\logs\knn_train_all.csv'
df = pd.read_csv(csv_path)

print(f"✓ 已載入 {len(df)} 筆資料")
print(f"  欄位: {df.columns. tolist()}")
print()

# ===== 2. 計算 Distance =====
df['Distance'] = df['Target_X'] - df['Platform_X']

print(f"✓ Distance 計算完成")
print(f"  Distance 範圍: [{df['Distance'].min():.1f}, {df['Distance'].max():.1f}]")
print()

# ===== 3. 只保留 Distance 和 Action =====
df_new = df[['Distance', 'Action']].copy()

print(f"✓ 新資料框大小: {df_new. shape}")
print(f"  欄位: {df_new. columns.tolist()}")
print(f"\n前 10 行:")
print(df_new.head(10))
print(f"\nAction 分佈:")
print(df_new['Action'].value_counts())
print()

# ===== 4. 保存新 CSV 檔案 =====
model_dir = os.path.dirname(csv_path)
new_csv_path = os.path.join(model_dir, 'distance_action. csv')

df_new.to_csv(new_csv_path, index=False)

print(f"✓ 新 CSV 檔案已保存: {new_csv_path}")
print(f"  大小: {len(df_new)} 筆資料")