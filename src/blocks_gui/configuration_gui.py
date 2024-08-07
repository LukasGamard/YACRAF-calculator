from general_gui import GUIModelingBlock, GUIClass, NumberIndicator
from buttons_gui import GUIAddAttributeButton
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
        
        self.__add_button = GUIAddAttributeButton(model, view, x+ADD_ATTRIBUTE_OFFSET_POSITION[0], y+ATTRIBUTE_HEIGHT+ADD_ATTRIBUTE_OFFSET_POSITION[1], self)
        self.add_attached_block(self.__add_button)
        
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
        
        for configuration_attribute_gui in self.__configuration_attributes_gui[index_first_move_up:]:
            configuration_attribute_gui.move_block(0, -ATTRIBUTE_HEIGHT)
            
        self.__add_button.move_block(0, -ATTRIBUTE_HEIGHT)
        
    def get_configuration_attributes_gui(self):
        return self.__configuration_attributes_gui
        
    def remove_configuration_attribute_gui(self, configuration_attribute_gui):
        self.__configuration_attributes_gui.remove(configuration_attribute_gui)
        
    def swap_attribute_places(self, configuration_attribute_gui_to_move, move_up):
        if move_up:
            steps_to_move_up = ATTRIBUTE_HEIGHT
        else:
            steps_to_move_up = -ATTRIBUTE_HEIGHT
            
        configuration_attributes_gui = self.__configuration_attributes_gui
        configuration_attributes = self.__configuration_class.get_configuration_attributes()
        
        move_from_index = configuration_attributes_gui.index(configuration_attribute_gui_to_move)
        move_to_index = move_from_index - steps_to_move_up
        
        if move_to_index >= len(configuration_attributes_gui) or move_to_index < 0:
            return
            
        # Swap GUI positions of blocks
        configuration_attributes_gui[move_from_index].move_block(0, -steps_to_move_up)
        configuration_attributes_gui[move_to_index].move_block(0, steps_to_move_up)
        
        # Swap position in lists
        configuration_attributes_gui[move_from_index], configuration_attributes_gui[move_to_index] = configuration_attributes_gui[move_to_index], configuration_attributes_gui[move_from_index]
        configuration_attributes[move_from_index], configuration_attributes[move_to_index] = configuration_attributes[move_to_index], configuration_attributes[move_from_index]
        
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
        Set new name for configuration class and update GUI blocks accordingly
        """
        
        self.__configuration_class.set_name(name)
        self.set_text(name)
        
        # Updated linked configuration classes
        if self.is_linked():
            for linked_configuration_class_gui in self.get_model().get_linked_configuration_classes_gui(self):
                linked_configuration_class_gui.set_text(name)
                
        # GUI setup classes contain the name of the configuration class in their headers
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.update_text()
            
        # Updated the text of the buttons that add the class to the setup views
        for add_to_setup_button in self.__to_setup_buttons.values():
            add_to_setup_button.set_text(name)
            
    def update_value_input_types(self, specific_attribute_index=None):
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.update_value_input_types(specific_attribute_index=specific_attribute_index, update_linked=False)
            
    def copy(self, view_to_copy_to):
        configuration_class_gui = GUIConfigurationClass(self.get_model(), view_to_copy_to, self.__configuration_class, GUI_BLOCK_START_COORDINATES[0][0], GUI_BLOCK_START_COORDINATES[0][1], self.get_linked_group_number())
        
        # Copy over stored GUI setup class versions
        for setup_class_gui in self.__setup_classes_gui:
            configuration_class_gui.add_setup_class_gui(setup_class_gui)
            
        # Copy over stored buttons to add the class to setup views
        for add_to_setup_button in self.__to_setup_buttons.values():
            configuration_class_gui.add_to_setup_button(view_to_copy_to, add_to_setup_button)
            
        return configuration_class_gui
        
    def delete(self):
        super().delete()
        
        if self.get_linked_group_number() == None:
            self.get_model().remove_add_to_setup_buttons(list(self.__to_setup_buttons.values()))
            
            delete_all(self.__setup_classes_gui)
            
        self.get_view().remove_configuration_class_gui(self)
        
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
        
    def delete(self):
        if self.is_deleted():
            return
            
        super().delete()
        
        delete_all(self.__connections)
        
        # Only the attribute is deleted, not the class itself
        if not self.__configuration_class_gui.is_deleted():
            delete_all(self.get_model().get_linked_configuration_attributes_gui(self))
            self.__configuration_class_gui.remove_attribute(self)
            delete_all(self.__setup_attributes_gui)
            
    def save_state(self):
        return {"configuration_attribute_gui": str(self), "name": self.get_name(), "symbol_value_type": self.__configuration_attribute.get_symbol_value_type(), "input_scalar": self.get_input_scalar(), "is_hidden": self.is_hidden()}
        
class GUIConfigurationInput(GUIModelingBlock):
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "?", x, y, INPUT_WIDTH, INPUT_HEIGHT, INPUT_COLOR, bind_left=MOUSE_DRAG, bind_right=MOUSE_PRESS, tags_rect=(TAG_INPUT,), tags_text=(TAG_INPUT_TEXT,))
        self.__attached_configuration_attribute_gui = None
        self.__connections = []
        self.__symbol_calculation_type = None
        self.__input_scalar_indicator = None
        self.__direction_out_from_block = None
        
    def left_pressed(self, event):
        # Move block if no connection was held and added
        if not self.attach_held_connection():
            super().left_pressed(event)
            
    def left_dragged(self, event):
        super().left_dragged(event)
        self.attempt_to_detach_from_attribute()
        
    def left_released(self, event):
        if super().left_released(event, False):
            self.attempt_to_attach_to_attribute()
            self.get_view().update_shown_order()
            
    def right_pressed(self, event):
        self.attach_held_connection()
        
    def open_options(self):
        return OptionsCalculationInput(self.get_model().get_root(), self)
        
    def attach_held_connection(self):
        held_connection = self.get_view().get_held_connection()
        
        if held_connection != None:
            direction = "LEFT"
            
            if self.__attached_configuration_attribute_gui != None and self.__attached_configuration_attribute_gui.get_x() < self.get_x():
                direction = "RIGHT"
                
            held_connection.set_end_location(self, direction)
            
            self.get_view().reset_held_connection()
            
            return True
            
        return False
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        # If panning or zooming, only the corresponding attribute should move the lines
        if not self.get_view().is_panning() and not self.get_view().is_zooming():
            for connection in self.__connections:
                connection.move_lines(move_x, move_y)
                
        if self.__input_scalar_indicator != None:
            self.__input_scalar_indicator.move(move_x, move_y)
            
    def scale(self, last_length_unit):
        super().scale(last_length_unit)
        
        if self.__input_scalar_indicator != None:
            self.__input_scalar_indicator.scale(last_length_unit)
            
    def attempt_to_attach_to_attribute(self):
        for configuration_class_gui in self.get_view().get_configuration_classes_gui():
            for configuration_attribute_gui in configuration_class_gui.get_configuration_attributes_gui():
                is_adjacent, direction_out_of_block = configuration_attribute_gui.is_adjacent([(self.get_x(), self.get_y())])
                
                if is_adjacent and not configuration_attribute_gui.has_configuration_input():
                    self.__attached_configuration_attribute_gui = configuration_attribute_gui
                    self.__attached_configuration_attribute_gui.set_configuration_input(self)
                    
                    self.__direction_out_from_block = direction_out_of_block
                    
                    # Update calculation type of input block but not the attribute
                    if self.__attached_configuration_attribute_gui.get_configuration_class_gui().is_linked() and self.__attached_configuration_attribute_gui.get_configuration_attribute().get_symbol_calculation_type() != None:
                        self.update_symbol_calculation_type()
                        
                    # Updated calculation type of attribute according to the input block
                    else:
                        self.__attached_configuration_attribute_gui.set_calculation_type(self.__symbol_calculation_type)
                        
                    for connection in self.__connections:
                        self.attempt_to_add_connection_to_attribute(connection)
                        
                        # If changing side of input block, the connections should also change side
                        connection.update_direction(self, self.__direction_out_from_block)
                        
                    self.__attached_configuration_attribute_gui.update_value_input_type_setup_attributes_gui()
                    self.update_input_scalar()
                    break
                    
    def attempt_to_detach_from_attribute(self):
        # Remove from being an input to an attribute
        if self.__attached_configuration_attribute_gui != None:
            self.__attached_configuration_attribute_gui.remove_configuration_input()
            
            # Find if this was the only linked copy that had an input block
            linked_configuration_attributes_with_input = 0
            
            for linked_configuration_attribute_gui in self.get_model().get_linked_configuration_attributes_gui(self.__attached_configuration_attribute_gui):
                if linked_configuration_attribute_gui.has_configuration_input():
                    linked_configuration_attributes_with_input += 1
                    
            # Reset calculation type and input scalar if this was the only linked copy that had an input block
            if linked_configuration_attributes_with_input == 0:
                self.__attached_configuration_attribute_gui.reset_calculation_type()
                self.__attached_configuration_attribute_gui.reset_input_scalar()
                
            for connection in self.__connections:
                input_configuration_attribute = connection.get_start_block().get_configuration_attribute()
                self.__attached_configuration_attribute_gui.get_configuration_attribute().remove_input_configuration_attribute(input_configuration_attribute)
                
            self.__attached_configuration_attribute_gui.update_value_input_type_setup_attributes_gui()
            self.__attached_configuration_attribute_gui = None
            self.__direction_out_from_block = None
            
            self.update_input_scalar(move_back_input=False)
            
    def is_attached(self):
        return self.__attached_configuration_attribute_gui != None
        
    def get_attached_configuration_attribute_gui(self):
        return self.__attached_configuration_attribute_gui
        
    def get_symbol_calculation_type(self):
        return self.__symbol_calculation_type
        
    def set_symbol_calculation_type(self, symbol_calculation_type):
        self.__symbol_calculation_type = symbol_calculation_type
        self.set_text(symbol_calculation_type)
        
        if self.__attached_configuration_attribute_gui != None:
            self.__attached_configuration_attribute_gui.set_calculation_type(symbol_calculation_type)
        
        self.update_connection_numbers()
        
    def update_symbol_calculation_type(self):
        if self.__attached_configuration_attribute_gui != None:
            self.__symbol_calculation_type = self.__attached_configuration_attribute_gui.get_configuration_attribute().get_symbol_calculation_type()
            text = self.__symbol_calculation_type
            
            if text == None:
                text = "?"
                
            self.set_text(text)
            
    def set_input_scalar(self, input_scalar):
        if self.__attached_configuration_attribute_gui != None:
            self.__attached_configuration_attribute_gui.set_input_scalar(input_scalar)
            
            self.update_input_scalar()
            
    def update_input_scalar(self, *, move_back_input=True, update_linked=True):
        if self.__input_scalar_indicator != None:
            self.__input_scalar_indicator.remove()
            
            if move_back_input:
                self.move_block(self.__input_scalar_indicator.get_x()-self.get_x()-0.5, 0)
                
        if self.__attached_configuration_attribute_gui != None:
            input_scalar = self.__attached_configuration_attribute_gui.get_input_scalar()
            
            if input_scalar != DEFAULT_INPUT_SCALAR:
                if input_scalar != None:
                    indicator_x = self.get_x() + 0.5
                    self.move_block(self.get_move_x_due_to_indicator(), 0)
                    
                    self.__input_scalar_indicator = NumberIndicator(self.get_view(), indicator_x, self.get_y()+0.5, INPUT_SCALAR_CIRCLE_RADIUS, INPUT_SCALAR_CIRCLE_COLOR, INPUT_SCALAR_CIRCLE_OUTLINE, input_scalar)
                    
            if update_linked:
                for linked_configuration_attribute_gui in self.get_model().get_linked_configuration_attributes_gui(self.__attached_configuration_attribute_gui):
                    if linked_configuration_attribute_gui.has_configuration_input():
                        linked_configuration_attribute_gui.get_configuration_input().update_input_scalar(update_linked=False)
                        
    def get_move_x_due_to_indicator(self):
        if self.__direction_out_from_block == "LEFT":
            return -1
            
        elif self.__direction_out_from_block == "RIGHT":
            return 1
            
    def attempt_to_add_connection_to_attribute(self, connection):
        if self.__attached_configuration_attribute_gui != None:
            is_internal = self.__attached_configuration_attribute_gui.get_configuration_class_gui() == connection.get_start_block().get_configuration_class_gui() and not connection.is_external()
            connected_configuration_attribute = connection.get_start_block().get_configuration_attribute()
            
            self.__attached_configuration_attribute_gui.get_configuration_attribute().add_input_configuration_attribute(connected_configuration_attribute, is_internal)
            
    def add_connection(self, connection):
        self.__connections.append(connection)
        self.attempt_to_add_connection_to_attribute(connection)
        
        self.update_connection_numbers()
            
    def remove_connection(self, connection):
        self.__connections.remove(connection)
        
        if self.__attached_configuration_attribute_gui != None:
            configuration_attribute_to_disconnect = connection.get_start_block().get_configuration_attribute()
            self.__attached_configuration_attribute_gui.get_configuration_attribute().remove_input_configuration_attribute(configuration_attribute_to_disconnect)
            
        self.update_connection_numbers()
            
    def update_connection_numbers(self):
        for i, connection in enumerate(self.__connections):
            if self.__symbol_calculation_type in ENUMERATED_INPUT_CALCULATION_TYPE_SYMBOLS:
                connection.set_num_order(i+1)
            else:
                connection.set_num_order(None)
                
    def delete(self):
        super().delete()
        self.attempt_to_detach_from_attribute()
                
        delete_all(self.__connections)
        self.get_view().remove_configuration_input_gui(self)
        
        if self.__input_scalar_indicator != None:
            self.__input_scalar_indicator.remove()
            
    def save_state(self):
        saved_states = super().save_state() | {"symbol_calculation_type": self.get_symbol_calculation_type(), "connections": [connection.save_state() for connection in self.__connections]}
        
        if self.__attached_configuration_attribute_gui != None and self.__attached_configuration_attribute_gui.get_input_scalar() != DEFAULT_INPUT_SCALAR:
            saved_states["x"] -= self.get_move_x_due_to_indicator()
            
        return saved_states
