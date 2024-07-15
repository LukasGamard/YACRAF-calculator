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
        
    def calculate_values(self):
        print(f"CALCULATING: {self}")
        for attribute in self.__setup_attributes:
            print(f"CALCULATING: {attribute}")
            attribute.calculate_value(self, self.__input_classes)
            
    def reset_calculated_values(self):
        for attribute in self.__setup_attributes:
            attribute.reset_value_if_inputs()
            
    def get_setup_attributes(self):
        return self.__setup_attributes
        
    def create_setup_attribute(self, configuration_attribute):
        setup_attribute = SetupAttribute(configuration_attribute)
        self.__setup_attributes.append(setup_attribute)
        
        return setup_attribute
        
    def add_input_class(self, input_class):
        self.__input_classes.append(input_class)
        
    def remove_input_class(self, input_class):
        self.__input_classes.remove(input_class)
        
    def get_instance_name(self):
        return self.__instance_name
        
class SetupAttribute:
    def __init__(self, configuration_attribute):
        self.__configuration_attribute = configuration_attribute
        self.__value = None
        
    def get_value(self):
        return self.__value
        
    def set_value(self, value):
        print("SET VALUE")
        self.__value = value
        
    def reset_value_if_inputs(self):
        if self.__configuration_attribute.has_input_attributes():
            self.__value = None
            return True
            
        return False
        
    def calculate_value(self, setup_class, connected_setup_classes):
        if self.__value != None:
            return
            
        connected_setup_attributes = []
        
        # Internal connections
        for internal_connected_setup_attribute in self.__configuration_attribute.get_connected_setup_attributes(setup_class, setup_class):
            connected_setup_attributes.append(internal_connected_setup_attribute)
            internal_connected_setup_attribute.calculate_value(setup_class, connected_setup_classes)
        
        # External connections
        for connected_setup_class in connected_setup_classes:
            if connected_setup_class is not self:
                new_connected_setup_attributes = self.__configuration_attribute.get_connected_setup_attributes(connected_setup_class, setup_class)
                connected_setup_attributes += new_connected_setup_attributes
                
                if len(new_connected_setup_attributes) > 0:
                    connected_setup_class.calculate_values()
                
        self.__value = combine_values(self.__configuration_attribute.get_symbol_calculation_type(), self.__configuration_attribute.get_symbol_value_type(), connected_setup_attributes)
        
    def get_symbol_value_type(self):
        return self.__configuration_attribute.get_symbol_value_type()
        
    def has_configuration_attribute(self, configuration_attribute):
        return self.__configuration_attribute == configuration_attribute
        
    def get_name(self):
        return self.__configuration_attribute.get_name()
