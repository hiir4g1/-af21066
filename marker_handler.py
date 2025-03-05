from qgis.core import QgsProject, QgsFeature, QgsGeometry, QgsVectorLayer, QgsField, QgsFields, QgsPointXY
from qgis.PyQt.QtCore import QVariant

#マーカーを作成するクラス
class MarkerHandler:
    def __init__(self, marker_layer_name,arg = 0):
        self.marker_layer_name = marker_layer_name
        self.arg = arg
        self.marker_layer = self.create_marker_layer()
        

    def get_layer_by_name(self, name):
        layers = QgsProject.instance().mapLayersByName(name)
        if not layers:
            raise Exception(f"レイヤー '{name}' が見つかりません")
        return layers[0]

    def create_marker_layer(self):
        
        # 同じ名前のレイヤーがすでに存在する場合、そのレイヤーを削除
        if self.arg == 0:
            existing_layers = QgsProject.instance().mapLayersByName(self.marker_layer_name)
            for existing_layer in existing_layers:
                QgsProject.instance().removeMapLayer(existing_layer)
        
        
        # スキーマを定義
        fields = QgsFields()
        fields.append(QgsField("ID", QVariant.Int))
        
        # 新しいポイントレイヤーを作成
        marker_layer = QgsVectorLayer("Point?crs=EPSG:4326", self.marker_layer_name, "memory")
        marker_layer.dataProvider().addAttributes(fields)
        marker_layer.updateFields()
        
        # プロジェクトにレイヤーを追加
        QgsProject.instance().addMapLayer(marker_layer)
        return marker_layer

    def add_marker(self, x, y, feature_id):
        point = QgsPointXY(x, y)
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(point))
        feature.setAttributes([feature_id])
        self.marker_layer.dataProvider().addFeature(feature)
        self.marker_layer.updateExtents()
        self.marker_layer.triggerRepaint()