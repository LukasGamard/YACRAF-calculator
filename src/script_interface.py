class ScriptInterface:
    def __init__(self, model):
        self.__model = model
        
    def override_attribute_values(self, override_value, attribute_name, class_configuration_name, class_instance_name=None):
        for setup_attribute_gui in self.__model.get_matching_setup_attributes_gui(attribute_name, class_configuration_name, class_instance_name=None):
            setup_attribute_gui.set_override_value(override_value)
            
    def set_class_marker(self, value, color, class_configuration_name, class_instance_name=None):
        for setup_class_gui in self.__model.get_matching_setup_classes_gui(class_configuration_name, class_instance_name):
            setup_class_gui.create_script_marker_indicator(value, color)
            
    def reset_script_changes(self):
        self.__model.reset_changes_by_script()
            
    def run_script(self):
        self.__model.calculate_values()
