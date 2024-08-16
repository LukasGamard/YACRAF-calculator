import os
import importlib.util
from general_gui import GUIModelingBlock
from script_interface import ScriptInterface
from options import OptionsSettings
from config import *

class GUIBlockButton(GUIModelingBlock):
    """
    Class managing custom buttons
    """
    def __init__(self, model, view, text, x, y, width, height, fill_color, tags_rect=(TAG_BUTTON,), tags_text=(TAG_BUTTON_TEXT,)):
        super().__init__(model, view, text, x, y, width, height, fill_color, bind_left=MOUSE_PRESS, tags_rect=tags_rect, tags_text=tags_text)
        
    def left_pressed(self, event):
        pass
        
class GUIAddAttributeButton(GUIBlockButton):
    """
    Button for adding an attribute to a class in a configuration view
    """
    def __init__(self, model, view, x, y, configuration_class_gui):
        super().__init__(model, view, "+", x, y, ADD_ATTRIBUTE_WIDTH, ADD_ATTRIBUTE_HEIGHT, ADD_ATTRIBUTE_COLOR, tags_rect=(), tags_text=())
        self.__configuration_class_gui = configuration_class_gui
        
    def left_pressed(self, event):
        self.__configuration_class_gui.create_attribute()
        
class GUIAddChangeViewButton(GUIBlockButton):
    """
    Button for adding another view
    """
    def __init__(self, model, view, x, y, is_configuration_view):
        super().__init__(model, view, "+", x, y, ADD_CHANGE_VIEW_WIDTH, ADD_CHANGE_VIEW_HEIGHT, ADD_CHANGE_VIEW_COLOR)
        self.__is_configuration_view = is_configuration_view
        
    def left_pressed(self, event):
        if self.__is_configuration_view:
            self.get_model().create_view(True, "New configuration")
        else:
            self.get_model().create_view(False, "New setup")
        
class GUISaveButton(GUIBlockButton):
    """
    Button for saving all views
    """
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "Save", x, y, SAVE_WIDTH, SAVE_HEIGHT, SAVE_COLOR)
        
    def left_pressed(self, event):
        self.get_model().save()
        
class GUISettingsButton(GUIBlockButton):
    """
    Button for opening up general settings
    """
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "Settings", x, y, SETTINGS_WIDTH, SETTINGS_HEIGHT, SETTINGS_COLOR)
        
    def left_pressed(self, event):
        OptionsSettings(self.get_model().get_root())
        
class GUIChangeViewButton(GUIBlockButton):
    """
    Button for changing to a specific view
    """
    def __init__(self, model, view, x, y, view_name, view_to_change_to):
        if view == view_to_change_to:
            color = CHANGE_VIEW_SELECTED_COLOR
        else:
            color = CHANGE_VIEW_COLOR
            
        super().__init__(model, view, view_name, x, y, CHANGE_VIEW_WIDTH, CHANGE_VIEW_HEIGHT, color)
        self.__view_to_change_to = view_to_change_to
        
    def left_pressed(self, event):
        self.get_model().change_view(self.__view_to_change_to)
        
class GUIAddConfigurationClassButton(GUIBlockButton):
    """
    Button for creating a new configuration class
    """
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "Add class", x, y, ADD_CLASS_WIDTH, ADD_CLASS_HEIGHT, ADD_CLASS_COLOR)
        
    def left_pressed(self, event):
        self.get_view().create_configuration_class_gui()
        
class GUIAddInputButton(GUIBlockButton):
    """
    Button for creating an input block
    """
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "Add input", x, y, ADD_INPUT_WIDTH, ADD_INPUT_HEIGHT, ADD_INPUT_COLOR)
        
    def left_pressed(self, event):
        self.get_view().create_configuration_input_gui()
        
class GUIAddToSetupButton(GUIBlockButton):
    """
    Button for creating a setup version of a configuration class
    """
    def __init__(self, model, view, x, y, configuration_class_gui):
        super().__init__(model, view, configuration_class_gui.get_name(), x, y, ADD_TO_SETUP_WIDTH, ADD_TO_SETUP_HEIGHT, ADD_TO_SETUP_COLOR)
        self.__configuration_class_gui = configuration_class_gui
        
        configuration_class_gui.add_to_setup_button(view, self)
        
    def left_pressed(self, event):
        self.get_view().create_setup_class_gui(configuration_class_gui=self.__configuration_class_gui)
         
class GUICalculateValuesButton(GUIBlockButton):
    """
    Button for calculating the values of setup attributes
    """
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "Calculate", x, y, CALCULATE_VALUES_WIDTH, CALCULATE_VALUES_HEIGHT, CALCULATE_VALUES_COLOR)
        
    def left_pressed(self, event):
        self.get_model().calculate_values()
        
class GUIAddConnectionButton(GUIBlockButton):
    """
    Button for creating a directional connection with triangle blocks
    """
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "Connection", x, y, ADD_CONNECTION_WIDTH, ADD_CONNECTION_HEIGHT, ADD_CONNECTION_COLOR)
        
    def left_pressed(self, event):
        self.get_view().create_connection_with_blocks()
        
class GUIRunScriptButton(GUIBlockButton):
    """
    Button for running a script
    """
    def __init__(self, model, view, script_path, script_name, x, y, is_clear_button=False):
        # The button runs a script
        if not is_clear_button:
            color = RUN_SCRIPT_COLOR
        # The button clears changes made by scripts
        else:
            color = RUN_SCRIPT_CLEAR_COLOR
            
        super().__init__(model, view, script_name, x, y, RUN_SCRIPT_WIDTH, RUN_SCRIPT_HEIGHT, color)
        self.__script_interface = ScriptInterface(model)
        self.__is_clear_button = is_clear_button
        
        # The button runs a script
        if not is_clear_button:
            # Import the module of the script
            spec = importlib.util.spec_from_file_location(script_name, os.path.join(script_path, f"{script_name}.py"))
            self.__script_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.__script_module)
            
    def left_pressed(self, event):
        if self.__is_clear_button:
            self.get_model().reset_script_changes()
            
        else:
            self.__script_module.script_control(self.__script_interface)
