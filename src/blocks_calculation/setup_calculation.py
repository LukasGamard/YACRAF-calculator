from general_calculation import check_input_value_types, extract_input_values, combine_values

class SetupClass:
    def __init__(self, instance_name, configuration_class):
        self.__instance_name = instance_name
        self.__configuration_class = configuration_class
        self.__setup_attributes = []
        self.__input_setup_classes = {} # Key: input_setup_class, Value: List of input scalars
        
        for configuration_attribute in configuration_class.get_configuration_attributes():
            self.create_setup_attribute(configuration_attribute)
            
    def get_instance_name(self):
        return self.__instance_name
        
    def set_instance_name(self, instance_name):
        self.__instance_name = instance_name
        
    def get_configuration_name(self):
        return self.__configuration_class.get_name()
        
    def calculate_values(self):
        """
        Calculate the final value of all setup attributes of this setup class
        """
        for attribute in self.__setup_attributes:
            attribute.calculate_value()
            
    def reset_calculated_values(self):
        """
        Reset the calculated value of all setup attributes of this setup class so that the program knows a new should be calculated later
        """
        for setup_attribute in self.__setup_attributes:
            setup_attribute.attempt_to_reset_value()
            
    def get_setup_attributes(self):
        return self.__setup_attributes
        
    def create_setup_attribute(self, configuration_attribute):
        setup_attribute = SetupAttribute(self, configuration_attribute)
        self.__setup_attributes.append(setup_attribute)
        
        return setup_attribute
        
    def remove_setup_attribute(self, configuration_attribute):
        for setup_attribute in self.__setup_attributes:
            if setup_attribute.has_configuration_attribute(configuration_attribute):
                self.__setup_attributes.remove(setup_attribute)
                break
        
    def get_input_setup_classes(self):
        return self.__input_setup_classes
        
    def add_input_setup_class(self, input_class, input_setup_class_scalars=None):
        self.__input_setup_classes[input_class] = input_setup_class_scalars
        
    def set_input_setup_class_scalars(self, input_class, input_scalars):
        self.__input_setup_classes[input_class] = input_scalars
        
    def remove_input_setup_class(self, input_class):
        if input_class in self.__input_setup_classes:
            self.__input_setup_classes.pop(input_class)
            
class SetupAttribute:
    def __init__(self, setup_class, configuration_attribute):
        self.__setup_class = setup_class
        self.__configuration_attribute = configuration_attribute
        self.__value = None
        self.__override_value = None
        
    def has_setup_class(self, setup_class):
        return self.__setup_class == setup_class
        
    def get_attribute_index(self):
        return self.__setup_class.get_setup_attributes().index(self)
        
    def get_value(self):
        return self.__value
        
    def set_value(self, value):
        self.__value = value
        
    def clear_value(self):
        self.__value = None
        
    def attempt_to_reset_value(self):
        """
        Reset value so that the program knows it should calculate a new one, but only if there is no override value and there are input attributes as this attribute otherwise should take a manual input
        """
        if self.__configuration_attribute.has_input_configuration_attributes() and not self.has_override_value():
            self.__value = None
            return True
            
        return False
        
    def has_override_value(self):
        return self.__override_value != None
        
    def get_override_value(self):
        return self.__override_value
        
    def set_override_value(self, override_value):
        self.__override_value = override_value
        
    def reset_override_value(self):
        self.__override_value = None
        
    def has_connected_setup_attributes(self, ):
        return len(self.get_connected_setup_attributes()) > 0
        
    def calculate_value(self):
        if self.__value != None:
            return
            
        connected_setup_attributes = []
        setup_input_scalars_per_attribute = []
        
        # First calculate any dependent connected setup attributes
        for connected_setup_attribute, input_setup_scalars in self.get_connected_setup_attributes().items():
            connected_setup_attributes.append(connected_setup_attribute)
            setup_input_scalars_per_attribute.append(input_setup_scalars)
            
            connected_setup_attribute.calculate_value()
            
        # Then calculate the value of this setup attribute considering all dependent connected setup attributes
        self.__value = combine_values(self.__configuration_attribute.get_symbol_calculation_type(), \
                                      self.__configuration_attribute.get_symbol_value_type(), \
                                      self.__configuration_attribute.get_input_configuration_attributes(), \
                                      connected_setup_attributes, \
                                      configuration_input_scalar=self.__configuration_attribute.get_input_scalar(), \
                                      setup_input_scalars_per_attribute=setup_input_scalars_per_attribute)
        
    def get_symbol_value_type(self):
        return self.__configuration_attribute.get_symbol_value_type()
        
    def has_configuration_attribute(self, configuration_attribute):
        return self.__configuration_attribute == configuration_attribute
        
    def get_name(self):
        return self.__configuration_attribute.get_name()
        
    def is_hidden(self):
        return self.__configuration_attribute.is_hidden()
        
    def get_connected_setup_attributes(self):
        filtered_connected_setup_attributes = {}
        connected_setup_classes = self.__setup_class.get_input_setup_classes() | {self.__setup_class: None}
        
        # Go through all connected configuration attributes
        for connected_configuration_attribute, is_internal in self.__configuration_attribute.get_input_configuration_attributes().items():
            # Go through all connected setup classes
            for connected_setup_class, input_scalars in connected_setup_classes.items():
                found_internal_connection = is_internal and connected_setup_class == self.__setup_class
                found_external_connection = not is_internal and connected_setup_class != self.__setup_class
                
                # If a setup class corresponding to the configuration class with the connected configuration attribute is currently connected
                if found_internal_connection or found_external_connection:
                    # Go through all setup attributes of the connected setup class to find the one with the correct configuration attribute
                    for connected_setup_attribute in connected_setup_class.get_setup_attributes():
                        if connected_setup_attribute.has_configuration_attribute(connected_configuration_attribute):
                            filtered_connected_setup_attributes[connected_setup_attribute] = input_scalars
                            
        return filtered_connected_setup_attributes
