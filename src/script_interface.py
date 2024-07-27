class ScriptInterface:
    def __init__(self, model):
        self.__model = model
        
    def get_attribute_values(self, *, class_type=None, class_instance=None, attribute=None):
        attribute_values = []
        
        for setup_attribute_gui, current_names in self.__model.get_matching_setup_attributes_gui(class_configuration_name=class_type, class_instance_name=class_instance, attribute_name=attribute).items():
            current_class_type, current_class_instance, current_attribute = current_names
            value = setup_attribute_gui.get_current_value()
            
            attribute_values.append((value, current_class_type, current_class_instance, current_attribute))
            
        return attribute_values
        
    def override_attribute_values(self, override_value, *, class_type=None, class_instance=None, attribute=None):
        for setup_attribute_gui in list(self.__model.get_matching_setup_attributes_gui(class_configuration_name=class_type, class_instance_name=class_instance, attribute_name=attribute).keys()):
            setup_attribute_gui.set_override_value(override_value)
            
    def set_class_marker(self, value, color, *, class_type=None, class_instance=None):
        for setup_class_gui in list(self.__model.get_matching_setup_classes_gui(class_configuration_name=class_type, class_instance_name=class_instance).keys()):
            setup_class_gui.create_script_marker_indicator(value, color)
            
    def get_input_classes(self, *, class_type=None, class_instance=None):
        input_classes = []
        
        for setup_class_gui in list(self.__model.get_matching_setup_classes_gui(class_configuration_name=class_type, class_instance_name=class_instance).keys()):
            for input_setup_class in setup_class_gui.get_setup_class().get_input_classes():
                input_classes.append((input_setup_class.get_name(), input_setup_class.get_instance_name()))
                
        return input_classes
        
    def reset_script_changes(self):
        self.__model.reset_changes_by_script()
        
    def run_script(self):
        self.__model.calculate_values()
