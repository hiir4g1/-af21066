from qgis.core import QgsProject, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer, QgsField, QgsFields, QgsWkbTypes
from qgis.PyQt.QtCore import QVariant
from itertools import groupby
import pandas as pd
from marker_handler import MarkerHandler
from get_start_end_coordinates import get_start_end_coordinates
from get_centroid_from_ID import get_centroid_from_ID
from create_avoidance_point import create_avoidance_point
from create_marker_by_type import create_marker_by_type
from padadf_df_to_routelayer import process_df_and_create_layers
from pandas_to_marker import pandas_to_marker


building_layer_names = ['53392577_bldg_6697_2_op — Building', '53392576_bldg_6697_2_op — Building']
limit_height = 0  # ビルの高さ制限

marker_layer_name = "intersect_maker_2"
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

            print(f"route_layer{route_layer.crs()}")

        except Exception as e:
            print(e)
            continue

        for route_feature in route_layer.getFeatures():
            route_geom = route_feature.geometry()

            for layer_name in building_layer_names:
                try:
                    building_layer = get_layer_by_name(layer_name)
                    print(f"building_layer{building_layer.crs()}")
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

# n番目の要素でまとめる
def group_by_nth_element(data, n):
    # n番目の要素でソート
    sorted_data = sorted(data, key=lambda x: x[n])

    # groupbyを使ってn番目の要素でグループ化
    grouped = groupby(sorted_data, key=lambda x: x[n])

    result = []
    # 結果をリストに格納
    for key, group in grouped:
        group_list = list(group)
        if len(group_list) > 1:  # 同じグループに複数の要素がある場合
            # 最初と最後の要素を取得
            first_item = group_list[0]
            last_item = group_list[-1]
            result.append((first_item, last_item))

    return result

#障害マーカーをタイプ別に分ける
def divide_types(intersecting_points, filtered_buildings):
    # intersecting_points と filtered_buildings をマッチング
    divided_points = [
        item1 for item1 in intersecting_points
        for item2 in filtered_buildings
        if item1[1] == item2[1] and item1[2] == item2[2]
    ]
    
    # ここでの divided_points は、filtered_buildings の項目と一致するものだけを選択する
    for route_layer_name, layer_name, building_id, height, x, y in divided_points:
        print(f"★ルートレイヤー名: {route_layer_name}, ビルレイヤー名: {layer_name}, 建物ID: {building_id}")
    
    # group_by_nth_element を使って、同じ建物IDとレイヤー名でグループ化
    result = group_by_nth_element(divided_points, 2)
    
    type_list = []
    # 結果を処理
    for (route_layer_name1, layer_name1, building_id1, height1, x1, y1), (route_layer_name2, layer_name2, building_id2, height2, x2, y2) in result:
        print(f"★★ルートレイヤー名: {route_layer_name1}, ビルレイヤー名: {layer_name1}, 建物ID: {building_id1}")
        print(f"★★ルートレイヤー名: {route_layer_name2}, ビルレイヤー名: {layer_name2}, 建物ID: {building_id2}")
        
        #ーーー
        start_coords, end_coords = get_start_end_coordinates(route_layer_name1)
        point_coords1 = [x1,y1]
        point_coords2 = [x2,y2]
        #高さを計算
        threshold_height1 = interpolate_height(start_coords,end_coords,point_coords1)
        threshold_height2 = interpolate_height(start_coords,end_coords,point_coords2)
        
        
        #type1が手前だけ重なっている
        #type2が奥だけ重なっている
        #type3が完全に重なっている
        if height1 >= threshold_height1 and height2 < threshold_height2:
            print("type1")
            route_type = 1
        elif height2 >= threshold_height2 and height1 < threshold_height1:
            print("type2")
            route_type = 2
        elif height1 >= threshold_height1 and height2 >= threshold_height2:
            print("type3")
            route_type = 3
        else:
            print("error : cant divide types :( ")
            route_type = 0
        type_list.append((
            (route_layer_name1, layer_name1, building_id1, height1, x1, y1),
            (route_layer_name2, layer_name2,building_id2, height2, x2, y2),
            route_type
        ))
            
        #ーーー
    return type_list

    



#marker_layer_name_2 = "障害建物"
#marker_handler_2 = MarkerHandler(marker_layer_name_2)

# #飛行経路と建物の交点
# intersecting_points = get_intersectintg_point()

# #3次元的に重なっている建物
# filtered_buildings = filter_buildings_by_height(intersecting_points)

# #重なっている建物のタイプを判定する
# type_list = divide_types(intersecting_points, filtered_buildings)
# #print(type_list)

# #type別にマーカーを作成する
# create_marker_by_type(type_list)

# CSVファイルのパス
csv_file_path = 'C:\\Users\\shu\\Documents\\qgis_program\\hotel.csv'

# pandasを使ってCSVファイルを読み込む
df = pd.read_csv(csv_file_path)

# レイヤを作成
process_df_and_create_layers(df)

df["point_type"] = 0

df2 = df
process_df_and_create_layers(df2)

while (True):
    #回避点を作るpadas data frameで回避点を含めた通過点一覧表を返す
    #飛行経路と建物の交点
    intersecting_points = get_intersectintg_point()

    #3次元的に重なっている建物
    filtered_buildings = filter_buildings_by_height(intersecting_points)
    print(f"ffiltered_buildings:\n{filtered_buildings}")

    #重なっている建物のタイプを判定する
    type_list = divide_types(intersecting_points, filtered_buildings)
    print(f"type_list:\n{type_list}")

    #type別にマーカーを作成する
    create_marker_by_type(type_list)
    
    #回避点を作成
    df2 = create_avoidance_point(type_list,10,df,1)

    #回避点を通る飛行経路を作成
    process_df_and_create_layers(df2)

    


    if df.equals(df2):
        break
    df = df2
    
#pandas_to_marker(df2)

df2.to_csv('C:\\Users\\shu\Documents\\qgis_program\\通過点.csv', index=False)

print("OK")

for route_layer_name, layer_name, building_id, height, x, y in filtered_buildings:
    print(f"ルートレイヤー名: {route_layer_name}, ビルレイヤー名: {layer_name}, 建物ID: {building_id}")
    #x, y = get_centroid_from_ID(layer_name, building_id)
    #marker_handler_2.add_marker(x, y, building_id)


