import tkinter as tk
from config import *

class Options:
    def __init__(self, root, block):
        super().__init__()
        self.__root = root
        self.__block = block
        self.__window = tk.Toplevel(root)
        
        # self.__window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.__window.title("Options")
        self.__window.config(bg=BACKGROUND_COLOR)
        
    def get_block(self):
        return self.__block
        
    def get_window(self):
        return self.__window
        
    def add_entry(self, text):
        self.__entry_name_text = tk.StringVar()
        self.__entry_name_text.set(self.__block.get_name())
        
        self.add_label(0, 0, 1, text)
        
        entry_name = tk.Entry(self.__window, textvariable=self.__entry_name_text)
        entry_name.grid(row=0, column=1, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING)
        
        self.__entry_name_text.trace("w", self.update_block_name)
        
    def add_label(self, row, column, columnspan, text):
        label = tk.Label(self.__window, text=text, bg=BACKGROUND_COLOR)
        label.grid(row=row, column=column, columnspan=columnspan, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING)
        
    def add_delete_button(self, row, column, columnspan, to_delete):
        delete_button = tk.Button(self.__window, text="Delete", command=lambda: self.delete(to_delete))
        delete_button.grid(row=row, column=column, columnspan=columnspan, sticky=tk.W+tk.E)
        
    def update_block_name(self, *args):
        self.get_block().set_name(self.__entry_name_text.get())
        
    def delete(self, to_delete):
        to_delete.delete()
        self.__window.destroy()
        
class OptionsConfigurationClass(Options):
    def __init__(self, root, configuration_class_gui):
        super().__init__(root, configuration_class_gui)
        
        self.add_entry("Name:")
        self.add_delete_button(1, 0, 2, configuration_class_gui)
        
class OptionsSetupClass(Options):
    def __init__(self, model, setup_class_gui, configuration_class_gui, setup_view_names):
        super().__init__(model.get_root(), setup_class_gui)
        self.__model = model
        self.__setup_class_gui = setup_class_gui
        self.__configuration_class_gui = configuration_class_gui
        
        self.add_entry("Name:")
        
        self.add_label(0, 0, 1, "Add linked copy to setup view:")
        
        for i, setup_view_name in enumerate(setup_view_names):
            link_button = tk.Button(self.get_window(), text=setup_view_name, command=lambda i=i: self.create_linked_setup_class_gui(i))
            link_button.grid(row=1+(i//2), column=i%2, sticky=tk.W+tk.E)
            
        self.add_delete_button(1+int(len(setup_view_names)+0.5), 0, 2, setup_class_gui)
        
    def create_linked_setup_class_gui(self, setup_view_number):
        self.__model.create_linked_setup_class_gui(self.__setup_class_gui, self.__configuration_class_gui, setup_view_number)
        
class OptionsConfigurationAttribute(Options):
    def __init__(self, root, configuration_attribute_gui):
        super().__init__(root, configuration_attribute_gui)
        self.__configuration_attribute_gui = configuration_attribute_gui
        self.__value_type = tk.StringVar()
        self.__is_hidden = tk.BooleanVar()
        
        self.add_entry("Name:")
        
        self.add_label(1, 0, 2, "Type of value:")
        
        for i, value_type_symbol_and_text in enumerate(ACTIVE_VALUE_TYPE_SYMBOLS_CONFIGS):
            value_type_symbol, text = value_type_symbol_and_text
            
            radio_button = tk.Radiobutton(self.get_window(), text=text, variable=self.__value_type, value=value_type_symbol, command=self.set_value_type, bg=BACKGROUND_COLOR, width=OPTION_RADIO_BUTTON_CONFIGURATION_ATTRIBUTE_WIDTH, anchor="w")
            radio_button.grid(row=2+i, columnspan=2, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING, sticky=tk.W+tk.E)
            
        row_after_radio_buttons = 2 + len(ACTIVE_VALUE_TYPE_SYMBOLS_CONFIGS)
        self.add_label(row_after_radio_buttons, 0, 2, "")
        
        self.__hidden_toggle = tk.Checkbutton(self.get_window(), text="Hide", variable=self.__is_hidden, command=self.set_is_hidden)
        self.__hidden_toggle.grid(row=row_after_radio_buttons+1, columnspan=2, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING, sticky=tk.W+tk.E)
        
        self.add_delete_button(row_after_radio_buttons+2, 0, 2, configuration_attribute_gui)
        
        """
        calculation_inputs = attribute_block.get_calculation_inputs()
        
        self.__label_value = tk.Label(self.get_window(), text="Value:", bg=BACKGROUND_COLOR)
        self.__label_value.grid(row=1, column=0, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING)
        
        if len(calculation_inputs) == 0:
            self.__entry_value = tk.Entry(self.get_window())
            self.__entry_value.grid(row=1, column=1, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING)
            self.__entry_value.insert(0, "SOMETHING")
        """
        
    def set_value_type(self):
        self.__configuration_attribute_gui.set_value_type(self.__value_type.get())
        
    def set_is_hidden(self):
        self.__attribute_block.set_hidden(self.__is_hidden.get())
            
class OptionsCalculationInput(Options):
    def __init__(self, root, configuration_input):
        super().__init__(root, configuration_input)
        self.__calculation_type_choice = tk.StringVar()
        
        for i, config in enumerate(ACTIVE_CALCULATION_TYPE_SYMBOLS_CONFIGS):
            calculation_symbol, text = config
            
            radio_button = tk.Radiobutton(self.get_window(), text=text, variable=self.__calculation_type_choice, value=calculation_symbol, command=self.set_calculation_type, bg=BACKGROUND_COLOR, width=OPTION_RADIO_BUTTON_CONFIGURATION_INPUT_WIDTH, anchor="w")
            radio_button.grid(row=i, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING, sticky=tk.W+tk.E)
            
        row_after_radio_buttons = len(ACTIVE_CALCULATION_TYPE_SYMBOLS_CONFIGS)
        
        self.add_label(row_after_radio_buttons, 0, 1, "")
        self.add_delete_button(row_after_radio_buttons+1, 0, 1, configuration_input)
        
    def set_calculation_type(self):
        self.get_block().set_symbol_calculation_type(self.__calculation_type_choice.get())
        
class OptionsConnection(Options):
    def __init__(self, root, connection):
        super().__init__(root, None)
        self.__connection = connection
        self.__is_external = tk.BooleanVar()
        
        self.__external_toggle = tk.Checkbutton(self.get_window(), text="External connection", variable=self.__is_external, command=self.set_is_external)
        self.__external_toggle.grid(row=0, padx=OPTION_FIELDS_PADDING, pady=OPTION_FIELDS_PADDING, sticky=tk.W+tk.E)
        
        self.add_delete_button(1, 0, 1, self.__connection)
        
    def set_is_external(self):
        self.__connection.set_is_external(self.__is_external.get())
