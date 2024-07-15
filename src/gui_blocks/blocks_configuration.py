from blocks_general import GUIModelingBlock
from blocks_buttons import GUIAddAttributeButton
from calculations_configuration import ConfigurationClass
from options import OptionsConfigurationClass, OptionsConfigurationAttribute, OptionsCalculationInput
from config import *

class GUIConfigurationClass(GUIModelingBlock):
    def __init__(self, model, view, x, y):
        self.__configuration_class = ConfigurationClass("New class")
        super().__init__(model, view, self.__configuration_class.get_name(), x, y, CLASS_WIDTH, CLASS_HEIGHT, CLASS_COLOR, bind_left=True, bind_right=True)
        self.__configuration_attributes_gui = []
        
        self.__setup_classes_gui = []
        self.__to_setup_buttons = []
        
        self.__add_button = GUIAddAttributeButton(model, view, x+CLASS_WIDTH//2, y+CLASS_HEIGHT, self)
        self.add_attached_block(self.__add_button)
        
    def right_clicked(self, event):
        OptionsConfigurationClass(self.get_model().get_root(), self)
        
    def get_configuration_class(self):
        return self.__configuration_class
        
    def create_attribute(self):
        height_offset = CLASS_HEIGHT + len(self.__configuration_attributes_gui) * ATTRIBUTE_HEIGHT
        
        configuration_attribute_gui = GUIConfigurationAttribute(self.get_model(), self.get_view(), self, self.get_x(), self.get_y()+height_offset)
        
        self.__configuration_attributes_gui.append(configuration_attribute_gui)
        self.add_attached_block(configuration_attribute_gui)
        
        self.__add_button.move_block(0, ATTRIBUTE_HEIGHT)
        
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.create_setup_attribute(configuration_attribute_gui)
            
    def get_configuration_attributes_gui(self):
        return self.__configuration_attributes_gui
        
    def add_setup_class_gui(self, setup_class_gui):
        self.__setup_classes_gui.append(setup_class_gui)
        
    def remove_configuration_attribute_gui(self, configuration_attribute_gui_to_remove):
        configuration_attribute_index = self.__configuration_attributes_gui.index(configuration_attribute_gui_to_remove)
        self.__configuration_attributes_gui.remove(configuration_attribute_gui_to_remove)
        
        for configuration_attribute_gui in self.__configuration_attributes_gui[configuration_attribute_index:]:
            configuration_attribute_gui.move_block(0, -1)
            
        self.__add_button.move_block(0, -1)
        
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.remove_setup_attribute_gui_by_index(configuration_attribute_index)
        
    def remove_setup_class_gui(self, setup_class_gui):
        self.__setup_classes_gui.remove(setup_class_gui)
        
    def add_to_setup_button(self, to_setup_button):
        self.__to_setup_buttons.append(to_setup_button)
        
    def get_name(self):
        return self.__configuration_class.get_name()
        
    def set_name(self, name):
        self.__configuration_class.set_name(name)
        self.set_text(name)
        
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.update_text()
            
        for add_to_setup_button in self.__to_setup_buttons:
            add_to_setup_button.set_text(name)
            
    def delete(self):
        super().delete()
        
        self.get_model().remove_add_to_setup_buttons(self.__to_setup_buttons)
        
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.delete()
            
        for configuration_attribute_gui in self.__configuration_attributes_gui:
            configuration_attribute_gui.delete()
            
        self.get_view().remove_configuration_class_gui(self)
        
    def save_state(self):
        saved_states = super().save_state() | {"name": self.get_name(), "configuration_class_gui": str(self), "configuration_attributes_gui": []}
        
        for configuration_attribute_gui in self.__configuration_attributes_gui:
            saved_states["configuration_attributes_gui"].append(configuration_attribute_gui.save_state())
            
        return saved_states
        
class GUIConfigurationAttribute(GUIModelingBlock):
    def __init__(self, model, view, configuration_class_gui, x, y):
        self.__configuration_attribute = configuration_class_gui.get_configuration_class().create_attribute("New Attribute")
        self.__configuration_class_gui = configuration_class_gui
        
        super().__init__(model, view, self.__configuration_attribute.get_name(), x, y, ATTRIBUTE_WIDTH, ATTRIBUTE_HEIGHT, ATTRIBUTE_COLOR, bind_left=True, bind_right=True)
        self.__configuration_input = None
        self.__connections = []
        self.__is_hidden = False
        
        self.__setup_attributes_gui = []
        
    def left_clicked(self, event):
        held_connection = self.get_view().get_held_connection()
        
        if held_connection == None:
            held_connection = self.get_model().create_connection(self, self.get_direction(event.x, event.y))
            held_connection.create_lines((event.x, event.y))
            
        else:
            self.get_view().reset_held_connection(True)
            
    def right_clicked(self, event):
        OptionsConfigurationAttribute(self.get_model().get_root(), self)
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        for connection in self.__connections:
            connection.create_lines()
            
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
        return self.__is_hidden
        
    def set_hidden(self, is_hidden):
        self.__is_hidden = is_hidden
        
    def add_setup_attribute_gui(self, setup_attribute_gui):
        self.__setup_attributes_gui.append(setup_attribute_gui)
        
    def remove_setup_attribute_gui(self, setup_attribute_gui):
        self.__setup_attributes_gui.remove(setup_attribute_gui)
        
    def get_name(self):
        return self.__configuration_attribute.get_name()
        
    def set_name(self, name):
        self.__configuration_attribute.set_name(name)
        self.update_text()
        
    def set_value_type(self, symbol_value_type):
        self.__configuration_attribute.set_symbol_value_type(symbol_value_type)
        self.update_text()
            
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
        
        for connection in self.__connections:
            connection.delete()
            
        self.__configuration_class_gui.remove_configuration_attribute_gui(self)
        
    def save_state(self):
        return {"configuration_attribute_gui": str(self), "name": self.get_name(), "symbol_value_type": self.__configuration_attribute.get_symbol_value_type(), "is_hidden": self.is_hidden()}

class GUIConfigurationInput(GUIModelingBlock):
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "?", x, y, INPUT_WIDTH, INPUT_HEIGHT, INPUT_COLOR, bind_left=True, bind_right=True)
        self.__attached_attribute_gui = None
        self.__connections = []
        self.__symbol_calculation_type = ""
        
    def left_clicked(self, event):
        held_connection = self.get_view().get_held_connection()
        direction = "LEFT"
        
        # If clicking to add a connection
        if held_connection != None:
            if self.__attached_attribute_gui != None and self.__attached_attribute_gui.get_x() < self.get_x():
                direction = "RIGHT"
                
            held_connection.set_end_location(self, direction)
            self.get_view().reset_held_connection()
            
        # If clicking to move the block
        else:
            super().left_clicked(event)
            
            # Put down block
            if not self.is_picked_up():
                self.put_down_block()
                            
            # Pick up block
            elif self.__attached_attribute_gui != None:
                self.__attached_attribute_gui.remove_configuration_input()
                self.__attached_attribute_gui = None
                
    def right_clicked(self, event):
        OptionsCalculationInput(self.get_model().get_root(), self)
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        for connection in self.__connections:
            connection.create_lines()
            
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
        
        for i in range(len(self.__connections)-1, -1, -1):
            self.__connections[i].delete()
            
    def save_state(self):
        return super().save_state() | {"symbol_calculation_type": self.get_symbol_calculation_type(), "connections": [connection.save_state() for connection in self.__connections]}
