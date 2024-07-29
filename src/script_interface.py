class ScriptInterface:
    def __init__(self, model):
        self.__model = model
        
    def get_class_names(self):
        class_names = []
        
        for setup_class_gui in self.__model.get_matching_setup_classes_gui(class_configuration_name=class_type):
            class_names.append(setup_class_gui.get_configuration_name())
            
        return class_names
        
    def get_class_instance_names(self, class_type):
        class_instance_names = []
        
        for setup_class_gui in self.__model.get_matching_setup_classes_gui(class_configuration_name=class_type):
            class_instance_names.append(setup_class_gui.get_name())
            
        return class_instance_names
        
    def get_attribute_names(self, class_type):
        attribute_names = []
        
        for setup_attribute_gui in self.__model.get_matching_setup_attributes_gui(class_configuration_name=class_type, class_instance_name=class_instance):
            attribute_names.append(setup_attribute_gui.get_name())
            
        return attribute_names
        
    def get_input_class_names(self, class_type, class_instance):
        input_classes = []
        
        for setup_class_gui in self.__model.get_matching_setup_classes_gui(class_configuration_name=class_type, class_instance_name=class_instance):
            for input_setup_class in setup_class_gui.get_setup_class().get_input_classes():
                input_classes.append((input_setup_class.get_name(), input_setup_class.get_instance_name()))
                
        return input_classes
        
    def get_attribute_value(self, class_type, class_instance, attribute):
        attribute_value = None
        
        for setup_attribute_gui in self.__model.get_matching_setup_attributes_gui(class_configuration_name=class_type, class_instance_name=class_instance, attribute_name=attribute):
            value = setup_attribute_gui.get_current_value()
            
            if attribute_values == None:
                attribute_value = value
                
            # If there is more than one value, convert to list
            elif not isinstance(attribute_value, list):
                attribute_value = [attribute_value, value]
                
            # More than two values
            else:
                attribute_value.append(value)
                
        return attribute_value
        
    def override_attribute_values(self, override_value, *, class_type=None, class_instance=None, attribute=None):
        for setup_attribute_gui in list(self.__model.get_matching_setup_attributes_gui(class_configuration_name=class_type, class_instance_name=class_instance, attribute_name=attribute).keys()):
            setup_attribute_gui.get_setup_attribute().set_override_value(override_value)
            
    def reset_override_attribute_values(self, *, class_type=None, class_instance=None, attribute=None):
        self.override_attribute_values(None)
            
    def set_class_marker(self, value, color, *, class_type=None, class_instance=None):
        for setup_class_gui in list(self.__model.get_matching_setup_classes_gui(class_configuration_name=class_type, class_instance_name=class_instance).keys()):
            setup_class_gui.create_script_marker_indicator(value, color)
            
    def calculate_values(self):
        self.__model.calculate_values()
        
    def reset_script_changes(self):
        self.__model.reset_changes_by_script()
