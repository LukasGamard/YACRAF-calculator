from helper_functions_general import convert_grid_coordinate_to_actual, get_actual_coordinates_after_zoom
from config import *

class GUICircleIndicator:
    """
    Indicator/marker that is shown as a circle
    """
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
        """
        Moves the indicator on the canvas
        """
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
        """
        Draws the indicator on the canvas
        """
        circle_radius = convert_grid_coordinate_to_actual(self.__view, self.__radius, 0)[0]
        actual_x, actual_y = convert_grid_coordinate_to_actual(self.__view, self.__x, self.__y)
        
        self.__circle = self.__view.get_canvas().create_oval(actual_x-circle_radius, actual_y-circle_radius, actual_x+circle_radius, actual_y+circle_radius, width=self.__outline_width, outline="black", fill=self.__color, tags=(TAG_INDICATOR,))
        self.__label = self.__view.get_canvas().create_text(actual_x, actual_y, text=text, font=FONT, tags=(TAG_INDICATOR_TEXT,))
        
    def remove(self):
        """
        Removed the indicator from the canvas
        """
        self.__view.get_canvas().delete(self.__circle)
        self.__view.get_canvas().delete(self.__label)
