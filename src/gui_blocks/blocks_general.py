import tkinter as tk
import numpy as np
from helper_functions import convert_grid_coordinate_to_actual, convert_actual_coordinate_to_grid, get_actual_coordinates_after_zoom, distance_to_closest_grid_intersection, delete_all
from options import OptionsConnection
from config import *

class GUIBlock:
    def __init__(self, model, view, pressable_items, x, y, width, height, *, bind_left=None, bind_right=None):
        self.__model = model
        self.__view = view
        self.__pressable_items = pressable_items
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        
        self.__draggable = bind_left == MOUSE_DRAG
        self.__picked_up = False
        self.__pick_up_actual_coordinate = (0, 0)
        
        for pressable_item in self.__pressable_items:
            if bind_left in (MOUSE_PRESS, MOUSE_DRAG):
                view.get_canvas().tag_bind(pressable_item, MOUSE_LEFT_PRESS, self.left_pressed)
                
            if bind_left == MOUSE_DRAG:
                view.get_canvas().tag_bind(pressable_item, MOUSE_LEFT_DRAG, self.left_dragged)
                view.get_canvas().tag_bind(pressable_item, MOUSE_LEFT_RELEASE, self.left_released)
                
            if bind_right == MOUSE_PRESS:
                view.get_canvas().tag_bind(pressable_item, MOUSE_RIGHT_PRESS, self.right_pressed)
                
    def left_pressed(self, event):
        # Pick up block
        if self.__draggable:
            self.__pick_up_actual_coordinate = (event.x, event.y)
            self.__picked_up = True
            
    def left_dragged(self, event):
        if self.__picked_up:
            move_x, move_y = convert_actual_coordinate_to_grid(self.__view, event.x-self.__pick_up_actual_coordinate[0], event.y-self.__pick_up_actual_coordinate[1])
            
            self.move_block(move_x, move_y)
            
            self.__pick_up_actual_coordinate = (event.x, event.y)
            
    def left_released(self, event):
        # Put down block
        if self.__picked_up:
            self.snap_to_grid()
            self.__picked_up = False
            
            return True
            
        return False
        
    def right_pressed(self, event):
        pass
        
    def scale(self, last_length_unit):
        for pressable_item in self.__pressable_items:
            item_type = self.__view.get_canvas().type(pressable_item)
            adjusted_actual_coordinates = get_actual_coordinates_after_zoom(self.__view, self.__view.get_canvas().coords(pressable_item), last_length_unit)
            
            if item_type == "rectangle":
                x1, y1, x2, y2 = adjusted_actual_coordinates
                self.__view.get_canvas().coords(pressable_item, x1, y1, x2, y2)
                
            elif item_type == "polygon":
                x1, y1, x2, y2, x3, y3 = adjusted_actual_coordinates
                self.__view.get_canvas().coords(pressable_item, x1, y1, x2, y2, x3, y3)
                
            elif item_type == "text":
                x, y = adjusted_actual_coordinates
                self.__view.get_canvas().coords(pressable_item, x, y)
                
                font_size = self.get_font_size()
                self.__view.get_canvas().itemconfig(pressable_item, font=(FONT[0], font_size))
        
    def get_font_size(self):
        return int(FONT[1] * self.get_view().get_length_unit() / LENGTH_UNIT)
            
    def snap_to_grid(self):
        move_x, move_y = distance_to_closest_grid_intersection(self.__view, self.__x, self.__y)
        
        self.move_block(move_x, move_y)
        
    def move_block(self, move_x, move_y):
        if move_x != 0 or move_y != 0:
            for pressable_item in self.__pressable_items:
                move_actual_x, move_actual_y = convert_grid_coordinate_to_actual(self.__view, move_x, move_y)
                self.get_canvas().move(pressable_item, move_actual_x, move_actual_y)
            
            self.__x = round(self.__x + move_x, 3)
            self.__y = round(self.__y + move_y, 3)
            
    def get_model(self):
        return self.__model
        
    def get_view(self):
        return self.__view
        
    def get_canvas(self):
        return self.__view.get_canvas()
        
    def get_x(self):
        return self.__x
        
    def get_y(self):
        return self.__y
        
    def get_width(self):
        return self.__width
        
    def get_height(self):
        return self.__height
        
    def get_direction(self, mouse_x, mouse_y):
        direction = "RIGHT"
        actual_mid_x = convert_grid_coordinate_to_actual(self.__view, self.get_x()+self.get_width()//2, 0)[0]
        
        if mouse_x < actual_mid_x:
            direction = "LEFT"
            
        return direction
        
    def delete(self):
        for pressable_items in self.__pressable_items:
            self.get_canvas().delete(pressable_items)
            
    def save_state(self):
        return {"x": self.__x, "y": self.__y}
        
class GUIModelingBlock(GUIBlock):
    def __init__(self, model, view, text, x, y, width, height, fill_color, *, bind_left=None, bind_right=None, has_value=False):
        canvas = view.get_canvas()
        actual_rect_x1, actual_rect_y1 = convert_grid_coordinate_to_actual(view, x, y)
        actual_rect_x2, actual_rect_y2 = convert_grid_coordinate_to_actual(view, x+width, y+height)
        
        self.__rect = canvas.create_rectangle(actual_rect_x1, actual_rect_y1, actual_rect_x2, actual_rect_y2, width=OUTLINE_WIDTH, outline=OUTLINE_COLOR, fill=fill_color)
        self.__entry_value = None
        self.__entry_value_window = None
        
        if has_value:
            actual_label_text_x, actual_label_text_y = convert_grid_coordinate_to_actual(view, x+width/4, y+height/2)
            actual_label_value_x, actual_label_value_y = convert_grid_coordinate_to_actual(view, x+width*3/4, y+height/2)
            
            self.__label_text = canvas.create_text(actual_label_text_x, actual_label_text_y, text=text, font=FONT)
            self.__label_value = canvas.create_text(actual_label_value_x, actual_label_value_y, text="-", font=FONT)
            
            self.__entry_text = tk.StringVar()
            self.__entry_text.set("Value")
        else:
            actual_label_text_x, actual_label_text_y = convert_grid_coordinate_to_actual(view, x+width/2, y+height/2)
            self.__label_text = canvas.create_text(actual_label_text_x, actual_label_text_y, text=text, font=FONT)
            
        pressable_items = [self.__rect, self.__label_text]
        
        if has_value:
            pressable_items.append(self.__label_value)
            
        super().__init__(model, view, pressable_items, x, y, width, height, bind_left=bind_left, bind_right=bind_right)
        self.__text = text
        self.__has_value = has_value
        self.__attached_blocks = []
        
        if has_value:
            self.enable_value_entry()
            
        self.__default_text_color = view.get_canvas().itemcget(self.__label_text, "fill")
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        for block in self.__attached_blocks:
            if block != self:
                block.move_block(move_x, move_y)
                
        if self.__has_value:
            if self.__entry_value != None:
                actual_move_x, actual_move_y = convert_grid_coordinate_to_actual(self.get_view(), move_x, move_y)
                new_actual_x, new_actual_y = self.get_view().get_canvas().coords(self.__entry_value_window)
                new_actual_x += actual_move_x
                new_actual_y += actual_move_y
                
                self.get_view().get_canvas().coords(self.__entry_value_window, new_actual_x, new_actual_y)
                
    def scale(self, last_length_unit):
        super().scale(last_length_unit)
        
        for attached_block in self.__attached_blocks:
            attached_block.scale(last_length_unit)
            
        if self.__entry_value != None:
            font_size = self.get_font_size()
            actual_width, actual_height = self.get_entry_size()
            actual_x, actual_y = get_actual_coordinates_after_zoom(self.get_view(), self.get_view().get_canvas().coords(self.__entry_value_window), last_length_unit)
            
            self.__entry_value.config(font=(FONT[0], font_size))
            self.get_view().get_canvas().coords(self.__entry_value_window, (actual_x, actual_y))
            self.get_view().get_canvas().itemconfig(self.__entry_value_window, width=actual_width, height=actual_height)
            
    def is_adjacent(self, coordinates):
        for coordinate in coordinates:
            coordinate_to_check = np.array(coordinate)
            
            for i in range(self.get_height()):
                coordinate_left = np.array((self.get_x() - 1, self.get_y() + i))
                coordinate_right = np.array((self.get_x() + self.get_width(), self.get_y() + i))
                
                if np.linalg.norm(coordinate_to_check - coordinate_left) < 0.5:
                    return True, "LEFT"
                    
                elif np.linalg.norm(coordinate_to_check - coordinate_right) < 0.5:
                    return True, "RIGHT"
                    
        return False, ""
        
    def get_text(self):
        return self.__text
        
    def set_text(self, text, space_from_end_to_break=1):
        self.__text = text
        self.get_canvas().itemconfig(self.__label_text, text=text)
        
    def has_input_entry(self):
        return self.__entry_value != None
        
    def enable_value_label(self):
        if self.__entry_value != None:
            self.get_view().get_canvas().delete(self.__entry_value_window)
            self.__entry_value_window = None
            self.__entry_value = None
            
    def enable_value_entry(self):
        if self.__entry_value == None:
            actual_width, actual_height = self.get_entry_size()
            actual_x, actual_y = convert_grid_coordinate_to_actual(self.get_view(), self.get_x()+self.get_width()/2, self.get_y())
            
            # Create Entry and Window to put Entry in to allow it be put inside the Canvas
            self.__entry_value = tk.Entry(self.get_view(), textvariable=self.__entry_text, font=FONT)
            self.__entry_value_window = self.get_canvas().create_window((actual_x, actual_y+OUTLINE_WIDTH), window=self.__entry_value, anchor="nw", width=actual_width, height=actual_height)
            
    def get_entry_size(self):
        width, height = convert_grid_coordinate_to_actual(self.get_view(), self.get_width()/2, self.get_height())
        width -= OUTLINE_WIDTH
        height -= OUTLINE_WIDTH * 2
        
        return width, height
        
    def get_entered_value(self):
        if self.__has_value and self.__entry_value != None:
            return self.__entry_text.get()
            
        return None
        
    def set_displayed_value(self, value, color=None):
        if color == None:
            color = self.__default_text_color
            
        # Set value in Label
        if self.__entry_value == None:
            self.get_view().get_canvas().itemconfig(self.__label_value, text=str(value), fill=color)
            
        # Set value in Entry
        else:
            self.__entry_value.delete(0, "end")
            self.__entry_value.insert(0, str(value))
            
    def add_attached_block(self, block):
        self.__attached_blocks.append(block)
        
    def remove_attached_block(self, block):
        self.__attached_blocks.remove(block)
        
    def has_attached_block(self, block):
        return block in self.__attached_blocks
        
    def delete(self):
        super().delete()
        
        delete_all(self.__attached_blocks)
        
        if self.__entry_value != None:
            self.get_view().get_canvas().delete(self.__entry_value_window)
            
class GUIConnectionCorner(GUIBlock):
    def __init__(self, model, view, connection, x, y):
        actual_x, actual_y = convert_grid_coordinate_to_actual(view, x+0.5-CORNER_WIDTH/2, y+0.5-CORNER_HEIGHT/2)
        actual_width, actual_height = convert_grid_coordinate_to_actual(view, CORNER_WIDTH, CORNER_HEIGHT)
        self.__rect = view.get_canvas().create_rectangle(actual_x, actual_y, actual_x+actual_width, actual_y+actual_height, width=OUTLINE_WIDTH, outline=OUTLINE_COLOR, fill=CORNER_COLOR)
        
        super().__init__(model, view, [self.__rect], x, y, CORNER_WIDTH, CORNER_HEIGHT, bind_left=None, bind_right=MOUSE_PRESS)
        self.__connection = connection
        
    """
    def left_pressed(self, event):
        pass
        if self.is_picked_up():
            self.get_view().set_moving_connection_corner(self)
        else:
            self.get_view().reset_moving_connection_corner()
    """
    
    def right_pressed(self, event):
        if self.__connection.has_options():
            OptionsConnection(self.get_model().get_root(), self.__connection)
            
        else:
            self.__connection.delete()
