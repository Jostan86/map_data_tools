import json
import numpy as np
import utm

old_path = "/media/jostan/MOAD/research_data/map_making_data/jazz_apple/map_data_jazz.json"
new_path = "/media/jostan/MOAD/research_data/map_making_data/jazz_apple/map_data_jazz_new.json"

print(utm.from_latlon(46.278, -119.681))
with open(old_path, 'rb') as f:
    map_data_old = json.load(f)

map_data_new = []

for object_data in map_data_old:
    object_data_new = {}
    object_data_new['object_number'] = object_data['object_number']
    # class_estimate = int(object_data['class_estimate'])
    # object_data_new['class_estimate'] = 0 if class_estimate == 2 else 1
    object_data_new['class_estimate'] = object_data['class_estimate']
    object_data_new['position_estimate'] = utm.to_latlon(object_data['position_estimate'][0], object_data['position_estimate'][1], 11, 'T')
    object_data_new['width_estimate'] = object_data['width_estimate']
    object_data_new['row_number'] = object_data['row_number']
    if object_data['position_estimates'] is None:
        object_data_new['position_estimates'] = None

    else:
        position_estimates = []
        for position_estimate in object_data['position_estimates']:
            lat_lon = utm.to_latlon(position_estimate[0], position_estimate[1], 11, 'T')
            position_estimates.append([lat_lon[0], lat_lon[1]])
        object_data_new['position_estimates'] = position_estimates

    object_data_new['width_estimates'] = object_data['width_estimates']
    # class_estimates = []
    # for class_estimate in object_data['class_estimates']:
    #     class_estimate = int(class_estimate)
    #     class_estimates.append(0 if class_estimate == 2 else 1)
    # object_data_new['class_estimates'] = class_estimates
    object_data_new['class_estimates'] = object_data['class_estimates']
    object_data_new['object_x_positions_in_image'] = object_data['object_x_positions_in_image']
    object_data_new['image_filenames'] = object_data['image_filenames']
    object_data_new['gnss_pose_estimates'] = object_data['gps_pose_estimates']
    object_data_new['object_positions_relative_to_camera'] = object_data['object_positions_relative_to_camera']
    object_data_new['test_tree'] = object_data['test_tree']
    object_data_new['test_tree_number'] = object_data['test_tree_number']
    object_data_new['ground_truth_width'] = object_data['ground_truth_diameter']
    object_data_new['ground_truth_position'] = None
    map_data_new.append(object_data_new)

with open(new_path, 'w') as f:
    json.dump(map_data_new, f, indent=4)



