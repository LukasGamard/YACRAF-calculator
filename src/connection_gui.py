import tkinter as tk
import numpy as np
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
            
            self.create_lines()
        
    def update_direction(self, affected_block, new_direction):
        if affected_block == self.__start_block:
            self.__start_direction = new_direction
            
        elif affected_block == self.__end_block:
            self.__end_direction = new_direction
            
        self.create_lines()
        
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
        actual_x = (x + 0.5) * LENGTH_UNIT
        actual_y = (y + 0.5) * LENGTH_UNIT
        
        if direction == "UP":
            actual_y += 0.5 * LENGTH_UNIT
        elif direction == "DOWN":
            actual_y -= 0.5 * LENGTH_UNIT
        elif direction == "LEFT":
            actual_x += 0.5 * LENGTH_UNIT
        elif direction == "RIGHT":
            actual_x -= 0.5 * LENGTH_UNIT
            
        return actual_x, actual_y
        
    def create_lines(self, mouse_location=None):
        corner_coordinates = self.create_corners(mouse_location)
        self.create_lines_from_corners(corner_coordinates)
        
        for corner_x, corner_y in corner_coordinates:
            self.__corners.append(GUIConnectionCorner(self.__model, self.__view, self, corner_x, corner_y))
        
        self.attempt_to_set_number()
        
    def attempt_to_set_number(self):
        if self.__num_order != None:
            num_order_actual_x = self.__start_x
            num_order_actual_y = self.__start_y + self.__start_block.get_height() / 2
            circle_radius = NUM_ORDER_CIRCLE_RADIUS * LENGTH_UNIT
            
            if self.__start_direction == "LEFT":
                num_order_actual_x += 1
                
            num_order_actual_x *= LENGTH_UNIT
            num_order_actual_y *= LENGTH_UNIT
            
            self.__circle_num_order = self.__view.get_canvas().create_oval(num_order_actual_x-circle_radius, num_order_actual_y-circle_radius, num_order_actual_x+circle_radius, num_order_actual_y+circle_radius, width=NUM_ORDER_CIRCLE_OUTLINE, outline=NUM_ORDER_CIRCLE_OUTLINE_COLOR, fill=NUM_ORDER_CIRCLE_COLOR)
            self.__label_num_order = self.__view.get_canvas().create_text(num_order_actual_x, num_order_actual_y, text=self.__num_order)
            
    def attempt_to_remove_number(self):
        if self.__circle_num_order != None:
            self.__view.get_canvas().delete(self.__circle_num_order)
            
        if self.__label_num_order != None:
            self.__view.get_canvas().delete(self.__label_num_order)
        
    def create_lines_from_corners(self, corner_coordinates):
        actual_coordinates = [self.get_actual_attached_coordinates(self.__start_x, self.__start_y, self.__start_direction)]
        
        for corner_x, corner_y in corner_coordinates:
            actual_coordinates.append(((corner_x+0.5)*LENGTH_UNIT, (corner_y+0.5)*LENGTH_UNIT))
            
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
            self.__end_x = mouse_location[0] // LENGTH_UNIT
            self.__end_y = mouse_location[1] // LENGTH_UNIT
            
            if self.__end_x > self.__start_x:
                self.__end_direction = "LEFT"
                self.__end_x -= 1
                
            else:
                self.__end_direction = "RIGHT"
                self.__end_x += 1
                
        position_start = (self.__start_x, self.__start_y, self.__start_direction)
        position_end = (self.__end_x, self.__end_y, self.__end_direction)
        
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
                        mid_y = int((start_y + end_y) / 2)
                        corners_from_start.append((start_x, mid_y))
                        corners_from_end.append((end_x, mid_y))
                        
                    else:
                        mid_x = int((start_x + end_x) / 2)
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
                
        """
        self.__start_x, self.__start_y = self.get_coordinates(self.__start_block, self.__start_direction)
        
        if mouse_location == None:
            self.__end_x, self.__end_y = self.get_coordinates(self.__end_block, self.__end_direction)
            
        else:
            self.__end_x = int(mouse_location[0] / LENGTH_UNIT)
            self.__end_y = int(mouse_location[1] / LENGTH_UNIT)
            
            if self.__end_x > self.__start_x:
                self.__end_direction = "LEFT"
                self.__end_x -= 1
                
            else:
                self.__end_direction = "RIGHT"
                self.__end_x += 1
                
        positions = sorted([(self.__start_x, self.__start_y, self.__start_direction), (self.__end_x, self.__end_y, self.__end_direction)], key=lambda x: x[2])
        directions = (positions[0][2], positions[1][2])
        are_reversed = directions[0] == self.__end_direction
        
        # Same direction
        if directions[0] == directions[1]:
            if directions[0] == "UP":
                matched_y = min(positions[0][1], positions[1][1]) - 1 # y-value of the one furthest up
                corners.append((self.__start_x, matched_y))
                corners.append((self.__end_x, matched_y))
                
            elif directions[0] == "RIGHT":
                matched_x = max(positions[0][0], positions[1][0]) + 1 # x-value of the one furthest to the right
                corners.append((matched_x, self.__start_y))
                corners.append((matched_x, self.__end_y))
                
            elif directions[0] == "DOWN":
                matched_y = max(positions[0][1], positions[1][1]) + 1 # y-value of the one furthest down
                corners.append((self.__start_x, matched_y))
                corners.append((self.__end_x, matched_y))
                
            elif directions[0] == "LEFT":
                matched_x = min(positions[0][0], positions[1][0]) - 1 # x-value of the one furthest to the left
                corners.append((matched_x, self.__start_y))
                corners.append((matched_x, self.__end_y))
                
        # Opposite directions
        elif directions == ("LEFT", "RIGHT"):
            if positions[0][0] <= positions[1][0] + 1:
                mid_y = int((positions[0][1] + positions[1][1]) / 2)
                corners.append((positions[0][0]-1, positions[0][1]))
                corners.append((positions[0][0]-1, mid_y))
                corners.append((positions[1][0]+1, mid_y))
                corners.append((positions[1][0]+1, positions[1][1]))
                
            else:
                mid_x = int((positions[0][0] + positions[1][0]) / 2)
                corners.append((mid_x, positions[0][1]))
                corners.append((mid_x, positions[1][1]))
                
            if are_reversed:
                corners.reverse()
                
        elif directions == ("DOWN", "UP"):
            if positions[0][1] >= positions[1][1] - 1:
                mid_x = int((positions[0][0] + positions[1][0]) / 2)
                corners.append((positions[1][0], positions[1][1]-1))
                corners.append((mid_x, positions[1][1]-1))
                corners.append((mid_x, positions[0][1]+1))
                corners.append((positions[0][0], positions[0][1]+1))
                
            else:
                mid_y = int((positions[0][1] + positions[1][1]) / 2)
                corners.append((positions[1][0], mid_y))
                corners.append((positions[0][0], mid_y))
        """
        
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
        
    def get_movable_items(self):
        movable_items = [self.__start_block]
        
        if self.__end_block != None:
            movable_items.append(self.__end_block)
            
        return movable_items
        
    def set_num_order(self, num_order):
        self.__num_order = num_order
        self.attempt_to_remove_number()
        self.attempt_to_set_number()
        
    def is_external(self):
        return self.__is_external
        
    def set_is_external(self, is_external):
        self.__is_external = is_external
        self.__end_block.set_input_attribute(self.__start_block.get_configuration_attribute(), not is_external)
        
        self.create_lines()
        
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
        self.create_lines()
        
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
            
    def attempt_to_disconnect_both_classes(self):
        start_class_gui = self.__start_block.get_attached_class()
        end_class_gui = self.__end_block.get_attached_class()
        
        if start_class_gui != None and end_class_gui != None:
            end_class_gui.get_setup_class().remove_input_class(start_class_gui.get_setup_class())
        
    def move_blocks(self, move_x, move_y, setup_block):
        if setup_block == self.__start_block.get_attached_class():
            self.__start_block.move_block(move_x, move_y)
            
        if setup_block == self.__end_block.get_attached_class():
            self.__end_block.move_block(move_x, move_y)
            
    def move_and_place_blocks(self, new_start_x, new_start_y, new_end_x, new_end_y):
        self.__start_block.move_block(new_start_x - GUI_BLOCK_START_COORDINATES[0][0], new_start_y - GUI_BLOCK_START_COORDINATES[0][1])
        self.__start_block.put_down_block()
        
        self.__end_block.move_block(new_end_x - GUI_BLOCK_START_COORDINATES[1][0], new_end_y - GUI_BLOCK_START_COORDINATES[1][1])
        self.__end_block.put_down_block()
        
    def delete(self):
        self.__start_block.delete_from_view()
        self.__end_block.delete_from_view()
        
        self.__view.delete_connection_with_blocks(self)
        
        for block in [self.__start_block, self.__end_block]:
            block.attempt_to_detach_from_class()
                
        self.remove_lines()
        
    def save_state(self):
        return {"start_block": self.__start_block.save_state(), "end_block": self.__end_block.save_state()}
