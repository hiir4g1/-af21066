def get_around_aviodance_point(start_coords, end_coords, final_max_distance_item, dist):
    around_xy_point = calculate_Q(start_coords, end_coords, final_max_distance_item, dist)

    distance1 = calculate_distance([start_coords[0],start_coords[1]],around_xy_point)
    distance2 = calculate_distance([end_coords[0],end_coords[1]],around_xy_point)
    around_z = (distance2*hight1+distance1*hight2)/(distance1+distance2)
    around_point = [around_xy_point[0],around_xy_point[1],around_z]