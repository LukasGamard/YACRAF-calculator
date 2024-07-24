import tkinter as tk
import numpy as np
from helper_functions import convert_grid_coordinate_to_actual, convert_actual_coordinate_to_grid, get_actual_coordinates_after_zoom, get_grid_mid_x, get_grid_mid_y
from blocks_general import GUIConnectionCorner
from blocks_setup import GUIConnectionTriangle
from config import *

class GUIConnection:
    def __init__(self, model, view, start_block, start_direction, *, end_block=None, end_direction=None, is_external=False):
        self.__model = model
        self.__view = view
        
        self.__start_block = start_block
        self.__start_x = 0
        self.__start_y = 0
        self.__start_direction = start_direction
        
        self.__end_block = end_block
        self.__end_x = 0
        self.__end_y = 0
        self.__end_direction = end_direction
        
        self.__corners = []
        self.__lines = []
        
        self.__num_order = None
        self.__circle_num_order = None
        self.__label_num_order = None
        
        self.__is_external = is_external
        
        self.attempt_to_add_connection_to_blocks()
        
    """
    def is_start_block(self, block):
        return self.__start_block == block
        
    def get_start_block(self):
        return self.__start_block
    """
    
    def get_start_block(self):
        return self.__start_block
        
    def get_end_block(self):
        return self.__end_block
        
    def get_other_block(self, block):
        if self.__start_block == block:
            return self.__end_block
            
        return self.__start_block
        
    def set_end_location(self, block, direction):
        self.__end_block = block
        self.__end_direction = direction
        
        self.attempt_to_add_connection_to_blocks()
        
    def attempt_to_add_connection_to_blocks(self):
        if self.__start_block != None and self.__end_block != None:
            self.__start_block.add_connection(self)
            self.__end_block.add_connection(self)
            
            self.create_new_lines()
        
    def update_direction(self, affected_block, new_direction):
        if affected_block == self.__start_block:
            self.__start_direction = new_direction
            
        elif affected_block == self.__end_block:
            self.__end_direction = new_direction
            
        self.create_new_lines()
        
    def get_coordinates(self, block, direction):
        x = block.get_x() + int(0.5 * block.get_width())
        y = block.get_y() + int(0.5 * block.get_height())
        
        if direction == "UP":
            y = block.get_y() - 1
        elif direction == "DOWN":
            y = block.get_y() + block.get_height()
        elif direction == "LEFT":
            x = block.get_x() - 1
        elif direction == "RIGHT":
            x = block.get_x() + block.get_width()
            
        return x, y
        
    def get_actual_attached_coordinates(self, x, y, direction):
        attached_x = x + 0.5
        attached_y = y + 0.5
        
        if direction == "UP":
            attached_y += 0.5
        elif direction == "DOWN":
            attached_y -= 0.5
        elif direction == "LEFT":
            attached_x += 0.5
        elif direction == "RIGHT":
            attached_x -= 0.5
            
        actual_x, actual_y = convert_grid_coordinate_to_actual(self.__view, attached_x, attached_y)
        
        return actual_x, actual_y
        
    def create_new_lines(self, mouse_location=None):
        corner_coordinates = self.create_corners(mouse_location)
        self.create_lines_from_corners(corner_coordinates)
        
        for corner_x, corner_y in corner_coordinates:
            self.__corners.append(GUIConnectionCorner(self.__model, self.__view, self, corner_x, corner_y))
    
        self.attempt_to_set_number()
        
    def scale(self, last_length_unit):
        for line in self.__lines:
            adjusted_actual_coordinates = get_actual_coordinates_after_zoom(self.__view, self.__view.get_canvas().coords(line), last_length_unit)
            x1, y1, x2, y2 = adjusted_actual_coordinates
            self.__view.get_canvas().coords(line, x1, y1, x2, y2)
            
        for corner in self.__corners:
            corner.scale(last_length_unit)
            
    def move_lines(self, move_x, move_y):
        # If currently panning or zooming, only move lines and corners
        if self.__view.is_panning() or self.__view.is_zooming():
            for corner in self.__corners:
                corner.move_block(move_x, move_y)
                
            for line in self.__lines:
                actual_move_x, actual_move_y = convert_grid_coordinate_to_actual(self.__view, move_x, move_y)
                self.__view.get_canvas().move(line, actual_move_x, actual_move_y)
                
        # If not panning, need to create completely new lines and corners
        else:
            self.create_new_lines()
        
    def attempt_to_set_number(self):
        if self.__num_order != None:
            num_order_x = self.__start_x
            num_order_y = self.__start_y + self.__start_block.get_height() / 2
            
            circle_radius = convert_grid_coordinate_to_actual(self.__view, NUM_ORDER_CIRCLE_RADIUS, 0)[0]
            
            if self.__start_direction == "LEFT":
                num_order_x += 1
                
            num_order_actual_x, num_order_actual_y = convert_grid_coordinate_to_actual(self.__view, num_order_x, num_order_y)
            
            self.__circle_num_order = self.__view.get_canvas().create_oval(num_order_actual_x-circle_radius, num_order_actual_y-circle_radius, num_order_actual_x+circle_radius, num_order_actual_y+circle_radius, width=NUM_ORDER_CIRCLE_OUTLINE, outline=NUM_ORDER_CIRCLE_OUTLINE_COLOR, fill=NUM_ORDER_CIRCLE_COLOR)
            self.__label_num_order = self.__view.get_canvas().create_text(num_order_actual_x, num_order_actual_y, text=self.__num_order, font=FONT)
            
    def attempt_to_remove_number(self):
        if self.__circle_num_order != None:
            self.__view.get_canvas().delete(self.__circle_num_order)
            
        if self.__label_num_order != None:
            self.__view.get_canvas().delete(self.__label_num_order)
        
    def create_lines_from_corners(self, corner_coordinates):
        actual_coordinates = [self.get_actual_attached_coordinates(self.__start_x, self.__start_y, self.__start_direction)]
        
        for corner_x, corner_y in corner_coordinates:
            actual_corner_x, actual_corner_y = convert_grid_coordinate_to_actual(self.__view, corner_x+0.5, corner_y+0.5)
            actual_coordinates.append((actual_corner_x, actual_corner_y))
            
        actual_coordinates.append(self.get_actual_attached_coordinates(self.__end_x, self.__end_y, self.__end_direction))
        
        for i in range(1, len(actual_coordinates)):
            from_x = actual_coordinates[i-1][0]
            from_y = actual_coordinates[i-1][1]
            to_x = actual_coordinates[i][0]
            to_y = actual_coordinates[i][1]
            
            if self.__is_external:
                line = self.__view.get_canvas().create_line(from_x, from_y, to_x, to_y, fill=CONNECTION_COLOR, width=CONNECTION_WIDTH, dash=CONNECTION_DASH)
            else:
                line = self.__view.get_canvas().create_line(from_x, from_y, to_x, to_y, fill=CONNECTION_COLOR, width=CONNECTION_WIDTH)
                
            self.__lines.append(line)
            
    def convert_direction_to_vector(self, direction):
        if direction == "UP":
            return np.array([0, -1])
        elif direction == "RIGHT":
            return np.array([1, 0])
        elif direction == "DOWN":
            return np.array([0, 1])
        elif direction == "LEFT":
            return np.array([-1, 0])
            
        print(f"Error: Did not recognize direction {direction}")
        
    def positions_dot_product(self, current_position, final_position):
        vector_to_final_position = np.array([final_position[0] - current_position[0], final_position[1] - current_position[1]])
        vector_direction = self.convert_direction_to_vector(current_position[2])
        
        vector_to_final_position_norm = np.linalg.norm(vector_to_final_position)
        
        if vector_to_final_position_norm != 0:
            vector_to_final_position = vector_to_final_position / vector_to_final_position_norm
        
        return np.dot(vector_to_final_position, vector_direction)
        
    def get_position_after_turn(self, current_position, final_position):
        current_direction = current_position[2]
        current_x, current_y, _ = current_position
        new_direction = ""
        
        if current_direction == "UP":
            if final_position[0] < current_position[0]:
                new_direction = "LEFT"
            else:
                new_direction = "RIGHT"
                
        elif current_direction == "RIGHT":
            if final_position[1] < current_position[1]:
                new_direction = "UP"
            else:
                new_direction = "DOWN"
                
        elif current_direction == "DOWN":
            if final_position[0] > current_position[0]:
                new_direction = "RIGHT"
            else:
                new_direction = "LEFT"
                
        elif current_direction == "LEFT":
            if final_position[1] > current_position[1]:
                new_direction = "DOWN"
            else:
                new_direction = "UP"
        
        else:
            print(f"Error: Did not recognize direction {current_direction}")
            
        return (current_x, current_y, new_direction)
        
    def create_corners(self, mouse_location=None):
        self.remove_lines()
        corners_from_start = []
        corners_from_end = []
        
        self.__start_x, self.__start_y = self.get_coordinates(self.__start_block, self.__start_direction)
        
        if mouse_location == None:
            self.__end_x, self.__end_y = self.get_coordinates(self.__end_block, self.__end_direction)
            
        else:
            end_x, end_y = convert_actual_coordinate_to_grid(self.__view, mouse_location[0], mouse_location[1])
            self.__end_x = end_x - 0.5
            self.__end_y = end_y - 0.5
            
            if self.__end_x > self.__start_x:
                self.__end_direction = "LEFT"
                self.__end_x -= 1
                
            else:
                self.__end_direction = "RIGHT"
                self.__end_x += 1
                
        position_start = (self.__start_x, self.__start_y, self.__start_direction)
        position_end = (self.__end_x, self.__end_y, self.__end_direction)
        
        # grid_offset_x, grid_offset_y = self.__view.get_grid_offset()
        
        while True:
            start_dot_product = self.positions_dot_product(position_start, position_end)
            end_dot_product = self.positions_dot_product(position_end, position_start)
            
            # Intersect with each other or are parallel
            if start_dot_product >= 0 and end_dot_product >= 0:
                start_x, start_y, _ = self.get_position_after_turn(position_start, position_end)
                end_x, end_y, _ = self.get_position_after_turn(position_end, position_start)
                
                # Parallel
                if abs(np.dot(self.convert_direction_to_vector(position_start[2]), self.convert_direction_to_vector(position_end[2]))) == 1:
                    if position_start[2] in ("DOWN", "UP"):
                        mid_y = get_grid_mid_y(self.__view, (start_y + end_y) / 2)
                        corners_from_start.append((start_x, mid_y))
                        corners_from_end.append((end_x, mid_y))
                        
                    else:
                        mid_x = get_grid_mid_x(self.__view, (start_x + end_x) / 2)
                        """
                        mid_x = (start_x + end_x) / 2
                        
                        # So that the connection does not jump up one value close to the left border
                        if mid_x <= 0.500000001:
                            mid_x -= 1
                        
                        # print(f"{(start_x + end_x) / 2}")
                        # print(grid_offset_x)
                        
                        # Account for the offset from panning
                        if grid_offset_x >= 0.5:
                            mid_x -= 1 - grid_offset_x
                        else:
                            mid_x += grid_offset_x
                        """
                            
                        corners_from_start.append((mid_x, start_y))
                        corners_from_end.append((mid_x, end_y))
                
                # Intersecting
                else:
                    if position_start[2] in ("DOWN", "UP"):
                        corners_from_start.append((start_x, end_y))
                        
                    else:
                        corners_from_start.append((end_x, start_y))
                
                break
                
            if start_dot_product <= end_dot_product:
                position_start = self.get_position_after_turn(position_start, position_end)
                corners_from_start.append((position_start[0], position_start[1]))
                
            else:
                position_end = self.get_position_after_turn(position_end, position_start)
                corners_from_end.append((position_end[0], position_end[1]))
                
            if len(corners_from_start + corners_from_end) >= 10:
                break
                
        corners_from_end.reverse()
        
        return corners_from_start + corners_from_end
        
    def remove_lines(self):
        for corner in self.__corners:
            corner.delete()
            
        for line in self.__lines:
            self.__view.get_canvas().delete(line)
            
        self.attempt_to_remove_number()
        
        self.__lines.clear()
        self.__corners.clear()
        
    """
    def get_movable_items(self):
        movable_items = [self.__start_block]
        
        if self.__end_block != None:
            movable_items.append(self.__end_block)
            
        return movable_items
    """
    
    def set_num_order(self, num_order):
        self.__num_order = num_order
        self.attempt_to_remove_number()
        self.attempt_to_set_number()
        
    def is_external(self):
        return self.__is_external
        
    def set_is_external(self, is_external):
        self.__is_external = is_external
        self.__end_block.set_input_attribute(self.__start_block.get_configuration_attribute(), not is_external)
        
        self.create_new_lines()
        
    def has_options(self):
        return True
        
    def delete(self):
        for block in [self.__start_block, self.__end_block]:
            if block != None:
                block.remove_connection(self)
                
        self.remove_lines()
        
    def save_state(self):
        return {"start_block": str(self.__start_block), "start_direction": self.__start_direction, "end_direction": self.__end_direction, "is_external": self.__is_external}
                
class GUIConnectionWithBlocks(GUIConnection):
    def __init__(self, model, view):
        self.__start_block = GUIConnectionTriangle(model, view, GUI_BLOCK_START_COORDINATES[0][0], GUI_BLOCK_START_COORDINATES[0][1], "RIGHT", False)
        self.__end_block = GUIConnectionTriangle(model, view, GUI_BLOCK_START_COORDINATES[1][0], GUI_BLOCK_START_COORDINATES[1][1], "RIGHT", True)
        
        super().__init__(model, view, self.__start_block, "RIGHT", end_block=self.__end_block, end_direction="LEFT")
        self.__view = view
        
        self.attempt_to_add_connection_to_blocks()
        self.create_new_lines()
        
        self.__is_deleted = False
        
        # self.__start_block.snap_to_grid()
        # self.__end_block.snap_to_grid()
        
    """
    def get_other_block(self, block):
        if block == self.__start_block.get_attached_class():
            return self.__end_block.get_attached_class()
            
        return self.__start_block.get_attached_class()
    """
    
    def attempt_to_connect_both_classes(self):
        start_class_gui = self.__start_block.get_attached_class()
        end_class_gui = self.__end_block.get_attached_class()
        
        if start_class_gui != None and end_class_gui != None:
            end_class_gui.get_setup_class().add_input_class(start_class_gui.get_setup_class())
            end_class_gui.update_value_input_types()
            
    def attempt_to_disconnect_both_classes(self):
        start_class_gui = self.__start_block.get_attached_class()
        end_class_gui = self.__end_block.get_attached_class()
        
        if start_class_gui != None and end_class_gui != None:
            end_class_gui.get_setup_class().remove_input_class(start_class_gui.get_setup_class())
            end_class_gui.update_value_input_types()
            
    def move_and_place_blocks(self, new_start_x, new_start_y, new_end_x, new_end_y):
        self.__start_block.move_block(new_start_x - GUI_BLOCK_START_COORDINATES[0][0], new_start_y - GUI_BLOCK_START_COORDINATES[0][1])
        self.__start_block.put_down_block()
        
        self.__end_block.move_block(new_end_x - GUI_BLOCK_START_COORDINATES[1][0], new_end_y - GUI_BLOCK_START_COORDINATES[1][1])
        self.__end_block.put_down_block()
        
    def get_movable_items(self):
        movable_items = []
        
        for potential_block in [self.__start_block, self.__end_block]:
            if not potential_block.is_attached():
                movable_items.append(potential_block)
                
        return movable_items
        
    def has_options(self):
        return False
        
    def delete(self):
        if not self.__is_deleted:
            self.__is_deleted = True
            
            self.remove_lines()
            self.__view.remove_connection_with_blocks(self)
            
            self.__start_block.delete()
            self.__end_block.delete()
        
    def save_state(self):
        return {"start_block": self.__start_block.save_state(), "end_block": self.__end_block.save_state()}
