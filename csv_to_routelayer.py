import csv
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPoint, QgsField
from PyQt5.QtCore import QVariant


#指定された2つの座標を結ぶルートレイヤーを作成する関数
def create_route_layer(coord1, coord2, layer_name):
    # :param coord1: 1つ目の座標（タプルまたはリスト）(lat, lon, height)
    # :param coord2: 2つ目の座標（タプルまたはリスト）(lat, lon, height)
    # :param layer_name: レイヤー名（文字列）
    
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


# CSVファイルのパス
csv_file_path = 'C:\\Users\\shu\\Documents\\qgis_program\\hotel.csv'

# CSVファイルを読み込み
data = []
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        lat = float(row['緯度'])
        lon = float(row['経度'])
        height = float(row['高さ[m]']) + 10  #高さに10mを加える
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
