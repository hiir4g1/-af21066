from qgis.core import QgsProject, QgsLayerTreeGroup

def group_layers_by_name(group_name, layer_names):
    root = QgsProject.instance().layerTreeRoot()
    group = root.findGroup(group_name)

    # グループが存在しない場合、新たに作成
    if group is None:
        group = QgsLayerTreeGroup(group_name)
        root.insertChildNode(0, group)  # 最上位に追加

    # レイヤーをグループに追加
    for layer_name in layer_names:
        layer = QgsProject.instance().mapLayersByName(layer_name)
        if layer:
            group.addLayer(layer[0])  # グループに追加

# レイヤー名を収集
layer_names_to_group = []
for layer in QgsProject.instance().mapLayers().values():
    if layer.name().startswith("Route"):
        layer_names_to_group.append(layer.name())

# グループを作成
group_layers_by_name("新しいグループ名", layer_names_to_group)

# グループに追加されていないレイヤーを削除
for layer in QgsProject.instance().mapLayers().values():
    if layer.name().startswith("Route") and layer.name() not in layer_names_to_group:
        QgsProject.instance().removeMapLayer(layer.id())  # レイヤーを削除