import pandas as pd
import math
#from csv_to_routelayer import create_route_layer
from get_start_end_coordinates import get_start_end_coordinates
from vertices_of_building import get_building_vertices_by_layer_and_id
from calculate_distance import calculate_distance
from check_point_position import cross_product, check_point_position, is_angle_rop_larger
from add_point_to_df import add_point_to_df

from calculate_distance_to_route import calculate_distance_to_route
from calculate_Q_new import calculate_Q_new


# 度をラジアンに変換
def deg_to_rad(deg):
    return deg * math.pi / 180

# ラジアンを度に変換
def rad_to_deg(rad):
    return rad * 180 / math.pi

# 球面上の点と大円弧の距離を求める関数
def spherical_distance(lat1, lng1, lat2, lng2, latQ, lngQ):
    # 緯度経度をラジアンに変換
    lat1, lng1 = deg_to_rad(lat1), deg_to_rad(lng1)
    lat2, lng2 = deg_to_rad(lat2), deg_to_rad(lng2)
    latQ, lngQ = deg_to_rad(latQ), deg_to_rad(lngQ)

    # 球面上の点 P1-P2 と Q との最短距離を計算
    dPQ = math.acos(math.sin(lat1) * math.sin(latQ) +
                    math.cos(lat1) * math.cos(latQ) * math.cos(lngQ - lng1))
    
    # P1からP2までの大円弧上にQの垂線の足を求め、距離を算出
    cross_track_distance = math.asin(math.sin(dPQ) * math.sin(lng2 - lng1))
    earth_radius_m = 6371000  # 地球の半径をメートル単位で設定
    return abs(cross_track_distance) * earth_radius_m

# 2点間の球面距離を計算する関数（地球の半径を考慮）
def spherical_distance_2(lat1, lng1, lat2, lng2):
    # 緯度経度をラジアンに変換
    lat1, lng1 = deg_to_rad(lat1), deg_to_rad(lng1)
    lat2, lng2 = deg_to_rad(lat2), deg_to_rad(lng2)

    # 球面距離（大円弧の距離）を計算
    d = math.acos(math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lng2 - lng1))
    earth_radius_m = 6371000  # 地球の半径（メートル）
    return d * earth_radius_m

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # 地球の半径 (メートル単位)
    
    # 度からラジアンに変換
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # ハーサイン公式
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # 距離 (メートル)
    distance = R * c
    return distance

# 直線と点Qの距離を求める関数
def distance_from_point_to_line(lat1, lon1, lat2, lon2, X, Y):
    # 緯度・経度をラジアンに変換
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    
    # 直線の方程式の係数 A, B, C を計算
    A = math.sin(phi2 - phi1)
    B = math.cos(phi1) * math.cos(phi2)
    C = lat2 * lon1 - lat1 * lon2
    
    # 点Q(X, Y)と直線lとの距離を求める
    distance = abs(A * X + B * Y + C) / math.sqrt(A**2 + B**2)
    
    # 距離をメートルで返す
    return distance


def check_east_west(lat1, lon1, lat2, lon2, y, x):
    # 外積を計算して、上側か下側かを判定
    cross = (lat2 - lat1) * (y - lon1) - (lon2 - lon1) * (x - lat1)
    
    # 飛行経路が北向きまたは南向きかを判定
    if lat2 > lat1:  # 北向き
        if cross >= 0:  # 左側（西側）
            return 1
        else:  # 右側（東側）
            return 2
    elif lat2 < lat1:  # 南向き
        if cross >= 0:  # 左側（東側）
            return 2
        else:  # 右側（西側）
            return 1
    else:
        return 1 # 緯度が変化しない場合

    
# 建物の横側を通ってよける場合の回避点の座標を計算する関数
def calculate_Q(start_coords, end_coords, coords, D):
    x1 ,y1, _ = start_coords
    x2 ,y2, _ = end_coords
    print(f"coords:{coords}")
    px = coords[0]
    py = coords[1]

    # 1度あたりの距離（赤道上）を計算
    degrees_per_meter = 1 / (111.32 * 1000)  # 1度あたりの距離（メートル単位）
    
    # Dメートルに対応する経度・緯度の変化量を計算
    degrees_to_move = D * degrees_per_meter

    # 直線の傾きを計算
    if x2 - x1 == 0:  # 垂直線の場合
        slope_L = None
        slope_perpendicular = 0
    else:
        slope_L = (y2 - y1) / (x2 - x1)
        slope_perpendicular = -1 / slope_L if slope_L != 0 else None

    # 垂直線上の2点を計算
    if slope_perpendicular is None:
        qx1, qy1 = px, py + degrees_to_move  # 北方向にDメートル
        qx2, qy2 = px, py - degrees_to_move  # 南方向にDメートル
    elif slope_perpendicular == 0:
        qx1, qy1 = px + degrees_to_move, py  # 東方向にDメートル
        qx2, qy2 = px - degrees_to_move, py  # 西方向にDメートル
    else:
        dx = degrees_to_move / math.sqrt(1 + slope_perpendicular ** 2)
        dy = slope_perpendicular * dx
        qx1, qy1 = px + dx, py + dy  # 1つ目の点
        qx2, qy2 = px - dx, py - dy  # 2つ目の点

    # 距離を計算して、最も近い点を選択
    dist1 = calculate_distance([x1, y1], [qx1, qy1])
    dist2 = calculate_distance([x1, y1], [qx2, qy2])

    if dist1 > dist2:
        qx, qy = qx1, qy1
    else:
        qx, qy = qx2, qy2

    return [qx, qy]

#回避点を作成する関数
#第三引数に何かを入れるとオプションがつけれる
def create_avoidance_point(data,dist,df,arg=None):

    print("実行中")
    print("最初のリスト")
    print(df)
    print("_____________")
    
    if arg != None:
        route_ID_key = set()
    
    for( info1, info2, route_type)in data:
        (route_layer_name1, layer_name1, building_id1, hight1, x1, y1) = info1
        (route_layer_name2, layer_name2, building_id2, hight2, x2, y2) = info2
        
        new_row_list = []
        start_coords, end_coords = get_start_end_coordinates(route_layer_name1)
        lat1 ,lon1, _ = start_coords
        lat2 ,lon2, _ = end_coords
        
        if arg != None:
            if route_layer_name1 in route_ID_key:
                continue
            else:
                route_ID_key.add(route_layer_name1)
        
        #type1
        if route_type == 1:
            new_x = x1
            new_y = y1
            new_z = hight1 + dist
            #new_row_list.append([new_x, new_y, new_z])
            df = add_point_to_df(df, new_x, new_y, new_z, 1, lon1, lat1)

        #type2
        elif route_type == 2:
            new_x = x2
            new_y = y2
            new_z = hight2 + dist
            new_row_list.append([new_x, new_y, new_z])
            df = add_point_to_df(df, new_x, new_y, new_z, 2, lon1, lat1)
            
        #type3
        elif route_type == 3:
                        
            # 対象の建物IDとレイヤー名に基づいて頂点を取得
            building_vertices = get_building_vertices_by_layer_and_id(layer_name1, building_id1)
            
            # 結果を表示
            if building_vertices:
                print(f"建物ID {building_id1} の頂点座標（重複なし）:")
                for vertex in building_vertices:
                    print(vertex)
            
            divide_bilding_vertices = []

            from marker_handler import MarkerHandler
            marker_layer_name = "頂点座標(重複なし)"
            marker_handler_頂点座標 = MarkerHandler(marker_layer_name)




            #飛行経路の片側ともう片側に分ける
            for x,y in building_vertices:
                print(f"lat1, lon1, lat2, lon2, x, y : {lat1, lon1, lat2, lon2, x, y}")
                marker_handler_頂点座標.add_marker(x,y,0)
                #distance = distance_from_point_to_line(lat1, lon1, lat2, lon2, x, y)

                distance = calculate_distance_to_route(route_layer_name1,y,x)

                '''
                #外積を計算
                cross = (lat2 - lat1) * (y - lon1) - (lon2 - lon1) * (x - lat1)
                #建物の頂点の座標が飛行経路の上側か下側かを判定
                #上側だったら1,下側だったら2をリストに追加
                if cross >= 0:
                    divide_bilding_vertices.append((x,y,1,distance))
                elif cross < 0:
                    divide_bilding_vertices.append((x,y,2,distance))
                else:
                    print("どちらでもないで候、どこかおかしいで候")
                '''
                divide_bilding_vertices.append((x, y, check_east_west(lat1, lon1, lat2, lon2, y, x),distance))



            print("type分けした後")
            print(divide_bilding_vertices)
            #上側と下側で分ける
            filtered_list_1 = [item for item in divide_bilding_vertices if item[2] == 1]
            filtered_list_2 = [item for item in divide_bilding_vertices if item[2] == 2]
            # distanceの最大値を持つ要素を探す
            max_distance_item_1 = max(filtered_list_1, key=lambda x: x[3])
            max_distance_item_2 = max(filtered_list_2, key=lambda x: x[3])
            #直線との距離が近かったほうを代入
            if max_distance_item_1[3] > max_distance_item_2[3]:
                final_max_distance_item = max_distance_item_2
            elif max_distance_item_1[3] < max_distance_item_2[3]:
                final_max_distance_item = max_distance_item_1
            elif max_distance_item_1[3] == max_distance_item_2[3]:
                print("同じ距離: ",max_distance_item_1,", ",max_distance_item_2)
                final_max_distance_item = max_distance_item_1
            else:
                print("直線との距離を求めることが出来ませんTT")
            print(f"final_max_distance_item : {final_max_distance_item}")
            #横の距離を比較するところまでは出来たよん
            #縦と横で比較する
            #別のファイルに縦横高さを渡したら距離を求める関数を作成してね→作ったよ
            sum_around = 0
            sum_over = 0
            
            #建物の上を通るときの飛行距離を計算する
            start_to_point1 = [x1, y1, hight1 + dist]
            point1_to_point2 = [x2, y2, hight2 + dist]
            point2_to_end = end_coords
            
            distance_start_to_point1 = calculate_distance(start_coords, start_to_point1)
            distance_point1_to_point2 = calculate_distance(start_to_point1, point1_to_point2)
            distance_point2_to_end = calculate_distance(point1_to_point2, point2_to_end)
            
            sum_over = distance_start_to_point1 + distance_point1_to_point2 + distance_point2_to_end
            
            
            #建物の横を通る時の計算
            #回避点を何処に作るかを工夫する必要あり
            final_max_distance_check_item = []
            '''

            for info01 in divide_bilding_vertices:
                x,y,_,_ = info01
                if check_point_position([lon1,lat1],[lon2,lat2],[final_max_distance_item[0],final_max_distance_item[1]],[x,y]):
                    if is_angle_rop_larger([lon1,lat1],[lon2,lat2],[x,y],[final_max_distance_item[0],final_max_distance_item[1]]):
                        final_max_distance_check_item.append(tuple(info01))
            '''
            around_point_list = []
            '''
            print("final_max_distance_check_item")
            print(final_max_distance_check_item)
            '''

            if final_max_distance_check_item:
                final_max_distance_check_item.append(tuple(final_max_distance_item))
                for info02 in final_max_distance_check_item:
                    print("info02")
                    print(info02)
                    x, y, eorw,_ = info02
                    around_xy_point = calculate_Q_new(start_coords, end_coords, info02, dist,eorw)
                    distance1 = calculate_distance([start_coords[0],start_coords[1]],around_xy_point)
                    distance2 = calculate_distance([end_coords[0],end_coords[1]],around_xy_point)
                    around_z = (distance2*hight1+distance1*hight2)/(distance1+distance2)
                    around_point_list.append((around_xy_point[0],around_xy_point[1],around_z))
                for i  in range(len(around_point_list)-1):
                    sum_around = sum_around + calculate_distance(around_point_list[i],around_point_list[i+1])
                sum_around = sum_around + calculate_distance(start_coords,around_point_list[0])
                sum_around = sum_around + calculate_distance(around_point_list[-1],end_coords)
            else:
                around_xy_point = calculate_Q_new(start_coords, end_coords, final_max_distance_item, dist, final_max_distance_item[2])
                distance1 = calculate_distance([start_coords[0],start_coords[1]],around_xy_point)
                distance2 = calculate_distance([end_coords[0],end_coords[1]],around_xy_point)
                around_z = (distance2*hight1+distance1*hight2)/(distance1+distance2)
                around_point_list.append((around_xy_point[0],around_xy_point[1],around_z))
                sum_around = calculate_distance(start_coords,around_point_list[0])+ calculate_distance(around_point_list[0],end_coords)
            
            print(f"around:{sum_around} over:{sum_over}")
            # if len(around_point_list) > 1:
            #     for i  in range(len(around_point_list)-1):
            #         sum_around = sum_around + calculate_distance(around_point_list[i],around_point_list[i+1])
            #     sum_around = sum_around + calculate_distance(start_coords,around_point_list[0])
            #     sum_around = sum_around + calculate_distance(around_point_list[-1],end_coords)
            # else :
            #     sum_around = calculate_distance(start_coords,around_point_list[0])+ calculate_distance(around_point_list[0],end_coords)
            
            
            #sum_around = calculate_distance(start_coords,around_point) + calculate_distance(around_point,end_coords)
            
            # if sum_over < sum_around:
            #     new_row_list.extend([start_to_point1,point1_to_point2])
            # elif sum_around < sum_over:
            #     new_row_list.append(around_point)
            # elif sum_around == sum_over:
            #     print(f"{start_to_point1},{point1_to_point2}と{around_point}のどちらの回避点でも同じ距離です。")
            #     new_row_list.append(around_point)
            # else:
            #     print("error : type3の回避点の作成に失敗")
            
            # if sum_over < sum_around:
            #     print("上に避けます")
            #     #new_row_list.extend([start_to_point1,point1_to_point2])
            #     df = add_point_to_df(df, *start_to_point1, 3, lon1, lat1)
            #     print("あいうえおtesttest")
            #     print(f"lon1 : {start_to_point1[0]} lat : {start_to_point1[1]}")
            #     df = add_point_to_df(df, *point1_to_point2, 4, start_to_point1[1], start_to_point1[0])
            # elif sum_around < sum_over:
            #     #new_row_list.append(around_point)
            #     print("横によけます")
            #     count = 0
            #     for list in around_point_list:
            #         if len(around_point_list) == 1:
            #            df = add_point_to_df(df,*list,5,lon1, lat1)
            #         else:
            #             if count == 0:
            #                 df = add_point_to_df(df,*list,i+6,lon1, lat1)
            #             else:
            #                 df = add_point_to_df(df,*list,i+6,list[count-1][0], list[count-1][1])
            # elif sum_around == sum_over:
            #     print(f"{start_to_point1},{point1_to_point2}と{around_point_list}のどちらの回避点でも同じ距離です。")
            #     df = add_point_to_df(df, *start_to_point1, 3, lon1, lat1)
            #     df = add_point_to_df(df, *point1_to_point2, 4, start_to_point1[0], start_to_point1[1])
            # else:
            #     print("error : type3の回避点の作成に失敗")
            

            # if sum_over < sum_around:
            #     print("上に避けます")
            #     #new_row_list.extend([start_to_point1,point1_to_point2])
            #     df = add_point_to_df(df, *start_to_point1, 3, lon1, lat1)
            #     print("あいうえおtesttest")
            #     print(f"lon1 : {start_to_point1[0]} lat : {start_to_point1[1]}")
            #     df = add_point_to_df(df, *point1_to_point2, 4, start_to_point1[1], start_to_point1[0])
            # elif sum_around < sum_over:
            #     #new_row_list.append(around_point)

            if sum_over < sum_around:
                print("上に避けます")
                #new_row_list.extend([start_to_point1,point1_to_point2])
                df = add_point_to_df(df, *start_to_point1, 3, lon1, lat1)
                print("あいうえおtesttest")
                print(f"lon1 : {start_to_point1[0]} lat : {start_to_point1[1]}")
                df = add_point_to_df(df, *point1_to_point2, 4, start_to_point1[1], start_to_point1[0])
            
            elif sum_around < sum_over:
                print("横によけます")
                count = 0
                for list in around_point_list:
                    if len(around_point_list) == 1:
                        df = add_point_to_df(df,*list,5,lon1, lat1)
                    else:
                        print("???")
                        print(list)
                        if count == 0:
                            df = add_point_to_df(df,*list,6,lon1, lat1)
                            
                        else:
                            df = add_point_to_df(df,*list,7,around_point_list[count-1][0], around_point_list[count-1][1])
                    count = count + 1


            # print("横によけます")
            # count = 0
            # for list in around_point_list:
            #     if len(around_point_list) == 1:
            #         df = add_point_to_df(df,*list,5,lon1, lat1)
            #     else:
            #         print("???")
            #         print(list)
            #         if count == 0:
            #             df = add_point_to_df(df,*list,6,lon1, lat1)
                        
            #         else:
            #             df = add_point_to_df(df,*list,7,around_point_list[count-1][0], around_point_list[count-1][1])
            #     count = count + 1

            
            # elif sum_around == sum_over:
            #     print(f"{start_to_point1},{point1_to_point2}と{around_point_list}のどちらの回避点でも同じ距離です。")
            #     df = add_point_to_df(df, *start_to_point1, 3, lon1, lat1)
            #     df = add_point_to_df(df, *point1_to_point2, 4, start_to_point1[0], start_to_point1[1])
            # else:
            #     print("error : type3の回避点の作成に失敗")



            #new_x, new_y, new_z の取り扱いで検討する必要あり
            #new_x, new_y, new_z をリストにするのはどうだろうか
        # for x, y, z in new_row_list:
        #     # 緯度経度で一致する行を検索
        #     target_row = df[(df['緯度'] == lon1) & (df['経度'] == lat1)]

        #     if not target_row.empty:
        #         # 一致する行が見つかった場合、そのインデックスを取得
        #         print("一致する行:", target_row)
        #         index = target_row.index[0]  # インデックスを取得
        #     else:
        #         # 一致する行が見つからなかった場合
        #         print("一致する行は見つかりませんでした。")
        #         # 新しい行を追加する処理を実行
        #         index = len(df)  # 新しい行はDataFrameの末尾に追加
            
        #     # 新しい行を追加
        #     new_row = {
        #         "hotel": "回避点",
        #         "緯度": y,
        #         "経度": x,
        #         "高さ[m]": z
        #     }
        #     print(f"追加する行：{new_row}")

        #     # インデックスの位置に新しい行を挿入
        #     df = pd.concat([df.iloc[:index + 1], pd.DataFrame([new_row]), df.iloc[index + 1:]]).reset_index(drop=True)

    print(df)
        
        
    return df