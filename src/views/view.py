import tkinter as tk
from buttons_gui import GUIAddChangeViewButton, GUISaveButton, GUISettingsButton, GUIChangeViewButton
from connection_with_blocks_gui import GUIConnectionWithBlocks
from options import OptionsView
from helper_functions_general import convert_actual_coordinate_to_grid
from config import *

class View(tk.Frame):
    """
    Class managing all objects in a view and the canvas that the corresponding items are drawn on
    """
    def __init__(self, model, name):
        super().__init__()
        self.__model = model
        self.__name = name
        self.__configuration_change_view_buttons = {} # View and corresponding button
        self.__setup_change_view_buttons = {} # View and corersponding button
        self.__selected_items = set() # Items that are highlighted by pressing on them
        
        self.__is_panning = False
        self.__is_zooming = False
        self.__panning_last_mouse_coordinate = (0, 0)
        self.__length_unit_difference = 0 # How much the length unit has been changed from LENGTH_UNIT
        self.__grid_offset = (0, 0) # How much items are offset from the grid in the range [0, 1) due to panning/zooming
        
        self.__canvas = tk.Canvas(self, width=settings.get_canvas_width(), height=settings.get_canvas_height(), bg=BACKGROUND_COLOR)
        self.__canvas_size = (settings.get_canvas_width(), settings.get_canvas_height())
        self.__add_change_configuration_view_button = GUIAddChangeViewButton(model, \
                                                                             self, \
                                                                             CHANGE_VIEW_CONFIGURATION_START_POSITION[0]+CHANGE_VIEW_WIDTH//2, \
                                                                             CHANGE_VIEW_CONFIGURATION_START_POSITION[1], \
                                                                             True)
        self.__add_change_setup_view_button = GUIAddChangeViewButton(model, \
                                                                     self, \
                                                                     CHANGE_VIEW_SETUP_START_POSITION[0]+CHANGE_VIEW_WIDTH//2, \
                                                                     CHANGE_VIEW_SETUP_START_POSITION[1], \
                                                                     False)
        self.__save_button = GUISaveButton(model, self, SAVE_POSITION[0], SAVE_POSITION[1])
        self.__settings_button = GUISettingsButton(model, self, SETTINGS_POSITION[0], SETTINGS_POSITION[1])
        
        self.__canvas.bind(MOUSE_LEFT_PRESS, self.pan_start)
        self.__canvas.bind(MOUSE_LEFT_DRAG, self.pan_move)
        self.__canvas.bind(MOUSE_LEFT_RELEASE, self.pan_stop)
        
        # Binds two variations to account for Linux, macOS, and Windows
        self.__canvas.bind(MOUSE_WHEEL_UP, self.zoom_in)
        self.__canvas.bind(MOUSE_WHEEL_DOWN, self.zoom_out)
        self.__canvas.bind(MOUSE_WHEEL, lambda event: self.zoom_in(event) if event.delta > 0 else self.zoom_out(event))
        
        # Changing the window size
        self.__canvas.bind("<Configure>", self.on_resize)
        
        self.__canvas.pack(expand=True, fill="both")
        
    def pan_start(self, event):
        """
        When starting to pan by pressing the canvas background
        """
        closest_item = self.__canvas.find_closest(event.x, event.y)
        actual_coords_closest_item = self.__canvas.bbox(closest_item)
        
        # Item on the canvas was pressed
        if actual_coords_closest_item != None:
            x1, y1, x2, y2 = actual_coords_closest_item
            self.__is_panning = not (x1 <= event.x <= x2 and y1 <= event.y <= y2)
            
        # Pressed on background
        else:
            self.__is_panning = True
            
        self.__canvas.focus_set()
        
        if self.__is_panning:
            self.unselect_all_items()
            self.__panning_last_mouse_coordinate = (event.x, event.y)
            
    def pan_move(self, event):
        """
        When dragging on the canvas background to pan the view
        """
        if self.__is_panning:
            # How much to move each item
            move_x, move_y = convert_actual_coordinate_to_grid(self, event.x-self.__panning_last_mouse_coordinate[0], event.y-self.__panning_last_mouse_coordinate[1])
            
            self.update_grid_offset(move_x, move_y)
            
            for movable_item in self.get_movable_items():
                movable_item.move_block(move_x, move_y)
                
            self.__panning_last_mouse_coordinate = (event.x, event.y)
            
    def pan_stop(self, event):
        """
        When stopping to pan by releasing the mouse button
        """
        self.__is_panning = False
    
    def zoom_in(self, event):
        if self.get_length_unit() < LENGTH_UNIT_ZOOM_LIMITS[1]:
            self.zoom(event, 1)
        
    def zoom_out(self, event):
        if self.get_length_unit() > LENGTH_UNIT_ZOOM_LIMITS[0]:
            self.zoom(event, -1)
        
    def zoom(self, event, length_unit_difference):
        """
        Zooming in or out the view
        
        length_unit_difference: The difference in length unit per grid square due to zooming
        """
        self.__is_zooming = True
        
        last_length_unit = self.get_length_unit()
        self.__length_unit_difference += length_unit_difference
        
        scale_origin_x, scale_origin_y = convert_actual_coordinate_to_grid(self, event.x, event.y) # Zoom around where the mouse is
        length_unit_change = last_length_unit / self.get_length_unit() - 1
        
        move_x = scale_origin_x * length_unit_change
        move_y = scale_origin_y * length_unit_change
        
        self.update_grid_offset(move_x, move_y)
        
        for movable_item in self.get_movable_items():
            movable_item.scale(last_length_unit) # Scales entire grid and all its components
            movable_item.move_block(move_x, move_y) # Moves all components on the grid to simulate zooming in at the coordinates of the mouse
            
        self.__is_zooming = False
        
    def on_resize(self, event):
        """
        Changing the window size
        """
        self.__canvas.config(width=event.width, height=event.height)
        
        actual_move_x = event.width - self.__canvas_size[0]
        actual_move_y = event.height - self.__canvas_size[1]
        move_x, move_y = convert_actual_coordinate_to_grid(self, actual_move_x, actual_move_y)
        
        self.__canvas_size = (event.width, event.height)
        
        # Buttons to move so that they do not end up outside the window
        for item_to_move_x in list(self.__configuration_change_view_buttons.values()) + \
                              list(self.__setup_change_view_buttons.values()) + \
                              [self.__add_change_configuration_view_button, self.__add_change_setup_view_button]:
            item_to_move_x.move_block(move_x, 0)
            
        self.__save_button.move_block(0, move_y)
        self.__settings_button.move_block(0, move_y)
        
        settings.set_canvas_size(event.width, event.height)
        
        return move_x, move_y
        
    def update_shown_order(self):
        """
        Refreshes the order that items should be shown in to make sure some are shown on top of others
        """
        for tag in (TAG_INPUT, TAG_INPUT_TEXT, TAG_CONNECTION_LINE, TAG_CONNECTION_CORNER, TAG_INDICATOR, TAG_INDICATOR_TEXT, TAG_BUTTON, TAG_BUTTON_TEXT):
            self.__canvas.tag_raise(tag)
            
    def open_options(self):
        return OptionsView(self.get_model(), self)
        
    def get_updated_font(self, *, label=None, has_line_break=False):
        """
        Returns the font size that should be used in a text field on the canvas given considering the current zoom level and whether there is a line break (need to lower font size further)
        """
        new_font_size = int(FONT[1] * self.get_length_unit() / LENGTH_UNIT + 0.5)
        
        if has_line_break:
            new_font_size -= FONT_DECREASE_LINE_BREAK
            
        if new_font_size < 1:
            new_font_size = 1
            
        if label == None:
            return (FONT[0], new_font_size)
            
        # Get existing attributes of the font
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
        """
        Adds a button to change to a specified view
        """
        # Move down the button that adds another view
        if not is_setup_view:
            self.__configuration_change_view_buttons[view_to_change_to] = GUIChangeViewButton(self.__model, self, x, y, view_to_change_to.get_name(), view_to_change_to)
            self.__add_change_configuration_view_button.move_block(0, CHANGE_VIEW_HEIGHT)
            
        else:
            self.__setup_change_view_buttons[view_to_change_to] = GUIChangeViewButton(self.__model, self, x, y, view_to_change_to.get_name(), view_to_change_to)
            self.__add_change_setup_view_button.move_block(0, CHANGE_VIEW_HEIGHT)
            
    def remove_change_view_button(self, view_to_remove):
        """
        Removes a button that changes to a specified view
        """
        # Move up the button that adds another view
        if view_to_remove in self.__configuration_change_view_buttons:
            change_view_buttons = self.__configuration_change_view_buttons
            self.__add_change_configuration_view_button.move_block(0, -CHANGE_VIEW_HEIGHT)
            
        elif view_to_remove in self.__setup_change_view_buttons:
            change_view_buttons = self.__setup_change_view_buttons
            self.__add_change_setup_view_button.move_block(0, -CHANGE_VIEW_HEIGHT)
            
        found_deleted = False
        
        # Move up all buttons that change view that are after the removed button
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
        """
        Change the text of a specific change view button within this view
        """
        if view_with_changed_name in self.__configuration_change_view_buttons:
            self.__configuration_change_view_buttons[view_with_changed_name].set_text(text)
            
        elif view_with_changed_name in self.__setup_change_view_buttons:
            self.__setup_change_view_buttons[view_with_changed_name].set_text(text)
            
    def move_change_view_button(self, view_to_move, up):
        """
        Moves a change view button up or down a step
        """
        to_move = CHANGE_VIEW_HEIGHT
        
        if up:
            to_move *= -1
        
        if view_to_move in self.__configuration_change_view_buttons:
            self.__configuration_change_view_buttons[view_to_move].move_block(0, to_move)
            
        elif view_to_move in self.__setup_change_view_buttons:
            self.__setup_change_view_buttons[view_to_move].move_block(0, to_move)
            
    def get_selected_items(self):
        return self.__selected_items
        
    def is_selected_item(self, selected_item):
        return selected_item in self.__selected_items
        
    def select_item(self, selected_item):
        # Unselect other items if not selecting multiple ones
        if not (self.get_model().is_currently_pressing_key("Shift_L") or self.get_model().is_currently_pressing_key("Shift_R")):
            self.unselect_all_items()
            
        # Highlight selected item
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
        """
        Returns the current length unit, including any difference due to zooming
        """
        return LENGTH_UNIT + self.__length_unit_difference
        
    def update_grid_offset(self, move_x, move_y):
        """
        Update the current offset of the grid due to panning/zooming
        """
        # Set the offset of each value to be within [0, 1)
        grid_offset_x = (self.__grid_offset[0] + move_x) % 1
        grid_offset_y = (self.__grid_offset[1] + move_y) % 1
        
        self.__grid_offset = (grid_offset_x, grid_offset_y)
        
    def get_grid_offset(self):
        return self.__grid_offset
        
    def set_grid_offset(self, offset_x, offset_y):
        self.__grid_offset = (offset_x, offset_y)
        
    def delete(self):
        self.destroy()
