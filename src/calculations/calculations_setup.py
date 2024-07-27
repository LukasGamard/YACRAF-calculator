from calculations_general import combine_values

class SetupClass:
    def __init__(self, instance_name, configuration_class):
        self.__instance_name = instance_name
        self.__configuration_class = configuration_class
        self.__setup_attributes = []
        self.__input_classes = []
        
    def get_instance_name(self):
        return self.__instance_name
        
    def set_instance_name(self, instance_name):
        self.__instance_name = instance_name
        
    def get_configuration_name(self):
        return self.__configuration_class.get_name()
        
    def calculate_values(self):
        for attribute in self.__setup_attributes:
            attribute.calculate_value()
            
    def reset_calculated_values(self):
        for attribute in self.__setup_attributes:
            attribute.reset_value_if_inputs()
            
    def get_setup_attributes(self):
        return self.__setup_attributes
        
    def create_setup_attribute(self, configuration_attribute):
        setup_attribute = SetupAttribute(self, configuration_attribute)
        self.__setup_attributes.append(setup_attribute)
        
        return setup_attribute
        
    def get_input_classes(self):
        return self.__input_classes
        
    def add_input_class(self, input_class):
        self.__input_classes.append(input_class)
        
    def remove_input_class(self, input_class):
        self.__input_classes.remove(input_class)
        
class SetupAttribute:
    def __init__(self, setup_class, configuration_attribute):
        self.__setup_class = setup_class
        self.__configuration_attribute = configuration_attribute
        self.__value = None
        self.__override_value = None
        
    def get_value(self):
        return self.__value
        
    def set_value(self, value):
        self.__value = value
        
    def reset_value_if_inputs(self):
        if self.__configuration_attribute.has_input_attributes():
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
        connected_setup_classes = self.__setup_class.get_input_classes()
        
        internal_connected_setup_attributes, external_connected_setup_attributes = self.get_connected_setup_attributes()
        
        return len(internal_connected_setup_attributes) > 0 or len(external_connected_setup_attributes) > 0
        
    def get_connected_setup_attributes(self):
        connected_setup_classes = self.__setup_class.get_input_classes()
        
        # Internal connections
        internal_connected_setup_attributes = self.__configuration_attribute.get_connected_setup_attributes(self.__setup_class, self.__setup_class)
        
        # External connections
        external_connected_setup_attributes = set()
        
        for connected_setup_class in connected_setup_classes:
            external_connected_setup_attributes |= self.__configuration_attribute.get_connected_setup_attributes(connected_setup_class, self.__setup_class)
                
        return internal_connected_setup_attributes, external_connected_setup_attributes
        
    def calculate_value(self):
        connected_setup_classes = self.__setup_class.get_input_classes()
        
        if self.__value != None:
            return
            
        internal_connected_setup_attributes, external_connected_setup_attributes = self.get_connected_setup_attributes()
        
        for internal_connected_setup_attribute in internal_connected_setup_attributes:
            internal_connected_setup_attribute.calculate_value(self.__setup_class, connected_setup_classes)
            
        for connected_setup_class in connected_setup_classes:
            connected_setup_class.calculate_values()
            
        self.__value = combine_values(self.__configuration_attribute.get_symbol_calculation_type(), self.__configuration_attribute.get_symbol_value_type(), internal_connected_setup_attributes|external_connected_setup_attributes)
        
    def get_symbol_value_type(self):
        return self.__configuration_attribute.get_symbol_value_type()
        
    def has_configuration_attribute(self, configuration_attribute):
        return self.__configuration_attribute == configuration_attribute
        
    def get_name(self):
        return self.__configuration_attribute.get_name()
