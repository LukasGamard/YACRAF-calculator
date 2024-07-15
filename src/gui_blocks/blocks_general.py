import tkinter as tk
from options import OptionsConnection
from config import *

class GUIBlock:
    def __init__(self, model, view, pressable_items, x, y, width, height, *, bind_left=False, bind_right=False):
        self.__model = model
        self.__view = view
        self.__pressable_items = pressable_items
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        
        self.__picked_up = False
        self.__pick_up_offset = (0, 0)
        
        for pressable_item in pressable_items:
            if bind_left:
                view.get_canvas().tag_bind(pressable_item, MOUSE_LEFT, self.left_clicked)
                
            if bind_right:
                view.get_canvas().tag_bind(pressable_item, MOUSE_RIGHT, self.right_clicked)
            
    def left_clicked(self, event):
        self.__picked_up = not self.__picked_up
        
        if self.__picked_up:
            self.__pick_up_offset = (event.x//LENGTH_UNIT - self.__x, event.y//LENGTH_UNIT - self.__y)
        
    def right_clicked(self, event):
        pass
            
    def move_block(self, move_x, move_y):
        if move_x != 0 or move_y != 0:
            for pressable_item in self.__pressable_items:
                self.get_canvas().move(pressable_item, move_x*LENGTH_UNIT, move_y*LENGTH_UNIT)
            
            self.__x += move_x
            self.__y += move_y
            
    def move_if_picked_up(self, mouse_x, mouse_y):
        if self.__picked_up:
            move_x = mouse_x // LENGTH_UNIT - self.__pick_up_offset[0] - self.__x
            move_y = mouse_y // LENGTH_UNIT - self.__pick_up_offset[1] - self.__y
            
            self.move_block(move_x, move_y)
            
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
        
    def is_picked_up(self):
        return self.__picked_up
        
    def get_direction(self, mouse_x, mouse_y):
        direction = "RIGHT"
        
        if mouse_x - (self.get_x() + self.get_width()//2) * LENGTH_UNIT < 0:
            direction = "LEFT"
            
        return direction
        
    def delete(self):
        for pressable_items in self.__pressable_items:
            self.get_canvas().delete(pressable_items)
            
    def save_state(self):
        return {"x": self.__x, "y": self.__y}
        
class GUIModelingBlock(GUIBlock):
    def __init__(self, model, view, text, x, y, width, height, fill_color, *, bind_left=False, bind_right=False, has_value=False):
        canvas = view.get_canvas()
        self.__rect = canvas.create_rectangle(x*LENGTH_UNIT, y*LENGTH_UNIT, (x+width)*LENGTH_UNIT, (y+height)*LENGTH_UNIT, width=OUTLINE_WIDTH, outline=OUTLINE_COLOR, fill=fill_color)
        self.__entry_value = None
        
        if has_value:
            self.__label_text = canvas.create_text(x*LENGTH_UNIT+(width/2*LENGTH_UNIT)//2, y*LENGTH_UNIT+(height*LENGTH_UNIT)//2, text=text)
            self.__label_value = canvas.create_text(x*LENGTH_UNIT+(width*3/2*LENGTH_UNIT)//2, y*LENGTH_UNIT+(height*LENGTH_UNIT)//2, text="-")
            
            self.__entry_text = tk.StringVar()
            self.__entry_text.set("Value")
        else:
            self.__label_text = canvas.create_text(x*LENGTH_UNIT+(width*LENGTH_UNIT)//2, y*LENGTH_UNIT+(height*LENGTH_UNIT)//2, text=text)
            
        pressable_items = [self.__rect, self.__label_text]
        
        if has_value:
            pressable_items.append(self.__label_value)
            
        super().__init__(model, view, pressable_items, x, y, width, height, bind_left=bind_left, bind_right=bind_right)
        self.__text = text
        self.__has_value = has_value
        self.__attached_blocks = []
        
        if has_value:
            self.enable_value_entry()
            
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        for block in self.__attached_blocks:
            if block != self:
                block.move_block(move_x, move_y)
                
        if self.__has_value:
            if self.__entry_value != None:
                current_x = self.__entry_value.winfo_x()
                current_y = self.__entry_value.winfo_y()
                self.__entry_value.place(x=move_x*LENGTH_UNIT+current_x, y=move_y*LENGTH_UNIT+current_y)
                
    def is_adjacent(self, coordinates):
        for coordinate in coordinates:
            for i in range(self.get_height()):
                # Left
                if coordinate == (self.get_x() - 1, self.get_y() + i):
                    return True, "LEFT"
                    
                # Right
                elif coordinate == (self.get_x() + self.get_width(), self.get_y() + i):
                    return True, "RIGHT"
                    
        return False, ""
        
    def get_text(self):
        return self.__text
        
    def set_text(self, text, space_from_end_to_break=1):
        self.__text = text
        self.get_canvas().itemconfig(self.__label_text, text=text)
        
    def enable_value_label(self):
        if self.__entry_value != None:
            self.__entry_value.destroy()
            self.__entry_value = None
            
    def enable_value_entry(self):
        if self.__entry_value == None:
            self.__entry_value = tk.Entry(self.get_view(), textvariable=self.__entry_text)
            self.__entry_value.place(x=self.get_x()*LENGTH_UNIT+(self.get_width()*LENGTH_UNIT)//2, y=self.get_y()*LENGTH_UNIT+OUTLINE_WIDTH, width=(self.get_width()*LENGTH_UNIT)//2, height=self.get_height()*LENGTH_UNIT-OUTLINE_WIDTH*2)
            
    def get_entered_value(self):
        if self.__has_value and self.__entry_value != None:
            return self.__entry_text.get()
            
        return None
        
    def set_displayed_value(self, value):
        # Set value in Label
        if self.__entry_value == None:
            self.get_canvas().itemconfig(self.__label_value, text=str(value))
            
        # Set value in Entry
        else:
            self.__entry_value.delete(0, "end")
            self.__entry_value.insert(0, str(value))
            
    def add_attached_block(self, block):
        self.__attached_blocks.append(block)
        
    def remove_attached_block(self, block):
        self.__attached_blocks.remove(block)
    
    def delete(self):
        super().delete()
        
        for attached_block in self.__attached_blocks:
            attached_block.delete()
            
        if self.__entry_value != None:
            self.__entry_value.destroy()
            
class GUIConnectionCorner(GUIBlock):
    def __init__(self, model, view, connection, x, y):
        actual_x = (x + 0.5 - CORNER_WIDTH / 2) * LENGTH_UNIT
        actual_y = (y + 0.5 - CORNER_HEIGHT / 2) * LENGTH_UNIT
        self.__rect = view.get_canvas().create_rectangle(actual_x, actual_y, actual_x+CORNER_WIDTH*LENGTH_UNIT, actual_y+CORNER_HEIGHT*LENGTH_UNIT, width=OUTLINE_WIDTH, outline=OUTLINE_COLOR, fill=CORNER_COLOR)
        
        super().__init__(model, view, [self.__rect], x, y, CORNER_WIDTH, CORNER_HEIGHT, bind_left=True, bind_right=True)
        self.__connection = connection
        
    def left_clicked(self, event):
        pass
        """
        if self.is_picked_up():
            self.get_view().set_moving_connection_corner(self)
        else:
            self.get_view().reset_moving_connection_corner()
        """
        
    def right_clicked(self, event):
        OptionsConnection(self.get_model().get_root(), self.__connection)
        
    def move_block(self, move_x, move_y):
        for pressable_item in self.__pressable_items:
            self.get_canvas().move(pressable_item, move_x*LENGTH_UNIT, move_y*LENGTH_UNIT)
            
        self.__x += move_x
        self.__y += move_y
