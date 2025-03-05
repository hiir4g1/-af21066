import math
from pyproj import Proj, transform


def calculate_angle(x1, y1, x2, y2,eorw):
    # 傾きを計算
    m = (y2 - y1) / (x2 - x1)
    
    # 傾きから角度を計算（ラジアン）
    angle_rad = math.atan(m)
    
    # ラジアンから度に変換
    if eorw == 2:
        angle_deg = math.degrees(angle_rad) - 90
    else :
        angle_deg = 90 - math.degrees(angle_rad)
    return angle_deg





def calculate_Q_new(start_coords, end_coords, coords ,distance, eastorwest, utm_epsg="epsg:6677"):
    
    x1 ,y1, _ = start_coords
    x2 ,y2, _ = end_coords
    print(f"coords:{coords}")
    longitude = coords[0]
    latitude = coords[1]
    angle = calculate_angle(x1, y1, x2, y2,eastorwest)
    if eastorwest == 0:
        angle = 180 - angle
    """
    指定した緯度経度から、東から北への指定角度方向に指定距離だけ進んだ新しい緯度経度を求める関数。
    
    Parameters:
    - latitude: 出発点の緯度（度単位）
    - longitude: 出発点の経度（度単位）
    - angle: 進行方向の角度（東から北への角度、度単位）
    - distance: 進む距離（メートル）
    - utm_epsg: 使用するUTM座標系のEPSGコード（デフォルトは"epsg:6677"）

    Returns:
    - 新しい緯度経度 (latitude_new, longitude_new)
    """
    # WGS84座標系（経緯度座標系）を設定
    wgs84 = Proj(init="epsg:4326")
    
    # 指定されたUTM座標系を設定
    utm = Proj(init=utm_epsg)
    
    # 出発点の緯度経度をUTM座標系に変換
    x, y = transform(wgs84, utm, longitude, latitude)
    
    # 進行方向の角度を基に、X成分（東方向）とY成分（北方向）を計算
    x_move = distance * math.cos(math.radians(angle))  # 東方向
    y_move = distance * math.sin(math.radians(angle))  # 北方向

    # 新しい座標を計算
    x_new = x + x_move
    y_new = y + y_move

    # 新しいUTM座標をWGS84経緯度座標系に変換
    longitude_new, latitude_new = transform(utm, wgs84, x_new, y_new)
    
    # 新しい緯度経度を返す
    return [longitude_new, latitude_new]