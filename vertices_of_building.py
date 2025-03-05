from qgis.core import QgsProject, QgsFeature, QgsGeometry, QgsPointXY, QgsWkbTypes
from qgis.PyQt.QtCore import QVariant
from marker_handler import MarkerHandler


# # 指定した建物レイヤー名
# target_building_layer = '53392577_bldg_6697_2_op — Building'

# # 特定の建物ID
# target_building_id = 1249  # 対象の建物ID

# レイヤーを読み込む関数
def get_layer_by_name(name):
    layers = QgsProject.instance().mapLayersByName(name)
    if not layers:
        raise Exception(f"レイヤー '{name}' が見つかりません")
    return layers[0]

# 特定の建物IDおよび建物レイヤー名に基づいて頂点を抽出する関数
def get_building_vertices_by_layer_and_id(layer_name, target_building_id):
    vertices = set()  # 重複を排除するためにセットを使用
    
    try:
        # レイヤーを取得
        building_layer = get_layer_by_name(layer_name)
    except Exception as e:
        print(f"レイヤーの読み込みエラー: {e}")
        return []

    # 建物のフィーチャーをループ
    for building_feature in building_layer.getFeatures():
        # 建物IDが一致する場合にのみ頂点を抽出
        if building_feature.id() == target_building_id:
            building_geom = building_feature.geometry()

            # 建物のジオメトリがポリゴンの場合のみ頂点を抽出
            if building_geom.type() == QgsWkbTypes.PolygonGeometry:
                # ポリゴンが複数の部分を持つ場合の処理
                if building_geom.isMultipart():
                    for part in building_geom.asGeometryCollection():
                        for vertex in part.vertices():
                            vertices.add((vertex.x(), vertex.y()))  # セットに追加
                else:
                    for vertex in building_geom.vertices():
                        vertices.add((vertex.x(), vertex.y()))  # セットに追加
            else:
                print(f"建物ID {target_building_id} のジオメトリはポリゴンではありません")
                return []
    
    return list(vertices)  # 最後にリストに戻す

# # 対象の建物IDとレイヤー名に基づいて頂点を取得
# building_vertices = get_building_vertices_by_layer_and_id(target_building_layer, target_building_id)

# # 結果を表示
# if building_vertices:
#     print(f"建物ID {target_building_id} の頂点座標（重複なし）:")
#     for vertex in building_vertices:
#         print(vertex)
# else:
#     print(f"建物ID {target_building_id} の頂点は見つかりませんでした。")


# marker_layer_name = "チョー点"
# marker_handler = MarkerHandler(marker_layer_name)
# for x,y in building_vertices:
#     marker_handler.add_marker(x, y, target_building_id)
