import os
import pickle
from view import View
from configuration_class_calculation import ConfigurationClass
from configuration_class_gui import GUIConfigurationClass
from configuration_input_gui import GUIConfigurationInput
from buttons_gui import GUIAddConfigurationClassButton, GUIAddInputButton
from connection_gui import GUIConnection
from helper_functions_general import delete_all
from config import *

class ConfigurationView(View):
    def __init__(self, model, name):
        super().__init__(model, name)
        self.__configuration_classes_gui = []
        self.__configuration_inputs_gui = []
        
        self.__add_configuration_class_button = GUIAddConfigurationClassButton(model, self, ADD_CLASS_POSITION[0], ADD_CLASS_POSITION[0])
        self.__add_input_button = GUIAddInputButton(model, self, ADD_INPUT_POSITION[0], ADD_INPUT_POSITION[1])
        
    def create_configuration_class_gui(self, *, x=GUI_BLOCK_START_COORDINATES[0][0], y=GUI_BLOCK_START_COORDINATES[0][1], configuration_class=None, linked_group_number=None):
        if configuration_class == None:
            configuration_class = ConfigurationClass("New class")
            
        configuration_class_gui = GUIConfigurationClass(self.get_model(), self, configuration_class, x, y, linked_group_number)
        
        self.get_model().create_add_to_setup_buttons(self.get_model().get_num_configuration_classes(), configuration_class_gui) # Add buttons to add the setup class version
        self.__configuration_classes_gui.append(configuration_class_gui)
        
        return configuration_class_gui
        
    def create_configuration_class_gui_copy(self, configuration_class_gui_to_copy, *, x=GUI_BLOCK_START_COORDINATES[0][0], y=GUI_BLOCK_START_COORDINATES[0][1]):
        configuration_class_gui = configuration_class_gui_to_copy.copy(self, x=x, y=y)
        self.__configuration_classes_gui.append(configuration_class_gui)
        
        return configuration_class_gui
        
    def remove_configuration_class_gui(self, configuration_class_gui):
        self.__configuration_classes_gui.remove(configuration_class_gui)
        
    def get_configuration_classes_gui(self):
        return self.__configuration_classes_gui
        
    def create_configuration_input_gui(self, *, x=GUI_BLOCK_START_COORDINATES[0][0], y=GUI_BLOCK_START_COORDINATES[0][1]):
        configuration_input_gui = GUIConfigurationInput(self.get_model(), self, x, y)
        self.__configuration_inputs_gui.append(configuration_input_gui)
        
        return configuration_input_gui
        
    def remove_configuration_input_gui(self, configuration_input_gui):
        self.__configuration_inputs_gui.remove(configuration_input_gui)
        
    def get_configuration_inputs_gui(self):
        return self.__configuration_inputs_gui
        
    def get_static_items(self):
        return [self.__add_configuration_class_button, self.__add_input_button]
        
    def get_movable_items(self):
        movable_items = self.__configuration_classes_gui.copy()
        
        for configuration_input_gui in self.__configuration_inputs_gui:
            if not configuration_input_gui.is_attached():
                movable_items.append(configuration_input_gui)
        
        return movable_items
        
    def save(self):
        saved_states_configuration_classes_gui = [class_gui.save_state() for class_gui in self.__configuration_classes_gui]
        saved_states_configuration_inputs_gui = [input_gui.save_state() for input_gui in self.__configuration_inputs_gui]
        
        file_path = os.path.join(CONFIGURATION_SAVES_PATH, f"{self.get_name()}.pickle")
        
        with open(file_path, "wb") as file_pickle:
            pickle.dump((self.get_grid_offset(), saved_states_configuration_classes_gui, saved_states_configuration_inputs_gui), file_pickle)
            
        return file_path
        
    def restore_save(self, file_path, linked_groups_per_number):
        if not SHOULD_RESTORE_SAVE:
            return {}
            
        # try:
        if True:
            with open(os.path.join(BASE_PATH, file_path), "rb") as file_pickle:
                grid_offset, saved_states_configuration_classes_gui, saved_states_configuration_inputs_gui = pickle.load(file_pickle)
                self.set_grid_offset(grid_offset[0], grid_offset[1])
                
                mapping_configuration_class_gui = {}
                mapping_configuration_attribute_gui = {}
                
                # Restore configuration classes
                for saved_states_configuration_class_gui in saved_states_configuration_classes_gui:
                    linked_group_number = saved_states_configuration_class_gui["linked_group_number"]
                    
                    # Should bind to already existing configuration class
                    if linked_group_number != None and linked_group_number in linked_groups_per_number:
                        configuration_class_gui = self.get_model().create_linked_configuration_class_gui(linked_groups_per_number[linked_group_number][0], self, x=saved_states_configuration_class_gui["x"], y=saved_states_configuration_class_gui["y"])
                        
                    else:
                        configuration_class_gui = self.create_configuration_class_gui(x=saved_states_configuration_class_gui["x"], y=saved_states_configuration_class_gui["y"], linked_group_number=linked_group_number)
                        
                        if linked_group_number != None:
                            linked_groups_per_number[linked_group_number] = [configuration_class_gui]
                            
                        # Set configuration class data
                        configuration_class_gui.set_name(saved_states_configuration_class_gui["name"])
                        
                        mapping_configuration_class_gui[saved_states_configuration_class_gui["configuration_class_gui"]] = configuration_class_gui
                            
                        # Restore configuration attributes
                        for saved_states_configuration_attribute_gui in saved_states_configuration_class_gui["configuration_attributes_gui"]:
                            # Create configuration attribute
                            configuration_class_gui.create_attribute()
                            configuration_attribute_gui = configuration_class_gui.get_configuration_attributes_gui()[-1]
                            
                            # Set configuration attribute data
                            configuration_attribute_gui.set_name(saved_states_configuration_attribute_gui["name"])
                            configuration_attribute_gui.set_value_type(saved_states_configuration_attribute_gui["symbol_value_type"])
                            configuration_attribute_gui.set_input_scalar(saved_states_configuration_attribute_gui["input_scalar"])
                            configuration_attribute_gui.set_hidden(saved_states_configuration_attribute_gui["is_hidden"])
                            
                            mapping_configuration_attribute_gui[saved_states_configuration_attribute_gui["configuration_attribute_gui"]] = configuration_attribute_gui
                            
                # Restore configuration inputs
                for saved_states_configuration_input_gui in saved_states_configuration_inputs_gui:
                    # Create configuration input
                    configuration_input_gui = self.create_configuration_input_gui(x=saved_states_configuration_input_gui["x"], y=saved_states_configuration_input_gui["y"])
                    
                    # Set configuration input data
                    configuration_input_gui.attempt_to_attach_to_attribute()
                    symbol_calculation_type = saved_states_configuration_input_gui["symbol_calculation_type"]
                    
                    if symbol_calculation_type != "":
                        configuration_input_gui.set_symbol_calculation_type(symbol_calculation_type)
                        
                    # Restore configuration connections
                    for saved_states_connection in saved_states_configuration_input_gui["connections"]:
                        connection = GUIConnection(self.get_model(), \
                                self, \
                                mapping_configuration_attribute_gui[saved_states_connection["start_block"]], \
                                saved_states_connection["start_direction"], \
                                end_block=configuration_input_gui, \
                                end_direction=saved_states_connection["end_direction"], \
                                corner_coordinates=saved_states_connection["corner_coordinates"], \
                                is_external=saved_states_connection["is_external"])
                                
            return mapping_configuration_class_gui
                                
        # except:
            # print("Creating new configuration view")
            
        return {}
        
    def delete(self):
        delete_all(self.__configuration_classes_gui)
        delete_all(self.__configuration_inputs_gui)
        
        super().delete()
