import csv
import pandas as pd
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPoint, QgsField
from PyQt5.QtCore import QVariant

# 指定された2つの座標を結ぶルートレイヤーを作成する関数
def create_route_layer(coord1, coord2, layer_name):
    # :param coord1: 1つ目の座標（タプルまたはリスト）(lat, lon, height)
    # :param coord2: 2つ目の座標（タプルまたはリスト）(lat, lon, height)
    # :param layer_name: レイヤー名（文字列）

    # 同じ名前のレイヤーがすでに存在する場合、そのレイヤーを削除
    existing_layers = QgsProject.instance().mapLayersByName(layer_name)
    for existing_layer in existing_layers:
        QgsProject.instance().removeMapLayer(existing_layer)

    # レイヤの作成
    layer = QgsVectorLayer('LineStringZ?crs=EPSG:4326', layer_name, 'memory')
    provider = layer.dataProvider()

    # フィールドの追加
    provider.addAttributes([
        QgsField('start_lat', QVariant.Double),
        QgsField('start_lon', QVariant.Double),
        QgsField('start_height', QVariant.Double),
        QgsField('end_lat', QVariant.Double),
        QgsField('end_lon', QVariant.Double),
        QgsField('end_height', QVariant.Double)
    ])
    layer.updateFields()

    # 座標をQgsPointに変換
    point1 = QgsPoint(coord1[1], coord1[0], coord1[2])  #(lon, lat, height)
    point2 = QgsPoint(coord2[1], coord2[0], coord2[2])  #(lon, lat, height)

    # LineStringジオメトリの作成
    line = QgsGeometry.fromPolyline([point1, point2])

    # フィーチャの作成
    feature = QgsFeature()
    feature.setGeometry(line)

    # 属性値の設定
    feature.setAttributes([coord1[0], coord1[1], coord1[2], coord2[0], coord2[1], coord2[2]])

    # フィーチャの追加
    provider.addFeature(feature)
    layer.updateExtents()

    # レイヤをQGISプロジェクトに追加
    QgsProject.instance().addMapLayer(layer)

    # QGISのマップキャンバスをリフレッシュしてビューを更新
    #iface.mapCanvas().refresh()
    
    
# 新たに作成した関数
def process_df_and_create_layers(df):
    # DataFrameから必要なデータを抽出
    data = []
    for _, row in df.iterrows():
        lat = float(row['緯度'])
        lon = float(row['経度'])
        if row['hotel'] != '回避点':
            height = float(row['高さ[m]']) + 3  # 高さにXmを加える
        else:
            height = float(row['高さ[m]'])
        data.append((lat, lon, height))

    # 各ルートごとにレイヤを作成
    for i in range(len(data)):
        if i == len(data) - 1:
            point1 = data[i]
            point2 = data[0]  # 最後の地点と最初の地点を結ぶ
        else:
            point1 = data[i]
            point2 = data[i + 1]  # 次の地点と結ぶ
        create_route_layer(point1, point2, f'Route_{i + 1}')
        print(f"Route_{i + 1}を作成しました")

# # CSVファイルのパス
# csv_file_path = 'C:\\Users\\shu\\Documents\\qgis_program\\hotel.csv'

# # pandasを使ってCSVファイルを読み込む
# df = pd.read_csv(csv_file_path)

# # 上記の関数を使ってレイヤを作成
# process_df_and_create_layers(df)
