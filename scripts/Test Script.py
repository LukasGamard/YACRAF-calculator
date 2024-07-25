# Available functions:
# Leaving input as None implies matching all blocks of said type

# script_if.get_attribute_values(*, class_type=None, class_instance=None, attribute=None)
#     returns list of tuple elements [(value, class_type, class_instance, attribute), ...]

# script_if.override_attribute_values(override_value, *, class_type=None, class_instance=None, attribute=None)

# script_if.set_class_marker(value, color, *, class_type=None, class_instance=None)

def script_logic(script_if):
    # Insert logic here
    script_if.override_attribute_values(2, class_type="Out", class_instance="TEST", attribute="Out Attribute 2")
    script_if.set_class_marker("A", "red", class_type="In")
    
    for value, class_type, class_instance, attribute in script_if.get_attribute_values(class_instance="New instance"):
        print(f"{class_type}, {class_instance}, {attribute}: {value}")
    
def script_control(script_if):
    script_if.reset_script_changes()
    script_logic(script_if)
    script_if.run_script()
