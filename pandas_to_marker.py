import pandas as pd
from marker_handler2 import MarkerHandler2

def pandas_to_marker(df,layer_name="通過点"):
    data = []
    for _, row in df.iterrows():
        lat = float(row['緯度'])
        lon = float(row['経度'])
        if row['hotel'] != '回避点':
            height = float(row['高さ[m]']) + 5  # 高さに10mを加える
        else:
            height = float(row['高さ[m]'])
        data.append((lat, lon, height))
    
    pandas_to_marker_handler = MarkerHandler2(layer_name)
    for y, x, z in data:
        pandas_to_marker_handler.add_marker(x, y, z, 0)
    return 0