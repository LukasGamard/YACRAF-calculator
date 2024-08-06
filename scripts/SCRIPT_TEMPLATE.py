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

# script_if.get_input_class_names(class_type, class_instance)
#     Returns a list of tuples including the class type and class instance names of all classes which the specified setup class instance takes input fro
#     [(input_class_type, input_class_instance), ...]

# script_if.get_attribute_value(class_type, class_instance, attribute, view=None)
#     Returns the value displayed by a specific setup attribute, which is a float if the value type, a list of values if a distribution, or otherwise a string
#     If there are overlapping attribute names for a specific class type, each attribute value is returned as part of a list

# script_if.override_attribute_values(override_value, *, class_type=None, class_instance=None, attribute=None, view=None)
#     Overrides the displayed value of matching attributes with a temporary one given in string format (as if it was entered through an entry field)

# script_if.reset_override_attribute_values(*, class_type=None, class_instance=None, attribute=None, view=None)
#     Resets any override value of matching attributes

# script_if.set_class_marker(value, color, *, class_type=None, class_instance=None, view=None)
#     Adds a visual marker on all matching class instances

# script_if.calculate_values()
#     Calculates all attribute values in the setup views based on the current configuration

def script_logic(script_if):
    # Insert logic here
    script_if.calculate_values()
    
def script_control(script_if):
    script_if.update_setup_structure()
    script_if.reset_script_changes()
    script_logic(script_if)
