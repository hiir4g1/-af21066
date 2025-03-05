# 必要なモジュールのインポート
from qgis.core import QgsProject, QgsFeatureRequest, QgsPointXY
from marker_handler import MarkerHandler

# 指定したレイヤー名と建物IDから2D重心を取得する関数
def get_centroid_from_ID(building_layer_name, building_id):
    # ビルのレイヤーを取得
    building_layers = QgsProject.instance().mapLayersByName(building_layer_name)
    
    if not building_layers:
        print(f"Error: Layer '{building_layer_name}' not found.")
        return None
    
    building_layer = building_layers[0]
    
    # フィーチャのIDを使って建物のフィーチャを取得
    feature_request = QgsFeatureRequest().setFilterFid(building_id)
    feature = next(building_layer.getFeatures(feature_request), None)
    
    if feature is None:
        print(f"Error: Feature with ID {building_id} not found in layer '{building_layer_name}'.")
        return None
    
    # ジオメトリを取得
    building_geom = feature.geometry()
    
    # 2Dの重心を計算
    centroid = building_geom.centroid()
    
    if centroid.isEmpty():
        print(f"Error: Centroid could not be calculated for feature {building_id} in layer '{building_layer_name}'.")
        return None
    else:
        point = centroid.asPoint()
        x, y = point.x(), point.y()
        print(f"Building ID: {building_id} in layer '{building_layer_name}', Centroid coordinates: ({x}, {y})")
        
        # 重心座標にマーカーを追加
        return x, y