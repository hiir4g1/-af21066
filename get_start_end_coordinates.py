#ルートレイヤーから最初と最後の座標を返すプログラム
from qgis.core import QgsProject, QgsFeature, QgsGeometry

def get_start_end_coordinates(layer_name):
    # レイヤーを取得
    layer = QgsProject.instance().mapLayersByName(layer_name)
    
    if not layer:
        print(f"Layer '{layer_name}' not found.")
        return None, None

    layer = layer[0]  # 最初のレイヤーを取得

    # 最初のフィーチャーを取得
    feature = next(layer.getFeatures())  # 最初のフィーチャーを取得

    # 線ジオメトリを取得
    geometry = feature.geometry()

    # 頂点を取得
    points = list(geometry.vertices())  # すべての頂点をリストに変換

    # 始点と終点の座標を取得
    if points:
        start_point = points[0]  # 始点
        end_point = points[-1]    # 終点

        # 座標を別々のリストで返す
        start_coords = [start_point.x(), start_point.y(), start_point.z()]
        end_coords = [end_point.x(), end_point.y(), end_point.z()]

        return start_coords, end_coords
    else:
        print("No points found in the geometry.")
        return None, None

# 使用例
# start_coords, end_coords = get_start_end_coordinates('Route_14')
# if start_coords and end_coords:
#     print(f"Start Coordinates: {start_coords}")
#     print(f"End Coordinates: {end_coords}")