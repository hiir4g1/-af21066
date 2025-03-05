import pandas as pd

def add_point_to_df(df,x, y, z, p,lon1, lat1):
    target_row = df[(df['緯度']  == lon1) & (df['経度'] == lat1)]

    if not target_row.empty:
        # 一致する行が見つかった場合、そのインデックスを取得
        print("一致する行:", target_row)
        index = target_row.index[0]  # インデックスを取得
    else:
        # 一致する行が見つからなかった場合
        print("一致する行は見つかりませんでした。")
        # 新しい行を追加する処理を実行
        index = len(df)  # 新しい行はDataFrameの末尾に追加

    # 新しい行を追加
    new_row = {
        "hotel": "回避点",
        "緯度": y,
        "経度": x,
        "高さ[m]": z,
        "point_type" : p
    }
    print(f"追加する行：{new_row}")

    # インデックスの位置に新しい行を挿入
    df = pd.concat([df.iloc[:index + 1], pd.DataFrame([new_row]), df.iloc[index + 1:]]).reset_index(drop=True)

    return df