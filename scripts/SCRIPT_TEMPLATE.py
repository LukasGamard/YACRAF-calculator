# Available functions:
# Leaving input as None implies matching all blocks of said type

# script_if.get_attribute_values(*, class_type=None, class_instance=None, attribute=None)
#     returns list of tuple elements [(value, class_type, class_instance, attribute), ...]

# script_if.override_attribute_values(override_value, *, class_type=None, class_instance=None, attribute=None)

# script_if.set_class_marker(value, color, *, class_type=None, class_instance=None)

# script_if.get_input_classes(*, class_type=None, class_instance=None)
#     returns list of tuple elements [(class_type, class_instance), ...]

def script_logic(script_if):
    # Insert logic here
    
def script_control(script_if):
    script_if.reset_script_changes()
    script_logic(script_if)
    script_if.run_script()
