from marker_handler import MarkerHandler
from get_centroid_from_ID import get_centroid_from_ID

def create_marker_by_type(list):
    marker_layer_name_type1 = "障害建物type1"
    marker_handler_type1 = MarkerHandler(marker_layer_name_type1,1)
    marker_layer_name_type2 = "障害建物type2"
    marker_handler_type2 = MarkerHandler(marker_layer_name_type2,1)
    marker_layer_name_type3 = "障害建物type3"
    marker_handler_type3 = MarkerHandler(marker_layer_name_type3,1)
    for(info1, _, route_type)in list:
        (route_layer_name1, layer_name1, building_id1, _, _, _) = info1
        
        if(route_type == 1):
            marker_handler_type1.add_marker(*get_centroid_from_ID(layer_name1, building_id1), building_id1)
        elif(route_type == 2):
            marker_handler_type2.add_marker(*get_centroid_from_ID(layer_name1, building_id1), building_id1)
        elif(route_type == 3):
            marker_handler_type3.add_marker(*get_centroid_from_ID(layer_name1, building_id1), building_id1)
        else:
            print("create_marker_by_type関数でマーカーを正常に作成できません")
    
    return None