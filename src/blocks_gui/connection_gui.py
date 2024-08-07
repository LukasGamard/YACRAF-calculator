import tkinter as tk
import numpy as np
from helper_functions import convert_value_to_string, convert_grid_coordinate_to_actual, convert_actual_coordinate_to_grid, get_actual_coordinates_after_zoom, distance_to_closest_grid_intersection, get_grid_mid_x, get_grid_mid_y
from general_gui import GUIConnectionCorner, NumberIndicator
from setup_gui import GUIConnectionTriangle, GUIConnectionScalarsIndicator
from options import OptionsConnection, OptionsConnectionWithBlocks
from config import *

class GUIConnection:
    """
    Connects blocks by lines
    """
    def __init__(self, model, view, start_block, start_direction, *, end_block=None, end_direction=None, corner_coordinates=None, is_external=False, mouse_location=None):
        self.__model = model
        self.__view = view
        
        self.__start_block = start_block
        self.__start_direction = start_direction # Direction which the first line goes out from the start block
        
        self.__end_block = end_block
        self.__end_direction = end_direction # Direction which the last line goes out from the end block
        
        self.__corners = []
        self.__lines = []
        
        # Indicator for which order connections are considered when calculating values (only applying to relevant calculation types)
        self.__num_order = None
        self.__num_order_indicator = None
        
        self.__is_external = is_external
        
        start_block.add_connection(self)
        
        # End block was specified
        if end_block != None:
            end_block.add_connection(self)
            
        self.create_new_lines(mouse_location)
        
        # Corner coordinates were specified
        if corner_coordinates != None:
            for i, corner in enumerate(self.__corners):
                move_x = corner_coordinates[i][0] - corner.get_x()
                move_y = corner_coordinates[i][1] - corner.get_y()
                
                corner.move_block(move_x, move_y)
                
            self.adjust_lines_to_dragged_corners()
            
    def scale(self, last_length_unit):
        """
        Scales items on the canvas when zooming
        """
        # Scale lines
        for line in self.__lines:
            adjusted_actual_coordinates = get_actual_coordinates_after_zoom(self.__view, self.__view.get_canvas().coords(line), last_length_unit)
            x1, y1, x2, y2 = adjusted_actual_coordinates
            self.__view.get_canvas().coords(line, x1, y1, x2, y2)
            
        # Scale corners        
        for corner in self.__corners:
            corner.scale(last_length_unit)
            
        # Scale connection order indicator
        if self.__num_order_indicator != None:
            self.__num_order_indicator.scale(last_length_unit)
            
    def open_options(self):
        return OptionsConnection(self.__model.get_root(), self)
            
    def get_start_block(self):
        return self.__start_block
        
    def get_end_block(self):
        return self.__end_block
        
    def set_end_location(self, block, direction):
        """
        Connects the connection to an end block
        """
        self.__end_block = block
        self.__end_direction = direction
        
        self.__end_block.add_connection(self)
        
        self.create_new_lines()
        
    def update_direction(self, affected_block, new_direction):
        """
        Updates the direction which the line goes out from a block
        """
        if affected_block == self.__start_block:
            self.__start_direction = new_direction
            
        elif affected_block == self.__end_block:
            self.__end_direction = new_direction
            
        self.create_new_lines()
        
    def get_attached_grid_coordinate(self, is_start_block):
        """
        Returns the grid coordinate that the line should start from considering its connected block
        """
        if is_start_block:
            block = self.__start_block
            direction = self.__start_direction
        else:
            block = self.__end_block
            direction = self.__end_direction
            
        # Center of block as default
        x = block.get_x() + int(0.5 * block.get_width())
        y = block.get_y() + int(0.5 * block.get_height())
        
        # Correct one of the values to get the correct coordinate considering the direction which the line goes out from the block
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
        """
        Returns the pixel start coordinate of the line
        """
        # Center of grid coordinate as default
        attached_x = x + 0.5
        attached_y = y + 0.5
        
        # Correct one of the values to get the correct pixel coordinate considering the direction of the line
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
        """
        Deletes existing lines and corners, creating new ones
        """
        self.remove_corners()
        self.remove_lines()
        
        start_x, start_y = self.get_attached_grid_coordinate(True)
        
        # The lines should follow the mouse around as it has not been connected to a block yet
        if mouse_location != None:
            end_x, end_y = convert_actual_coordinate_to_grid(self.__view, mouse_location[0], mouse_location[1])
            end_x -= 0.5
            end_y -= 0.5
            
            # Direction which the line should attach to the mouse
            if end_x > start_x:
                self.__end_direction = "LEFT"
                end_x -= 1
            else:
                self.__end_direction = "RIGHT"
                end_x += 1
        else:
            end_x, end_y = self.get_attached_grid_coordinate(False)
            
        corner_coordinates = self.create_corners(start_x, start_y, end_x, end_y)
        
        # Create corners
        for corner_x, corner_y in corner_coordinates:
            self.__corners.append(GUIConnectionCorner(self.__model, self.__view, self, corner_x, corner_y))
            
        # Draw lines based on the created corners
        self.create_lines_from_corners(start_x, start_y, end_x, end_y)
        
    def adjust_lines_to_dragged_corners(self):
        self.remove_lines()
        
        start_x, start_y = self.get_attached_grid_coordinate(True)
        end_x, end_y = self.get_attached_grid_coordinate(False)
        
        self.create_lines_from_corners(start_x, start_y, end_x, end_y)
        
    def get_corners(self):
        return self.__corners
                
    def get_adjacent_corners(self, corner):
        corner_index = self.__corners.index(corner)
        adjacent_corners = []
        
        # Previous corner
        if corner_index > 0:
            adjacent_corners.append(self.__corners[corner_index-1])
            
        # Next corner
        if corner_index < len(self.__corners) - 1:
            adjacent_corners.append(self.__corners[corner_index+1])
            
        return adjacent_corners
        
    def allowed_corner_movement_directions(self, corner):
        adjacent_corners = self.get_adjacent_corners(corner)
        allowed_directions = set()
        
        for adjacent_corner in adjacent_corners:
            # Adjacent corner is above or below
            if adjacent_corner.get_x() == corner.get_x():
                allowed_directions.update({"LEFT", "RIGHT"})
                
            # Adjacent corner is to the left or the right
            elif adjacent_corner.get_y() == corner.get_y():
                allowed_directions.update({"UP", "DOWN"})
                
        return list(allowed_directions)
        
    def move_lines(self, move_x, move_y):
        # If currently panning or zooming, only move lines and corners
        if self.__view.is_panning() or self.__view.is_zooming():
            for corner in self.__corners:
                corner.move_block(move_x, move_y)
                
            for line in self.__lines:
                actual_move_x, actual_move_y = convert_grid_coordinate_to_actual(self.__view, move_x, move_y)
                self.__view.get_canvas().move(line, actual_move_x, actual_move_y)
                
            if self.__num_order_indicator != None:
                self.__num_order_indicator.move(move_x, move_y)
                
            return True
            
        # If not panning, need to create completely new lines and corners
        else:
            self.create_new_lines()
            
            return False
            
    def attempt_to_set_number(self):
        if self.__num_order != None:
            num_order_x, num_order_y = self.get_attached_grid_coordinate(True)
            
            if self.__start_direction == "LEFT":
                num_order_x += 1
                
            num_order_y += 0.5
            
            self.__num_order_indicator = NumberIndicator(self.__view, num_order_x, num_order_y, NUM_ORDER_CIRCLE_RADIUS, NUM_ORDER_CIRCLE_COLOR, NUM_ORDER_CIRCLE_OUTLINE, self.__num_order)
            
    def attempt_to_remove_number(self):
        if self.__num_order_indicator != None:
            self.__num_order_indicator.remove()
            self.__num_order_indicator = None
            
    def create_lines_from_corners(self, start_x, start_y, end_x, end_y):
        actual_coordinates = [self.get_actual_attached_coordinates(start_x, start_y, self.__start_direction)]
        
        for corner in self.__corners:
            actual_corner_x, actual_corner_y = convert_grid_coordinate_to_actual(self.__view, corner.get_x()+0.5, corner.get_y()+0.5)
            actual_coordinates.append((actual_corner_x, actual_corner_y))
            
        actual_coordinates.append(self.get_actual_attached_coordinates(end_x, end_y, self.__end_direction))
        
        for i in range(1, len(actual_coordinates)):
            from_x = actual_coordinates[i-1][0]
            from_y = actual_coordinates[i-1][1]
            to_x = actual_coordinates[i][0]
            to_y = actual_coordinates[i][1]
            
            if self.__is_external:
                line = self.__view.get_canvas().create_line(from_x, from_y, to_x, to_y, fill=CONNECTION_COLOR, width=CONNECTION_WIDTH, dash=CONNECTION_DASH, tags=(TAG_CONNECTION_LINE,))
            else:
                line = self.__view.get_canvas().create_line(from_x, from_y, to_x, to_y, fill=CONNECTION_COLOR, width=CONNECTION_WIDTH, tags=(TAG_CONNECTION_LINE,))
                
            self.__lines.append(line)
            
        self.attempt_to_set_number()
        
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
        
    def create_corners(self, start_x, start_y, end_x, end_y):
        corners_from_start = []
        corners_from_end = []
        
        position_start = (start_x, start_y, self.__start_direction)
        position_end = (end_x, end_y, self.__end_direction)
        
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
        
    def remove_corners(self):
        """
        for i in range(len(self.__corners)-1, -1, -1):
            if remove_manually_moved or not self.__corners[i].is_manually_moved():
                self.__corners[i].delete()
                self.__corners.pop(i)
        """
        for corner in self.__corners:
            corner.delete()
            
        self.__corners.clear()
        
    def remove_lines(self):
        for line in self.__lines:
            self.__view.get_canvas().delete(line)
            
        self.attempt_to_remove_number()
        
        self.__lines.clear()
        
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
        
    def set_external(self, is_external):
        self.__is_external = is_external
        self.__end_block.get_attached_configuration_attribute_gui().get_configuration_attribute().add_input_configuration_attribute(self.__start_block.get_configuration_attribute(), not is_external)
        
        self.create_new_lines()
        
    def delete(self):
        self.__start_block.remove_connection(self)
                
        if self.__end_block != None:
            self.__end_block.remove_connection(self)
            attached_configuration_attribute_gui = self.__end_block.get_attached_configuration_attribute_gui()
            
            if attached_configuration_attribute_gui != None:
                attached_configuration_attribute_gui.get_configuration_class_gui().update_value_input_types()
                
        self.remove_corners()
        self.remove_lines()
        
    def save_state(self):
        saved_states = {"start_block": str(self.__start_block), "start_direction": self.__start_direction, "end_direction": self.__end_direction, "corner_coordinates": [], "is_external": self.__is_external}
        
        for corner in self.__corners:
            saved_states["corner_coordinates"].append((corner.get_x(), corner.get_y()))
            
        return saved_states
                
class GUIConnectionWithBlocks(GUIConnection):
    def __init__(self, model, view):
        self.__start_block = GUIConnectionTriangle(model, view, GUI_BLOCK_START_COORDINATES[0][0], GUI_BLOCK_START_COORDINATES[0][1], "RIGHT", False)
        self.__end_block = GUIConnectionTriangle(model, view, GUI_BLOCK_START_COORDINATES[1][0], GUI_BLOCK_START_COORDINATES[1][1], "RIGHT", True)
        
        self.__model = model
        self.__view = view
        self.__input_scalars = None
        self.__input_scalars_indicator = None
        super().__init__(model, view, self.__start_block, "RIGHT", end_block=self.__end_block, end_direction="LEFT")
        
        self.__is_deleted = False
        
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
    """
    
    def scale(self, last_length_unit):
        super().scale(last_length_unit)
        
        if self.__input_scalars_indicator != None:
            self.__input_scalars_indicator.scale(last_length_unit)
            
    def create_new_lines(self, mouse_location=None):
        super().create_new_lines()
        
        self.update_input_scalars_indicator()
        
    def move_lines(self, move_x, move_y):
        only_moved = super().move_lines(move_x, move_y)
        
        if only_moved and self.__input_scalars_indicator != None:
            self.__input_scalars_indicator.move_block(move_x, move_y)
    
    def open_options(self):
        return OptionsConnectionWithBlocks(self.__model.get_root(), self)
        
    def get_start_setup_class_gui(self):
        return self.__start_block.get_attached_setup_class_gui()
    
    def get_end_setup_class_gui(self):
        return self.__end_block.get_attached_setup_class_gui()
    
    def get_start_setup_class(self):
        start_attached_setup_class_gui = self.__start_block.get_attached_setup_class_gui()
        
        if start_attached_setup_class_gui == None:
            return None
        
        return start_attached_setup_class_gui.get_setup_class()
        
    def get_end_setup_class(self):
        end_attached_setup_class_gui = self.__end_block.get_attached_setup_class_gui()
        
        if end_attached_setup_class_gui == None:
            return None
            
        return end_attached_setup_class_gui.get_setup_class()
    
    def move_and_place_blocks(self, new_start_x, new_start_y, new_end_x, new_end_y, input_scalars_indicator_coordinate):
        self.__start_block.move_block(new_start_x - GUI_BLOCK_START_COORDINATES[0][0], new_start_y - GUI_BLOCK_START_COORDINATES[0][1])
        self.__start_block.put_down_block()
        
        self.__end_block.move_block(new_end_x - GUI_BLOCK_START_COORDINATES[1][0], new_end_y - GUI_BLOCK_START_COORDINATES[1][1])
        self.__end_block.put_down_block()
        
        if self.__input_scalars_indicator != None:
            self.__input_scalars_indicator.move_block(input_scalars_indicator_coordinate[0] - self.__input_scalars_indicator.get_x(), input_scalars_indicator_coordinate[1] - self.__input_scalars_indicator.get_y())
            
    def get_movable_items(self):
        movable_items = []
        
        for potential_block in [self.__start_block, self.__end_block]:
            if not potential_block.is_attached():
                movable_items.append(potential_block)
                
        return movable_items
        
    def get_input_scalars(self):
        return self.__input_scalars
        
    def set_input_scalars(self, input_scalars):
        if input_scalars != None and input_scalars[0] == DEFAULT_INPUT_SCALAR:
            self.reset_input_scalars()
            return
            
        self.__input_scalars = input_scalars
        
        start_setup_class_gui = self.get_start_setup_class_gui()
        end_setup_class_gui = self.get_end_setup_class_gui()
        
        if start_setup_class_gui != None and end_setup_class_gui != None:
            end_setup_class_gui.get_setup_class().set_input_setup_class_scalars(start_setup_class_gui.get_setup_class(), input_scalars)
            
        self.update_input_scalars_indicator()
        
    def reset_input_scalars(self):
        self.set_input_scalars(None)
        
    def get_input_scalars_string(self):
        if self.__input_scalars != None:
            return convert_value_to_string(self.__input_scalars)
            
        return str(DEFAULT_INPUT_SCALAR)
        
    def update_input_scalars_indicator(self):
        if self.__input_scalars_indicator != None:
            self.__input_scalars_indicator.delete(False)
            
        if self.__input_scalars != None:
            if (len(self.__input_scalars) == 1 and self.__input_scalars[0] != DEFAULT_INPUT_SCALAR) or len(self.__input_scalars) == 3:
                self.__input_scalars_indicator = GUIConnectionScalarsIndicator(self.__model, self.__view, self)
                
    def get_scalars_indicator_start_coordinate(self):
        corners = self.get_corners()
        end_x, end_y = self.get_attached_grid_coordinate(False)
        
        if len(corners) > 0:
            start_x, start_y = corners[-1].get_x(), corners[-1].get_y()
            
        else:
            start_x, start_y = self.get_attached_grid_coordinate(True)
            
        indicator_x = abs(start_x + end_x) / 2
        indicator_y = abs(start_y + end_y) / 2
        
        indicator_x -= INPUT_SCALARS_INDICATOR_WIDTH // 2
        indicator_y -= INPUT_SCALARS_INDICATOR_HEIGHT // 2
        
        offset_from_grid_x, offset_from_grid_y = distance_to_closest_grid_intersection(self.__view, indicator_x, indicator_y)
        
        indicator_x -= offset_from_grid_x
        indicator_y -= offset_from_grid_y
        
        return indicator_x, indicator_y
        
    def allowed_scalars_indicator_movement_directions(self):
        allowed_directions = []
        indicator_pos = (self.__input_scalars_indicator.get_x()+self.__input_scalars_indicator.get_width()//2, self.__input_scalars_indicator.get_y()+self.__input_scalars_indicator.get_height()//2)
        
        start_x, start_y = self.get_attached_grid_coordinate(True)
        end_x, end_y = self.get_attached_grid_coordinate(False)
        corners = self.get_corners()
        
        coordinates = [(start_x, start_y)] + [(corner.get_x(), corner.get_y()) for corner in corners] + [(end_x, end_y)]
        
        for i in range(1, len(coordinates)):
            first_pos, second_pos = coordinates[i-1], coordinates[i]
            
            # Vertically aligned
            if indicator_pos[0] == first_pos[0] == second_pos[0]:
                if indicator_pos[1] > min(first_pos[1], second_pos[1]):
                    allowed_directions.append("UP")
                    
                if indicator_pos[1] < max(first_pos[1], second_pos[1]):
                    allowed_directions.append("DOWN")
                    
            # Horizontally aligned
            if indicator_pos[1] == first_pos[1] == second_pos[1]:
                if indicator_pos[0] > min(first_pos[0], second_pos[0]):
                    allowed_directions.append("LEFT")
                    
                if indicator_pos[0] < max(first_pos[0], second_pos[0]):
                    allowed_directions.append("RIGHT")
                    
        return allowed_directions
        
    def is_deleted(self):
        return self.__is_deleted()
        
    def delete(self):
        if not self.__is_deleted:
            self.__is_deleted = True
            
            if self.__input_scalars_indicator != None:
                self.__input_scalars_indicator.delete()
                
            self.remove_corners()
            self.remove_lines()
            self.__view.remove_connection_with_blocks(self)
            
            self.__start_block.delete()
            self.__end_block.delete()
            
    def save_state(self):
        saved_states = {"start_block": self.__start_block.save_state(), "end_block": self.__end_block.save_state(), "input_scalars": self.__input_scalars}
        
        if self.__input_scalars_indicator == None:
            saved_states["input_scalars_indicator_coordinate"] = None
        else:
            saved_states["input_scalars_indicator_coordinate"] = (self.__input_scalars_indicator.get_x(), self.__input_scalars_indicator.get_y())
            
        return saved_states

