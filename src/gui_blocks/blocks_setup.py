import numpy as np
from helper_functions import convert_grid_coordinate_to_actual, get_triangle_coordinates
from blocks_general import GUIBlock, GUIModelingBlock
from options import OptionsSetupClass
from config import *

class GUISetupClass(GUIModelingBlock):
    def __init__(self, model, view, setup_class, configuration_class_gui, x, y, linked_group_number=None):
        self.__configuration_class_gui = configuration_class_gui
        self.__setup_class = setup_class
        
        super().__init__(model, view, self.__setup_class.get_instance_name(), x, y, CLASS_WIDTH*SETUP_WIDTH_MULTIPLIER, CLASS_HEIGHT, CLASS_COLOR, bind_left=MOUSE_DRAG, bind_right=MOUSE_PRESS)
        self.__setup_attributes_gui = []
        self.__connections = []
        
        self.__linked_group_number = linked_group_number
        self.__circle_linked_group = None
        self.__label_linked_group = None
        
        configuration_class_gui.add_setup_class_gui(self)
        
        for configuration_attribute_gui, setup_attribute in zip(self.__configuration_class_gui.get_configuration_attributes_gui(), self.__setup_class.get_setup_attributes()):
            self.convert_to_attribute_gui(configuration_attribute_gui, setup_attribute)
            
        self.update_text()
        
        if self.__linked_group_number != None:
            self.update_linked_group_indicator()
            
        # self.snap_to_grid()
        
    def right_pressed(self, event):
        OptionsSetupClass(self.get_model(), self, self.__configuration_class_gui, self.get_model().get_setup_view_names())
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        if self.__linked_group_number != None:
            actual_move_x, actual_move_y = convert_grid_coordinate_to_actual(self.get_view(), move_x, move_y)
            
            self.get_canvas().move(self.__circle_linked_group, actual_move_x, actual_move_y)
            self.get_canvas().move(self.__label_linked_group, actual_move_x, actual_move_y)
            
    def scale(self, last_length_unit):
        super().scale(last_length_unit)
        
        for connection in self.__connections:
            # Only scale connection if this class is connected to the start block of the connection to avoid moving it twice
            if self.has_attached_block(connection.get_start_block()):
                connection.scale(last_length_unit)
            
    def is_adjacent(self, coordinates):
        # Above class
        for coordinate in coordinates:
            coordinate_to_check = np.array(coordinate)
            
            for i in range(self.get_width()):
                coordinate_up = np.array((self.get_x() + i, self.get_y() - 1))
                
                if np.linalg.norm(coordinate_to_check - coordinate_up) < 0.5:
                    return True, "UP"
                    
                if len(self.__setup_attributes_gui) == 0:
                    coordinate_down = np.array((self.get_x() + i, self.get_y() + self.get_height()))
                else:
                    last_attribute = self.__setup_attributes_gui[-1]
                    coordinate_down = np.array((last_attribute.get_x() + i, last_attribute.get_y() + last_attribute.get_height()))
                    
                # Below last attribute
                if np.linalg.norm(coordinate_to_check - coordinate_down) < 0.5:
                    return True, "DOWN"
                        
        # Sides of class
        is_adjacent_side, direction = super().is_adjacent(coordinates)
        
        if is_adjacent_side:
            return True, direction 
                
        for i, attribute in enumerate(self.__setup_attributes_gui):
            # Sides of attribute
            is_adjacent_side, direction = attribute.is_adjacent(coordinates)
            
            if is_adjacent_side:
                return True, direction
                    
        return False, ""
        
    def create_setup_attribute(self, configuration_attribute_gui):
        setup_attribute = self.__setup_class.create_setup_attribute(configuration_attribute_gui.get_configuration_attribute())
        self.convert_to_attribute_gui(configuration_attribute_gui, setup_attribute)
        
    def convert_to_attribute_gui(self, configuration_attribute_gui, setup_attribute):
        if not configuration_attribute_gui.is_hidden():
            setup_attribute_gui = GUISetupAttribute(self.get_model(), self.get_view(), setup_attribute, configuration_attribute_gui, self.get_x(), self.get_y()+CLASS_HEIGHT+len(self.__setup_attributes_gui)*ATTRIBUTE_HEIGHT)
            
            self.__setup_attributes_gui.append(setup_attribute_gui)
            self.add_attached_block(setup_attribute_gui)
            
    def get_setup_class(self):
        return self.__setup_class
        
    def get_setup_attributes_gui(self):
        return self.__setup_attributes_gui
        
    def remove_setup_attribute_gui_by_index(self, setup_attribute_gui_index):
        self.__setup_attributes_gui.pop(setup_attribute_gui_index)
        
        for setup_attribute_gui in self.__setup_attributes_gui[setup_attribute_gui_index:]:
            setup_attribute_gui.move_block(0, -1)
            
    def add_connection(self, connection):
        self.__connections.append(connection)
        
    def remove_connection(self, connection):
        if connection in self.__connections:
            self.__connections.remove(connection)
            
    def get_linked_group_number(self):
        return self.__linked_group_number
        
    def set_linked_group_number(self, linked_group_number):
        self.__linked_group_number = linked_group_number
        self.update_linked_group_indicator()
        
    def update_linked_group_indicator(self):
        # Remove any existing indicator
        if self.__circle_linked_group != None:
            self.get_canvas().delete(self.__circle_linked_group)
            self.__circle_linked_group = None
            
        if self.__label_linked_group != None:
            self.get_canvas().delete(self.__label_linked_group)
            self.__label_linked_group = None
                
        # Add or update indicator
        if self.__linked_group_number != None:
            circle_radius = convert_grid_coordinate_to_actual(self.get_view(), LINKED_GROUP_CIRCLE_RADIUS, 0)[0]
            actual_x, actual_y = convert_grid_coordinate_to_actual(self.get_view(), self.get_x(), self.get_y())
            
            self.__circle_linked_group = self.get_view().get_canvas().create_oval(actual_x-circle_radius, actual_y-circle_radius, actual_x+circle_radius, actual_y+circle_radius, width=LINKED_GROUP_CIRCLE_OUTLINE, outline=LINKED_GROUP_CIRCLE_OUTLINE_COLOR, fill=LINKED_GROUP_CIRCLE_COLOR)
            self.__label_linked_group = self.get_view().get_canvas().create_text(actual_x, actual_y, text=self.__linked_group_number, font=FONT)
            
    def update_value_input_types(self):
        for setup_attribute_gui in self.__setup_attributes_gui:
            setup_attribute_gui.update_value_input_type(self, self.__setup_class.get_input_classes())
            
    def calculate_values(self):
        self.__setup_class.calculate_values()
        
        for setup_attribute_gui in self.__setup_attributes_gui:
            setup_attribute_gui.update_value()
        
    def reset_calculated_values(self):
        self.__setup_class.reset_calculated_values()
        
        for setup_attribute_gui in self.__setup_attributes_gui:
            setup_attribute_gui.add_entered_value_to_attribute()
            
    def get_name(self):
        return self.__setup_class.get_instance_name()
        
    def set_name(self, name):
        self.__setup_class.set_instance_name(name)
        self.update_text()
        
    def update_text(self):
        self.set_text(f"{self.__configuration_class_gui.get_name()}: {self.__setup_class.get_instance_name()}")
        
    def delete(self):
        super().delete()
        self.__configuration_class_gui.remove_setup_class_gui(self)
        self.get_view().remove_setup_class_gui(self)
        
        if self.__linked_group_number != None:
            self.get_canvas().delete(self.__circle_linked_group)
            self.get_canvas().delete(self.__label_linked_group)
            
            self.get_model().remove_setup_class_gui_from_linked_group(self)
        
    def save_state(self):
        saved_states = super().save_state() | {"name": self.get_name(), "linked_group_number": self.__linked_group_number, "configuration_class_gui": str(self.__configuration_class_gui), "setup_attributes_gui": []}
        
        for setup_attribute_gui in self.__setup_attributes_gui:
            saved_states["setup_attributes_gui"].append(setup_attribute_gui.save_state())
            
        return saved_states
        
class GUISetupAttribute(GUIModelingBlock):
    def __init__(self, model, view, setup_attribute, configuration_attribute_gui, x, y):
        self.__setup_attribute = setup_attribute
        self.__configuration_attribute_gui = configuration_attribute_gui
        
        super().__init__(model, view, configuration_attribute_gui.get_text(), x, y, ATTRIBUTE_WIDTH*SETUP_WIDTH_MULTIPLIER, ATTRIBUTE_HEIGHT, ATTRIBUTE_COLOR, has_value=True)
        
        configuration_attribute_gui.add_setup_attribute_gui(self)
        # self.add_attached_block(self.__value_distribution)
        
    def update_value_input_type(self, setup_class, connected_setup_classes):
        has_currently_connected_inputs = self.__setup_attribute.has_connected_setup_attributes(setup_class, connected_setup_classes)
        
        if has_currently_connected_inputs:
            self.enable_value_label()
        else:
            self.enable_value_entry()
            
    def add_entered_value_to_attribute(self):
        if self.has_input_entry():
            self.__setup_attribute.set_value(self.get_entered_value())
            
    def update_value(self):
        if self.__setup_attribute.has_override_value():
            self.enable_value_label()
            self.set_displayed_value(self.__setup_attribute.get_override_value(), "red")
        else:
            self.set_displayed_value(self.__setup_attribute.get_value())
            
    def set_override_value(self, override_value):
        self.__setup_attribute.set_override_value(override_value)
        
    def reset_override_value(self):
        self.__setup_attribute.reset_override_value()
        self.update_value_input_type()
            
    def set_name(self, name):
        self.__setup_attribute.set_name(name)
        
    def delete(self):
        super().delete()
        self.__configuration_attribute_gui.remove_setup_attribute_gui(self)
        
    def save_state(self):
        self.add_entered_value_to_attribute()
        
        return super().save_state() | {"value": self.__setup_attribute.get_value()}
                
class GUIConnectionTriangle(GUIBlock):
    def __init__(self, model, view, x, y, direction, is_end_block):
        self.__is_end_block = is_end_block
        self.__triangle = view.get_canvas().create_polygon(get_triangle_coordinates(view, x, y, direction), width=OUTLINE_WIDTH, outline=OUTLINE_COLOR, fill=CONNECTION_END_COLOR)
        
        super().__init__(model, view, [self.__triangle], x, y, CONNECTION_END_WIDTH, CONNECTION_END_HEIGHT, bind_left=MOUSE_DRAG, bind_right=MOUSE_PRESS)
        self.__connection = None
        self.__attached_class_gui = None
        
        self.__is_deleted = False
        
    def left_pressed(self, event):
        super().left_pressed(event)
        
        # Disconnect from class
        if self.__attached_class_gui != None:
            self.attempt_to_detach_from_class()
            
    def left_released(self, event):
        if super().left_released(event):
            self.put_down_block()
            
    def right_pressed(self, event):
        self.delete()
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        # If panning or zooming, only the start block should move the lines
        if (not self.get_view().is_panning() and not self.get_view().is_zooming()) or not self.__is_end_block:
            self.__connection.move_lines(move_x, move_y)
            
    def put_down_block(self):
        for setup_class_gui in self.get_view().get_setup_classes_gui():
            is_adjacent, direction = setup_class_gui.is_adjacent([(self.get_x(), self.get_y())])
            
            # Attach to class
            if is_adjacent:
                setup_class_gui.add_connection(self.__connection)
                setup_class_gui.add_attached_block(self)
                self.__attached_class_gui = setup_class_gui
                self.__connection.attempt_to_connect_both_classes()
                
                self.__connection.update_direction(self, direction)
                self.rotate_triangle(direction)
                return
        
    def rotate_triangle(self, new_direction):
        if self.__is_end_block:
            directions = ["UP", "RIGHT", "DOWN", "LEFT"]
            new_direction = directions[(directions.index(new_direction) + 2) % len(directions)]
            
        new_coordinates = get_triangle_coordinates(self.get_view(), self.get_x(), self.get_y(), new_direction)
        self.get_view().get_canvas().coords(self.__triangle, new_coordinates)
        
    def add_connection(self, connection):
        self.__connection = connection
        
    def get_attached_class(self):
        return self.__attached_class_gui
        
    def is_attached(self):
        return self.__attached_class_gui != None
        
    def is_attached(self):
        return self.__attached_class_gui != None
        
    def attempt_to_detach_from_class(self):
        if self.__attached_class_gui != None:
            self.__connection.attempt_to_disconnect_both_classes()
            self.__attached_class_gui.remove_connection(self.__connection)
            self.__attached_class_gui.remove_attached_block(self)
            self.__attached_class_gui = None
            
    def delete(self):
        if not self.__is_deleted:
            self.__is_deleted = True
            
            super().delete()
            self.attempt_to_detach_from_class()
            
            self.__connection.delete()
