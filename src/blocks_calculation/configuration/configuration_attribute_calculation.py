from config import *

class ConfigurationAttribute:
    def __init__(self, name, configuration_class):
        self.__name = name
        self.__configuration_class = configuration_class
        self.__symbol_value_type = None
        self.__symbol_calculation_type = None
        self.__input_configuration_attributes = {} # Key: input_configuration_attribute, Value: is_internal
        self.__input_scalar = DEFAULT_INPUT_SCALAR
        self.__is_hidden = False
        
    def get_name(self):
        return self.__name
        
    def set_name(self, name):
        self.__name = name
        
    def get_configuration_class(self):
        return self.__configuration_class
        
    def get_symbol_value_type(self):
        return self.__symbol_value_type
        
    def set_symbol_value_type(self, symbol_value_type):
        self.__symbol_value_type = symbol_value_type
        
    def get_symbol_calculation_type(self):
        return self.__symbol_calculation_type
        
    def set_symbol_calculation_type(self, symbol_calculation_type):
        self.__symbol_calculation_type = symbol_calculation_type
        
    def get_input_configuration_attributes(self):
        return self.__input_configuration_attributes
        
    def has_input_configuration_attributes(self):
        return len(self.__input_configuration_attributes) > 0
        
    def add_input_configuration_attribute(self, input_configuration_attribute, is_internal):
        self.__input_configuration_attributes[input_configuration_attribute] = is_internal
        
    def remove_input_configuration_attribute(self, input_configuration_attribute):
        self.__input_configuration_attributes.pop(input_configuration_attribute)
        
    def get_input_scalar(self):
        return self.__input_scalar
        
    def set_input_scalar(self, input_scalar):
        self.__input_scalar = input_scalar
        
    def reset_input_scalar(self):
        self.__input_scalar = DEFAULT_INPUT_SCALAR
        
    def is_hidden(self):
        return self.__is_hidden
        
    def set_hidden(self, is_hidden):
        self.__is_hidden = is_hidden
