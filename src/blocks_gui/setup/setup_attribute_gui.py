from general_gui import GUIModelingBlock
from helper_functions_general import convert_grid_coordinate_to_actual, get_actual_coordinates_after_zoom
from config import *

class GUISetupAttribute(GUIModelingBlock):
    """
    Manages a GUI setup attribute
    """
    def __init__(self, model, view, setup_attribute, setup_class_gui, configuration_attribute_gui, x, y):
        self.__setup_attribute = setup_attribute
        self.__setup_class_gui = setup_class_gui
        self.__configuration_attribute_gui = configuration_attribute_gui
        
        width = ATTRIBUTE_WIDTH * SETUP_WIDTH_MULTIPLIER
        height = ATTRIBUTE_HEIGHT
        text_width = ATTRIBUTE_WIDTH
        
        actual_label_value_x, actual_label_value_y = convert_grid_coordinate_to_actual(view, x+width*3/4, y+height/2)
        self.__label_value = view.get_canvas().create_text(actual_label_value_x, actual_label_value_y, text="-", font=FONT)
        
        super().__init__(model, view, configuration_attribute_gui.get_name(), x, y, width, height, ATTRIBUTE_COLOR, text_width=text_width, \
                                                                                                                    label_text_x=x+width/4, \
                                                                                                                    additional_pressable_items=[self.__label_value], \
                                                                                                                    bind_left=MOUSE_PRESS)
        
        # Manual entry field
        self.__entry_value = None
        self.__entry_value_window = None
        self.__entry_text = tk.StringVar()
        
        configuration_attribute_gui.add_setup_attribute_gui(self)
        self.update_text()
        
        # If setup_attribute does not have any value, clear and potentially set default value
        if setup_attribute.get_value() == None:
            self.update_value_input_type()
            
        # If setup_attribute already has a value (for example, if this is a linked copy), do not clear it and update the displayed value so that it shows
        else:
            self.update_value_input_type(False)
            self.update_displayed_value()
            
        # Update set value whenever the entry field is edited
        self.__entry_text.trace("w", lambda *args: self.add_entered_value_to_attribute())
        
    def left_pressed(self, event):
        super().left_pressed(event)
        self.set_input_attributes_highlight(True)
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        # Move entry field if it exists
        if self.__entry_value != None:
            actual_move_x, actual_move_y = convert_grid_coordinate_to_actual(self.get_view(), move_x, move_y)
            new_actual_x, new_actual_y = self.get_view().get_canvas().coords(self.__entry_value_window)
            new_actual_x += actual_move_x
            new_actual_y += actual_move_y
            
            self.get_view().get_canvas().coords(self.__entry_value_window, new_actual_x, new_actual_y)
            
    def scale(self, last_length_unit):
        super().scale(last_length_unit)
        
        # Scale entry field if it exists
        if self.__entry_value != None:
            actual_width, actual_height = self.get_entry_size()
            actual_x, actual_y = get_actual_coordinates_after_zoom(self.get_view(), \
                                                                   self.get_view().get_canvas().coords(self.__entry_value_window), \
                                                                   last_length_unit)
            
            self.__entry_value.config(font=self.get_view().get_updated_font())
            self.get_view().get_canvas().coords(self.__entry_value_window, (actual_x, actual_y))
            self.get_view().get_canvas().itemconfig(self.__entry_value_window, width=actual_width, height=actual_height)
            
    def open_options(self):
        pass
        
    def unhighlight(self):
        super().unhighlight()
        self.set_input_attributes_highlight(False)
        
    def set_input_attributes_highlight(self, highlight):
        """
        Sets the current highlight of all connected setup attributes that this one currently takes as input
        """
        for connected_setup_attribute_gui in self.__setup_class_gui.get_connected_setup_attributes_gui(self.__setup_attribute):
            if not self.get_view().is_selected_item(connected_setup_attribute_gui):
                # Set highlight
                if highlight:
                    connected_setup_attribute_gui.highlight(HIGHLIGHT_INPUT_COLOR)
                    
                # Remove highlight
                else:
                    connected_setup_attribute_gui.unhighlight()
                    
    def update_value_input_type(self, clear_value=True):
        """
        Update the input value type (manual entry field or calculated value) of this setup attribute based on whether there are connected input attributes
        """
        has_currently_connected_inputs = self.__setup_attribute.has_connected_setup_attributes()
        
        # No manual entry as it takes input from connected attributes
        if has_currently_connected_inputs and \
           self.__configuration_attribute_gui.get_configuration_attribute().get_symbol_calculation_type() != SYMBOL_CALCULATION_TYPE_QUALITATIVE:
            self.switch_to_value_label(clear_value)
        else:
            self.switch_to_value_entry(clear_value)
            
    def switch_to_value_label(self, clear_value=True):
        """
        Switches to no manual input
        """
        if self.__entry_value != None:
            self.get_view().get_canvas().delete(self.__entry_value_window)
            self.__entry_value_window = None
            self.__entry_value = None
            
            # Reset any manually entered value
            if clear_value:
                self.__setup_attribute.clear_value()
                self.set_displayed_value("-")
                
    def switch_to_value_entry(self, clear_value=True):
        """
        Switches to manual entry input field
        """
        if self.__entry_value == None:
            actual_width, actual_height = self.get_entry_size()
            actual_x, actual_y = convert_grid_coordinate_to_actual(self.get_view(), self.get_x()+self.get_width()/2, self.get_y())
            
            # Create Entry and Window to put Entry in to allow it be put inside the Canvas
            self.__entry_value = tk.Entry(self.get_view(), textvariable=self.__entry_text, font=FONT)
            self.__entry_value_window = self.get_canvas().create_window((actual_x, actual_y+OUTLINE_WIDTH), \
                                                                         window=self.__entry_value, \
                                                                         anchor="nw", \
                                                                         width=actual_width, \
                                                                         height=actual_height)
            
            # Reset any calculated value as the input now should be entered manually, where a default value is entered
            if clear_value:
                self.__setup_attribute.set_value("Value")
                self.update_displayed_value()
                
            # When starting to edit the entered value, unselect all blocks to avoid accidentally deleting them
            self.__entry_value.bind("<FocusIn>", lambda event: self.get_view().unselect_all_items())
            
    def get_entry_size(self):
        """
        Returns the pixel width and height that an entry field should be
        """
        width, height = convert_grid_coordinate_to_actual(self.get_view(), self.get_width()/2, self.get_height())
        width -= OUTLINE_WIDTH
        height -= OUTLINE_WIDTH * 2
        
        return width, height
        
    def get_setup_attribute(self):
        return self.__setup_attribute
        
    def get_setup_class_gui(self):
        return self.__setup_class_gui
        
    def add_entered_value_to_attribute(self):
        """
        Sets the value of the setup attribute to that entered in the entry
        """
        if self.__entry_value != None:
            self.__setup_attribute.set_value(self.__entry_text.get())
            
            for linked_setup_attribute_gui in self.get_model().get_linked_setup_attributes_gui(self):
            	linked_setup_attribute_gui.update_displayed_value()
            	
    def set_displayed_value(self, value, color=None):
        """
        Sets the value that is displayed either as the resulting calculated value or that in an entry field
        """
        if color == None:
            color = TEXT_COLOR
            
        if value == None:
            value = "ERROR"
            
        # Set value in Label
        if self.__entry_value == None:
            self.get_view().get_canvas().itemconfig(self.__label_value, text=str(value), fill=color)
            
        # Set value in Entry
        else:
            self.__entry_value.delete(0, "end")
            self.__entry_value.insert(0, str(value))
            
    def update_displayed_value(self):
        """
        Updates the currently shown value, where an override value is shown if it exists
        """
        if self.__setup_attribute.has_override_value():
            self.switch_to_value_label(False)
            self.set_displayed_value(self.__setup_attribute.get_override_value(), "red")
            
        else:
            self.set_displayed_value(self.__setup_attribute.get_value())
            
    def attempt_to_reset_override_value(self):
        """
        Remove the override value if it exists and update the displayed value accordingly
        """
        if self.__setup_attribute.has_override_value():
            self.__setup_attribute.reset_override_value()
            self.update_value_input_type(False)
            self.update_displayed_value()
            
            return True
            
        return False
        
    def get_name(self):
        return self.__configuration_attribute_gui.get_name()
        
    def update_text(self):
        text, is_bold = self.__configuration_attribute_gui.get_attribute_text()
        self.set_text(text, is_bold)
        
    def delete(self):
        super().delete()
        
        self.__configuration_attribute_gui.remove_setup_attribute_gui(self)
        self.__setup_class_gui.remove_setup_attribute_gui(self)
        
        if self.__entry_value != None:
            self.get_view().get_canvas().delete(self.__entry_value_window)
            
    def save_state(self):
        return super().save_state() | {"value": self.__setup_attribute.get_value()}
