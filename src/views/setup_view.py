import os
import pickle
from view import View
from setup_class_gui import GUISetupClass
from buttons_gui import GUIAddToSetupButton, GUICalculateValuesButton, GUIAddConnectionButton, GUIRunScriptButton
from connection_gui import GUIConnection
from connection_with_blocks_gui import GUIConnectionWithBlocks
from helper_functions_general import delete_all
from config import *

class SetupView(View):
    def __init__(self, model, name):
        super().__init__(model, name)
        self.__setup_classes_gui = []
        self.__connections_with_blocks = []
        self.__to_setup_buttons = []
        # self.__moving_connection_corner = None
        
        self.__add_connection_button = GUIAddConnectionButton(model, self, ADD_CONNECTION_POSITION[0], ADD_CONNECTION_POSITION[1])
        self.__calculate_value_button = GUICalculateValuesButton(model, self, CALCULATE_VALUES_POSITION[0], CALCULATE_VALUES_POSITION[1])
        
        self.__run_script_buttons = []
        
        for file_name_full in os.listdir(f"{BASE_PATH}/{SCRIPTS_PATH}"):
            if file_name_full.strip()[-3:] == ".py":
                file_name = file_name_full.strip().replace(".py", "")
                
                if file_name != "SCRIPT_TEMPLATE":
                    if len(self.__run_script_buttons) == 0:
                        self.__run_script_buttons.append(GUIRunScriptButton(model, self, "Clear script", RUN_SCRIPT_START_POSITION[0], RUN_SCRIPT_START_POSITION[1], True))
                        
                    run_script_x = RUN_SCRIPT_START_POSITION[0] - len(self.__run_script_buttons) * RUN_SCRIPT_WIDTH
                    self.__run_script_buttons.append(GUIRunScriptButton(model, self, file_name, run_script_x, RUN_SCRIPT_START_POSITION[1]))
                    
    def on_resize(self, event):
        move_x, move_y = super().on_resize(event)
        
        self.__add_connection_button.move_block(move_x/2, 0)
        self.__calculate_value_button.move_block(move_x/2, 0)
        
        for run_script_button in self.__run_script_buttons:
            run_script_button.move_block(move_x, move_y)
            
    def create_connection_with_blocks(self):
        connection_with_blocks = GUIConnectionWithBlocks(self.get_model(), self)
        self.__connections_with_blocks.append(connection_with_blocks)
        
        return connection_with_blocks
        
    def create_setup_class_gui(self, configuration_class_gui, *, x=GUI_BLOCK_START_COORDINATES[0][0], y=GUI_BLOCK_START_COORDINATES[0][1], setup_class=None, linked_group_number=None):
        if setup_class == None:
            setup_class = configuration_class_gui.get_configuration_class().create_setup_version()
            
        setup_class_gui = GUISetupClass(self.get_model(), self, setup_class, configuration_class_gui, x, y, linked_group_number)
        self.__setup_classes_gui.append(setup_class_gui)
        
        return setup_class_gui
        
    def get_setup_classes_gui(self):
        return self.__setup_classes_gui
        
    def remove_setup_class_gui(self, setup_class_gui):
        self.__setup_classes_gui.remove(setup_class_gui)
        
    """
    def set_moving_connection_corner(self, moving_connection_corner):
        self.__moving_connection_corner = moving_connection_corner
        
    def reset_moving_connection_corner(self):
        self.__moving_connection_corner = None
    """
    
    def get_movable_items(self):
        movable_items = self.__setup_classes_gui.copy()
        
        for connection in self.__connections_with_blocks:
            movable_items += connection.get_movable_items()
        
        # if self.__moving_connection_corner != None:
            # movable_items.append(self.__moving_connection_corner)
            
        return movable_items
    
    def reset_calculated_values(self):
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.reset_calculated_values()
            
    def calculate_values(self):
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.calculate_values()
            
    def reset_override_values(self):
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.reset_override_value()
            
    def get_matching_setup_classes_gui(self, *, class_configuration_name=None, class_instance_name=None):
        matching_setup_classes_gui = []
        
        for setup_class_gui in self.__setup_classes_gui:
            if class_configuration_name == None or setup_class_gui.get_configuration_name() == class_configuration_name:
                if class_instance_name == None or setup_class_gui.get_name() == class_instance_name:
                    matching_setup_classes_gui.append(setup_class_gui)
                    
        return matching_setup_classes_gui
        
    def remove_connection_with_blocks(self, connection):
        self.__connections_with_blocks.remove(connection)
        
    def create_add_to_setup_button(self, current_number_of_buttons, configuration_class_gui):
        self.__to_setup_buttons.append(GUIAddToSetupButton(self.get_model(), self, ADD_TO_SETUP_START_POSITION[0], ADD_TO_SETUP_START_POSITION[1]+current_number_of_buttons*ADD_TO_SETUP_HEIGHT, configuration_class_gui))
        
    def remove_add_to_setup_button(self, to_setup_button):
        to_setup_button.delete()
        
        button_index = self.__to_setup_buttons.index(to_setup_button)
        self.__to_setup_buttons.remove(to_setup_button)
        
        for to_setup_button_to_move in self.__to_setup_buttons[button_index:]:
            to_setup_button_to_move.move_block(0, -ADD_TO_SETUP_HEIGHT)
            
    def get_static_items(self):
        return [self.__add_connection_button, self.__calculate_value_button] + self.__to_setup_buttons
        
    def save(self):
        saved_states_setup_classes_gui = [class_gui.save_state() for class_gui in self.__setup_classes_gui]
        saved_states_connections_with_blocks = [connection.save_state() for connection in self.__connections_with_blocks]
        
        file_path = os.path.join(SETUP_SAVES_PATH, f"{self.get_name()}.pickle")
        
        with open(file_path, "wb") as file_pickle:
            pickle.dump((self.get_grid_offset(), saved_states_setup_classes_gui, saved_states_connections_with_blocks), file_pickle)
            
        return file_path
        
    def restore_save(self, file_path, mapping_configuration_class_gui, linked_groups_per_number):
        if not SHOULD_RESTORE_SAVE:
            return
            
        # try:
        if True:
            with open(os.path.join(BASE_PATH, file_path), "rb") as file_pickle:
                grid_offset, saved_states_setup_classes_gui, saved_states_connections_with_blocks = pickle.load(file_pickle)
                self.set_grid_offset(grid_offset[0], grid_offset[1])
                
                # Restore setup classes
                for saved_states_setup_class_gui in saved_states_setup_classes_gui:
                    linked_group_number = saved_states_setup_class_gui["linked_group_number"]
                    
                    configuration_class_gui = mapping_configuration_class_gui[saved_states_setup_class_gui["configuration_class_gui"]]
                    
                    # Should bind to already existing setup class
                    if linked_group_number != None and linked_group_number in linked_groups_per_number:
                        setup_class_gui = self.get_model().create_linked_setup_class_gui(linked_groups_per_number[linked_group_number][0], configuration_class_gui, self, x=saved_states_setup_class_gui["x"], y=saved_states_setup_class_gui["y"])
                        
                    else:
                        setup_class_gui = self.create_setup_class_gui(configuration_class_gui, x=saved_states_setup_class_gui["x"], y=saved_states_setup_class_gui["y"], linked_group_number=linked_group_number)
                        
                        if linked_group_number != None:
                            linked_groups_per_number[linked_group_number] = [setup_class_gui]
                        
                    # Set setup class data
                    setup_class_gui.set_name(saved_states_setup_class_gui["name"])
                    
                    for saved_states_setup_attribute_gui, setup_attribute_gui in zip(saved_states_setup_class_gui["setup_attributes_gui"], setup_class_gui.get_setup_attributes_gui()):
                        setup_attribute_gui.set_displayed_value(saved_states_setup_attribute_gui["value"])
                        
                # Restore setup connections
                for saved_states_connection_with_blocks in saved_states_connections_with_blocks:
                    connection_with_blocks = self.create_connection_with_blocks()
                    
                    saved_states_start_block = saved_states_connection_with_blocks["start_block"]
                    saved_states_end_block = saved_states_connection_with_blocks["end_block"]
                    
                    connection_with_blocks.set_input_scalars(saved_states_connection_with_blocks["input_scalars"])
                    input_scalars_indicator_coordinate = saved_states_connection_with_blocks["input_scalars_indicator_coordinate"]
                    
                    connection_with_blocks.move_and_place_blocks(saved_states_start_block["x"], saved_states_start_block["y"], saved_states_end_block["x"], saved_states_end_block["y"], input_scalars_indicator_coordinate)
                    
        # except:
            # print("Creating new setup view")
            
    def delete(self):
        delete_all(self.__setup_classes_gui)
        delete_all(self.__connections_with_blocks)
        
        super().delete()
