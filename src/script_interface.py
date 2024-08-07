from helper_functions import convert_string_to_value

class ScriptInterface:
    """
    Methods that scripts can interact with to manipulate the program
    
    Meaning of values passed to methods for finding/matching blocks in setup views, where None considers all:
    class_type: Name of class type (for example, Attack event)
    class_instance: Name of class instance (for example, DoS attack)
    attribute: Name of attribute (for example, Local difficulty)
    view: Setup view name to consider, where None considers all
    """
    def __init__(self, model):
        self.__model = model
        self.__setup_structure = None # Structure of all blocks in setup views
        
    def get_class_type_names(self, view=None):
        """
        Returns a list of class names (those specified in configuration views) found in the specified setup views
        """
        return list(self.__setup_structure.get_names([view]))
        
    def get_class_instance_names(self, class_type, view=None):
        """
        Returns a list of class instance names (those specified in setup views) found in the specified setup views
        """
        return list(self.__setup_structure.get_names([view, class_type]))
        
    def get_attribute_names(self, class_type):
        """
        Returns a list of attribute names for a specific class type
        """
        class_instance_name = self.get_class_instance_names(class_type)[0]
        return list(self.__setup_structure.get_names([None, class_type, class_instance_name]))
        
    def get_input_class_names(self, class_type, class_instance):
        """
        Returns a list of tuples including the class type and class instance names of all classes which the specified setup class instance takes input from
        """
        input_class_names = set()
        
        for setup_class_gui in self.__setup_structure.get_elements([None, class_type, class_instance]):
            # Add any newly found input class name that had not been previously added
            for input_setup_class in setup_class_gui.get_setup_class().get_input_setup_classes():
                input_class_names.add((input_setup_class.get_configuration_name(), input_setup_class.get_instance_name()))
                
        return list(input_class_names)
        
    def get_attribute_value(self, class_type, class_instance, attribute, view=None):
        """
        Returns the value displayed by a specific setup attribute, which is a list if there are overlapping attribute names for a specific class type
        """
        attributes_values = None
        
        for setup_attribute_gui in self.__setup_structure.get_elements([view, class_type, class_instance, attribute]):
            setup_attribute = setup_attribute_gui.get_setup_attribute()
            
            if setup_attribute.has_override_value():
                value_string = setup_attribute.get_override_value()
            else:
                value_string = setup_attribute.get_value()
                
            # Convert string value into a single value, list of values if a distribution, or keep as string
            try:
                value = convert_string_to_value(value_string)
            except:
                value = value_string
                
            # First attribute
            if attributes_values == None:
                attributes_values = value
                
            # If there is a second attribute, convert to list
            elif not isinstance(attributes_values, list):
                attributes_values = [attribute_value, value]
                
            # More than two attributes
            else:
                attributes_values.append(value)
                
        return attributes_values
        
    def override_attribute_values(self, override_value, *, class_type=None, class_instance=None, attribute=None, view=None):
        """
        Overrides the displayed value of matching attributes with a temporary one
        """
        for setup_attribute_gui in self.__setup_structure.get_elements([view, class_type, class_instance, attribute]):
            setup_attribute_gui.get_setup_attribute().set_override_value(override_value)
            
    def reset_override_attribute_values(self, *, class_type=None, class_instance=None, attribute=None, view=None):
        """
        Resets any override value of matching attributes
        """
        for setup_attribute_gui in self.__setup_structure.get_elements([view, class_type, class_instance, attribute]):
            setup_attribute_gui.attempt_to_reset_override_value()
        
    def set_class_marker(self, value, color, *, class_type=None, class_instance=None, view=None):
        """
        Adds a visual marker on all matching class instances
        """
        for setup_class_gui in self.__setup_structure.get_elements([view, class_type, class_instance]):
            setup_class_gui.create_script_marker_indicator(value, color)
            
    def calculate_values(self):
        """
        Calculates all attribute values in the setup views based on the current configuration
        """
        self.__model.calculate_values()
        
    def reset_script_changes(self):
        """
        Reset any changes made by scripts, such as override values and markers
        """
        self.__model.reset_script_changes()
        
    def update_setup_structure(self):
        self.__setup_structure = SetupStructureNode()
        
        for setup_view in self.__model.get_setup_views():
            view_node = self.__setup_structure.add_next_node(setup_view, setup_view.get_name())
            
            for setup_class_gui in setup_view.get_setup_classes_gui():
                class_node = view_node.add_next_node(setup_class_gui, setup_class_gui.get_configuration_name())
                class_instance_node = class_node.add_next_node(setup_class_gui, setup_class_gui.get_name())
                
                for setup_attribute_gui in setup_class_gui.get_setup_attributes_gui():
                    class_instance_node.add_element(setup_attribute_gui, setup_attribute_gui.get_name())
                    
class SetupStructureNode:
    """
    Structure containing all setup blocks
    """
    def __init__(self):
        self.__next_node_per_name = {} # Key: Name of element, Value: Element (for example, a class instance)
        self.__elements = {} # Stores all elements (for example, all class instances), where Key: Element, Value: Name
        self.__names = [] # Stores all unique names of elements (for example, names of all class instances)
        
    def add_next_node(self, element, name):
        """
        Creates a new node if is the first occurrence of the name, but also storing the element and (potentially) name in this node
        """
        first_name_occurence = True
        
        # Is first occurrence
        if name not in self.__names:
            next_node = SetupStructureNode()
            self.__next_node_per_name[name] = next_node
            
        # Not first occurrence
        else:
            next_node = self.__next_node_per_name[name]
            first_name_occurence = False
            
        self.add_element(element, name, first_name_occurence)
        
        return next_node
        
    def add_element(self, element, name, knows_it_is_first_name_occurence=False):
        self.__elements[element] = name
        
        if knows_it_is_first_name_occurence or name not in self.__names:
            self.__names.append(name)
            
    def get_next_nodes(self, name):
        # Matches with all nodes
        if name == None:
            return list(self.__next_node_per_name.values())
            
        # Matches with specific node
        elif name in self.__next_node_per_name:
            return [self.__next_node_per_name[name]]
            
        else:
            return []
            
    def get_elements(self, names):
        """
        names: List of names to match on the format [view, class_type, class_instance, attribute] that is recursively matched one name per node at a time, stopping early if there are less names and matches everything in a layer if None (for example, [None, class_type] matches all class types in all setup views)
        
        Returns a list of all matched elements of the specific layer (for example, [None, class_type] would get all class types of all setup views
        """
        # Sought elements does not exist at this node
        if len(names) > 1:
            found_elements = []
            
            for next_node in self.get_next_nodes(names[0]):
                found_elements += next_node.get_elements(names[1:])
                
            return found_elements
            
        # At final specified layer
        elif len(names) == 1 and names[0] != None:
            elements = []
            
            # Find the specified element
            for element, name in self.__elements.items():
                if name == names[0]:
                    elements.append(element)
                    
            return elements
            
        return list(self.__elements.keys())
        
    def get_names(self, names):
        """
        names: List of names to match on the format [view, class_type, class_instance, attribute] that is recursively matched one name per node at a time, stopping early if there are less names and matches everything in a layer if None (for example, [None, class_type] matches all class types in all setup views)
        
        Returns a list of all matched names of the next layer (for example, [None, class_type] would get all class instance names of all setup views
        """
        
        if len(names) > 0:
            found_names = []
            
            for next_node in self.get_next_nodes(names[0]):
                found_names += next_node.get_names(names[1:])
                
            return found_names
            
        return self.__names
