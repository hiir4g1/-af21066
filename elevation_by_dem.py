from qgis.core import QgsRasterLayer, QgsProject
from qgis.core import QgsPointXY, QgsCoordinateReferenceSystem, QgsCoordinateTransform

def get_elevation_from_dem(dem_layer_name, latitude, longitude):
    # DEMレイヤーを取得
    dem_layers = QgsProject.instance().mapLayersByName(dem_layer_name)
    if not dem_layers:
        return None, "指定されたDEMレイヤーが見つかりません"
    
    dem_layer = dem_layers[0]
    
    # DEMレイヤーの座標系を取得
    dem_crs = dem_layer.crs()
    
    # WGS84からDEMの座標系に直接変換
    wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")  # WGS84のEPSGコード
    transform = QgsCoordinateTransform(wgs84, dem_crs, QgsProject.instance())
    
    # 座標変換してDEMの座標系に合わせる
    point = transform.transform(QgsPointXY(longitude, latitude))
    
    # 標高を取得
    elevation, result = dem_layer.dataProvider().sample(point, 1)  # 1はバンド番号
    if not result:
        return None, "指定されたポイントはDEMデータの範囲外です"
    
    return elevation, None

# 使用例
dem_layer_name = "qgis1"  # DEMレイヤーの名前
latitude = 35.56456998
  # 緯度
longitude = 139.7127101  # 経度

elevation, error = get_elevation_from_dem(dem_layer_name, latitude, longitude)
if error:
    print(error)
else:
    print(f"標高: {elevation} メートル")
