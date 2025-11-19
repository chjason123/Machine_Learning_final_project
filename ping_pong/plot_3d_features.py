#!/usr/bin/env python3
"""
plot_3d_features.py

說明：
  讀入 CSV（預設檔名 mlplay_training_data.csv），
  將每個 frame（偵數）作為 X 軸、各項特徵（feature）作為 Y 軸、特徵數值作為 Z 軸，
  繪製 3D surface（或 wireframe）圖並輸出成檔案與顯示。

用法範例：
  python plot_3d_features.py --csv mlplay_training_data.csv --downsample 5 --out plot.png

參數：
  --csv        CSV 路徑（預設 mlplay_training_data.csv）
  --downsample 每 N 個 frames 取一個以加速繪圖（預設 1，不下採樣）
  --out        輸出圖檔 (png)，若省略則不存檔
  --surface    若指定為 0 則改用 wireframe（預設 surface）

需求套件：
  pandas, numpy, matplotlib
  pip install pandas numpy matplotlib
"""

import argparse
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (needed for 3D projection)


def load_and_prepare(csv_path: str):
    # 讀 CSV
    try:
        df = pd.read_csv(csv_path, low_memory=False)
    except Exception as e:
        print(f"無法讀取 CSV：{e}", file=sys.stderr)
        raise

    if 'frame' not in df.columns:
        raise ValueError("CSV 中找不到 'frame' 欄位，請確認檔案格式。")

    # 將 frame 轉為整數（可能有空值或非數值）
    df['frame'] = pd.to_numeric(df['frame'], errors='coerce')
    df = df.dropna(subset=['frame'])
    df['frame'] = df['frame'].astype(int)

    # 排除 timestamp（如果存在），因為它不是一個用於繪圖的特徵
    excluded = {'timestamp'}
    features = [c for c in df.columns if c not in excluded and c != 'frame']

    if not features:
        raise ValueError("沒有可用的特徵欄位來繪圖。")

    # 處理每一個特徵：數值欄保留；類別欄轉為 category code
    df2 = df[['frame']].copy()
    for feat in features:
        col = df[feat]
        if pd.api.types.is_numeric_dtype(col):
            # 轉數值（可能含 NaN）
            df2[feat] = pd.to_numeric(col, errors='coerce')
        else:
            # 類別型：轉成 ordinal code（NaN 會變為 -1，改為 np.nan）
            cat = pd.Categorical(col)
            codes = pd.Series(cat.codes).replace(-1, np.nan)
            df2[feat] = codes.astype(float)

    # 以 frame 分組取平均（若同一偵數有多列）
    grouped = df2.groupby('frame').mean().sort_index()
    # grouped 的 index 是 frame， columns 是 features
    return grouped


def downsample_df(df: pd.DataFrame, step: int):
    if step <= 1:
        return df
    # 只取 index 的每 step
    idx = df.index.to_numpy()
    take = idx[::step]
    return df.loc[take]


def plot_3d_surface(grouped: pd.DataFrame, out_path: str = None, surface: bool = True):
    frames = grouped.index.to_numpy()
    features = grouped.columns.tolist()

    if frames.size == 0 or len(features) == 0:
        raise ValueError("沒有足夠資料來繪圖。")

    # Z 要是 shape (n_features, n_frames) 才好做 meshgrid (Y 為 features)
    Z = grouped.values.T  # shape (n_features, n_frames)

    # 建立網格：X 為 frames 的 mesh，Y 為 feature index 的 mesh
    F_idx = np.arange(len(features))
    X, Y = np.meshgrid(frames, F_idx)  # X shape (n_features, n_frames), Y shape (n_features, n_frames)

    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_subplot(111, projection='3d')

    # 處理 NaN：plot_surface 不接受 NaN，替換為 0（或可改為插值）
    Z_plot = np.nan_to_num(Z, nan=np.nanmean(Z) if np.isfinite(np.nanmean(Z)) else 0.0)

    if surface:
        surf = ax.plot_surface(X, Y, Z_plot, cmap='viridis', edgecolor='none', rstride=1, cstride=1, antialiased=True)
        fig.colorbar(surf, shrink=0.6, aspect=12, pad=0.1, label='feature value')
    else:
        ax.plot_wireframe(X, Y, Z_plot, rstride=1, cstride=1)

    # 設定軸標籤
    ax.set_xlabel('frame')
    ax.set_ylabel('features')
    ax.set_zlabel('value')

    # 把 feature 的名稱放在 y 軸刻度上
    ax.set_yticks(F_idx)
    # 若 feature 名稱過長或過多，縮小字型並旋轉顯示
    ax.set_yticklabels(features, fontsize=8)

    # 調整視角，讓圖看起來較直觀
    ax.view_init(elev=45, azim=-120)

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=200)
        print(f"已儲存圖檔：{out_path}")
    plt.show()


def plot_3d_lines(grouped: pd.DataFrame, out_path: str = None):
    frames = grouped.index.to_numpy()
    features = grouped.columns.tolist()

    if frames.size == 0 or len(features) == 0:
        raise ValueError("沒有足夠資料來繪圖。")

    # Z 要是 shape (n_features, n_frames)
    Z = grouped.values.T  # shape (n_features, n_frames)

    # 建立網格：X 為 frames，Y 為 feature index
    F_idx = np.arange(len(features))
    X, Y = np.meshgrid(frames, F_idx)

    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_subplot(111, projection='3d')

    # 繪製每個特徵的折線圖
    for i, feature in enumerate(features):
        ax.plot(X[i], Y[i], Z[i], label=feature)

    # 設定軸標籤
    ax.set_xlabel('frame')
    ax.set_ylabel('features')
    ax.set_zlabel('value')

    # 把 feature 的名稱放在 y 軸刻度上
    ax.set_yticks(F_idx)
    ax.set_yticklabels(features, fontsize=8)

    # 調整視角
    ax.view_init(elev=45, azim=-120)

    # 顯示圖例
    ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1.05, 1))

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=200)
        print(f"已儲存圖檔：{out_path}")
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="將 CSV 的 frames x features x values 繪成 3D 圖")
    parser.add_argument("--csv", type=str, default="mlplay_training_data.csv", help="CSV 檔案路徑")
    parser.add_argument("--downsample", type=int, default=1, help="每 N 個 frames 取一個（預設 1，不下採樣）")
    parser.add_argument("--out", type=str, default=None, help="輸出圖檔 (png)，若省略則只顯示不存檔")
    args = parser.parse_args()

    grouped = load_and_prepare(args.csv)
    if args.downsample and args.downsample > 1:
        grouped = downsample_df(grouped, args.downsample)
        print(f"已對 frames 進行每 {args.downsample} 下採樣，結果 frames 數：{len(grouped)}")

    plot_3d_lines(grouped, out_path=args.out)


if __name__ == "__main__":
    main()