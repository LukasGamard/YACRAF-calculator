from blocks_general import GUIBlock
from config import *

class GUIBlockButton(GUIBlock):
    def __init__(self, model, view, text, x, y, width, height, fill_color):
        canvas = view.get_canvas()
        self.__rect = canvas.create_rectangle(x*LENGTH_UNIT, y*LENGTH_UNIT, (x+width)*LENGTH_UNIT, (y+height)*LENGTH_UNIT, width=OUTLINE_WIDTH, outline=OUTLINE_COLOR, fill=fill_color)
        self.__label = canvas.create_text(x*LENGTH_UNIT+(width*LENGTH_UNIT)//2, y*LENGTH_UNIT+(height*LENGTH_UNIT)//2, text=text)
        
        super().__init__(model, view, [self.__rect, self.__label], x, y, CHANGE_VIEW_WIDTH, CHANGE_VIEW_HEIGHT, bind_left=True, bind_right=False)
        
    def left_clicked(self, event):
        pass
        
    def set_text(self, text):
        self.__text = text
        self.get_canvas().itemconfig(self.__label, text=text)
        
    def delete(self):
        self.get_canvas().delete(self.__rect)
        self.get_canvas().delete(self.__label)

class GUIAddAttributeButton(GUIBlockButton):
    def __init__(self, model, view, x, y, configuration_class_gui):
        super().__init__(model, view, "+", x, y, ADD_WIDTH, ADD_HEIGHT, ADD_COLOR)
        self.__configuration_class_gui = configuration_class_gui
        
    def left_clicked(self, event):
        self.__configuration_class_gui.create_attribute()
        
class GUISaveButton(GUIBlockButton):
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "Save", x, y, SAVE_WIDTH, SAVE_HEIGHT, SAVE_COLOR)
        
    def left_clicked(self, event):
        self.get_model().save()
        
class GUIChangeViewButton(GUIBlockButton):
    def __init__(self, model, view, x, y, view_name, view_to_change_to):
        if view == view_to_change_to:
            color = CHANGE_VIEW_SELECTED_COLOR
        else:
            color = CHANGE_VIEW_COLOR
            
        super().__init__(model, view, view_name, x, y, CHANGE_VIEW_WIDTH, CHANGE_VIEW_HEIGHT, color)
        self.__view_to_change_to = view_to_change_to
        
    def left_clicked(self, event):
        self.get_model().change_view(self.__view_to_change_to)

class GUIAddConfigurationClassButton(GUIBlockButton):
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "Add class", x, y, ADD_CLASS_WIDTH, ADD_CLASS_HEIGHT, ADD_CLASS_COLOR)
        
    def left_clicked(self, event):
        self.get_view().create_configuration_class_gui()
        
class GUIAddToSetupButton(GUIBlockButton):
    def __init__(self, model, view, x, y, configuration_class_gui):
        super().__init__(model, view, f"Add {configuration_class_gui.get_name()}", x, y, ADD_TO_SETUP_WIDTH, ADD_TO_SETUP_HEIGHT, ADD_TO_SETUP_COLOR)
        self.__configuration_class_gui = configuration_class_gui
        
        configuration_class_gui.add_to_setup_button(self)
        
    def left_clicked(self, event):
        self.get_view().create_setup_class_gui(self.__configuration_class_gui)
        
class GUIAddInputButton(GUIBlockButton):
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "Add input", x, y, ADD_INPUT_WIDTH, ADD_INPUT_HEIGHT, ADD_INPUT_COLOR)
        
    def left_clicked(self, event):
        self.get_view().create_configuration_input_gui()
        
class GUICalculateValuesButton(GUIBlockButton):
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "Calculate", x, y, CALCULATE_VALUES_WIDTH, CALCULATE_VALUES_HEIGHT, CALCULATE_VALUES_COLOR)
        
    def left_clicked(self, event):
        self.get_view().calculate_values()
        
class GUIAddConnectionButton(GUIBlockButton):
    def __init__(self, model, view, x, y):
        super().__init__(model, view, "Connection", x, y, ADD_CONNECTION_WIDTH, ADD_CONNECTION_HEIGHT, ADD_CONNECTION_COLOR)
        
    def left_clicked(self, event):
        self.get_view().create_connection_with_blocks()
