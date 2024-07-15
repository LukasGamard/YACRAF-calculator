import tkinter as tk
import pickle
from blocks_configuration import GUIConfigurationClass, GUIConfigurationInput
from blocks_setup import GUISetupClass, GUIConnectionTriangle
from blocks_buttons import GUISaveButton, GUIAddConfigurationClassButton, GUIAddToSetupButton, GUIAddInputButton, GUICalculateValuesButton, GUIAddConnectionButton
from connection_gui import GUIConnection, GUIConnectionWithBlocks
from config import *

class View(tk.Frame):
    def __init__(self, model, name):
        super().__init__()
        self.__name = name
        self.__canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg=BACKGROUND_COLOR)
        self.__background_rect = self.__canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill=BACKGROUND_COLOR, outline="")
        self.__save_button = GUISaveButton(model, self, 0, CANVAS_HEIGHT//LENGTH_UNIT-SAVE_HEIGHT)
        
        self.__canvas.pack()
        
        self.__held_connection = None
        self.__canvas.bind(MOUSE_MOTION, self.move_items)
        
        self.__is_panning = False
        self.__panning_last_coordinate = (0, 0)
        self.__canvas.tag_bind(self.__background_rect, MOUSE_LEFT, self.left_clicked)
        
    def left_clicked(self, event):
        self.__is_panning = not self.__is_panning
        self.__panning_last_coordinate = (event.x // LENGTH_UNIT, event.y // LENGTH_UNIT)
        
    def get_name(self):
        return self.__name
        
    def get_canvas(self):
        return self.__canvas
        
    def move_items(self, event):
        for block in self.get_movable_items():
            if self.__is_panning:
                if isinstance(block, (GUIConfigurationClass, GUISetupClass)) or (isinstance(block, (GUIConfigurationInput, GUIConnectionTriangle)) and not block.is_attached()):
                    move_x = event.x // LENGTH_UNIT - self.__panning_last_coordinate[0]
                    move_y = event.y // LENGTH_UNIT - self.__panning_last_coordinate[1]
                    
                    block.move_block(move_x, move_y)
                
            else:
                block.move_if_picked_up(event.x, event.y)
                
        if self.__held_connection != None:
            self.__held_connection.create_lines((event.x, event.y))
            
        self.__panning_last_coordinate = (event.x // LENGTH_UNIT, event.y // LENGTH_UNIT)
            
    def get_held_connection(self):
        return self.__held_connection
        
    def set_held_connection(self, connection):
        self.__held_connection = connection
        
    def reset_held_connection(self, remove_line=False):
        if remove_line:
            self.__held_connection.remove_lines()
            
        self.__held_connection = None
        
class ConfigurationView(View):
    def __init__(self, model, name):
        super().__init__(model, name)
        self.__model = model
        self.__configuration_classes_gui = []
        self.__configuration_inputs_gui = []
        
        GUIAddConfigurationClassButton(model, self, 0, 0)
        GUIAddInputButton(model, self, 0, CHANGE_VIEW_HEIGHT)
        
    def create_configuration_class_gui(self, *, x=GUI_BLOCK_START_COORDINATES[0][0], y=GUI_BLOCK_START_COORDINATES[0][1]):
        configuration_class_gui = GUIConfigurationClass(self.__model, self, x, y)
        
        self.__model.create_add_to_setup_buttons(len(self.__configuration_classes_gui), configuration_class_gui) # Add buttons to add the setup class version
        self.__configuration_classes_gui.append(configuration_class_gui)
        
        return configuration_class_gui
        
    def remove_configuration_class_gui(self, configuration_class_gui):
        self.__configuration_classes_gui.remove(configuration_class_gui)
        
    def get_configuration_classes_gui(self):
        return self.__configuration_classes_gui
        
    def create_configuration_input_gui(self, *, x=GUI_BLOCK_START_COORDINATES[0][0], y=GUI_BLOCK_START_COORDINATES[0][1]):
        configuration_input_gui = GUIConfigurationInput(self.__model, self, x, y)
        self.__configuration_inputs_gui.append(configuration_input_gui)
        
        return configuration_input_gui
        
    def get_movable_items(self):
        return self.__configuration_classes_gui + self.__configuration_inputs_gui
        
    def save(self, file_number):
        saved_states_configuration_classes_gui = [class_gui.save_state() for class_gui in self.__configuration_classes_gui]
        saved_states_configuration_inputs_gui = [input_gui.save_state() for input_gui in self.__configuration_inputs_gui]
        
        with open(f"saved_views/saved_view_{file_number}.pickle", "wb") as file_pickle:
            pickle.dump((saved_states_configuration_classes_gui, saved_states_configuration_inputs_gui), file_pickle)
            
    def restore_save(self, file_number):
        if not SHOULD_RESTORE_SAVE:
            return {}
            
        # try:
        if True:
            with open(f"saved_views/saved_view_{file_number}.pickle", "rb") as file_pickle:
                saved_states_configuration_classes_gui, saved_states_configuration_inputs_gui = pickle.load(file_pickle)
                mapping_configuration_class_gui = {}
                mapping_configuration_attribute_gui = {}
                
                # Restore configuration classes
                for saved_states_configuration_class_gui in saved_states_configuration_classes_gui:
                    # Create configuration class
                    configuration_class_gui = self.create_configuration_class_gui(x=saved_states_configuration_class_gui["x"], y=saved_states_configuration_class_gui["y"])
                    
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
                        configuration_attribute_gui.set_hidden(saved_states_configuration_attribute_gui["is_hidden"])
                        
                        mapping_configuration_attribute_gui[saved_states_configuration_attribute_gui["configuration_attribute_gui"]] = configuration_attribute_gui
                        
                # Restore configuration inputs
                for saved_states_configuration_input_gui in saved_states_configuration_inputs_gui:
                    # Create configuration input
                    configuration_input_gui = self.create_configuration_input_gui(x=saved_states_configuration_input_gui["x"], y=saved_states_configuration_input_gui["y"])
                    
                    # Set configuration input data
                    configuration_input_gui.put_down_block()
                    symbol_calculation_type = saved_states_configuration_input_gui["symbol_calculation_type"]
                    if symbol_calculation_type != "":
                        configuration_input_gui.set_symbol_calculation_type(symbol_calculation_type)
                    
                    # Restore configuration connections
                    for saved_states_connection in saved_states_configuration_input_gui["connections"]:
                        connection = GUIConnection(self.__model, \
                                self, mapping_configuration_attribute_gui[saved_states_connection["start_block"]], \
                                saved_states_connection["start_direction"], \
                                end_block=configuration_input_gui, \
                                end_direction=saved_states_connection["end_direction"], \
                                is_external=saved_states_connection["is_external"])
                                
            return mapping_configuration_class_gui
                                
        # except:
            # print("Creating new configuration view")
            
        return {}
        
class SetupView(View):
    def __init__(self, model, name):
        super().__init__(model, name)
        self.__model = model
        self.__setup_classes_gui = []
        self.__connections_with_blocks = []
        self.__to_setup_buttons = []
        # self.__moving_connection_corner = None
        
        mid_x = int(CANVAS_WIDTH / (2 * LENGTH_UNIT))
        
        GUIAddConnectionButton(model, self, mid_x - ADD_CONNECTION_WIDTH, 0)
        GUICalculateValuesButton(model, self, mid_x, 0)
        
    def create_connection_with_blocks(self):
        connection_with_blocks = GUIConnectionWithBlocks(self.__model, self)
        self.__connections_with_blocks.append(connection_with_blocks)
        
        return connection_with_blocks
        
    def create_setup_class_gui(self, configuration_class_gui, *, x=GUI_BLOCK_START_COORDINATES[0][0], y=GUI_BLOCK_START_COORDINATES[0][1], setup_class=None, linked_group_number=None):
        if setup_class == None:
            setup_class = configuration_class_gui.get_configuration_class().create_setup_version()
            
        setup_class_gui = GUISetupClass(self.__model, self, setup_class, configuration_class_gui, x, y, linked_group_number)
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
        self.__model.reset_calculated_values_all_setup_views()
        
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.calculate_values()
                    
    def delete_connection_with_blocks(self, connection):
        self.__connections_with_blocks.remove(connection)
        
    def create_add_to_setup_button(self, current_number_of_buttons, configuration_class_gui):
        self.__to_setup_buttons.append(GUIAddToSetupButton(self.__model, self, 0, current_number_of_buttons*ADD_TO_SETUP_HEIGHT, configuration_class_gui))
        
    def remove_add_to_setup_button(self, to_setup_button):
        to_setup_button.delete()
        
        button_index = self.__to_setup_buttons.index(to_setup_button)
        self.__to_setup_buttons.remove(to_setup_button)
        
        for to_setup_button_to_move in self.__to_setup_buttons[button_index:]:
            to_setup_button_to_move.move_block(0, -1)
        
    def save(self, file_number):
        saved_states_setup_classes_gui = [class_gui.save_state() for class_gui in self.__setup_classes_gui]
        saved_states_connections_with_blocks = [connection.save_state() for connection in self.__connections_with_blocks]
        
        with open(f"saved_views/saved_view_{file_number}.pickle", "wb") as file_pickle:
            pickle.dump((saved_states_setup_classes_gui, saved_states_connections_with_blocks), file_pickle)
            
    def restore_save(self, file_number, mapping_configuration_class_gui, linked_groups_per_number):
        if not SHOULD_RESTORE_SAVE:
            return {}
            
        # try:
        if True:
            with open(f"saved_views/saved_view_{file_number}.pickle", "rb") as file_pickle:
                saved_states_setup_classes_gui, saved_states_connections_with_blocks = pickle.load(file_pickle)
                
                # Restore setup classes
                for saved_states_setup_class_gui in saved_states_setup_classes_gui:
                    linked_group_number = saved_states_setup_class_gui["linked_group_number"]
                    
                    configuration_class_gui = mapping_configuration_class_gui[saved_states_setup_class_gui["configuration_class_gui"]]
                    setup_class = None
                    
                    # Should bind to already existing setup class
                    if linked_group_number != None and linked_group_number in linked_groups_per_number:
                        setup_class = linked_groups_per_number[linked_group_number][0].get_setup_class()
                    
                    setup_class_gui = self.create_setup_class_gui(configuration_class_gui, x=saved_states_setup_class_gui["x"], y=saved_states_setup_class_gui["y"], setup_class=setup_class, linked_group_number=linked_group_number)
                    
                    # Add to group if there was one
                    if linked_group_number != None:
                        if linked_group_number not in linked_groups_per_number:
                            linked_groups_per_number[linked_group_number] = [setup_class_gui]
                        else:
                            linked_groups_per_number[linked_group_number].append(setup_class_gui)
                            
                    # Set setup class data
                    setup_class_gui.set_name(saved_states_setup_class_gui["name"])
                    
                    for saved_states_setup_attribute_gui, setup_attribute_gui in zip(saved_states_setup_class_gui["setup_attributes_gui"], setup_class_gui.get_setup_attributes_gui()):
                        setup_attribute_gui.set_displayed_value(saved_states_setup_attribute_gui["value"])
                    
                for saved_states_connection_with_blocks in saved_states_connections_with_blocks:
                    connection_with_blocks = self.create_connection_with_blocks()
                    
                    saved_states_start_block = saved_states_connection_with_blocks["start_block"]
                    saved_states_end_block = saved_states_connection_with_blocks["end_block"]
                    
                    connection_with_blocks.move_and_place_blocks(saved_states_start_block["x"], saved_states_start_block["y"], saved_states_end_block["x"], saved_states_end_block["y"])
                
            return linked_groups_per_number
            
        # except:
            # print("Creating new setup view")
            
        return {}
