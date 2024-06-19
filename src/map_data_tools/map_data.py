#!/usr/bin/env python3
import json
import numpy as np
import utm
from dataclasses import dataclass

@dataclass
class ObjectData:
    object_number: int = None
    position_estimate: list = None
    width_estimate: float = None
    class_estimate: int = None
    position_estimates: list = None
    width_estimates: list = None
    class_estimates: list = None
    object_x_positions_in_image: list = None
    image_filenames: list = None
    gnss_pose_estimates: list = None
    object_positions_relative_to_camera: list = None
    row_number: int = None
    test_tree: bool = False
    test_tree_number: int = None
    ground_truth_width: float = None
    ground_truth_position: list = None
    gnss_format: str = "lat_lon"
    utm_zone_number: int = None
    utm_zone_letter: str = None


    # make other creation method from dict
    @classmethod
    def from_all_data_dict(cls, data):
        return cls(object_number=data['object_number'],
                   position_estimate=data['position_estimate'],
                   width_estimate=data['width_estimate'],
                   class_estimate=data['class_estimate'],
                   position_estimates=data['position_estimates'],
                   width_estimates=data['width_estimates'],
                   class_estimates=data['class_estimates'],
                   object_x_positions_in_image=data['object_x_positions_in_image'],
                   image_filenames=data['image_filenames'],
                   gnss_pose_estimates=data['gnss_pose_estimates'],
                   object_positions_relative_to_camera=data['object_positions_relative_to_camera'],
                   row_number=data['row_number'],
                   test_tree=data['test_tree'],
                   test_tree_number=data['test_tree_number'],
                   ground_truth_width=data['ground_truth_width'],
                   ground_truth_position=data['ground_truth_position'])

    @classmethod
    def from_dict(cls, data):
        object_data = cls(object_number=data['object_number'],
                          position_estimate=data['position_estimate'],
                          width_estimate=data['width_estimate'],
                          class_estimate=data['class_estimate'],
                          row_number=data['row_number'])

        if 'test_tree' in data:
            object_data.test_tree = data['test_tree']
        if 'test_tree_number' in data:
            object_data.test_tree_number = data['test_tree_number']
        if 'ground_truth_width' in data:
            object_data.ground_truth_width = data['ground_truth_width']
        if 'ground_truth_position' in data:
            object_data.ground_truth_position = data['ground_truth_position']
        return object_data

    def convert_to_utm(self):
        if self.gnss_format == "utm":
            return

        utm_coords = utm.from_latlon(self.position_estimate[0], self.position_estimate[1])
        self.utm_zone_number = utm_coords[2]
        self.utm_zone_letter = utm_coords[3]
        self.position_estimate = utm_coords[:2]

        if self.position_estimates is not None:
            for i in range(len(self.position_estimates)):
                self.position_estimates[i] = utm.from_latlon(self.position_estimates[i][0], self.position_estimates[i][1])[:2]

        self.gnss_format = "utm"

    def convert_to_lat_lon(self):
        if self.gnss_format == "lat_lon":
            return

        self.position_estimate = utm.to_latlon(self.position_estimate[0], self.position_estimate[1], self.utm_zone_number, self.utm_zone_letter)

        if self.position_estimates is not None:
            for i in range(len(self.position_estimates)):
                self.position_estimates[i] = utm.to_latlon(self.position_estimates[i][0], self.position_estimates[i][1], self.utm_zone_number, self.utm_zone_letter)

        self.gnss_format = "lat_lon"

class MapData:
    def __init__(self, map_data_path, move_origin=False, origin_offset=(0, 0)):
        self.map_data_path = map_data_path
        self.move_origin = move_origin
        self.origin_offset = origin_offset

        self.map_data = None

        self.object_numbers = None
        self.all_class_estimates = None
        self.all_position_estimates = None
        self.all_width_estimates = None
        self.test_tree_numbers = None
        self.test_tree_indexes = None

        self.utm_zone_number = None
        self.utm_zone_letter = None



        self.open_object_list()
        self.convert_to_utm_coords()
        self.load_numpy_arrays()

    def __len__(self):
        return len(self.map_data)

    def __getitem__(self, index):
        return self.map_data[index]

    def open_object_list(self):
        with open(self.map_data_path, 'rb') as f:
            json_map_data = json.load(f)

        self.map_data = []

        for object_data in json_map_data:
            self.map_data.append(ObjectData.from_dict(object_data))

    def load_numpy_arrays(self):
        all_class_estimates = []
        all_position_estimates = []
        all_width_estimates = []
        object_numbers = []
        test_tree_numbers = []
        test_tree_indexes = []

        for object_data in self.map_data:
            if object_data.test_tree:
                test_tree_numbers.append(int(object_data.test_tree_number))
                test_tree_indexes.append(1)
            else:
                test_tree_indexes.append(0)

            all_class_estimates.append(object_data.class_estimate)
            all_position_estimates.append(object_data.position_estimate)
            all_width_estimates.append(object_data.width_estimate)
            object_numbers.append(object_data.object_number)

        self.object_numbers = np.array(object_numbers, dtype=int)
        self.all_class_estimates = np.array(all_class_estimates, dtype=int)
        self.all_position_estimates = np.array(all_position_estimates)
        self.all_width_estimates = np.array(all_width_estimates)
        self.test_tree_numbers = test_tree_numbers
        self.test_tree_indexes = np.array(test_tree_indexes, dtype=bool)

        if self.move_origin:
            x_min = np.min(self.all_position_estimates[:, 0]) - self.origin_offset[0]
            y_min = np.min(self.all_position_estimates[:, 1]) - self.origin_offset[1]

            self.all_position_estimates[:, 0] -= x_min
            self.all_position_estimates[:, 1] -= y_min

    def convert_to_utm_coords(self):
        for object_data in self.map_data:
            object_data.convert_to_utm()
        # utm_coords = utm.from_latlon(self.map_data[0].position_estimate[0], self.map_data[0].position_estimate[1])
        # self.utm_zone_number = utm_coords[2]
        # self.utm_zone_letter = utm_coords[3]
        # for object_data in self.map_data:
        #     object_data.position_estimate = utm.from_latlon(object_data.position_estimate[0], object_data.position_estimate[1])[:2]
        #
        #     if object_data.position_estimates is not None:
        #         for i in range(len(object_data.position_estimates)):
        #             object_data.position_estimates[i] = utm.from_latlon(object_data.position_estimates[i][0], object_data.position_estimates[i][1])[:2]

    def convert_to_lat_lon_coords(self):
        for object_data in self.map_data:
            object_data.convert_to_lat_lon()
        # for object_data in self.map_data:
        #     lat_lon = utm.to_latlon(object_data.position_estimate[0], object_data.position_estimate[1], self.utm_zone_number, self.utm_zone_letter)
        #     object_data.position_estimate = [lat_lon[0], lat_lon[1]]
        #
        #     if object_data.position_estimates is not None:
        #         for i in range(len(object_data.position_estimates)):
        #             lat_lon = utm.to_latlon(object_data.position_estimates[i][0], object_data.position_estimates[i][1], self.utm_zone_number, self.utm_zone_letter)
        #             object_data.position_estimates[i] = [lat_lon[0], lat_lon[1]]

    def save_shareable_version(self, save_path):
        self.convert_to_lat_lon_coords()
        shareable_map_data = []
        for object_data in self.map_data:
            share_object_data = {'object_number': object_data.object_number,
                                 'position_estimate': object_data.position_estimate,
                                 'width_estimate': object_data.width_estimate,
                                 'class_estimate': object_data.class_estimate,
                                 'row_number': object_data.row_number,
                                 'ground_truth_width': object_data.ground_truth_width,
                                 'ground_truth_position': object_data.ground_truth_position}
            if object_data.test_tree:
                share_object_data['test_tree'] = object_data.test_tree
                share_object_data['test_tree_number'] = object_data.test_tree_number

            shareable_map_data.append(share_object_data)

        with open(save_path, 'w') as f:
            json.dump(shareable_map_data, f, indent=4)
        self.convert_to_utm_coords()

    def make_plot(self, dot_size=5, save_path=None, title_fontsize=14, label_fontsize=12, figsize=(6, 10), dpi=500, x_offset=15, y_offset=5, title=None):
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=figsize, dpi=dpi)
        ax = plt.axes()

        tree_positions = self.all_position_estimates[self.all_class_estimates == 0]
        post_positions = self.all_position_estimates[self.all_class_estimates == 1]

        ax.scatter(tree_positions[:, 0], tree_positions[:, 1], label='Tree', color=(0 / 255, 158 / 255, 115 / 255),
                   s=dot_size)
        ax.scatter(post_positions[:, 0], post_positions[:, 1], label='Post', color=(230 / 255, 159 / 255, 0.0),
                   s=dot_size)

        ax.set_aspect('equal')
        ax.set_xlabel('Easting (m)', fontsize=label_fontsize)
        ax.set_ylabel('Northing (m)', fontsize=label_fontsize)
        if title is not None:
            ax.set_title(title, fontsize=title_fontsize)

        ax.set_xlim([self.all_position_estimates[:, 0].min() - x_offset, self.all_position_estimates[:, 0].max() + x_offset])
        ax.set_ylim([self.all_position_estimates[:, 1].min() - y_offset, self.all_position_estimates[:, 1].max() + y_offset])

        ax.legend()

        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()


if __name__ == "__main__":
    map_data = MapData("/media/jostan/MOAD/research_data/map_making_data/jazz_apple/map_data_jazz_new.json")
    map_data.save_shareable_version("/media/jostan/MOAD/research_data/map_making_data/jazz_apple/map_data_jazz_new_share.json")
    map_data.make_plot()

