from blocks_general import GUIBlock, GUIModelingBlock
from options import OptionsSetupClass
from config import *

class GUISetupClass(GUIModelingBlock):
    def __init__(self, model, view, setup_class, configuration_class_gui, x, y, linked_group_number=None):
        self.__configuration_class_gui = configuration_class_gui
        self.__setup_class = setup_class
        
        super().__init__(model, view, self.__setup_class.get_instance_name(), x, y, CLASS_WIDTH*SETUP_WIDTH_MULTIPLIER, CLASS_HEIGHT, CLASS_COLOR, bind_left=True, bind_right=True)
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
        
    def right_clicked(self, event):
        OptionsSetupClass(self.get_model(), self, self.__configuration_class_gui, self.get_model().get_setup_view_names())
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        for connection in self.__connections:
            connection.move_blocks(move_x, move_y, self)
            
        if self.__linked_group_number != None:
            actual_move_x = move_x * LENGTH_UNIT
            actual_move_y = move_y * LENGTH_UNIT
            
            self.get_canvas().move(self.__circle_linked_group, actual_move_x, actual_move_y)
            self.get_canvas().move(self.__label_linked_group, actual_move_x, actual_move_y)
            
    def is_adjacent(self, coordinates):
        for coordinate in coordinates:
            for i in range(self.get_width()):
                # Above class
                if coordinate == (self.get_x() + i, self.get_y() - 1):
                    return True, "UP"
                    
                if len(self.__setup_attributes_gui) > 0:
                    last_attribute = self.__setup_attributes_gui[-1]
                    
                    # Below last attribute
                    if coordinate == (last_attribute.get_x() + i, last_attribute.get_y() + last_attribute.get_height()):
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
            circle_radius = LINKED_GROUP_CIRCLE_RADIUS * LENGTH_UNIT
            
            actual_x = self.get_x() * LENGTH_UNIT
            actual_y = self.get_y() * LENGTH_UNIT
            
            self.__circle_linked_group = self.get_view().get_canvas().create_oval(actual_x-circle_radius, actual_y-circle_radius, actual_x+circle_radius, actual_y+circle_radius, width=LINKED_GROUP_CIRCLE_OUTLINE, outline=LINKED_GROUP_CIRCLE_OUTLINE_COLOR, fill=LINKED_GROUP_CIRCLE_COLOR)
            self.__label_linked_group = self.get_view().get_canvas().create_text(actual_x, actual_y, text=self.__linked_group_number)
        
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
        
        super().__init__(model, view, configuration_attribute_gui.get_text(), x, y, ATTRIBUTE_WIDTH*SETUP_WIDTH_MULTIPLIER, ATTRIBUTE_HEIGHT, ATTRIBUTE_COLOR, bind_left=False, bind_right=False, has_value=True)
        
        configuration_attribute_gui.add_setup_attribute_gui(self)
        # self.add_attached_block(self.__value_distribution)
        
    def add_entered_value_to_attribute(self):
        if not self.__configuration_attribute_gui.get_configuration_attribute().has_input_attributes():
            self.__setup_attribute.set_value(self.get_entered_value())
        
    def update_value(self):
        if self.__configuration_attribute_gui.get_configuration_attribute().has_input_attributes():
            self.enable_value_label()
            self.set_displayed_value(self.__setup_attribute.get_value())
            
    def set_name(self, name):
        self.__setup_attribute.set_name(name)
        
    def delete(self):
        super().delete()
        self.__configuration_attribute_gui.remove_setup_attribute_gui(self)
        
    def save_state(self):
        return super().save_state() | {"value": self.__setup_attribute.get_value()}
                
class GUIConnectionTriangle(GUIBlock):
    def __init__(self, model, view, x, y, direction, is_end_block):
        self.__is_end_block = is_end_block
        self.__triangle = view.get_canvas().create_polygon(self.get_triangle_coordinates(x, y, direction), width=OUTLINE_WIDTH, outline=OUTLINE_COLOR, fill=CONNECTION_END_COLOR)
        self.__view = view
        
        super().__init__(model, view, [self.__triangle], x, y, CONNECTION_END_WIDTH, CONNECTION_END_HEIGHT, bind_left=True, bind_right=True)
        self.__connection = None
        self.__attached_class_gui = None
        
    def left_clicked(self, event):
        super().left_clicked(event)
        
        if not self.is_picked_up():
            self.put_down_block()
                    
        elif self.__attached_class_gui != None:
            self.__connection.attempt_to_disconnect_both_classes()
            self.__attached_class_gui.remove_connection(self.__connection)
            self.__attached_class_gui = None
            
    def right_clicked(self, event):
        self.__connection.delete()
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        self.__connection.create_lines()
        
    def put_down_block(self):
        for setup_class_gui in self.get_view().get_setup_classes_gui():
            is_adjacent, direction = setup_class_gui.is_adjacent([(self.get_x(), self.get_y())])
            
            if is_adjacent:
                setup_class_gui.add_connection(self.__connection)
                self.__attached_class_gui = setup_class_gui
                self.__connection.attempt_to_connect_both_classes()
                
                self.__connection.update_direction(self, direction)
                self.rotate_triangle(direction)
                return
        
    def rotate_triangle(self, new_direction):
        if self.__is_end_block:
            directions = ["UP", "RIGHT", "DOWN", "LEFT"]
            new_direction = directions[(directions.index(new_direction) + 2) % len(directions)]
            
        new_coordinates = self.get_triangle_coordinates(self.get_x(), self.get_y(), new_direction)
        self.__view.get_canvas().coords(self.__triangle, new_coordinates)
        
    def get_triangle_coordinates(self, x, y, direction):
        upper_left = [x, y]
        upper_right = [x+CONNECTION_END_WIDTH, y]
        lower_left = [x, y+CONNECTION_END_HEIGHT]
        lower_right = [x+CONNECTION_END_WIDTH, y+CONNECTION_END_HEIGHT]
        
        if direction == "UP":
            coordinates = [x+CONNECTION_END_WIDTH/2, y] + lower_right + lower_left
        elif direction == "RIGHT":
            coordinates = upper_left + [x+CONNECTION_END_WIDTH, y+CONNECTION_END_HEIGHT/2] + lower_left
        elif direction == "DOWN":
            coordinates = upper_left + upper_right + [x+CONNECTION_END_WIDTH/2, y+CONNECTION_END_HEIGHT]
        elif direction == "LEFT":
            coordinates = upper_right + lower_right + [x, y+CONNECTION_END_HEIGHT/2]
            
        for i in range(len(coordinates)):
            coordinates[i] *= LENGTH_UNIT
            
        return coordinates
        
    def add_connection(self, connection):
        self.__connection = connection
        
    def get_attached_class(self):
        return self.__attached_class_gui
        
    def is_attached(self):
        return self.__attached_class_gui != None
        
    def attempt_to_detach_from_class(self):
        if self.__attached_class_gui != None:
            self.__attached_class_gui.remove_connection(self)
            
