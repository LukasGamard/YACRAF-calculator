import tkinter as tk
import numpy as np
from helper_functions import convert_grid_coordinate_to_actual, get_actual_coordinates_after_zoom, get_triangle_coordinates, get_max_directions_movement
from general_gui import GUIBlock, GUIModelingBlock, GUIClass, NumberIndicator
from options import OptionsSetupClass
from config import *

class GUISetupClass(GUIClass):
    def __init__(self, model, view, setup_class, configuration_class_gui, x, y, linked_group_number=None):
        self.__configuration_class_gui = configuration_class_gui
        self.__setup_class = setup_class
        
        super().__init__(model, view, self.__setup_class.get_instance_name(), x, y, CLASS_WIDTH*SETUP_WIDTH_MULTIPLIER, CLASS_HEIGHT, False, linked_group_number)
        self.__setup_attributes_gui = []
        self.__connections = []
        
        self.__script_marker_indicators = []
        
        configuration_class_gui.add_setup_class_gui(self)
        
        for setup_attribute, configuration_attribute_gui in zip(self.__setup_class.get_setup_attributes(), self.__configuration_class_gui.get_configuration_attributes_gui()):
            if not configuration_attribute_gui.is_hidden():
                self.create_setup_attribute_gui(setup_attribute, configuration_attribute_gui)
                
        self.update_text()
        
    def right_pressed(self, event):
        self.open_options()
        
    def open_options(self):
        return OptionsSetupClass(self.get_model(), self, self.__configuration_class_gui, self.get_model().get_setup_views())
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        for script_marker_indicator in self.__script_marker_indicators:
            script_marker_indicator.move(move_x, move_y)
            
    def scale(self, last_length_unit):
        super().scale(last_length_unit)
        
        for connection in self.__connections:
            # Only scale connection if this class is connected to the start block of the connection to avoid moving it twice
            if self.has_attached_block(connection.get_start_block()):
                connection.scale(last_length_unit)
                
        for script_marker_indicator in self.__script_marker_indicators:
            script_marker_indicator.scale(last_length_unit)
            
    def is_adjacent(self, coordinates):
        # Above class
        for coordinate in coordinates:
            coordinate_to_check = np.array(coordinate)
            
            for i in range(self.get_width()):
                coordinate_up = np.array((self.get_x() + i, self.get_y() - 1))
                
                if np.linalg.norm(coordinate_to_check - coordinate_up) < 0.5:
                    return True, "UP"
                    
                if len(self.__setup_attributes_gui) == 0:
                    coordinate_down = np.array((self.get_x() + i, self.get_y() + self.get_height()))
                else:
                    last_attribute = self.__setup_attributes_gui[-1]
                    coordinate_down = np.array((last_attribute.get_x() + i, last_attribute.get_y() + last_attribute.get_height()))
                    
                # Below last attribute
                if np.linalg.norm(coordinate_to_check - coordinate_down) < 0.5:
                    return True, "DOWN"
                        
        # Sides of class
        is_adjacent_side, direction = super().is_adjacent(coordinates)
        
        if is_adjacent_side:
            return True, direction 
                
        for i, attribute in enumerate(self.__setup_attributes_gui):
            # Sides of attribute
            is_adjacent_side, direction = attribute.is_adjacent(coordinates)
            
            if is_adjacent_side:
                return True, direction
                    
        return False, ""
        
    def create_setup_attribute_gui(self, setup_attribute, configuration_attribute_gui):
        """
        Creates and adds a GUI version of a setup attribute
        """
        setup_attribute_gui = GUISetupAttribute(self.get_model(), self.get_view(), setup_attribute, self, configuration_attribute_gui, self.get_x(), self.get_y()+CLASS_HEIGHT+len(self.__setup_attributes_gui)*ATTRIBUTE_HEIGHT)
        
        self.__setup_attributes_gui.append(setup_attribute_gui)
        self.add_attached_block(setup_attribute_gui)
        
        return setup_attribute_gui
        
    def update_setup_attribute_gui_order(self):
        # Map each setup attribute (in their current order) to an index value to be sorted according to
        index_map = {value: index for index, value in enumerate(self.__setup_class.get_setup_attributes())}
        
        sorted_setup_attributes_gui = sorted(self.__setup_attributes_gui, key=lambda attribute_gui: index_map[attribute_gui.get_setup_attribute()])
        
        # Move position of GUI blocks
        for i, setup_attribute_gui in enumerate(sorted_setup_attributes_gui):
            steps_moved = i - self.__setup_attributes_gui.index(setup_attribute_gui)
            setup_attribute_gui.move_block(0, steps_moved)
            
        self.__setup_attributes_gui = sorted_setup_attributes_gui
        
    def get_connected_setup_attributes_gui(self, setup_attribute):
        connected_setup_attributes_gui = []
        
        for connected_setup_attribute in setup_attribute.get_connected_setup_attributes():
            for connected_setup_class_gui in self.get_connected_setup_classes_gui() + [self]:
                if connected_setup_attribute.has_setup_class(connected_setup_class_gui.get_setup_class()):
                    if not connected_setup_attribute.is_hidden():
                        attribute_index = connected_setup_attribute.get_attribute_index()
                        connected_setup_attribute_gui = connected_setup_class_gui.get_setup_attributes_gui()[attribute_index]
                        
                        connected_setup_attributes_gui.append(connected_setup_attribute_gui)
                        
                    else:
                        connected_setup_attributes_gui += connected_setup_class_gui.get_connected_setup_attributes_gui(connected_setup_attribute)
                        
        return connected_setup_attributes_gui
        
    def get_setup_class(self):
        return self.__setup_class
        
    def get_setup_attributes_gui(self):
        return self.__setup_attributes_gui
        
    def remove_setup_attribute_gui(self, setup_attribute_gui_to_remove):
        index_first_move_up = self.__setup_attributes_gui.index(setup_attribute_gui_to_remove)
        self.__setup_attributes_gui.remove(setup_attribute_gui_to_remove)
        self.remove_attached_block(setup_attribute_gui_to_remove)
        
        for setup_attribute_gui in self.__setup_attributes_gui[index_first_move_up:]:
            setup_attribute_gui.move_block(0, -ATTRIBUTE_HEIGHT)
            
    def add_connection(self, connection):
        self.__connections.append(connection)
        
    def remove_connection(self, connection):
        if connection in self.__connections:
            self.__connections.remove(connection)
            
    def get_connected_setup_classes_gui(self):
        connected_setup_classes_gui = []
        
        for connection in self.__connections:
            setup_class_gui = connection.get_start_setup_class_gui()
            
            if setup_class_gui not in (None, self):
                connected_setup_classes_gui.append(setup_class_gui)
                
        return connected_setup_classes_gui
        
    def create_script_marker_indicator(self, text, color, update_linked=True):
        self.__script_marker_indicators.append(NumberIndicator(self.get_view(), self.get_x()+2*SCRIPT_MARKER_CIRCLE_RADIUS*(0.5+len(self.__script_marker_indicators)), self.get_y()-SCRIPT_MARKER_CIRCLE_RADIUS, SCRIPT_MARKER_CIRCLE_RADIUS, color, SCRIPT_MARKER_CIRCLE_OUTLINE, text))
        
        if update_linked:
            for linked_setup_class_gui in self.get_model().get_linked_setup_classes_gui(self):
                linked_setup_class_gui.create_script_marker_indicator(text, color, False)
                
    def reset_changes_by_scripts(self):
        for setup_attribute_gui in self.__setup_attributes_gui:
            setup_attribute_gui.attempt_to_reset_override_value()
            
        for script_marker_indicator in self.__script_marker_indicators:
            script_marker_indicator.remove()
            
        self.__script_marker_indicators = []
        
    def update_value_input_types(self, *, specific_attribute_index=None, update_linked=True):
        for i, setup_attribute_gui in enumerate(self.__setup_attributes_gui):
            if specific_attribute_index == None or i == specific_attribute_index:
                setup_attribute_gui.update_value_input_type()
                
        if update_linked:
            for linked_setup_class_gui in self.get_model().get_linked_setup_classes_gui(self):
                linked_setup_class_gui.update_value_input_types(specific_attribute_index=specific_attribute_index, update_linked=False)
                
    def calculate_values(self):
        self.__setup_class.calculate_values()
        
        for setup_attribute_gui in self.__setup_attributes_gui:
            setup_attribute_gui.update_value()
        
    def reset_calculated_values(self):
        self.__setup_class.reset_calculated_values()
        
        for setup_attribute_gui in self.__setup_attributes_gui:
            setup_attribute_gui.add_entered_value_to_attribute()
            
    def get_configuration_name(self):
        return self.__configuration_class_gui.get_name()
        
    def get_name(self):
        return self.__setup_class.get_instance_name()
        
    def set_name(self, name):
        self.__setup_class.set_instance_name(name)
        self.update_text()
        
    def update_text(self):
        self.set_text(f"{self.__configuration_class_gui.get_name()}: {self.__setup_class.get_instance_name()}")
        
    def delete(self):
        super().delete()
        
        self.__configuration_class_gui.remove_setup_class_gui(self)
        self.get_view().remove_setup_class_gui(self)
        
    def save_state(self):
        saved_states = super().save_state() | {"name": self.get_name(), "configuration_class_gui": str(self.__configuration_class_gui), "setup_attributes_gui": []}
        
        for setup_attribute_gui in self.__setup_attributes_gui:
            saved_states["setup_attributes_gui"].append(setup_attribute_gui.save_state())
            
        return saved_states
        
class GUISetupAttribute(GUIModelingBlock):
    def __init__(self, model, view, setup_attribute, setup_class_gui, configuration_attribute_gui, x, y):
        self.__setup_attribute = setup_attribute
        self.__setup_class_gui = setup_class_gui
        self.__configuration_attribute_gui = configuration_attribute_gui
        
        width = ATTRIBUTE_WIDTH * SETUP_WIDTH_MULTIPLIER
        height = ATTRIBUTE_HEIGHT
        text_width = ATTRIBUTE_WIDTH
        
        actual_label_value_x, actual_label_value_y = convert_grid_coordinate_to_actual(view, x+width*3/4, y+height/2)
        self.__label_value = view.get_canvas().create_text(actual_label_value_x, actual_label_value_y, text="-", font=FONT)
        
        super().__init__(model, view, configuration_attribute_gui.get_name(), x, y, width, height, ATTRIBUTE_COLOR, text_width=text_width, label_text_x=x+width/4, additional_pressable_items=[self.__label_value], bind_left=MOUSE_PRESS)
        self.__entry_value = None
        self.__entry_value_window = None
        
        self.__entry_text = tk.StringVar()
        self.__entry_text.set("Value")
        
        configuration_attribute_gui.add_setup_attribute_gui(self)
        
        self.update_text()
        self.update_value_input_type()
        
    def left_pressed(self, event):
        super().left_pressed(event)
        self.set_input_attributes_highlight(True)
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        if self.__entry_value != None:
            actual_move_x, actual_move_y = convert_grid_coordinate_to_actual(self.get_view(), move_x, move_y)
            new_actual_x, new_actual_y = self.get_view().get_canvas().coords(self.__entry_value_window)
            new_actual_x += actual_move_x
            new_actual_y += actual_move_y
            
            self.get_view().get_canvas().coords(self.__entry_value_window, new_actual_x, new_actual_y)
            
    def scale(self, last_length_unit):
        super().scale(last_length_unit)
        
        if self.__entry_value != None:
            actual_width, actual_height = self.get_entry_size()
            actual_x, actual_y = get_actual_coordinates_after_zoom(self.get_view(), self.get_view().get_canvas().coords(self.__entry_value_window), last_length_unit)
            
            self.__entry_value.config(font=self.get_view().get_updated_font())
            self.get_view().get_canvas().coords(self.__entry_value_window, (actual_x, actual_y))
            self.get_view().get_canvas().itemconfig(self.__entry_value_window, width=actual_width, height=actual_height)
            
    def open_options(self):
        pass
        
    def unhighlight(self):
        super().unhighlight()
        self.set_input_attributes_highlight(False)
            
    def set_input_attributes_highlight(self, adding_color):
        for connected_setup_attribute_gui in self.__setup_class_gui.get_connected_setup_attributes_gui(self.__setup_attribute):
            if not self.get_view().is_selected_item(connected_setup_attribute_gui):
                if adding_color:
                    connected_setup_attribute_gui.highlight(HIGHLIGHT_INPUT_COLOR)
                else:
                    connected_setup_attribute_gui.unhighlight()
                    
    def update_value_input_type(self, clear_value=True):
        has_currently_connected_inputs = self.__setup_attribute.has_connected_setup_attributes()
        
        if has_currently_connected_inputs and self.__configuration_attribute_gui.get_configuration_attribute().get_symbol_calculation_type() != SYMBOL_CALCULATION_TYPE_QUALITATIVE:
            self.switch_to_value_label(clear_value)
        else:
            self.switch_to_value_entry(clear_value)
            
    def switch_to_value_label(self, clear_value=True):
        if self.__entry_value != None:
            self.get_view().get_canvas().delete(self.__entry_value_window)
            self.__entry_value_window = None
            self.__entry_value = None
            
            # Reset any manually entered value
            if clear_value:
                self.__setup_attribute.clear_value()
                self.set_displayed_value("-")
                
    def switch_to_value_entry(self, clear_value=True):
        if self.__entry_value == None:
            actual_width, actual_height = self.get_entry_size()
            actual_x, actual_y = convert_grid_coordinate_to_actual(self.get_view(), self.get_x()+self.get_width()/2, self.get_y())
            
            # Create Entry and Window to put Entry in to allow it be put inside the Canvas
            self.__entry_value = tk.Entry(self.get_view(), textvariable=self.__entry_text, font=FONT)
            self.__entry_value_window = self.get_canvas().create_window((actual_x, actual_y+OUTLINE_WIDTH), window=self.__entry_value, anchor="nw", width=actual_width, height=actual_height)
            
            # Reset any calculated value as the input now should be entered manually
            if clear_value:
                self.__setup_attribute.clear_value()
                self.set_displayed_value("Value")
                
            # When starting the edit the entered value, unselect all blocks to avoid accidentally deleting them
            self.__entry_value.bind("<FocusIn>", lambda event: self.get_view().unselect_all_items())
            
            self.get_canvas().tag_lower(self.__entry_value_window)
            
    def get_entry_size(self):
        width, height = convert_grid_coordinate_to_actual(self.get_view(), self.get_width()/2, self.get_height())
        width -= OUTLINE_WIDTH
        height -= OUTLINE_WIDTH * 2
        
        return width, height
        
    def get_setup_attribute(self):
        return self.__setup_attribute
        
    def add_entered_value_to_attribute(self):
        if self.__entry_value != None:
            self.__setup_attribute.set_value(self.__entry_text.get())
            
    """
    def clear_setup_attribute_value(self):
        self.__setup_attribute.clear_value()
    """
            
    def set_displayed_value(self, value, color=None):
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
            
    def update_value(self):
        if self.__setup_attribute.has_override_value():
            self.switch_to_value_label(False)
            self.set_displayed_value(self.__setup_attribute.get_override_value(), "red")
            
        else:
            self.set_displayed_value(self.__setup_attribute.get_value())
            
    def attempt_to_reset_override_value(self):
        if self.__setup_attribute.has_override_value():
            self.__setup_attribute.reset_override_value()
            self.update_value_input_type(False)
            self.update_value()
            
            return True
            
        return False
        
    def get_name(self):
        return self.__configuration_attribute_gui.get_name()
                
    # def is_hidden(self):
        # return self.__configuration_attribute_gui.is_hidden()
        
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
        self.add_entered_value_to_attribute()
        
        return super().save_state() | {"value": self.__setup_attribute.get_value()}
        
class GUIConnectionTriangle(GUIBlock):
    def __init__(self, model, view, x, y, direction, is_end_block):
        self.__is_end_block = is_end_block
        self.__triangle = view.get_canvas().create_polygon(get_triangle_coordinates(view, x, y, direction), width=OUTLINE_WIDTH, outline=OUTLINE_COLOR, fill=CONNECTION_END_COLOR, tags=(TAG_CONNECTION_CORNER,))
        
        super().__init__(model, view, [self.__triangle], x, y, CONNECTION_END_WIDTH, CONNECTION_END_HEIGHT, bind_left=MOUSE_DRAG)
        self.__connection = None
        self.__attached_setup_class_gui = None
        
        self.__is_deleted = False
        
    def left_pressed(self, event):
        super().left_pressed(event)
        
        # Disconnect from class
        if self.__attached_setup_class_gui != None:
            self.attempt_to_detach_from_class()
            
    def left_released(self, event):
        if super().left_released(event, False):
            self.put_down_block()
            
        self.get_view().update_shown_order()
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        # If panning or zooming, only the start block should move the lines
        if (not self.get_view().is_panning() and not self.get_view().is_zooming()) or not self.__is_end_block:
            self.__connection.move_lines(move_x, move_y)
            
    def open_options(self):
        self.__connection.open_options()
            
    def put_down_block(self):
        for setup_class_gui in self.get_view().get_setup_classes_gui():
            is_adjacent, direction = setup_class_gui.is_adjacent([(self.get_x(), self.get_y())])
            
            # Attach to class
            if is_adjacent:
                setup_class_gui.add_connection(self.__connection)
                setup_class_gui.add_attached_block(self)
                self.__attached_setup_class_gui = setup_class_gui
                
                self.__connection.update_direction(self, direction)
                self.rotate_triangle(direction)
                
                start_setup_class = self.__connection.get_start_setup_class()
                end_setup_class = self.__connection.get_end_setup_class()
                
                if start_setup_class != None and end_setup_class != None:
                    end_setup_class.add_input_setup_class(start_setup_class, self.__connection.get_input_scalars())
                    self.__connection.get_end_setup_class_gui().update_value_input_types()
                    
                break
                
    def rotate_triangle(self, new_direction):
        if self.__is_end_block:
            directions = ["UP", "RIGHT", "DOWN", "LEFT"]
            new_direction = directions[(directions.index(new_direction) + 2) % len(directions)]
            
        new_coordinates = get_triangle_coordinates(self.get_view(), self.get_x(), self.get_y(), new_direction)
        self.get_view().get_canvas().coords(self.__triangle, new_coordinates)
        
        self.update_highlight(HIGHLIGHT_SELECTED_COLOR)
        
    def add_connection(self, connection):
        self.__connection = connection
        
    def get_attached_setup_class_gui(self):
        return self.__attached_setup_class_gui
        
    def is_attached(self):
        return self.__attached_setup_class_gui != None
        
    def attempt_to_detach_from_class(self):
        if self.__attached_setup_class_gui != None:
            end_setup_class = self.__connection.get_end_setup_class()
            
            if end_setup_class != None:
                end_setup_class.remove_input_setup_class(self.__connection.get_start_setup_class())
                
            self.__attached_setup_class_gui.remove_connection(self.__connection)
            self.__attached_setup_class_gui.remove_attached_block(self)
            
            if self.__connection.get_end_setup_class_gui() != None:
                self.__connection.get_end_setup_class_gui().update_value_input_types()
                
            self.__attached_setup_class_gui = None
            
    def delete(self):
        super().delete()
        
        if not self.__is_deleted:
            self.__is_deleted = True
            self.attempt_to_detach_from_class()
            
            self.__connection.delete()
            
class GUIConnectionScalarsIndicator(GUIModelingBlock):
    def __init__(self, model, view, connection):
        self.__connection = connection
        x, y = connection.get_scalars_indicator_start_coordinate()
        
        super().__init__(model, view, self.__connection.get_input_scalars_string(), x, y, INPUT_SCALARS_INDICATOR_WIDTH, INPUT_SCALARS_INDICATOR_HEIGHT, INPUT_SCALARS_INDICATOR_COLOR, bind_left=MOUSE_DRAG, tags_rect=(TAG_INDICATOR,), tags_text=(TAG_INDICATOR_TEXT,))
        
    def left_dragged(self, event):
        allowed_movement_directions = self.__connection.allowed_scalars_indicator_movement_directions()
        max_positive_move_x, max_negative_move_x, max_positive_move_y, max_negative_move_y = get_max_directions_movement(allowed_movement_directions)
        
        super().left_dragged(event, max_positive_move_x=max_positive_move_x, max_negative_move_x=max_negative_move_x, max_positive_move_y=max_positive_move_y, max_negative_move_y=max_negative_move_y, single_direction=True)
        
    def open_options(self):
        return self.__connection.open_options()
        
    def update_displayed_input_scalars(self):
        self.set_text(self.__connection.get_input_scalars_string())
        
    def delete(self, reset_input_scalars=True):
        super().delete()
        
        if reset_input_scalars:
            self.__connection.reset_input_scalars()
