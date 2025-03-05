from qgis.core import *
from PyQt5.QtCore import QVariant


#レイヤーを読み込む関数
def get_layer_by_name(name):
    layers = QgsProject.instance().mapLayersByName(name)
    if not layers:
        raise Exception(f"レイヤー '{name}' が見つかりません")
    return layers[0]

# レイヤー名と緯度経度を渡すと、距離を計算する関数
def calculate_distance_to_route(route_layer_name, latitude, longitude):
    # レイヤーを取得
    route_layer = get_layer_by_name(route_layer_name)
    
    if not route_layer.isValid():
        raise Exception(f"レイヤー '{route_layer_name}' が無効です")
    
    # 点レイヤーを作成
    point_layer = QgsVectorLayer("Point?crs=EPSG:4326", "point_layer", "memory")
    pr = point_layer.dataProvider()
    point_layer.startEditing()

    # 緯度経度から点を作成
    point = QgsPointXY(longitude, latitude)
    point_feature = QgsFeature()
    point_feature.setGeometry(QgsGeometry.fromPointXY(point))

    # 点をレイヤーに追加
    pr.addFeature(point_feature)
    point_layer.commitChanges()

    # ルートレイヤー内の唯一のルートを取得
    route_feature = next(route_layer.getFeatures(), None)

    if route_feature is None:
        raise Exception(f"ルートレイヤー '{route_layer_name}' にルートがありません")

    # ルートのジオメトリを取得
    route_geometry = route_feature.geometry()

    # 点とルート間の最短距離を計算
    distance = route_geometry.distance(point_feature.geometry())

    return distance