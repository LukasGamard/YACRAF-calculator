from blocks_general import GUIModelingBlock, GUIClass
from blocks_buttons import GUIAddAttributeButton
from options import OptionsConfigurationClass, OptionsConfigurationAttribute, OptionsCalculationInput
from helper_functions import delete_all
from config import *

class GUIConfigurationClass(GUIClass):
    def __init__(self, model, view, configuration_class, x, y, linked_group_number=None):
        self.__configuration_class = configuration_class
        super().__init__(model, view, self.__configuration_class.get_name(), x, y, CLASS_WIDTH, CLASS_HEIGHT, True, linked_group_number)
        self.__configuration_attributes_gui = []
        
        self.__setup_classes_gui = []
        self.__to_setup_buttons = {} # Add to setup button per view
        
        self.__add_button = GUIAddAttributeButton(model, view, x+CLASS_WIDTH//2, y+CLASS_HEIGHT, self)
        self.add_attached_block(self.__add_button)
        
        # self.snap_to_grid()
        
    def right_pressed(self, event):
        OptionsConfigurationClass(self.get_model(), self, self.get_model().get_configuration_views())
        
    def get_configuration_class(self):
        return self.__configuration_class
        
    def create_attribute(self, *, configuration_attribute=None):
        if configuration_attribute == None:
            configuration_attribute = self.__configuration_class.create_attribute("New Attribute")
            
        height_offset = CLASS_HEIGHT + len(self.__configuration_attributes_gui) * ATTRIBUTE_HEIGHT
        
        configuration_attribute_gui = GUIConfigurationAttribute(self.get_model(), self.get_view(), configuration_attribute, self, self.get_x(), self.get_y()+height_offset)
        
        self.__configuration_attributes_gui.append(configuration_attribute_gui)
        self.add_attached_block(configuration_attribute_gui)
        
        self.__add_button.move_block(0, ATTRIBUTE_HEIGHT)
        
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.create_setup_attribute(configuration_attribute_gui)
            
    def get_configuration_attributes_gui(self):
        return self.__configuration_attributes_gui
        
    def remove_configuration_attribute_gui(self, configuration_attribute_gui_to_remove):
        index_first_move_up = self.__configuration_attributes_gui.index(configuration_attribute_gui_to_remove)
        self.__configuration_attributes_gui.remove(configuration_attribute_gui_to_remove)
        
        for configuration_attribute_gui in self.__configuration_attributes_gui[index_first_move_up:]:
            configuration_attribute_gui.move_block(0, -ATTRIBUTE_HEIGHT)
            
        self.__add_button.move_block(0, -ATTRIBUTE_HEIGHT)
        
    def add_setup_class_gui(self, setup_class_gui):
        self.__setup_classes_gui.append(setup_class_gui)
        
    def remove_setup_class_gui(self, setup_class_gui):
        self.__setup_classes_gui.remove(setup_class_gui)
        
    def add_to_setup_button(self, view, to_setup_button):
        self.__to_setup_buttons[view] = to_setup_button
        
    def remove_to_setup_button(self, view):
        self.__to_setup_buttons.pop(view)
        
    def get_name(self):
        return self.__configuration_class.get_name()
        
    def set_name(self, name):
        self.__configuration_class.set_name(name)
        self.set_text(name)
        
        if self.get_linked_group_number() != None:
            for linked_configuration_class_gui in self.get_model().get_linked_configuration_classes_gui(self.get_linked_group_number()):
                if linked_configuration_class_gui is not self:
                    linked_configuration_class_gui.set_text(name)
        
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.update_text()
            
        for add_to_setup_button in self.__to_setup_buttons.values():
            add_to_setup_button.set_text(name)
            
    def copy(self, view_to_copy_to, x, y):
        configuration_class_gui = GUIConfigurationClass(self.get_model(), view_to_copy_to, self.__configuration_class, x, y, self.get_linked_group_number())
        
        # Create configuration attributes
        for configuration_attribute_gui in self.__configuration_attributes_gui:
            configuration_class_gui.create_attribute(configuration_attribute=configuration_attribute_gui.get_configuration_attribute())
            
        for setup_class_gui in self.__setup_classes_gui:
            configuration_class_gui.add_setup_class_gui(setup_class_gui)
            
        for add_to_setup_button in self.__to_setup_buttons.values():
            configuration_class_gui.add_to_setup_button(add_to_setup_button)
            
        return configuration_class_gui
        
    def delete(self):
        super().delete()
        self.get_view().remove_configuration_class_gui(self)
        
        if self.get_linked_group_number() == None:
            self.get_model().remove_add_to_setup_buttons(list(self.__to_setup_buttons.values()))
            
            delete_all(self.__setup_classes_gui)
        
    def save_state(self):
        saved_states = super().save_state() | {"name": self.get_name(), "configuration_class_gui": str(self), "configuration_attributes_gui": []}
        
        for configuration_attribute_gui in self.__configuration_attributes_gui:
            saved_states["configuration_attributes_gui"].append(configuration_attribute_gui.save_state())
            
        return saved_states
        
class GUIConfigurationAttribute(GUIModelingBlock):
    def __init__(self, model, view, configuration_attribute, configuration_class_gui, x, y):
        self.__configuration_attribute = configuration_attribute
        self.__configuration_class_gui = configuration_class_gui
        
        super().__init__(model, view, self.__configuration_attribute.get_name(), x, y, ATTRIBUTE_WIDTH, ATTRIBUTE_HEIGHT, ATTRIBUTE_COLOR, bind_left=MOUSE_PRESS, bind_right=MOUSE_PRESS)
        self.__configuration_input = None
        self.__connections = []
        
        self.__setup_attributes_gui = []
        
        self.update_text()
        
    def left_pressed(self, event):
        held_connection = self.get_view().get_held_connection()
        
        if held_connection == None:
            held_connection = self.get_model().create_connection(self, self.get_direction(event.x, event.y))
            held_connection.create_new_lines((event.x, event.y))
            
        else:
            self.get_view().reset_held_connection(True)
            
    def right_pressed(self, event):
        OptionsConfigurationAttribute(self.get_model().get_root(), self)
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        for connection in self.__connections:
            connection.move_lines(move_x, move_y)
            
    def scale(self, last_length_unit):
        super().scale(last_length_unit)
        
        for connection in self.__connections:
            connection.scale(last_length_unit)
            
    def get_linked_configuration_attributes_gui(self):
        linked_configuration_attributes_gui = []
        linked_group_number = self.__configuration_class_gui.get_linked_group_number()
        
        if linked_group_number != None:
            index_configuration_attribute_gui = self.__configuration_class_gui.get_configuration_attributes_gui().index(self)
            
            for linked_configuration_class_gui in self.get_model().get_linked_configuration_classes_gui(linked_group_number):
                if linked_configuration_class_gui is not self:
                    linked_configuration_attribute_gui = linked_configuration_class_gui.get_configuration_attributes_gui()[index_configuration_attribute_gui]
                    linked_configuration_attributes_gui.append(linked_configuration_attribute_gui)
                    
        return linked_configuration_attributes_gui
        
    def get_configuration_attribute(self):
        return self.__configuration_attribute
        
    def get_configuration_class_gui(self):
        return self.__configuration_class_gui
            
    def set_configuration_input(self, configuration_input):
        self.__configuration_input = configuration_input
        self.add_attached_block(configuration_input)
        
        # self.__configuration_attribute.set_symbol_calculation_type(configuration_input.get_symbol_.get())
        
    def remove_configuration_input(self):
        self.remove_attached_block(self.__configuration_input)
        self.__configuration_input = None
        
        self.__configuration_attribute.set_symbol_calculation_type(None)
        
    """
    def get_configuration_input(self):
        return self.__configuration_input
    """
    
    def add_connection(self, connection):
        self.__connections.append(connection)
        
    def remove_connection(self, connection):
        self.__connections.remove(connection)
        
    def is_hidden(self):
        return self.__configuration_attribute.is_hidden()
        
    def set_hidden(self, is_hidden):
        self.__configuration_attribute.set_hidden(is_hidden)
        
    def add_setup_attribute_gui(self, setup_attribute_gui):
        self.__setup_attributes_gui.append(setup_attribute_gui)
        
    def remove_setup_attribute_gui(self, setup_attribute_gui):
        self.__setup_attributes_gui.remove(setup_attribute_gui)
        
    def get_name(self):
        return self.__configuration_attribute.get_name()
        
    def set_name(self, name):
        self.__configuration_attribute.set_name(name)
        self.update_text()
        
        for linked_configuration_attribute_gui in self.get_linked_configuration_attributes_gui():
            linked_configuration_attribute_gui.update_text()
            
    def set_value_type(self, symbol_value_type):
        self.__configuration_attribute.set_symbol_value_type(symbol_value_type)
        self.update_text()
        
        for linked_configuration_attribute_gui in self.get_linked_configuration_attributes_gui():
            linked_configuration_attribute_gui.update_text()
            
    def update_text(self):
        if self.__configuration_attribute.get_symbol_value_type() != None:
            text = f"{self.__configuration_attribute.get_name()} ({self.__configuration_attribute.get_symbol_value_type()})"
        else:
            text = f"{self.__configuration_attribute.get_name()}"
        
        self.set_text(text)
        
        for setup_attribute_gui in self.__setup_attributes_gui:
            setup_attribute_gui.set_text(text)
        
    def delete(self):
        super().delete()
        
        delete_all(self.__connections)
        
        # Only the attribute is deleted, not the class itself
        if not self.__configuration_class_gui.is_deleted():
            self.__configuration_class_gui.remove_configuration_attribute_gui(self)
            delete_all(self.__setup_attributes_gui)
        
    def save_state(self):
        return {"configuration_attribute_gui": str(self), "name": self.get_name(), "symbol_value_type": self.__configuration_attribute.get_symbol_value_type(), "is_hidden": self.is_hidden()}

class GUIConfigurationInput(GUIModelingBlock):
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "?", x, y, INPUT_WIDTH, INPUT_HEIGHT, INPUT_COLOR, bind_left=MOUSE_DRAG, bind_right=MOUSE_PRESS)
        self.__attached_attribute_gui = None
        self.__connections = []
        self.__symbol_calculation_type = ""
        
        # self.snap_to_grid()
        
    def left_pressed(self, event):
        held_connection = self.get_view().get_held_connection()
        direction = "LEFT"
        
        # If clicking to add a held connection
        if held_connection != None:
            if self.__attached_attribute_gui != None and self.__attached_attribute_gui.get_x() < self.get_x():
                direction = "RIGHT"
                
            held_connection.set_end_location(self, direction)
            self.get_view().reset_held_connection()
            
        # Move block
        else:
            super().left_pressed(event)
            
            # Remove from being an input to an attribute
            if self.__attached_attribute_gui != None:
                self.__attached_attribute_gui.remove_configuration_input()
                self.__attached_attribute_gui = None
                
    def left_released(self, event):
        if super().left_released(event):
            self.put_down_block()
        
    def right_pressed(self, event):
        OptionsCalculationInput(self.get_model().get_root(), self)
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        # If panning or zooming, only the corresponding attribute should move the lines
        if not self.get_view().is_panning() and not self.get_view().is_zooming():
            for connection in self.__connections:
                connection.move_lines(move_x, move_y)
                
    def put_down_block(self):
        for configuration_class_gui in self.get_view().get_configuration_classes_gui():
            for configuration_attribute_gui in configuration_class_gui.get_configuration_attributes_gui():
                if configuration_attribute_gui.is_adjacent([(self.get_x(), self.get_y())])[0]:
                    self.__attached_attribute_gui = configuration_attribute_gui
                    self.__attached_attribute_gui.set_configuration_input(self)
                    return
                    
    def is_attached(self):
        return self.__attached_attribute_gui != None
            
    def get_symbol_calculation_type(self):
        return self.__symbol_calculation_type
        
    def set_symbol_calculation_type(self, symbol_calculation_type):
        self.__symbol_calculation_type = symbol_calculation_type
        self.set_text(symbol_calculation_type)
        
        self.update_connection_numbers()
        
        if self.__attached_attribute_gui != None:
            self.__attached_attribute_gui.get_configuration_attribute().set_symbol_calculation_type(symbol_calculation_type)
        
    def update_connection_numbers(self):
        for i, connection in enumerate(self.__connections):
            if self.__symbol_calculation_type in ENUMERATED_INPUT_CALCULATION_TYPE_SYMBOLS:
                connection.set_num_order(i+1)
            else:
                connection.set_num_order(None)
                
    def add_connection(self, connection):
        self.__connections.append(connection)
        
        is_internal = self.__attached_attribute_gui.get_configuration_class_gui() == connection.get_start_block().get_configuration_class_gui() and not connection.is_external()
        
        self.set_input_attribute(connection.get_start_block().get_configuration_attribute(), is_internal)
        self.update_connection_numbers()
        
    def remove_connection(self, connection):
        self.__attached_attribute_gui.get_configuration_attribute().remove_input_attribute(connection.get_start_block().get_configuration_attribute())
        self.__connections.remove(connection)
        self.update_connection_numbers()
        
    def set_input_attribute(self, connected_configuration_attribute, is_internal):
        self.__attached_attribute_gui.get_configuration_attribute().set_input_attribute(connected_configuration_attribute, is_internal)
        
    def delete(self):
        super().delete()
        
        delete_all(self.__connections)
        
        self.get_view().remove_configuration_input_gui(self)
            
    def save_state(self):
        return super().save_state() | {"symbol_calculation_type": self.get_symbol_calculation_type(), "connections": [connection.save_state() for connection in self.__connections]}
