from general_gui import GUIModelingBlock
from configuration_attribute_calculation import ConfigurationAttribute
from helper_functions_general import delete_all
from options import OptionsConfigurationAttribute
from config import *

class GUIConfigurationAttribute(GUIModelingBlock):
    def __init__(self, model, view, configuration_attribute, configuration_class_gui, x, y):
        self.__configuration_attribute = configuration_attribute
        self.__configuration_class_gui = configuration_class_gui
        
        super().__init__(model, view, self.__configuration_attribute.get_name(), x, y, ATTRIBUTE_WIDTH, ATTRIBUTE_HEIGHT, ATTRIBUTE_COLOR, bind_left=MOUSE_PRESS, bind_right=MOUSE_PRESS)
        self.__configuration_input = None
        self.__connections = []
        
        self.__setup_attributes_gui = []
        
    def right_pressed(self, event):
        held_connection = self.get_view().get_held_connection()
        
        if held_connection == None:
            held_connection = self.get_model().create_connection(self, self.get_direction(event.x, event.y), (event.x, event.y))
            
    def open_options(self):
        return OptionsConfigurationAttribute(self.get_model().get_root(), self.__configuration_class_gui, self)
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        for connection in self.__connections:
            connection.move_lines(move_x, move_y)
            
    def scale(self, last_length_unit):
        super().scale(last_length_unit)
        
        for connection in self.__connections:
            connection.scale(last_length_unit)
        
    def get_configuration_attribute(self):
        return self.__configuration_attribute
        
    def get_configuration_class_gui(self):
        return self.__configuration_class_gui
        
    """
    def update_configuration_input_symbol(self):
        if self.__configuration_input != None:
            self.__configuration_input.update_symbol_calculation_type()
    """
            
    def set_configuration_input(self, configuration_input):
        self.__configuration_input = configuration_input
        self.add_attached_block(configuration_input)
        
        self.update_text()
        
    def remove_configuration_input(self):
        self.remove_attached_block(self.__configuration_input)
        self.__configuration_input = None
        
        self.update_text()
        
    def has_configuration_input(self):
        return self.__configuration_input != None
        
    def get_configuration_input(self):
        return self.__configuration_input
    
    def add_connection(self, connection):
        self.__connections.append(connection)
    
    def remove_connection(self, connection):
        self.__connections.remove(connection)
        
    def is_hidden(self):
        return self.__configuration_attribute.is_hidden()
        
    def set_hidden(self, is_hidden):
        self.__configuration_attribute.set_hidden(is_hidden)
        
        if is_hidden:
            for setup_attribute_gui in self.__setup_attributes_gui:
                setup_attribute_gui.get_setup_attribute().clear_value()
                
            delete_all(self.__setup_attributes_gui)
            
        else:
            for setup_class_gui in self.__configuration_class_gui.get_setup_classes_gui():
                # Find the correct setup attribute without a GUI version
                for i, setup_attribute in enumerate(setup_class_gui.get_setup_class().get_setup_attributes()):
                    if setup_attribute.has_configuration_attribute(self.__configuration_attribute):
                        setup_class_gui.create_setup_attribute_gui(setup_attribute, self)
                        break
                        
                setup_class_gui.update_setup_attribute_gui_order()
                
    def add_setup_attribute_gui(self, setup_attribute_gui):
        self.__setup_attributes_gui.append(setup_attribute_gui)
        
    def remove_setup_attribute_gui(self, setup_attribute_gui):
        self.__setup_attributes_gui.remove(setup_attribute_gui)
        
    def get_name(self):
        return self.__configuration_attribute.get_name()
        
    def set_name(self, name):
        self.__configuration_attribute.set_name(name)
        self.update_text()
        
        for linked_configuration_attribute_gui in self.get_model().get_linked_configuration_attributes_gui(self):
            linked_configuration_attribute_gui.update_text()
            
    def set_value_type(self, symbol_value_type):
        self.__configuration_attribute.set_symbol_value_type(symbol_value_type)
        self.update_text()
        
        for linked_configuration_attribute_gui in self.get_model().get_linked_configuration_attributes_gui(self):
            linked_configuration_attribute_gui.update_text()
            
    def set_calculation_type(self, symbol_calculation_type, update_linked=True):
        if update_linked:
            self.__configuration_attribute.set_symbol_calculation_type(symbol_calculation_type)
            
        if self.__configuration_input != None:
            self.__configuration_input.update_symbol_calculation_type()
        
        if update_linked:
            for linked_attribute_gui in self.get_model().get_linked_configuration_attributes_gui(self):
                linked_attribute_gui.set_calculation_type(symbol_calculation_type, False)
                
        for setup_attribute_gui in self.__setup_attributes_gui:
            setup_attribute_gui.update_value_input_type()
            
        self.update_text()
        
    def reset_calculation_type(self):
        self.set_calculation_type(None)
        
    def get_input_scalar(self):
        return self.__configuration_attribute.get_input_scalar()
        
    def set_input_scalar(self, input_scalar):
        self.__configuration_attribute.set_input_scalar(input_scalar)
        
    def reset_input_scalar(self):
        self.__configuration_attribute.reset_input_scalar()
        
    def get_attribute_text(self):
        text = ""
        is_bold = self.__configuration_attribute.get_symbol_calculation_type() != None
        
        if self.__configuration_attribute.get_symbol_value_type() != None:
            text = f"{self.__configuration_attribute.get_name()} ({self.__configuration_attribute.get_symbol_value_type()})"
        else:
            text = f"{self.__configuration_attribute.get_name()}"
            
        return text, is_bold
        
    def update_text(self):
        text, is_bold = self.get_attribute_text()
        
        self.set_text(text, is_bold)
        
        for setup_attribute_gui in self.__setup_attributes_gui:
            setup_attribute_gui.update_text()
            
    def update_value_input_type_setup_attributes_gui(self):
        attribute_index = self.__configuration_class_gui.get_configuration_attributes_gui().index(self)
        self.__configuration_class_gui.update_value_input_types(specific_attribute_index=attribute_index)
        
    def delete(self, manual_delete=False):
        if self.is_deleted():
            return
            
        super().delete()
        
        delete_all(self.__connections)
        
        # Only the attribute is deleted, not the class itself
        if manual_delete:
            delete_all(self.get_model().get_linked_configuration_attributes_gui(self))
            self.__configuration_class_gui.remove_attribute(self)
            delete_all(self.__setup_attributes_gui)
            
    def save_state(self):
        return {"configuration_attribute_gui": str(self), "name": self.get_name(), "symbol_value_type": self.__configuration_attribute.get_symbol_value_type(), "input_scalar": self.get_input_scalar(), "is_hidden": self.is_hidden()}
