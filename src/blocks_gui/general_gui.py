import tkinter as tk
import tkinter.font as tkfont
import numpy as np
from helper_functions import convert_grid_coordinate_to_actual, convert_actual_coordinate_to_grid, get_actual_coordinates_after_zoom, distance_to_closest_grid_intersection, get_max_directions_movement, delete_all
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
        self.__has_line_break_text = False
        self.__shapes_highlight = []
        
        self.__draggable = bind_left == MOUSE_DRAG
        self.__pick_up_actual_coordinate = (0, 0)
        
        for pressable_item in self.__pressable_items:
            if bind_left in (MOUSE_PRESS, MOUSE_DRAG):
                view.get_canvas().tag_bind(pressable_item, MOUSE_LEFT_PRESS, self.left_pressed)
                
            if bind_left == MOUSE_DRAG:
                view.get_canvas().tag_bind(pressable_item, MOUSE_LEFT_DRAG, self.left_dragged)
                view.get_canvas().tag_bind(pressable_item, MOUSE_LEFT_RELEASE, self.left_released)
                
            if bind_right == MOUSE_PRESS:
                view.get_canvas().tag_bind(pressable_item, MOUSE_RIGHT_PRESS, self.right_pressed)
                
        self.__was_dragged = False
        self.__is_deleted = False
        
        GUIBlock.scale(self, view.get_length_unit())
        
        if not isinstance(self, GUIConnectionCorner):
            view.update_shown_order()
            
    def left_pressed(self, event):
        self.__view.select_item(self)
        
        # Pick up block
        if self.__draggable:
            self.__pick_up_actual_coordinate = (event.x, event.y)
            
    def left_dragged(self, event, *, max_positive_move_x=None, max_negative_move_x=None, max_positive_move_y=None, max_negative_move_y=None, single_direction=False):
        if self.__draggable:
            self.__was_dragged = True
            move_x, move_y = convert_actual_coordinate_to_grid(self.__view, event.x-self.__pick_up_actual_coordinate[0], event.y-self.__pick_up_actual_coordinate[1])
            
            if max_positive_move_x != None and move_x > max_positive_move_x:
                move_x = max_positive_move_x
                
            elif max_negative_move_x != None and move_x < max_negative_move_x:
                move_x = max_negative_move_x
                
            if max_positive_move_y != None and move_y > max_positive_move_y:
                move_y = max_positive_move_y
                
            elif max_negative_move_y != None and move_y < max_negative_move_y:
                move_y = max_negative_move_y
                
            if single_direction:
                if abs(move_x) >= abs(move_y):
                    move_y = 0
                else:
                    move_x = 0
                    
            self.move_block(move_x, move_y)
            
            self.__pick_up_actual_coordinate = (event.x, event.y)
            
            return move_x, move_y
            
        return 0, 0
        
    def left_released(self, event, update_shown_order=True):
        did_put_down_block = False
        
        # Put down block, where it needs to have been dragged to correct its position to avoid always drawing new connection lines that reset custom paths
        if self.__draggable and self.__was_dragged:
            self.snap_to_grid()
            did_put_down_block = True
            
            if update_shown_order:
                self.__view.update_shown_order()
                
        self.__was_dragged = False
        
        return did_put_down_block
        
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
                self.__view.get_canvas().itemconfig(pressable_item, font=self.__view.get_updated_font(label=pressable_item, has_line_break=self.__has_line_break_text))
                
    def highlight(self, color):
        GUIBlock.unhighlight(self)
        
        for pressable_item in self.__pressable_items:
            item_type = self.__view.get_canvas().type(pressable_item)
            actual_coordinates = self.__view.get_canvas().coords(pressable_item)
            
            if item_type == "rectangle":
                x1, y1, x2, y2 = actual_coordinates
                rect = self.__view.get_canvas().create_rectangle(x1-HIGHLIGHT_BORDER_WIDTH, y1-HIGHLIGHT_BORDER_WIDTH, x2+HIGHLIGHT_BORDER_WIDTH, y2+HIGHLIGHT_BORDER_WIDTH, width=0, fill=color)
                
                self.__view.get_canvas().tag_lower(rect)
                self.__shapes_highlight.append(rect)
                
            elif item_type == "polygon":
                actual_coordinate_pairs = list(zip(actual_coordinates[0::2], actual_coordinates[1::2]))
                actual_center_x = sum(x for x, y in actual_coordinate_pairs) / 3
                actual_center_y = sum(y for x, y in actual_coordinate_pairs) / 3
                
                new_actual_coordinate_pairs = []
                
                for x, y in actual_coordinate_pairs:
                    vector_from_center = (x - actual_center_x, y - actual_center_y)
                    magnitude = (vector_from_center[0] ** 2 + vector_from_center[1] ** 2) ** 0.5
                    
                    for vector_value, old_actual_value in zip(vector_from_center, (x, y)):
                        new_actual_coordinate_pairs.append(old_actual_value + (vector_value / magnitude) * HIGHLIGHT_BORDER_WIDTH * 2)
                        
                x1, y1, x2, y2, x3, y3 = new_actual_coordinate_pairs
                triangle = self.__view.get_canvas().create_polygon(x1, y1, x2, y2, x3, y3, width=0, fill=color)
                
                self.__view.get_canvas().tag_lower(triangle)
                self.__shapes_highlight.append(triangle)
                
    def unhighlight(self):
        for shape_highlight in self.__shapes_highlight:
            self.__view.get_canvas().delete(shape_highlight)
            
        self.__shapes_highlight.clear()
        
    def update_highlight(self, color):
        if len(self.__shapes_highlight) > 0:
            self.unhighlight()
            self.highlight(color)
            
    def snap_to_grid(self):
        move_x, move_y = distance_to_closest_grid_intersection(self.__view, self.__x, self.__y)
        
        self.move_block(move_x, move_y)
        
    def move_block(self, move_x, move_y):
        if move_x != 0 or move_y != 0:
            move_actual_x, move_actual_y = convert_grid_coordinate_to_actual(self.__view, move_x, move_y)
            
            for pressable_item in self.__pressable_items:
                self.get_canvas().move(pressable_item, move_actual_x, move_actual_y)
                
            for shape_highlight in self.__shapes_highlight:
                self.get_canvas().move(shape_highlight, move_actual_x, move_actual_y)
                
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
        
    def has_line_break_text(self):
        return self.__has_line_break_text
        
    def set_line_break_text(self, has_line_break_text):
        self.__has_line_break_text = has_line_break_text
        
    def get_text_width(self):
        return self.__text_width
        
    def get_direction(self, mouse_x, mouse_y):
        direction = "RIGHT"
        actual_mid_x = convert_grid_coordinate_to_actual(self.__view, self.get_x()+self.get_width()//2, 0)[0]
        
        if mouse_x < actual_mid_x:
            direction = "LEFT"
            
        return direction
        
    def is_deleted(self):
        return self.__is_deleted
        
    def delete(self):
        self.__is_deleted = True
        self.get_view().unselect_item(self)
        
        for pressable_items in self.__pressable_items:
            self.get_canvas().delete(pressable_items)
            
        GUIBlock.unhighlight(self)
        
    def save_state(self):
        return {"x": self.__x, "y": self.__y}
        
class GUIModelingBlock(GUIBlock):
    def __init__(self, model, view, text, x, y, width, height, fill_color, *, text_width=None, label_text_x=None, additional_pressable_items=None, bind_left=None, bind_right=None, tags_rect=(), tags_text=()):
        canvas = view.get_canvas()
        actual_rect_x1, actual_rect_y1 = convert_grid_coordinate_to_actual(view, x, y)
        actual_rect_x2, actual_rect_y2 = convert_grid_coordinate_to_actual(view, x+width, y+height)
        
        self.__rect = canvas.create_rectangle(actual_rect_x1, actual_rect_y1, actual_rect_x2, actual_rect_y2, width=OUTLINE_WIDTH, outline=OUTLINE_COLOR, fill=fill_color, tags=tags_rect)
        
        if label_text_x == None:
            label_text_x = x + width / 2
            
        actual_label_text_x, actual_label_text_y = convert_grid_coordinate_to_actual(view, label_text_x, y+height/2)
        self.__label_text = canvas.create_text(actual_label_text_x, actual_label_text_y, text=text, font=FONT, justify="center", tags=tags_text)
        self.__default_text_color = view.get_canvas().itemcget(self.__label_text, "fill")
        
        pressable_items = [self.__rect, self.__label_text]
        
        if additional_pressable_items != None:
            for additional_pressable_item in additional_pressable_items:
                canvas.tag_raise(additional_pressable_item)
                
            pressable_items += additional_pressable_items
            
        super().__init__(model, view, pressable_items, x, y, width, height, bind_left=bind_left, bind_right=bind_right)
        self.__text = text
        self.__attached_blocks = []
        
        if text_width != None:
            self.__text_width = text_width
        else:
            self.__text_width = width
            
        self.set_text(text)
            
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        for block in self.__attached_blocks:
            if block != self:
                block.move_block(move_x, move_y)
                
    def scale(self, last_length_unit):
        super().scale(last_length_unit)
        
        for attached_block in self.__attached_blocks:
            attached_block.scale(last_length_unit)
            
    def highlight(self, color):
        super().highlight(color)
        
        for attached_block in self.__attached_blocks:
            attached_block.highlight(color)
            
    def unhighlight(self):
        super().unhighlight()
        
        for attached_block in self.__attached_blocks:
            attached_block.unhighlight()
            
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
        
    def set_text(self, text, is_bold=False):
        actual_maximum_text_width = convert_grid_coordinate_to_actual(self.get_view(), self.__text_width, 0)[0] - 2 * OUTLINE_WIDTH
        font = self.get_view().get_updated_font(label=self.__label_text)
        
        if is_bold:
            font = (font[0], font[1], "bold")
            actual_text_width = tkfont.Font(family=font[0], size=font[1], weight=font[2]).measure(text)
        else:
            font = (font[0], font[1])
            actual_text_width = tkfont.Font(family=font[0], size=font[1]).measure(text)
            
        # Should add line break and lower font size
        if actual_text_width >= actual_maximum_text_width:
            self.set_line_break_text(True)
            
            # Find the space that is closest to the middle and line break there
            words = text.split()
            mid_index = len(text) // 2
            current_number_of_characters = 0
            
            for i, word in enumerate(words):
                current_number_of_characters += len(word) + 1
                
                if current_number_of_characters >= mid_index:
                    if current_number_of_characters - mid_index < len(word) // 2:
                        text = " ".join(words[:i+1]) + "\n" + " ".join(words[i+1:])
                    else:
                        text = " ".join(words[:i]) + "\n" + " ".join(words[i:])
                        
                    break
                    
        else:
            self.set_line_break_text(False)
            
        font = self.get_view().get_updated_font(label=self.__label_text, has_line_break=self.has_line_break_text())
        
        if is_bold:
            font = (font[0], font[1], "bold")
        else:
            font = (font[0], font[1])
            
        self.__text = text
        self.get_canvas().itemconfig(self.__label_text, text=text, font=font, fill=TEXT_COLOR)
         
    def get_default_text_color(self):
        return self.__default_text_color
            
    def add_attached_block(self, block):
        self.__attached_blocks.append(block)
        
    def remove_attached_block(self, block):
        self.__attached_blocks.remove(block)
        
    def has_attached_block(self, block):
        return block in self.__attached_blocks
        
    def delete(self):
        delete_all(self.__attached_blocks)
        super().delete()
        
class GUIClass(GUIModelingBlock):
    def __init__(self, model, view, text, x, y, width, height, is_configuration_class, linked_group_number=None):
        super().__init__(model, view, text, x, y, width, height, CLASS_COLOR, bind_left=MOUSE_DRAG)
        self.__is_configuration_class = is_configuration_class
        self.__linked_group_number = linked_group_number
        self.__linked_group_indicator = None
        
        if self.__linked_group_number != None:
            self.update_linked_group_indicator()
            
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        if self.__linked_group_indicator != None:
            self.__linked_group_indicator.move(move_x, move_y)
            
    def scale(self, last_length_unit):
        super().scale(last_length_unit)
        
        if self.__linked_group_indicator != None:
            self.__linked_group_indicator.scale(last_length_unit)
            
    def is_linked(self):
        return self.__linked_group_number != None
        
    def get_linked_group_number(self):
        return self.__linked_group_number
        
    def set_linked_group_number(self, linked_group_number):
        self.__linked_group_number = linked_group_number
        self.update_linked_group_indicator()
                
    def update_linked_group_indicator(self):
        # Remove any existing indicator
        if self.__linked_group_indicator != None:
            self.__linked_group_indicator.remove()
                
        # Add or update indicator
        if self.__linked_group_number != None:
            if self.__linked_group_indicator == None:
                self.__linked_group_indicator = NumberIndicator(self.get_view(), self.get_x()+self.get_width(), self.get_y(), LINKED_GROUP_CIRCLE_RADIUS, LINKED_GROUP_CIRCLE_COLOR, LINKED_GROUP_CIRCLE_OUTLINE, self.__linked_group_number)
            else:
                self.__linked_group_indicator.create(self.__linked_group_number)
                
    def delete(self):
        super().delete()
        
        if self.__linked_group_number != None:
            self.__linked_group_indicator.remove()
            self.get_model().remove_class_gui_from_linked_group(self, self.__is_configuration_class)
                    
    def save_state(self):
        return super().save_state() | {"linked_group_number": self.__linked_group_number}
        
class GUIConnectionCorner(GUIBlock):
    def __init__(self, model, view, connection, x, y):
        actual_x, actual_y = convert_grid_coordinate_to_actual(view, x+0.5-CORNER_WIDTH/2, y+0.5-CORNER_HEIGHT/2)
        actual_width, actual_height = convert_grid_coordinate_to_actual(view, CORNER_WIDTH, CORNER_HEIGHT)
        self.__rect = view.get_canvas().create_rectangle(actual_x, actual_y, actual_x+actual_width, actual_y+actual_height, width=OUTLINE_WIDTH, outline=OUTLINE_COLOR, fill=CORNER_COLOR, tags=(TAG_CONNECTION_CORNER,))
        
        super().__init__(model, view, [self.__rect], x, y, CORNER_WIDTH, CORNER_HEIGHT, bind_left=MOUSE_DRAG)
        self.__connection = connection
        
    def left_dragged(self, event):
        allowed_movement_directions = self.__connection.allowed_corner_movement_directions(self)
        max_positive_move_x, max_negative_move_x, max_positive_move_y, max_negative_move_y = get_max_directions_movement(allowed_movement_directions)
        
        move_x, move_y = super().left_dragged(event, max_positive_move_x=max_positive_move_x, max_negative_move_x=max_negative_move_x, max_positive_move_y=max_positive_move_y, max_negative_move_y=max_negative_move_y)
        
        for adjacent_corner in self.__connection.get_adjacent_corners(self):
            adjacent_corner.move_block(move_x, move_y)
            
        self.__connection.adjust_lines_to_dragged_corners()
        
    def left_released(self, event):
        super().left_released(event, False)
        
        for adjacent_corner in self.__connection.get_adjacent_corners(self):
            adjacent_corner.snap_to_grid()
            
        self.__connection.adjust_lines_to_dragged_corners()
        
        self.get_view().update_shown_order()
        
    def open_options(self):
        self.__connection.open_options()
        
class NumberIndicator:
    def __init__(self, view, x, y, radius, color, outline_width, text):
        self.__view = view
        self.__x = x
        self.__y = y
        self.__radius = radius
        self.__color = color
        self.__outline_width = outline_width
        self.__circle = None
        self.__label = None
        
        self.create(text)
        
    def move(self, move_x, move_y):
        actual_move_x, actual_move_y = convert_grid_coordinate_to_actual(self.__view, move_x, move_y)
        
        self.__view.get_canvas().move(self.__circle, actual_move_x, actual_move_y)
        self.__view.get_canvas().move(self.__label, actual_move_x, actual_move_y)
        
    def scale(self, last_length_unit):
        circle_x1, circle_y1, circle_x2, circle_y2 = get_actual_coordinates_after_zoom(self.__view, self.__view.get_canvas().coords(self.__circle), last_length_unit)
        label_x, label_y = get_actual_coordinates_after_zoom(self.__view, self.__view.get_canvas().coords(self.__label), last_length_unit)
        
        self.__view.get_canvas().coords(self.__circle, circle_x1, circle_y1, circle_x2, circle_y2)
        self.__view.get_canvas().coords(self.__label, label_x, label_y)
        self.__view.get_canvas().itemconfig(self.__label, font=self.__view.get_updated_font(label=self.__label))
        
    def get_x(self):
        return self.__x
        
    def create(self, text):
        circle_radius = convert_grid_coordinate_to_actual(self.__view, self.__radius, 0)[0]
        actual_x, actual_y = convert_grid_coordinate_to_actual(self.__view, self.__x, self.__y)
        
        self.__circle = self.__view.get_canvas().create_oval(actual_x-circle_radius, actual_y-circle_radius, actual_x+circle_radius, actual_y+circle_radius, width=self.__outline_width, outline="black", fill=self.__color, tags=(TAG_INDICATOR,))
        self.__label = self.__view.get_canvas().create_text(actual_x, actual_y, text=text, font=FONT, tags=(TAG_INDICATOR_TEXT,))
        
    def remove(self):
        self.__view.get_canvas().delete(self.__circle)
        self.__view.get_canvas().delete(self.__label)
