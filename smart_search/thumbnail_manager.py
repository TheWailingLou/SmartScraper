#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""".

Created on Sat Sep 11 14:35:41 2021

@author: louis
"""


import random
import uuid
random.seed()


class ThumbnailManager():
    def __init__(self,
                 page_thumbnails,
                 randomize_order=True,
                 randomize_sub_order=None,
                 side_panel_depth=3):

        location_nodes = []
        for i in range(0, len(page_thumbnails)-1):
            element = page_thumbnails[i]
            location_nodes.append(
                self.create_root_location_node_for_index(element, i))

        if randomize_order:
            randomized_nodes = []
            while len(location_nodes) > 0:
                randomized_nodes.append(location_nodes.pop(
                    random.randint(0, len(location_nodes)-1)))
            self.root_thumbnail_nodes = randomized_nodes

        else:
            self.root_thumbnail_nodes = location_nodes

        self.location_tree = ThumbnailLocationTree(self.root_thumbnail_nodes)

        if randomize_sub_order is None:
            self.randomize_sub_order = randomize_order
        else:
            self.randomize_sub_order = randomize_sub_order

        self.current_index = 0

        self.inner_index = None

        self.new_thumbnails_checked = 0

        self.good_thumbnail_locations = []
        self.good_thumbnail_location_index = 0
        self.analysis_id_to_thumbnail_location = {}

        self.current_location = self.root_thumbnail_nodes[0]

    def try_get_analyzed_parent_analysis_ids(self):
        analysis_ids = []

        for root_node in self.root_thumbnail_nodes:
            analysis_id = self.try_get_analysis_id_by_location(root_node)
            if analysis_id:
                analysis_ids.append(analysis_id)

        if len(analysis_ids) > 0:
            return analysis_ids
        else:
            return False

    def try_get_analyzed_sibling_analysis_ids(self):
        siblings = self.try_get_all_siblings()

        if not siblings:
            return False

        analysis_ids = []

        for sibling in siblings:
            analysis_id = self.try_get_analysis_id_by_location(sibling)
            if analysis_id:
                analysis_ids.append(analysis_id)

        if len(analysis_ids) > 0:
            return analysis_ids
        else:
            return False

    def try_get_analysis_id_by_location(self, location):
        for id in self.analysis_id_to_thumbnail_location.keys():
            analyzed_loc = self.analysis_id_to_thumbnail_location[id]
            if analyzed_loc.id == location.id:
                return id

        return False

    def try_get_current_thumbnail_path(self):
        return self.get_path_to_location(self.current_location)

    def try_get_current_thumbnail_location(self):
        return self.current_location

    def set_child_thumbs(self, side_pannel_thumbs):
        if self.current_location is None:
            raise Exception("Current location does not exist, "
                            "cannot set side panel thumbs!")

        side_panel_location_refs = []

        for i in range(0, len(side_pannel_thumbs)-1):
            location = ThumbnailLocationData(side_pannel_thumbs[i], i)
            node = ThumbnailLocationNode(
                location,
                parent_node_ref=self.current_location.id)
            self.location_tree.add_location(node)
            side_panel_location_refs.append(node.id)

        if self.randomize_sub_order:
            randomized_side_panel_location_refs = []

            while len(side_panel_location_refs) > 0:
                randomized_side_panel_location_refs.append(
                    side_panel_location_refs.pop(
                        random.randint(0, len(side_panel_location_refs)-1)))

            self.current_location.child_node_refs = \
                randomized_side_panel_location_refs

        else:
            self.current_location.child_node_refs = side_panel_location_refs

        self.location_tree.update_location(self.current_location)

    def attach_analysis_id_to_thumbnail(self, analysis_id):
        self.analysis_id_to_thumbnail_location[analysis_id] = \
            self.current_location

    def try_pop_index_for_analysis_id(self, analysis_id):
        return self.analysis_id_to_thumbnail_location.pop(analysis_id, False)

    def get_thumbnail_location_with_analysis_id(self, analysis_id):
        location = self.try_pop_index_for_analysis_id(analysis_id)
        if location:
            return self.get_path_to_location(location)
        else:
            raise Exception("No matching thumbnail found for analysis id!")

    def analyzed_thumbnails_left(self):
        return len(self.analysis_id_to_thumbnail_location.keys()) > 0

    def try_get_next_root(self):
        self.current_index += 1
        if (self.current_index < len(self.root_thumbnail_nodes)):
            self.current_location = \
                self.root_thumbnail_nodes[self.current_index]
            return self.try_get_current_thumbnail_location()
        else:
            return False

    def try_get_first_child_location(self):
        if self.current_location is None:
            print("Can't get next child, current location does not exist!")
            return False

        if self.current_location.child_node_refs is None or \
                len(self.current_location.child_node_refs) == 0:
            print("Can't get next child, node has no children!")
            return False

        self.current_location.current_child_index = 0
        self.location_tree.update_location(self.current_location)

        node_ref = self.current_location.child_node_refs[0]

        self.current_location = self.location_tree.get_location_by_id(node_ref)

        return self.try_get_current_thumbnail_location()

    def try_get_all_siblings(self):
        parent_node = self.try_get_parent()

        if not parent_node:
            return False

        sibling_refs = parent_node.child_node_refs

        sibling_nodes = []
        for ref in sibling_refs:
            sibling_node = self.location_tree.get_location_by_id(ref)
            sibling_nodes.append(sibling_node)

        return sibling_nodes

    def try_get_parent(self):
        if not self.has_parent():
            return False

        parent_node = self.location_tree.get_location_by_id(
            self.current_location.parent_node_ref)

        return parent_node

    def has_parent(self):
        if self.current_location is None:
            return False

        if self.current_location.parent_node_ref is None:
            return False

        return True

    def try_set_current_location_by_analysis_id(self, analysis_id):
        if analysis_id in self.analysis_id_to_thumbnail_location.keys():
            self.current_location = self.analysis_id_to_thumbnail_location[
                analysis_id]
        else:
            return False

    def try_get_next_sibling(self):
        parent_node = self.try_get_parent()

        if not parent_node:
            return False

        if (parent_node.current_child_index is not None):
            parent_node.current_child_index += 1
        else:
            parent_node.current_child_index = 0

        self.location_tree.update_location(parent_node)

        if parent_node.current_child_index < len(parent_node.child_node_refs):
            node_ref = parent_node.child_node_refs[
                parent_node.current_child_index]
            self.current_location = self.location_tree.get_location_by_id(
                node_ref)
            return self.try_get_current_thumbnail_location()
        else:
            print("Can't get next sibling, already on last sibling! "
                  "parent child refs: ",
                  len(parent_node.child_node_refs),
                  parent_node.current_child_index)
            return False

    def good_thumbnails_left(self):
        return self.good_thumbnail_location_index < len(
            self.good_thumbnail_locations)

    def get_next_good_thumbnail_location(self):
        location = self.good_thumbnail_locations[
            self.good_thumbnail_location_index]
        self.good_thumbnail_location_index += 1
        path = self.get_path_to_location(location)
        return path

    def get_random_thumbnail_location(self):
        print("Selecting randomly from root thumbnails!")
        location = self.root_thumbnail_nodes[random.randint(
            0,
            len(self.root_thumbnail_nodes)-1)]
        return self.get_path_to_location(location)

    def current_thumbnail_good(self):
        self.good_thumbnail_locations.append(self.current_location)

    def root_thumbnails_left(self):
        return self.current_index < len(self.root_thumbnail_nodes)

    def increment_new_thumbnails_checked(self):
        self.new_thumbnails_checked += 1

    def get_new_checked_count(self):
        return self.new_thumbnails_checked

    def create_root_location_node_for_index(self, element, index):
        location_data = ThumbnailLocationData(element, index)
        node = ThumbnailLocationNode(
            location_data,
            child_node_refs=None,
            parent_node_ref=None)
        return node

    def get_path_to_location(self, location):
        return self.location_tree.get_path_to_location(location)


class ThumbnailLocationTree():
    def __init__(self, location_nodes):
        self.locations = {}
        self.log_verbose = False
        for node in location_nodes:
            self.locations[node.id] = node

    def get_location_by_id(self, id):
        if id in self.locations:
            return self.locations[id]
        else:
            raise Exception("Location was not in tree!")

    def add_location(self, location_node):
        if location_node.id in self.locations:
            raise Exception("Location already exists in tree!")
        else:
            self.locations[location_node.id] = location_node

    def update_location(self, location_node):
        if location_node.id in self.locations:
            self.locations[location_node.id] = location_node
        else:
            raise Exception("Location node not in tree, cannot update!")

    def get_path_to_location(self, location):
        current_location = location
        path = []
        while current_location.parent_node_ref is not None:
            path.append(current_location.location_data)
            current_location = self.get_location_by_id(
                current_location.parent_node_ref)

        path.append(current_location.location_data)

        if self.log_verbose:
            print("\nPath indexes:")
            for loc in path:
                print("\t", loc.index)

        path.reverse()
        return path


class ThumbnailLocationNode():
    def __init__(
            self,
            location_data,
            child_node_refs=None,
            parent_node_ref=None):
        self.location_data = location_data
        self.id = str(uuid.uuid4())
        self.current_child_index = None
        self.child_node_refs = child_node_refs
        self.parent_node_ref = parent_node_ref


class ThumbnailLocationData():
    def __init__(self, element, index):
        self.element = element
        self.index = index
