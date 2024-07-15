from calculations_setup import SetupClass

class ConfigurationClass:
    def __init__(self, name):
        self.__name = name
        self.__configuration_attributes = []
        
    def get_name(self):
        return self.__name
        
    def set_name(self, name):
        self.__name = name
        
    def get_configuration_attributes(self):
        return self.__configuration_attributes
        
    def create_attribute(self, attribute_name, symbol_value_type=None):
        configuration_attribute = ConfigurationAttribute(attribute_name, symbol_calculation_type=symbol_value_type)
        self.__configuration_attributes.append(configuration_attribute)
        
        return configuration_attribute
        
    def create_setup_version(self):
        setup_class = SetupClass("New instance", self)
        
        for configuration_attribute in self.__configuration_attributes:
            setup_class.create_setup_attribute(configuration_attribute)
            
        return setup_class
        
class ConfigurationAttribute:
    def __init__(self, name, *, symbol_value_type=None, symbol_calculation_type=None):
        self.__name = name
        self.__symbol_value_type = symbol_value_type
        self.__symbol_calculation_type = symbol_calculation_type
        self.__input_attributes = {}
        
    def get_name(self):
        return self.__name
        
    def set_name(self, name):
        self.__name = name
        
    def get_symbol_value_type(self):
        return self.__symbol_value_type
        
    def set_symbol_value_type(self, symbol_value_type):
        self.__symbol_value_type = symbol_value_type
        
    def get_symbol_calculation_type(self):
        return self.__symbol_calculation_type
        
    def set_symbol_calculation_type(self, symbol_calculation_type):
        self.__symbol_calculation_type = symbol_calculation_type
        
    def has_input_attributes(self):
        return len(self.__input_attributes) > 0
        
    def set_input_attribute(self, input_attribute, is_internal):
        self.__input_attributes[input_attribute] = is_internal
        print(self.__input_attributes[input_attribute])
        
    def remove_input_attribute(self, input_attribute):
        self.__input_attributes.pop(input_attribute)
        
    def get_connected_setup_attributes(self, connected_setup_class, current_setup_class):
        filtered_connected_setup_attributes = set()
        
        for connected_configuration_attribute, is_internal in self.__input_attributes.items():
            print(is_internal)
            print(connected_configuration_attribute)
            print(f"{connected_setup_class} {current_setup_class}")
            if (is_internal and connected_setup_class == current_setup_class) or (not is_internal and connected_setup_class != current_setup_class):
                for connected_setup_attribute in connected_setup_class.get_setup_attributes():
                    if connected_setup_attribute.has_configuration_attribute(connected_configuration_attribute):
                        filtered_connected_setup_attributes.add(connected_setup_attribute)
                        print("ADD")
                        
        print(filtered_connected_setup_attributes)
        return filtered_connected_setup_attributes
