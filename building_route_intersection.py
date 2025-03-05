from qgis.core import QgsProject, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer, QgsField, QgsFields, QgsWkbTypes
from qgis.PyQt.QtCore import QVariant
from marker_handler import MarkerHandler
from get_start_end_coordinates import get_start_end_coordinates
from get_centroid_from_ID import get_centroid_from_ID


building_layer_names = ['53392577_bldg_6697_2_op — Building', '53392576_bldg_6697_2_op — Building']
limit_height = 0  # ビルの高さ制限

marker_layer_name = "intersect_maker"
marker_handler = MarkerHandler(marker_layer_name)

# 複数のルートレイヤーを取得
route_layer_names = []
for layer in QgsProject.instance().mapLayers().values():
    if layer.name().startswith("Route"):
        route_layer_names.append(layer.name())

#レイヤーを読み込む関数
def get_layer_by_name(name):
    layers = QgsProject.instance().mapLayersByName(name)
    if not layers:
        raise Exception(f"レイヤー '{name}' が見つかりません")
    return layers[0]


#交点を求めてマーカーを作成する関数
#[route_layer_name, layer_name, building_id, height, x, y]in intersecting_points
def get_intersectintg_point():
    #交点の情報を入れるリスト
    intersecting_points = []

    #交点を求めてマーカーを作成
    for route_layer_name in route_layer_names:
        try:
            route_layer = get_layer_by_name(route_layer_name)
        except Exception as e:
            print(e)
            continue

        for route_feature in route_layer.getFeatures():
            route_geom = route_feature.geometry()

            for layer_name in building_layer_names:
                try:
                    building_layer = get_layer_by_name(layer_name)
                except Exception as e:
                    print(e)
                    continue

                for building_feature in building_layer.getFeatures():
                    building_geom = building_feature.geometry()
                    try:
                        height = building_feature['measuredHeight']
                    except KeyError:
                        print(f"フィールド 'measuredHeight' が見つかりません")
                        continue

                    if building_geom.intersects(route_geom):
                        intersection = building_geom.intersection(route_geom)

                        if intersection.isEmpty():
                            continue

                        geom_type = intersection.type()

                        if geom_type == QgsWkbTypes.PointGeometry:
                            point = intersection.asPoint()
                            x, y = point.x(), point.y()
                            if height >= limit_height:
                                intersecting_points.append((route_layer_name, layer_name, building_feature.id(), height, x, y))
                                marker_handler.add_marker(x, y, building_feature.id())

                        elif geom_type == QgsWkbTypes.LineGeometry or geom_type == QgsWkbTypes.CurveGeometry:
                            if intersection.isMultipart():
                                for line in intersection.asMultiPolyline():
                                    for point in line:
                                        x, y = point.x(), point.y()
                                        if height >= limit_height:
                                            intersecting_points.append((route_layer_name, layer_name, building_feature.id(), height, x, y))
                                            marker_handler.add_marker(x, y, building_feature.id())
                            else:
                                for point in intersection.asPolyline():
                                    x, y = point.x(), point.y()
                                    if height >= limit_height:
                                        intersecting_points.append((route_layer_name, layer_name, building_feature.id(), height, x, y))
                                        marker_handler.add_marker(x, y, building_feature.id())

                        elif geom_type == QgsWkbTypes.PolygonGeometry:
                            centroid = intersection.centroid().asPoint()
                            x, y = centroid.x(), centroid.y()
                            if height >= limit_height:
                                intersecting_points.append((route_layer_name, layer_name, building_feature.id(), height, x, y))
                                marker_handler.add_marker(x, y, building_feature.id())

                        elif geom_type == QgsWkbTypes.MultiLineStringGeometry:
                            for line in intersection.asMultiPolyline():
                                for point in line:
                                    x, y = point.x(), point.y()
                                    if height >= limit_height:
                                        intersecting_points.append((route_layer_name, layer_name, building_feature.id(), height, x, y))
                                        marker_handler.add_marker(x, y, building_feature.id())
                                        
    return intersecting_points



#線形補完を使い、間の点の座標でのラインの高さを計算する
def interpolate_height(point1, point2, target_point):
    lat1, lon1, height1 = point1
    lat2, lon2, height2 = point2
    target_lat, target_lon = target_point

    # 緯度経度の距離を計算するための単純な近似
    distance1 = ((lat2 - target_lat) ** 2 + (lon2 - target_lon) ** 2) ** 0.5
    distance2 = ((lat1 - target_lat) ** 2 + (lon1 - target_lon) ** 2) ** 0.5

    # 総距離
    total_distance = distance1 + distance2

    # 高さの線形補間
    if total_distance == 0:
        return height1  # 重なっている場合
    height = (height1 * distance1 + height2 * distance2) / total_distance
    return height



#重なっている建物を判定する
def filter_buildings_by_height(intersecting_points):
    
    # 結果を保存するリスト
    filtered_buildings = []
    
    # 表示済みの (建物ID, ビルレイヤー) の組み合わせを記録するセット
    displayed_building_keys = set()

    # 高さでフィルタリングし、かつ重複する建物ID + レイヤー名は1つだけ表示する
    for route_layer_name, layer_name, building_id, height, x, y in intersecting_points:
        start_coords, end_coords = get_start_end_coordinates(route_layer_name)
        point_coords = [x,y]
        #高さを計算
        threshold_height = interpolate_height(start_coords,end_coords,point_coords)
        # 重複チェックのために (建物ID, ビルレイヤー名) のペアを作成
        building_key = (building_id, layer_name)
        
        # 高さがラインの高さ以上で、かつまだ表示されていない建物ID + レイヤー名のペアを追加
        if height > threshold_height and building_key not in displayed_building_keys:
            # フィルタ結果に追加
            filtered_buildings.append((route_layer_name, layer_name, building_id, height, x, y))
            # 表示済みのキーをセットに追加
            displayed_building_keys.add(building_key)
            print(f"(建物の高さ,ラインの高さ)  ({height}, {threshold_height})")
    return filtered_buildings



marker_layer_name_2 = "障害建物"
marker_handler_2 = MarkerHandler(marker_layer_name_2)
intersecting_points = get_intersectintg_point()
filtered_buildings = filter_buildings_by_height(intersecting_points)

for route_layer_name, layer_name, building_id, height, x, y in filtered_buildings:
    print(f"ルートレイヤー名: {route_layer_name}, ビルレイヤー名: {layer_name}, 建物ID: {building_id}")
    x, y = get_centroid_from_ID(layer_name, building_id)
    marker_handler_2.add_marker(x, y, building_id)


