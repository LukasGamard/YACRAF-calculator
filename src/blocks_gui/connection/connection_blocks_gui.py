from general_gui import GUIBlock, GUIModelingBlock
from helper_functions_general import convert_grid_coordinate_to_actual, get_triangle_coordinates, get_max_directions_movement
from config import *

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
        
    def delete(self, manual_delete=False):
        if not self.is_deleted():
            super().delete()
            
            if manual_delete:
                self.__connection.delete()
                
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
                
        self.__connection.correct_scalars_indicator_location()
        
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
        
    def delete(self, manual_delete=False):
        super().delete()
        
        if manual_delete:
            self.__connection.reset_input_scalars()
