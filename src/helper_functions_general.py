import numpy as np
import tkinter.font as tkfont

def convert_value_to_string(value):
    """
    Takes a NumPy array or list as input and converts it to a string
    """
    if not isinstance(value, (np.ndarray, list)):
        print(f"Error: Could not convert {value} to string")
        return None
        
    final_value = []
    
    for element in value:
        rounded_value = round(float(element), 3)
        
        # If the float does not have any decimal numbers, convert it to an integer for a better looking output
        if rounded_value == int(rounded_value):
            rounded_value = int(rounded_value)
            
        final_value.append(str(rounded_value))
        
    return " / ".join(final_value)
    
def convert_string_to_value(string):
    """
    Takes a string as input and converts it to a list of floats
    """
    return [float(element.strip()) for element in string.split("/")]
    
def convert_grid_coordinate_to_actual(grid_x, grid_y, length_unit):
    """
    Converts/scales a coordinate in the grid to one based on pixels
    """
    actual_x = round(grid_x * length_unit, 3)
    actual_y = round(grid_y * length_unit, 3)
    
    return actual_x, actual_y
    
def convert_actual_coordinate_to_grid(actual_x, actual_y, length_unit):
    """
    Converts/scales a coordinate based on pixels to one based on the grid
    """
    grid_x = round(actual_x / length_unit, 3)
    grid_y = round(actual_y / length_unit, 3)
    
    return grid_x, grid_y
    
def get_actual_coordinates_after_scale(actual_coordinates_before_scale, new_length_unit, last_length_unit):
    """
    actual_coordinates_before_scale: A sequence of x and y values (for example, a tuple (x1, y1, x2, y2)) before the coordinate was scaled
    new_length_unit: The length unit before the scaling
    last_length_unit: The length unit after the scaling
    
    Converts the pixel values before scaling (such as zooming a view) to the corresponding ones after the scaling
    """
    adjusted_actual_coordinates = []
    
    for i in range(0, len(actual_coordinates_before_scale), 2):
        previous_actual_x = actual_coordinates_before_scale[i]
        previous_actual_y = actual_coordinates_before_scale[i+1]
        
        # Convert to grid coordinates using the length unit before the scaling
        previous_grid_x, previous_grid_y = convert_actual_coordinate_to_grid(previous_actual_x, previous_actual_y, last_length_unit)
        
        # Convert the grid coordinates back to pixel coordinates using the new length unit after the zoom
        for value in convert_grid_coordinate_to_actual(previous_grid_x, previous_grid_y, new_length_unit):
            adjusted_actual_coordinates.append(value)
            
    return adjusted_actual_coordinates
    
def distance_to_closest_grid_intersection(view, grid_x, grid_y):
    """
    Find the distance from a grid coordinate to the closest grid intersection considering the offset of the grid due to panning/zooming
    The x and y distances are in the range [-0.5, 0.5)
    """
    grid_offset_x, grid_offset_y = view.get_grid_offset()
    
    grid_distance_x = round(int(grid_x + 0.5 - grid_offset_x) - grid_x + grid_offset_x, 3)
    grid_distance_y = round(int(grid_y + 0.5 - grid_offset_y) - grid_y + grid_offset_y, 3)
    
    if grid_x <= -0.5:
        grid_distance_x -= 1
        
    if grid_y <= -0.5:
        grid_distance_y -= 1
        
    return grid_distance_x, grid_distance_y
    
def get_grid_mid_x(view, grid_x):
    """
    Get the x coordinate in the middle of the current grid square considering the offset of the grid due to panning/zooming
    """
    grid_offset_x, _ = view.get_grid_offset()
    
    grid_mid_x = round(int(grid_x - grid_offset_x + 0.5) + grid_offset_x, 3)
    
    return grid_mid_x
    
def get_grid_mid_y(view, grid_y):
    """
    Get the y cooridinate in the middle of the current grid square considering the offset of the grid due to panning/zooming
    """
    _, grid_offset_y = view.get_grid_offset()
    
    grid_mid_y = round(int(grid_y - grid_offset_y + 0.5) + grid_offset_y, 3)
    
    return grid_mid_y
    
def get_triangle_coordinates(view, x, y, direction):
    """
    Returns the corner coordinates of a triangle based on the direction which the triangle should point in
    """
    from config import CONNECTION_END_WIDTH, CONNECTION_END_HEIGHT
    
    # default coordinates for each corner in a square
    upper_left = [x, y]
    upper_right = [x+CONNECTION_END_WIDTH, y]
    lower_left = [x, y+CONNECTION_END_HEIGHT]
    lower_right = [x+CONNECTION_END_WIDTH, y+CONNECTION_END_HEIGHT]
    
    # Combine two of the corners from a square with the point of the triangle that points in the specified direction
    if direction == "UP":
        coordinates = [x+CONNECTION_END_WIDTH/2, y] + lower_right + lower_left
    elif direction == "RIGHT":
        coordinates = upper_left + [x+CONNECTION_END_WIDTH, y+CONNECTION_END_HEIGHT/2] + lower_left
    elif direction == "DOWN":
        coordinates = upper_left + upper_right + [x+CONNECTION_END_WIDTH/2, y+CONNECTION_END_HEIGHT]
    elif direction == "LEFT":
        coordinates = upper_right + lower_right + [x, y+CONNECTION_END_HEIGHT/2]
        
    # Convert the grid coordinates to pixel coordinates
    actual_coordinates = []
    
    for i in range(0, len(coordinates), 2):
        actual_x, actual_y = convert_grid_coordinate_to_actual(coordinates[i], coordinates[i+1], view.get_length_unit())
        actual_coordinates += [actual_x, actual_y]
        
    return actual_coordinates
    
def get_max_directions_movement(allowed_movement_directions):
    """
    allowed_movement_directions: A list of directions that a block cannot move in
    
    Returns a list of the maximum distance a block can move in any direction, where None means no limit
    """
    max_positive_move_x, max_negative_move_x, max_positive_move_y, max_negative_move_y = [None] * 4
    
    if "RIGHT" not in allowed_movement_directions:
        max_positive_move_x = 0
        
    if "LEFT" not in allowed_movement_directions:
        max_negative_move_x = 0
        
    if "DOWN" not in allowed_movement_directions:
        max_positive_move_y = 0
        
    if "UP" not in allowed_movement_directions:
        max_negative_move_y = 0
        
    return max_positive_move_x, max_negative_move_x, max_positive_move_y, max_negative_move_y
    
def get_font(length_unit, *, canvas_and_label=None, has_line_break=False):
    """
    canvas_and_label: Tuple (canvas, label)
    has_line_break: Whether the text should line break
    
    Returns the font size that should be used in a text field on the canvas given considering the current scaling (zoom) level and whether there is a line break (need to lower font size further)
    """
    from config import LENGTH_UNIT, FONT, FONT_DECREASE_LINE_BREAK
    
    new_font_size = int(FONT[1] * length_unit / LENGTH_UNIT + 0.5)
    
    if has_line_break:
        new_font_size -= FONT_DECREASE_LINE_BREAK
        
    if new_font_size < 1:
        new_font_size = 1
        
    if canvas_and_label == None:
        return (FONT[0], new_font_size)
        
    canvas, label = canvas_and_label
    
    # Get existing attributes of the font
    current_font = canvas.itemcget(label, "font").split()
    
    if len(current_font) == 2:
        updated_font = (current_font[0], new_font_size)
        
    elif len(current_font) == 3:
        updated_font = (current_font[0], new_font_size, current_font[2])
        
    else:
        print(f"Error: Found font {current_font}")
        
    return updated_font
    
def delete_all(to_delete_list, manual_delete=False):
    """
    Calls the delete method of all elements in to_delete_list
    """
    from configuration_attribute_gui import GUIConfigurationAttribute
    from connection_blocks_gui import GUIConnectionCorner, GUIConnectionScalarsIndicator
    
    for i in range(len(to_delete_list)-1, -1, -1):
        if manual_delete and isinstance(to_delete_list[i], (GUIConfigurationAttribute, GUIConnectionCorner, GUIConnectionScalarsIndicator)):
            to_delete_list[i].delete(True)
        else:
            to_delete_list[i].delete()
