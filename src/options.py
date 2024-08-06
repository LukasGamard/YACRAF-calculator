import tkinter as tk
from config import *

class Options:
    def __init__(self, root, to_configure):
        super().__init__()
        self.__root = root
        self.__to_configure = to_configure
        self.__window = tk.Toplevel(root)
        
        # self.__window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.__window.title("Options")
        self.__window.config(bg=BACKGROUND_COLOR)
        
    def get_to_configure(self):
        return self.__to_configure
        
    def get_window(self):
        return self.__window
        
    def add_name_entry(self, text):
        self.__entry_name_text = tk.StringVar()
        self.__entry_name_text.set(self.__to_configure.get_name())
        
        self.add_label(0, 0, 1, text)
        
        entry_name = tk.Entry(self.__window, textvariable=self.__entry_name_text, font=FONT)
        entry_name.grid(row=0, column=1, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING)
        
        self.__entry_name_text.trace("w", lambda *args: self.set_name(self.__entry_name_text.get()))
        
    def add_label(self, row, column, columnspan, text):
        label = tk.Label(self.__window, text=text, font=FONT, bg=BACKGROUND_COLOR)
        label.grid(row=row, column=column, columnspan=columnspan, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING)
        
    def add_swap_buttons(self, row, column, columnspan):
        move_up_button = tk.Button(self.__window, text="Move up", font=FONT, command=lambda: self.move(True))
        move_up_button.grid(row=row, column=column, columnspan=columnspan, sticky=tk.W+tk.E)
        
        move_down_button = tk.Button(self.__window, text="Move down", font=FONT, command=lambda: self.move(False))
        move_down_button.grid(row=row+1, column=column, columnspan=columnspan, sticky=tk.W+tk.E)
        
    def add_delete_button(self, row, column, columnspan, to_delete):
        delete_button = tk.Button(self.__window, text="Delete", font=FONT, command=lambda: self.delete(to_delete))
        delete_button.grid(row=row, column=column, columnspan=columnspan, sticky=tk.W+tk.E)
        
    def add_scalar_entry(self, row, label_text, entry_text):
        self.__entry_scalar_text = tk.StringVar()
        self.__entry_scalar_text.set(entry_text)
        
        self.add_label(row, 0, 1, label_text)
        
        entry_scalar = tk.Entry(self.get_window(), textvariable=self.__entry_scalar_text, font=FONT)
        entry_scalar.grid(row=row, column=1, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING)
        
        self.__entry_scalar_text.trace("w", lambda *args: self.set_scalar(self.__entry_scalar_text.get()))
        
    def set_name(self, name):
        self.__to_configure.set_name(name)
        
    def move(self, up):
        pass
        
    def delete(self, to_delete):
        if to_delete != None:
            to_delete.delete()
            
        self.__window.destroy()
        
class OptionsView(Options):
    def __init__(self, model, view):
        super().__init__(model.get_root(), view)
        self.__model = model
        self.__view = view
        
        self.add_name_entry("Name:")
        self.add_label(1, 0, 2, "Move view button:")
        self.add_swap_buttons(2, 0, 2)
        self.add_delete_button(4, 0, 2, None)
        
    def move(self, up):
        self.__model.swap_view_places(self.__view, up)
        
    def delete(self, to_delete):
        super().delete(to_delete)
        self.__model.delete_view(self.__view)
        
class OptionsConfigurationClass(Options):
    def __init__(self, model, configuration_class_gui, configuration_views):
        super().__init__(model.get_root(), configuration_class_gui)
        self.__model = model
        self.__configuration_class_gui = configuration_class_gui
        
        self.add_name_entry("Name:")
        
        self.add_label(1, 0, 2, "Add linked copy to setup view:")
        
        for i, configuration_view in enumerate(configuration_views):
            link_button = tk.Button(self.get_window(), text=configuration_view.get_name(), font=FONT, command=lambda configuration_view=configuration_view: self.create_linked_configuration_class_gui(configuration_view))
            link_button.grid(row=2+i, columnspan=2, sticky=tk.W+tk.E)
            
        row_after_link_buttons = 2 + len(configuration_views)
        
    def create_linked_configuration_class_gui(self, configuration_view):
        self.__model.create_linked_configuration_class_gui(self.__configuration_class_gui, configuration_view)
        
class OptionsConfigurationAttribute(Options):
    def __init__(self, root, configuration_class_gui, configuration_attribute_gui):
        super().__init__(root, configuration_attribute_gui)
        self.__configuration_class_gui = configuration_class_gui
        self.__configuration_attribute_gui = configuration_attribute_gui
        self.__value_type = tk.StringVar()
        self.__is_hidden = tk.BooleanVar()
        
        symbol_value_type = configuration_attribute_gui.get_configuration_attribute().get_symbol_value_type()
        
        if symbol_value_type == None:
            symbol_value_type = ""
            
        self.__value_type.set(symbol_value_type)
        self.__is_hidden.set(configuration_attribute_gui.is_hidden())
        
        self.add_name_entry("Name:")
        self.add_swap_buttons(1, 0, 2)
        
        self.add_label(3, 0, 2, "Type of value:")
        
        for i, value_type_symbol_and_text in enumerate(ACTIVE_VALUE_TYPE_SYMBOLS_CONFIGS):
            value_type_symbol, text = value_type_symbol_and_text
            
            radio_button = tk.Radiobutton(self.get_window(), text=text, font=FONT, variable=self.__value_type, value=value_type_symbol, command=self.set_value_type, bg=BACKGROUND_COLOR, width=OPTION_RADIO_BUTTON_CONFIGURATION_ATTRIBUTE_WIDTH, anchor="w")
            radio_button.grid(row=4+i, columnspan=2, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING, sticky=tk.W+tk.E)
            
        row_after_radio_buttons = 5 + len(ACTIVE_VALUE_TYPE_SYMBOLS_CONFIGS)
        self.__hidden_toggle = tk.Checkbutton(self.get_window(), text="Hide from setup views", font=FONT, variable=self.__is_hidden, command=self.set_is_hidden)
        self.__hidden_toggle.grid(row=row_after_radio_buttons, columnspan=2, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING, sticky=tk.W+tk.E)
        
    def move(self, up):
        self.__configuration_class_gui.swap_attribute_places(self.__configuration_attribute_gui, up)
        
    def set_value_type(self):
        symbol_value_type = self.__value_type.get()
        
        if symbol_value_type == "":
            symbol_value_type = None
            
        self.__configuration_attribute_gui.set_value_type(symbol_value_type)
        
    def set_is_hidden(self):
        self.__configuration_attribute_gui.set_hidden(self.__is_hidden.get())
            
class OptionsCalculationInput(Options):
    def __init__(self, root, configuration_input):
        super().__init__(root, configuration_input)
        self.__calculation_type_choice = tk.StringVar()
        
        self.__calculation_type_choice.set(configuration_input.get_symbol_calculation_type())
        
        for i, config in enumerate(ACTIVE_CALCULATION_TYPE_SYMBOLS_CONFIGS):
            calculation_symbol, text = config
            
            radio_button = tk.Radiobutton(self.get_window(), text=text, font=FONT, variable=self.__calculation_type_choice, value=calculation_symbol, command=self.set_calculation_type, bg=BACKGROUND_COLOR, width=OPTION_RADIO_BUTTON_CONFIGURATION_INPUT_WIDTH, anchor="w")
            radio_button.grid(row=i, columnspan=2, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING, sticky=tk.W+tk.E)
            
        row_after_radio_buttons = len(ACTIVE_CALCULATION_TYPE_SYMBOLS_CONFIGS)
        
        attached_configuration_attribute_gui = self.get_to_configure().get_attached_configuration_attribute_gui()
        
        if attached_configuration_attribute_gui != None:
            entry_text = attached_configuration_attribute_gui.get_configuration_attribute().get_input_scalar()
        else:
            entry_text = 1
            
        self.add_scalar_entry(row_after_radio_buttons, "Scalar (float):", entry_text)
        
    def set_calculation_type(self):
        self.get_to_configure().set_symbol_calculation_type(self.__calculation_type_choice.get())
        
    def set_scalar(self, input_scalar):
        try:
            input_scalar = float(input_scalar)
        except:
            input_scalar = 1
            
        self.get_to_configure().set_input_scalar(float(input_scalar))
        
class OptionsSetupClass(Options):
    def __init__(self, model, setup_class_gui, configuration_class_gui, setup_views):
        super().__init__(model.get_root(), setup_class_gui)
        self.__model = model
        self.__setup_class_gui = setup_class_gui
        self.__configuration_class_gui = configuration_class_gui
        # self.__is_connected_to_all = tk.BooleanVar()
        
        # self.__is_connected_to_all.set(False)
        
        self.add_name_entry("Name:")
        
        self.add_label(1, 0, 2, "Add linked copy to setup view:")
        
        for i, setup_view in enumerate(setup_views):
            link_button = tk.Button(self.get_window(), text=setup_view.get_name(), font=FONT, command=lambda setup_view=setup_view: self.create_linked_setup_class_gui(setup_view))
            link_button.grid(row=2+i, columnspan=2, sticky=tk.W+tk.E)
            
        row_after_radio_buttons = 2 + len(setup_views)
        
        # self.__connect_all_toggle = tk.Checkbutton(self.get_window(), text="Connect to all blocks in view", font=FONT, variable=self.__is_connected_to_all, command=self.connect_to_all)
        # self.__connect_all_toggle.grid(row=row_after_radio_buttons, columnspan=2, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING, sticky=tk.W+tk.E)
        
    def create_linked_setup_class_gui(self, setup_view):
        self.__model.create_linked_setup_class_gui(self.__setup_class_gui, self.__configuration_class_gui, setup_view)
        
    def connect_to_all(self):
        pass
        
class OptionsConnection(Options):
    def __init__(self, root, connection):
        super().__init__(root, None)
        self.__connection = connection
        self.__is_external = tk.BooleanVar()
        
        self.__is_external.set(connection.is_external())
        
        self.__external_toggle = tk.Checkbutton(self.get_window(), text="External connection", font=FONT, variable=self.__is_external, command=self.set_is_external)
        self.__external_toggle.grid(row=0, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING, sticky=tk.W+tk.E)
        
    def set_is_external(self):
        self.__connection.set_external(self.__is_external.get())
        
class OptionsConnectionWithBlocks(Options):
    def __init__(self, root, connection):
        super().__init__(root, None)
        self.__connection = connection
        
        entry_text = connection.get_input_scalars_string()
        
        if entry_text == None:
            entry_text = DEFAULT_INPUT_SCALAR
        
        self.add_scalar_entry(0, "Scalar (float or a / b / c:", entry_text)
        
    def set_scalar(self, input_scalars):
        final_input_scalars = []
        
        try:
            for input_scalar in input_scalars.split("/"):
                final_input_scalars.append(float(input_scalar.strip()))
                
        except:
            final_input_scalars = None
            
        self.__connection.set_input_scalars(final_input_scalars)
