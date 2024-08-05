import tkinter as tk
import pickle
import os
from configuration_calculation import ConfigurationClass
from configuration_gui import GUIConfigurationClass, GUIConfigurationInput
from setup_gui import GUISetupClass, GUIConnectionTriangle
from buttons_gui import GUIAddChangeViewButton, GUISaveButton, GUIAddConfigurationClassButton, GUIAddToSetupButton, GUIAddInputButton, GUICalculateValuesButton, GUIAddConnectionButton, GUIChangeViewButton, GUIRunScriptButton
from connection_gui import GUIConnection, GUIConnectionWithBlocks
from options import OptionsView
from helper_functions import convert_actual_coordinate_to_grid, delete_all
from config import *

class View(tk.Frame):
    def __init__(self, model, name):
        super().__init__()
        self.__model = model
        self.__name = name
        self.__configuration_change_view_buttons = {} # View and corresponding button
        self.__setup_change_view_buttons = {} # View and corersponding button
        self.__held_connection = None
        self.__selected_items = set()
        
        self.__is_panning = False
        self.__is_zooming = False
        self.__panning_last_mouse_coordinate = (0, 0)
        self.__length_unit_difference = 0
        self.__grid_offset = (0, 0) # How much items are offset from the grid in the range [0, 1) due to panning/zooming
        
        self.__canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg=BACKGROUND_COLOR)
        self.__canvas_size = (CANVAS_WIDTH, CANVAS_HEIGHT)
        self.__add_change_configuration_view_button = GUIAddChangeViewButton(model, self, CHANGE_VIEW_CONFIGURATION_START_POSITION[0]+CHANGE_VIEW_WIDTH//2, CHANGE_VIEW_CONFIGURATION_START_POSITION[1], True)
        self.__add_change_setup_view_button = GUIAddChangeViewButton(model, self, CHANGE_VIEW_SETUP_START_POSITION[0]+CHANGE_VIEW_WIDTH//2, CHANGE_VIEW_SETUP_START_POSITION[1], False)
        self.__save_button = GUISaveButton(model, self, SAVE_POSITION[0], SAVE_POSITION[1])
        
        self.__canvas.bind(MOUSE_LEFT_PRESS, self.pan_start)
        self.__canvas.bind(MOUSE_LEFT_DRAG, self.pan_move)
        self.__canvas.bind(MOUSE_LEFT_RELEASE, self.pan_stop)
        self.__canvas.bind(MOUSE_MOTION, self.move_items)
        
        # Binds two variations to cover Linux, macOS, and Windows
        self.__canvas.bind(MOUSE_WHEEL_UP, self.zoom_in)
        self.__canvas.bind(MOUSE_WHEEL_DOWN, self.zoom_out)
        self.__canvas.bind(MOUSE_WHEEL, lambda event: self.zoom_in(event) if event.delta > 0 else self.zoom_out(event))
        
        self.__canvas.bind("<Configure>", self.on_resize)
        
        self.__canvas.pack(expand=True, fill="both")
        
    def pan_start(self, event):
        self.__is_panning = len(self.__canvas.gettags(self.__canvas.find_closest(event.x, event.y))) == 0
        
        print(self.__canvas.gettags(self.__canvas.find_closest(event.x, event.y)))
        
        self.__canvas.focus_set()
        
        if self.__is_panning:
            self.unselect_all_items()
            self.__panning_last_mouse_coordinate = (event.x, event.y)
            
    def pan_move(self, event):
        if self.__is_panning:
            """
            # Move all items
            self.__canvas.scan_dragto(event.x, event.y, gain=1)
            
            # Move back static items that should not have been moved
            for button in self.__change_view_buttons + [self.__save_button] + self.get_static_items():
                move_x = (self.__canvas.canvasx(0) - self.__panning_last_offset[0]) / LENGTH_UNIT
                move_y = (self.__canvas.canvasy(0) - self.__panning_last_offset[1]) / LENGTH_UNIT
                
                button.move_block(move_x, move_y)
                
            self.__panning_last_offset = (self.__canvas.canvasx(0), self.__canvas.canvasy(0))
            """
            
            move_x, move_y = convert_actual_coordinate_to_grid(self, event.x-self.__panning_last_mouse_coordinate[0], event.y-self.__panning_last_mouse_coordinate[1])
            
            self.update_grid_offset(move_x, move_y)
            
            for movable_item in self.get_movable_items():
                movable_item.move_block(move_x, move_y)
                
            self.__panning_last_mouse_coordinate = (event.x, event.y)
            
    def pan_stop(self, event):
        # Snap blocks to grid
        if self.__is_panning:
            """
            for movable_item in self.get_movable_items():
                movable_item.snap_to_grid()
                
                x = movable_item.get_x()
                y = movable_item.get_y()
                
                move_x = int(x + 0.5) - x
                move_y = int(y + 0.5) - y
                
                if x < 0:
                    move_x -= 1
                    
                if y < 0:
                    move_y -= 1
                
                movable_item.move_block(move_x, move_y)
            """
            self.__is_panning = False
    
    def zoom_in(self, event):
        if self.get_length_unit() < LENGTH_UNIT_ZOOM_LIMITS[1]:
            self.zoom(event, 1)
        
    def zoom_out(self, event):
        if self.get_length_unit() > LENGTH_UNIT_ZOOM_LIMITS[0]:
            self.zoom(event, -1)
        
    def zoom(self, event, length_unit_difference):
        self.__is_zooming = True
        
        last_length_unit = self.get_length_unit()
        self.__length_unit_difference += length_unit_difference
        
        scale_origin_x, scale_origin_y = convert_actual_coordinate_to_grid(self, event.x, event.y) # Remove?
        length_unit_change = last_length_unit / self.get_length_unit() - 1
        
        move_x = scale_origin_x * length_unit_change
        move_y = scale_origin_y * length_unit_change
        
        self.update_grid_offset(move_x, move_y)
        
        for movable_item in self.get_movable_items():
            movable_item.scale(last_length_unit) # Scales entire grid and all its components
            movable_item.move_block(move_x, move_y) # Moves all components on the grid to simulate zooming in at the coordinates of the mouse
            
        self.__is_zooming = False
        
    def on_resize(self, event):
        self.__canvas.config(width=event.width, height=event.height)
        
        actual_move_x = event.width - self.__canvas_size[0]
        actual_move_y = event.height - self.__canvas_size[1]
        move_x, move_y = convert_actual_coordinate_to_grid(self, actual_move_x, actual_move_y)
        
        self.__canvas_size = (event.width, event.height)
        
        for item_to_move_x in list(self.__configuration_change_view_buttons.values()) + list(self.__setup_change_view_buttons.values()) + [self.__add_change_configuration_view_button, self.__add_change_setup_view_button]:
            item_to_move_x.move_block(move_x, 0)
            
        self.__save_button.move_block(0, move_y)
        
        return move_x, move_y
        
    def open_options(self):
        return OptionsView(self.get_model(), self)
        
    def get_updated_font(self, *, label=None, has_line_break=False):
        new_font_size = int(FONT[1] * self.get_length_unit() / LENGTH_UNIT + 0.5)
        
        if has_line_break:
            new_font_size -= FONT_DECREASE_LINE_BREAK
        
        if new_font_size < 1:
            new_font_size = 1
        
        if label == None:
            return (FONT[0], new_font_size)
            
        current_font = self.__canvas.itemcget(label, "font").split()
        
        if len(current_font) == 2:
            updated_font = (current_font[0], new_font_size)
            
        elif len(current_font) == 3:
            updated_font = (current_font[0], new_font_size, current_font[2])
            
        else:
            print(f"Error: Found font {current_font}")
            
        return updated_font
        
    def get_model(self):
        return self.__model
        
    def get_name(self):
        return self.__name
        
    def set_name(self, name):
        self.__name = name
        self.__model.set_text_change_view_buttons(self, name) # Need to update the text of the change view buttons in all views
        
    def get_canvas(self):
        return self.__canvas
        
    def add_change_view_button(self, x, y, view_to_change_to, is_setup_view):
        if not is_setup_view:
            self.__configuration_change_view_buttons[view_to_change_to] = GUIChangeViewButton(self.__model, self, x, y, view_to_change_to.get_name(), view_to_change_to)
            self.__add_change_configuration_view_button.move_block(0, CHANGE_VIEW_HEIGHT)
            
        else:
            self.__setup_change_view_buttons[view_to_change_to] = GUIChangeViewButton(self.__model, self, x, y, view_to_change_to.get_name(), view_to_change_to)
            self.__add_change_setup_view_button.move_block(0, CHANGE_VIEW_HEIGHT)
            
    def remove_change_view_button(self, view_to_remove):
        if view_to_remove in self.__configuration_change_view_buttons:
            change_view_buttons = self.__configuration_change_view_buttons
            self.__add_change_configuration_view_button.move_block(0, -CHANGE_VIEW_HEIGHT)
            
        elif view_to_remove in self.__setup_change_view_buttons:
            change_view_buttons = self.__setup_change_view_buttons
            self.__add_change_setup_view_button.move_block(0, -CHANGE_VIEW_HEIGHT)
            
        found_deleted = False
        
        # Adjust the position of all affected buttons that change view
        for current_view, change_view_button in change_view_buttons.items():
            if current_view == view_to_remove:
                found_deleted = True
                    
            # Move up all buttons for changing view
            elif found_deleted:
                change_view_button.move_block(0, -CHANGE_VIEW_HEIGHT)
                
        # Remove the button to change view
        change_view_buttons[view_to_remove].delete()
        change_view_buttons.pop(view_to_remove)
        
    def set_text_change_view_button(self, view_with_changed_name, text):
        # Find and change the text of a specific change view button within this view
        if view_with_changed_name in self.__configuration_change_view_buttons:
            self.__configuration_change_view_buttons[view_with_changed_name].set_text(text)
            
        elif view_with_changed_name in self.__setup_change_view_buttons:
            self.__setup_change_view_buttons[view_with_changed_name].set_text(text)
            
    def move_change_view_button(self, view_to_move, up):
        to_move = CHANGE_VIEW_HEIGHT
        
        if up:
            to_move *= -1
        
        if view_to_move in self.__configuration_change_view_buttons:
            self.__configuration_change_view_buttons[view_to_move].move_block(0, to_move)
            
        elif view_to_move in self.__setup_change_view_buttons:
            self.__setup_change_view_buttons[view_to_move].move_block(0, to_move)
            
    def move_items(self, event):
        if self.__held_connection != None:
            self.__held_connection.create_new_lines((event.x, event.y))
            
    def get_held_connection(self):
        return self.__held_connection
        
    def set_held_connection(self, connection):
        self.__held_connection = connection
        
    def reset_held_connection(self, remove_connection=False):
        if remove_connection:
            self.__held_connection.delete()
            
        self.__held_connection = None
        
    def get_selected_items(self):
        return self.__selected_items
        
    def is_selected_item(self, selected_item):
        return selected_item in self.__selected_items
        
    def select_item(self, selected_item):
        if not (self.get_model().is_currently_pressing_key("Shift_L") or self.get_model().is_currently_pressing_key("Shift_R")):
            self.unselect_all_items()
            
        if selected_item not in self.__selected_items:
            selected_item.highlight(HIGHLIGHT_SELECTED_COLOR)
            self.__selected_items.add(selected_item)
            
    def unselect_item(self, unselected_item):
        if unselected_item in self.__selected_items:
            unselected_item.unhighlight()
            self.__selected_items.remove(unselected_item)
            
    def unselect_all_items(self):
        for selected_item in self.__selected_items:
            selected_item.unhighlight()
            
        self.__selected_items.clear()
        
    def is_zooming(self):
        return self.__is_zooming
        
    def is_panning(self):
        return self.__is_panning
        
    def get_length_unit(self):
        return LENGTH_UNIT + self.__length_unit_difference
        
    def update_grid_offset(self, move_x, move_y):
        grid_offset_x = (self.__grid_offset[0] + move_x) % 1
        grid_offset_y = (self.__grid_offset[1] + move_y) % 1
        
        self.__grid_offset = (grid_offset_x, grid_offset_y)
        
    def get_grid_offset(self):
        return self.__grid_offset
        
    def set_grid_offset(self, offset_x, offset_y):
        self.__grid_offset = (offset_x, offset_y)
        
    def delete(self):
        self.destroy()
        
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
        
    def create_configuration_class_gui_copy(self, configuration_class_gui_to_copy):
        configuration_class_gui = configuration_class_gui_to_copy.copy(self)
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
            with open(f"{BASE_PATH}/{file_path}", "rb") as file_pickle:
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
            with open(f"{BASE_PATH}/{file_path}", "rb") as file_pickle:
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
                    
                for saved_states_connection_with_blocks in saved_states_connections_with_blocks:
                    connection_with_blocks = self.create_connection_with_blocks()
                    
                    saved_states_start_block = saved_states_connection_with_blocks["start_block"]
                    saved_states_end_block = saved_states_connection_with_blocks["end_block"]
                    
                    connection_with_blocks.move_and_place_blocks(saved_states_start_block["x"], saved_states_start_block["y"], saved_states_end_block["x"], saved_states_end_block["y"])
            
        # except:
            # print("Creating new setup view")
            
    def delete(self):
        delete_all(self.__setup_classes_gui)
        delete_all(self.__connections_with_blocks)
        
        super().delete()
