from general_gui import GUIClass
from buttons_gui import GUIAddAttributeButton
from options import OptionsConfigurationClass
from configuration_attribute_gui import GUIConfigurationAttribute
from helper_functions_general import delete_all
from config import *

class GUIConfigurationClass(GUIClass):
    """
    Manages a GUI configuration class
    """
    def __init__(self, model, view, configuration_class, x, y, linked_group_number=None):
        self.__configuration_class = configuration_class
        super().__init__(model, view, self.__configuration_class.get_name(), x, y, CLASS_WIDTH, CLASS_HEIGHT, True, linked_group_number)
        self.__configuration_attributes_gui = []
        
        self.__setup_classes_gui = []
        self.__to_setup_buttons = {} # Key: View, Value: Create setup version button
        
        self.__add_button = GUIAddAttributeButton(model, view, x+ADD_ATTRIBUTE_OFFSET_POSITION[0], y+ATTRIBUTE_HEIGHT+ADD_ATTRIBUTE_OFFSET_POSITION[1], self)
        self.add_attached_block(self.__add_button)
        
        # Create GUI configuration attributes
        for configuration_attribute in configuration_class.get_configuration_attributes():
            self.create_attribute(configuration_attribute=configuration_attribute, update_linked=False)
            
    def open_options(self):
        return OptionsConfigurationClass(self.get_model(), self, self.get_model().get_configuration_views())
        
    def get_configuration_class(self):
        return self.__configuration_class
        
    def create_attribute(self, *, configuration_attribute=None, update_linked=True):
        """
        Create configuration attribute and any corresponding setup attributes
        If given an exisiting configuration attribute, will only create the corresponding GUI blocks
        """
        # Create new configuration attribute and corresponding setup attributes
        if configuration_attribute == None:
            configuration_attribute = self.__configuration_class.create_attribute("New Attribute")
            
        height_offset = CLASS_HEIGHT + len(self.__configuration_attributes_gui) * ATTRIBUTE_HEIGHT
        
        # Create GUI configuration attribute
        configuration_attribute_gui = GUIConfigurationAttribute(self.get_model(), self.get_view(), configuration_attribute, self, self.get_x(), self.get_y()+height_offset)
        
        self.__configuration_attributes_gui.append(configuration_attribute_gui)
        self.add_attached_block(configuration_attribute_gui)
        
        # Update text to get bold if there is a linked copy with bold text
        configuration_attribute_gui.update_text()
        
        self.__add_button.move_block(0, ATTRIBUTE_HEIGHT)
        
        # Create GUI setup attributes
        if not configuration_attribute.is_hidden():
            for setup_class_gui in self.__setup_classes_gui:
                newest_setup_attribute = setup_class_gui.get_setup_class().get_setup_attributes()[-1]
                setup_class_gui.create_setup_attribute_gui(newest_setup_attribute, configuration_attribute_gui)
                
        # Update any existing linked GUI configuration classes
        if update_linked:
            for linked_configuration_class_gui in self.get_model().get_linked_configuration_classes_gui(self):
                linked_configuration_class_gui.create_attribute(configuration_attribute=configuration_attribute, update_linked=False)
                
    def remove_attribute(self, configuration_attribute_gui_to_remove):
        index_first_move_up = self.__configuration_attributes_gui.index(configuration_attribute_gui_to_remove)
        self.__configuration_class.remove_attribute(configuration_attribute_gui_to_remove.get_configuration_attribute())
        self.__configuration_attributes_gui.remove(configuration_attribute_gui_to_remove)
        
        # Move up all attributes after the removed one
        for configuration_attribute_gui in self.__configuration_attributes_gui[index_first_move_up:]:
            configuration_attribute_gui.move_block(0, -ATTRIBUTE_HEIGHT)
            
        self.__add_button.move_block(0, -ATTRIBUTE_HEIGHT)
        
    def get_configuration_attributes_gui(self):
        return self.__configuration_attributes_gui
        
    def remove_configuration_attribute_gui(self, configuration_attribute_gui):
        self.__configuration_attributes_gui.remove(configuration_attribute_gui)
        
    def swap_attribute_places(self, configuration_attribute_gui_to_move, move_up):
        """
        Switches the location of two adjacent attributes
        """
        if move_up:
            steps_to_move_up = ATTRIBUTE_HEIGHT
        else:
            steps_to_move_up = -ATTRIBUTE_HEIGHT
            
        configuration_attributes_gui = self.__configuration_attributes_gui
        configuration_attributes = self.__configuration_class.get_configuration_attributes()
        
        move_from_index = configuration_attributes_gui.index(configuration_attribute_gui_to_move)
        move_to_index = move_from_index - steps_to_move_up
        
        # No attribute to switch location with
        if move_to_index >= len(configuration_attributes_gui) or move_to_index < 0:
            return
            
        # Swap GUI positions of blocks
        configuration_attributes_gui[move_from_index].move_block(0, -steps_to_move_up)
        configuration_attributes_gui[move_to_index].move_block(0, steps_to_move_up)
        
        # Swap position in lists
        configuration_attributes_gui[move_from_index], configuration_attributes_gui[move_to_index] = configuration_attributes_gui[move_to_index], configuration_attributes_gui[move_from_index]
        configuration_attributes[move_from_index], configuration_attributes[move_to_index] = configuration_attributes[move_to_index], configuration_attributes[move_from_index]
        
        # Update all setup attributes
        for setup_class_gui in self.__setup_classes_gui:
            setup_attributes = setup_class_gui.get_setup_class().get_setup_attributes()
            setup_attributes[move_from_index], setup_attributes[move_to_index] = setup_attributes[move_to_index], setup_attributes[move_from_index]
            
            setup_class_gui.update_setup_attribute_gui_order()
            
    def get_setup_classes_gui(self):
        return self.__setup_classes_gui
            
    def add_setup_class_gui(self, setup_class_gui):
        self.__setup_classes_gui.append(setup_class_gui)
        
    def remove_setup_class_gui(self, setup_class_gui):
        self.__setup_classes_gui.remove(setup_class_gui)
            
    def add_to_setup_button(self, view, to_setup_button):
        self.__to_setup_buttons[view] = to_setup_button
        
    def remove_to_setup_button(self, view):
        if view in self.__to_setup_buttons:
            self.__to_setup_buttons.pop(view)
            
    def get_name(self):
        return self.__configuration_class.get_name()
        
    def set_name(self, name):
        """
        Set new name for configuration class and update the text of GUI blocks accordingly
        """
        self.__configuration_class.set_name(name)
        self.set_text(name)
        
        # Update linked GUI configuration classes
        if self.is_linked():
            for linked_configuration_class_gui in self.get_model().get_linked_configuration_classes_gui(self):
                linked_configuration_class_gui.set_text(name)
                
        # Update GUI setup classes containing the name of the configuration class in their headers
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.update_text()
            
        # Update the text of the buttons that add the class to the setup views
        for add_to_setup_button in self.__to_setup_buttons.values():
            add_to_setup_button.set_text(name)
            
    def update_value_input_types(self, specific_attribute_index=None):
        """
        Update the value input type of setup attributes (entry for manual input or text that is updated when calculating values)
        """
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.update_value_input_types(specific_attribute_index=specific_attribute_index, update_linked=False)
            
    def copy(self, view_to_copy_to, *, x=GUI_BLOCK_START_COORDINATES[0][0], y=GUI_BLOCK_START_COORDINATES[0][1]):
        """
        Creates a copy of this GUI configuration class in the specified view
        """
        configuration_class_gui = GUIConfigurationClass(self.get_model(), view_to_copy_to, self.__configuration_class, x, y, self.get_linked_group_number())
        
        # Copy over stored GUI setup class versions
        for setup_class_gui in self.__setup_classes_gui:
            configuration_class_gui.add_setup_class_gui(setup_class_gui)
            
        # Copy over stored buttons to add the class to setup views
        for add_to_setup_button in self.__to_setup_buttons.values():
            configuration_class_gui.add_to_setup_button(view_to_copy_to, add_to_setup_button)
            
        return configuration_class_gui
        
    def delete(self):
        super().delete()
        
        # Remove button for creating setup version and delete all setup class version if there are no currently linked copies of this configuration class
        if self.get_linked_group_number() == None:
            self.get_model().remove_add_to_setup_buttons(list(self.__to_setup_buttons.values()))
            
            delete_all(self.__setup_classes_gui)
            
        self.get_view().remove_configuration_class_gui(self)
        
    def save_state(self):
        saved_states = super().save_state() | {"name": self.get_name(), "configuration_class_gui": str(self), "configuration_attributes_gui": []}
        
        for configuration_attribute_gui in self.__configuration_attributes_gui:
            saved_states["configuration_attributes_gui"].append(configuration_attribute_gui.save_state())
            
        return saved_states
