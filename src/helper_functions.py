from config import *

def convert_grid_coordinate_to_actual(view, grid_x, grid_y, length_unit=None):
    if length_unit == None:
        length_unit = view.get_length_unit()
        
    actual_x = round(grid_x * length_unit, 3)
    actual_y = round(grid_y * length_unit, 3)
    
    return actual_x, actual_y
    
def convert_actual_coordinate_to_grid(view, actual_x, actual_y, length_unit=None):
    if length_unit == None:
        length_unit = view.get_length_unit()
        
    grid_x = round(actual_x / length_unit, 3)
    grid_y = round(actual_y / length_unit, 3)
    
    return grid_x, grid_y
    
def get_actual_coordinates_after_zoom(view, actual_coordinates_before_zoom, last_length_unit):
    adjusted_actual_coordinates = []
    
    for i in range(0, len(actual_coordinates_before_zoom), 2):
        previous_actual_x = actual_coordinates_before_zoom[i]
        previous_actual_y = actual_coordinates_before_zoom[i+1]
        
        grid_x, grid_y = convert_actual_coordinate_to_grid(view, previous_actual_x, previous_actual_y, last_length_unit)
        
        for value in convert_grid_coordinate_to_actual(view, grid_x, grid_y):
            adjusted_actual_coordinates.append(value)
            
    return adjusted_actual_coordinates
    
def distance_to_closest_grid_intersection(view, grid_x, grid_y):
    grid_offset_x, grid_offset_y = view.get_grid_offset()
    
    grid_distance_x = round(int(grid_x + 0.5 - grid_offset_x) - grid_x + grid_offset_x, 3)
    grid_distance_y = round(int(grid_y + 0.5 - grid_offset_y) - grid_y + grid_offset_y, 3)
    
    if grid_x <= -0.5:
        grid_distance_x -= 1
        
    if grid_y <= -0.5:
        grid_distance_y -= 1
    
    return grid_distance_x, grid_distance_y
    
def get_grid_mid_x(view, grid_x):
    grid_offset_x, _ = view.get_grid_offset()
    
    grid_mid_x = round(int(grid_x - grid_offset_x + 0.5) + grid_offset_x, 3)
    
    return grid_mid_x
    
def get_grid_mid_y(view, grid_y):
    _, grid_offset_y = view.get_grid_offset()
    
    grid_mid_y = round(int(grid_y - grid_offset_y + 0.5) + grid_offset_y, 3)
    
    return grid_mid_y
    
def get_triangle_coordinates(view, x, y, direction):
    upper_left = [x, y]
    upper_right = [x+CONNECTION_END_WIDTH, y]
    lower_left = [x, y+CONNECTION_END_HEIGHT]
    lower_right = [x+CONNECTION_END_WIDTH, y+CONNECTION_END_HEIGHT]
    
    if direction == "UP":
        coordinates = [x+CONNECTION_END_WIDTH/2, y] + lower_right + lower_left
    elif direction == "RIGHT":
        coordinates = upper_left + [x+CONNECTION_END_WIDTH, y+CONNECTION_END_HEIGHT/2] + lower_left
    elif direction == "DOWN":
        coordinates = upper_left + upper_right + [x+CONNECTION_END_WIDTH/2, y+CONNECTION_END_HEIGHT]
    elif direction == "LEFT":
        coordinates = upper_right + lower_right + [x, y+CONNECTION_END_HEIGHT/2]
        
    actual_coordinates = []
    
    for i in range(0, len(coordinates), 2):
        actual_x, actual_y = convert_grid_coordinate_to_actual(view, coordinates[i], coordinates[i+1])
        actual_coordinates += [actual_x, actual_y]
        
    return actual_coordinates
    
def swap_attribute_places(index_to_move, move_up, attributes_gui, attributes):
    if move_up and index_to_move > 0:
        attributes_gui[index_to_move].move_block(0, -ATTRIBUTE_HEIGHT)
        attributes_gui[index_to_move-1].move_block(0, ATTRIBUTE_HEIGHT)
        
        attributes_gui[index_to_move], attributes_gui[index_to_move-1] = attributes_gui[index_to_move-1], attributes_gui[index_to_move]
        attributes[index_to_move], attributes[index_to_move-1] = attributes[index_to_move-1], attributes[index_to_move]
        
    elif not move_up and index_to_move < len(attributes_gui) - 1:
        attributes_gui[index_to_move].move_block(0, ATTRIBUTE_HEIGHT)
        attributes_gui[index_to_move+1].move_block(0, -ATTRIBUTE_HEIGHT)
        
        attributes_gui[index_to_move], attributes_gui[index_to_move+1] = attributes_gui[index_to_move+1], attributes_gui[index_to_move]
        attributes[index_to_move], attributes[index_to_move+1] = attributes[index_to_move+1], attributes[index_to_move]
        
def delete_all(to_delete_list):
    for i in range(len(to_delete_list)-1, -1, -1):
        to_delete_list[i].delete()
