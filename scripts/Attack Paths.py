# Available functions:

# Meaning of values passed to methods for finding/matching blocks in setup views, where None considers all:
# class_type: Name of class type (for example, Attack event)
# class_instance: Name of class instance (for example, DoS attack)
# attribute: Name of attribute (for example, Local difficulty)
# view: Setup view name to consider, where None considers all

# Values passed to the methods should either be a string or a float/integer

# script_if.get_class_type_names(view=None)
#     Returns a list of class names (those specified in configuration views) found in the specified setup views

# script_if.get_class_instance_names(class_type, view=None)
#     Returns a list of class instance names (those specified in setup views) found in the specified setup views

# script_if.get_attribute_names(class_type)
#     Returns a list of attribute names for a specific class type

# script_if.get_input_class_names(class_type, class_instance, *, input_class_type=None, input_class_instance=None, view=None)
#     Returns a list of tuples including the class type and class instance names of all classes which the specified setup class instance takes input from, considering the optional filtering of classes
#     [(input_class_type, input_class_instance), ...]

# script_if.get_attribute_value(class_type, class_instance, attribute, view=None)
#     Returns the value displayed by a specific setup attribute, which is a float if the value type, a list of values if a distribution, or otherwise a string
#     If there are overlapping attribute names for a specific class type, each attribute value is returned as part of a list

# script_if.convert_value_to_string(attribute_value)
#     Returns the specified attribute value as a formatted string

# script_if.override_attribute_values(override_value, *, class_type=None, class_instance=None, attribute=None, view=None)
#     Overrides the displayed value of matching attributes with a temporary one given in string format (as if it was entered through an entry field)

# script_if.reset_override_attribute_values(*, class_type=None, class_instance=None, attribute=None, view=None)
#     Resets any override value of matching attributes

# script_if.set_class_marker(value, color, *, class_type=None, class_instance=None, view=None)
#     Adds a visual marker on all matching class instances

# script_if.calculate_values()
#     Calculates all attribute values in the setup views based on the current configuration

def mark_easiest_previous_attack(script_if, attack_event_type, attack_event_instance, color, value_index=None):
    input_classes = script_if.get_input_class_names(attack_event_type, attack_event_instance, input_class_type="Attack event AND") + \
                    script_if.get_input_class_names(attack_event_type, attack_event_instance, input_class_type="Attack event OR")
    
    for i, value in enumerate(script_if.get_attribute_value(attack_event_type, attack_event_instance, "Global difficulty")):
        if value_index == None or i == value_index:
            script_if.set_class_marker(i, color, class_type=attack_event_type, class_instance=attack_event_instance)
            
            current_easiest_previous_attack = None
            current_lowest_difficulty = None
            
            for input_class_name, input_class_instance in input_classes:
                global_difficulty = script_if.get_attribute_value(input_class_name, input_class_instance, "Global difficulty")
                
                if current_lowest_difficulty == None or global_difficulty[i] < current_lowest_difficulty:
                    current_easiest_previous_attack = (input_class_name, input_class_instance)
                    current_lowest_difficulty = global_difficulty[i]
                    
            if current_easiest_previous_attack != None:
                mark_easiest_previous_attack(script_if, current_easiest_previous_attack[0], current_easiest_previous_attack[1], color, i)
                
def script_logic(script_if):
    # Insert logic here
    script_if.calculate_values()
    
    num_input_to_per_instance = {} # How many attack events each attack event is connected to, Key: Tuple (class_type, class_instance), Value: number attack events that takes it as input
    colors = ("red", "light blue", "green", "yellow", "orange", "magenta", "gray")
    
    for attack_event_type in ("Attack event AND", "Attack event OR"):
        for attack_event_instance in script_if.get_class_instance_names(attack_event_type):
            if (attack_event_type, attack_event_instance) not in num_input_to_per_instance:
                num_input_to_per_instance[(attack_event_type, attack_event_instance)] = 0
                
            for input_class_names in script_if.get_input_class_names(attack_event_type, attack_event_instance, input_class_type="Attack event AND") + \
                                     script_if.get_input_class_names(attack_event_type, attack_event_instance, input_class_type="Attack event OR"):
                # print(f"{input_class_names} are input to {(attack_event_type, attack_event_instance)}")
                if input_class_names not in num_input_to_per_instance:
                    num_input_to_per_instance[input_class_names] = 1
                else:
                    num_input_to_per_instance[input_class_names] += 1
                    
    current_end_point = 0
    
    for class_names, num_input_to in num_input_to_per_instance.items():
        if num_input_to == 0:
            input_class_type, input_class_instance = class_names
            
            mark_easiest_previous_attack(script_if, input_class_type, input_class_instance, colors[current_end_point])
            current_end_point += 1
            
def script_control(script_if):
    script_if.reset_script_changes()
    script_logic(script_if)
