class ScriptInterface:
    def __init__(self, model):
        self.__model = model
        self.__setup_structure = None
        
    def get_class_type_names(self, view=None):
        return list(self.__setup_structure.get_names([view]))
        
    def get_class_instance_names(self, class_type, view=None):
        return list(self.__setup_structure.get_names([view, class_type]))
        
    def get_attribute_names(self, class_type, view=None):
        class_instance_name = self.get_class_instance_names(class_type, view)[0]
        return list(self.__setup_structure.get_names([view, class_type, class_instance_name]))
        
    def get_input_class_names(self, class_type, class_instance):
        input_class_names = set()
        
        for setup_class_gui in self.__setup_structure.get_elements([None, class_type, class_instance]):
            for input_setup_class in setup_class_gui.get_setup_class().get_input_setup_classes():
                input_class_names.add((input_setup_class.get_configuration_name(), input_setup_class.get_instance_name()))
                
        return list(input_class_names)
        
    def get_attribute_value(self, class_type, class_instance, attribute, view=None):
        attribute_value = None
        
        for setup_attribute_gui in self.__setup_structure.get_elements([view, class_type, class_instance, attribute]):
            value = setup_attribute_gui.get_current_value()
            
            # First value
            if attribute_values == None:
                attribute_value = value
                
            # If there is a second value, convert to list
            elif not isinstance(attribute_value, list):
                attribute_value = [attribute_value, value]
                
            # More than two values
            else:
                attribute_value.append(value)
                
        return attribute_value
        
    def override_attribute_values(self, override_value, *, class_type=None, class_instance=None, attribute=None, view=None):
        for setup_attribute_gui in self.__setup_structure.get_elements([view, class_type, class_instance, attribute]):
            setup_attribute_gui.get_setup_attribute().set_override_value(override_value)
            
    def reset_override_attribute_values(self, *, class_type=None, class_instance=None, attribute=None, view=None):
        self.override_attribute_values(None, class_type=class_type, class_instance=class_instance, attribute=attribute, view=view)
        
    def set_class_marker(self, value, color, *, class_type=None, class_instance=None, view=None):
        for setup_class_gui in self.__setup_structure.get_elements([view, class_type, class_instance]):
            setup_class_gui.create_script_marker_indicator(value, color)
            
    def calculate_values(self):
        self.__model.calculate_values()
        
    def reset_script_changes(self):
        self.__model.reset_changes_by_script()
        
    def update_setup_structure(self):
        setup_structure = SetupStructureNode()
        
        for setup_view in self.__model.get_setup_views():
            view_node = setup_structure.add_next_node(setup_view, setup_view.get_name())
            
            for setup_class_gui in setup_view.get_setup_classes_gui():
                class_node = view_node.add_next_node(setup_class_gui, setup_class_gui.get_configuration_name())
                class_instance_node = class_node.add_next_node(setup_class_gui, setup_class_gui.get_name())
                
                for setup_attribute_gui in setup_class_gui.get_setup_attributes_gui():
                    class_instance_node.add_element(setup_attribute_gui, setup_attribute_gui.get_name())
                    
class SetupStructureNode:
    def __init__(self):
        self.__next_node_per_name = {}
        self.__elements = []
        self.__names = set()
        
    def add_next_node(self, element, name):
        if name not in self.__names:
            next_node = SetupStructureNode()
            self.__next_node_per_name[name] = next_node
            
        else:
            next_node = self.__next_node_per_name[name]
            
        self.add_element(element, name)
        
        return next_node
        
    def add_element(self, element, name):
        self.__elements.append(element)
        self.__names.add(name)
        
    def get_next_nodes(self, name):
        if name == None:
            return list(self.__next_node_per_name)
            
        elif name in self.__next_node_per_name:
            return [self.__next_node_per_name[name]]
            
        else:
            print(f"Error: Could not find {name}")
            return []
            
    def get_elements(self, names):
        if len(names) > 0:
            found_elements = []
            
            for next_node in self.get_next_nodes(names[0]):
                found_elements += next_node.get_elements(names[1:])
                
            return found_elements
            
        return self.__elements
        
    def get_names(self, names):
        if len(names) > 0:
            found_names = []
            
            for next_node in self.get_next_nodes(names[0]):
                found_names += next_node.get_names(names[1:])
                
            return found_names
            
        return self.__names
