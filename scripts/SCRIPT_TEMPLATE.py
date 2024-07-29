# Available functions:
# Default value of None implies matching all blocks

# script_if.get_class_names()
#     Returns a list of names of all found classes

# script_if.get_class_instance_names(class_type)
#     Returns a list of names of all found class instances for a specific class type

# script_if.get_attribute_names(class_type)
#     Returns a list of names of all found attributes for a specific class type

# script_if.get_input_class_names(class_type, class_instance)
#     Returns a list of tuples of class type and corresponding class instances that are inputs for a specific pair of class type and class instance
#     [(input_class_type, input_class_instance), ...]

# script_if.get_attribute_value(class_type, class_instance, attribute)
#     Returns the value displayed by a specific attribute, which is a list if there are overlapping attribute names for a specific class type

# script_if.override_attribute_values(override_value, *, class_type=None, class_instance=None, attribute=None)
#     Overrides the value of matching attributes

# script_if.reset_override_attribute_values(*, class_type=None, class_instance=None, attribute=None)
#     Removes the override value of matching attributes

# script_if.set_class_marker(value, color, *, class_type=None, class_instance=None)
#     Adds a visual marker on all matching class instances

# script_if.calculate_values()
#     Calculates all attribute values based on the current configuration

def script_logic(script_if):
    # Insert logic here
    
def script_control(script_if):
    script_if.reset_script_changes()
    script_logic(script_if)
