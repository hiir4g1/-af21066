import math

def calculate_distance(coord1, coord2):
    # 地球の半径（平均）[m]
    R = 6371000  
    
    # 緯度、経度、高さをそれぞれ取り出す（高さがない場合は0に設定）
    lat1, lon1 = coord1[0], coord1[1]
    lat2, lon2 = coord2[0], coord2[1]
    alt1 = coord1[2] if len(coord1) > 2 else 0  # 高さ情報がなければ0
    alt2 = coord2[2] if len(coord2) > 2 else 0  # 高さ情報がなければ0
    
    # ラジアンに変換
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # 高度差
    delta_alt = alt2 - alt1
    
    # ハブの公式
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    
    a = math.sin(delta_lat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # 地表上の2点間の距離
    distance_surface = R * c
    
    # 3次元の距離
    distance = math.sqrt(distance_surface**2 + delta_alt**2)
    
    return distance

# 使用例
coord1 = [35.6895, 139.6917]  # 東京（高さ情報なし）
coord2 = [34.0522, -118.2437, 0] # ロサンゼルス（高さ情報あり）
distance = calculate_distance(coord1, coord2)
print(f"距離: {distance} m")
