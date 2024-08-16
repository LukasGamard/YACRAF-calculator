import os
import importlib.util
from general_gui import GUIModelingBlock
from script_interface import ScriptInterface
from options import OptionsSettings
from config import *

class ButtonPress(GUIModelingBlock):
    """
    Class managing a custom button
    """
    def __init__(self, model, view, text, x, y, width, height, fill_color, command, *, tags_rect=(TAG_BUTTON,), tags_text=(TAG_BUTTON_TEXT,)):
        super().__init__(model, view, text, x, y, width, height, fill_color, bind_left=MOUSE_PRESS, tags_rect=tags_rect, tags_text=tags_text)
        self.__command = command
        
    @staticmethod
    def add_attribute(model, view, configuration_class_gui, x, y):
        command = lambda: configuration_class_gui.create_attribute()
        return ButtonPress(model, view, "+", x, y, ADD_ATTRIBUTE_WIDTH, ADD_ATTRIBUTE_HEIGHT, ADD_ATTRIBUTE_COLOR, command, tags_rect=(), tags_text=())
        
    @staticmethod
    def add_view(model, view, x, y, is_configuration_view):
        if is_configuration_view:
            command = lambda: model.create_view(True, "New configuration")
        else:
            command = lambda: model.create_view(False, "New setup")
            
        return ButtonPress(model, view, "+", x, y, ADD_CHANGE_VIEW_WIDTH, ADD_CHANGE_VIEW_HEIGHT, ADD_CHANGE_VIEW_COLOR, command)
        
    @staticmethod
    def save(model, view):
        command = lambda: model.save()
        return ButtonPress(model, view, "Save", SAVE_POSITION[0], SAVE_POSITION[1], SAVE_WIDTH, SAVE_HEIGHT, SAVE_COLOR, command)
        
    @staticmethod
    def settings(model, view):
        command = lambda: OptionsSettings(model.get_root())
        return ButtonPress(model, view, "Settings", SETTINGS_POSITION[0], SETTINGS_POSITION[1], SETTINGS_WIDTH, SETTINGS_HEIGHT, SETTINGS_COLOR, command)
        
    @staticmethod
    def change_view(model, view, x, y, view_name, view_to_change_to):
        if view == view_to_change_to:
            color = CHANGE_VIEW_SELECTED_COLOR
            command = None
        else:
            color = CHANGE_VIEW_COLOR
            command = lambda: model.change_view(view_to_change_to)
        
        return ButtonPress(model, view, view_name, x, y, CHANGE_VIEW_WIDTH, CHANGE_VIEW_HEIGHT, color, command)
        
    @staticmethod
    def add_configuration_class(model, view):
        command = lambda: view.create_configuration_class_gui()
        return ButtonPress(model, view, "Add class", ADD_CLASS_POSITION[0], ADD_CLASS_POSITION[1], ADD_CLASS_WIDTH, ADD_CLASS_HEIGHT, ADD_CLASS_COLOR, command)
        
    @staticmethod
    def add_input(model, view):
        command = lambda: view.create_configuration_input_gui()
        return ButtonPress(model, view, "Add input", ADD_INPUT_POSITION[0], ADD_INPUT_POSITION[1], ADD_INPUT_WIDTH, ADD_INPUT_HEIGHT, ADD_INPUT_COLOR, command)
        
    @staticmethod
    def add_to_setup(model, view, configuration_class_gui, current_number_of_buttons):
        x = ADD_TO_SETUP_START_POSITION[0]
        y = ADD_TO_SETUP_START_POSITION[1] + current_number_of_buttons * ADD_TO_SETUP_HEIGHT
        command = lambda: view.create_setup_class_gui(configuration_class_gui=configuration_class_gui)
        
        to_setup_button = ButtonPress(model, view, configuration_class_gui.get_name(), x, y, ADD_TO_SETUP_WIDTH, ADD_TO_SETUP_HEIGHT, ADD_TO_SETUP_COLOR, command)
        configuration_class_gui.add_to_setup_button(view, to_setup_button)
        
        return to_setup_button
        
    @staticmethod
    def calculate_values(model, view):
        command = lambda: model.calculate_values()
        return ButtonPress(model, view, "Calculate", CALCULATE_VALUES_POSITION[0], CALCULATE_VALUES_POSITION[1], CALCULATE_VALUES_WIDTH, CALCULATE_VALUES_HEIGHT, CALCULATE_VALUES_COLOR, command)
        
    @staticmethod
    def create_connection(model, view):
        command = lambda: view.create_connection_with_blocks()
        return ButtonPress(model, view, "Connection", ADD_CONNECTION_POSITION[0], ADD_CONNECTION_POSITION[1], ADD_CONNECTION_WIDTH, ADD_CONNECTION_HEIGHT, ADD_CONNECTION_COLOR, command)
        
    @staticmethod
    def run_script(model, view, script_path, script_name, num_script_buttons):
        # Import the module of the script
        spec = importlib.util.spec_from_file_location(script_name, os.path.join(script_path, f"{script_name}.py"))
        script_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script_module)
        
        x = RUN_SCRIPT_START_POSITION[0] - num_script_buttons * RUN_SCRIPT_WIDTH
        y = RUN_SCRIPT_START_POSITION[1]
        script_interface = ScriptInterface(model)
        command = lambda: script_module.script_control(script_interface)
        return ButtonPress(model, view, script_name, x, y, RUN_SCRIPT_WIDTH, RUN_SCRIPT_HEIGHT, RUN_SCRIPT_COLOR, command)
        
    @staticmethod
    def clear_script(model, view):
        command = lambda: model.reset_script_changes()
        return ButtonPress(model, view, "Clear script", RUN_SCRIPT_START_POSITION[0], RUN_SCRIPT_START_POSITION[1], RUN_SCRIPT_WIDTH, RUN_SCRIPT_HEIGHT, RUN_SCRIPT_CLEAR_COLOR, command)
        
    def left_pressed(self, event):
        if self.__command != None:
            self.__command()
