# Available functions:
# script_if.override_attribute_values(override_value, attribute_name, class_configuration_name, class_instance_name=None)
# script_if.set_class_marker(value, color, class_configuration_name, class_instance_name=None)

def script_logic(script_if):
    # Insert logic here
    script_if.override_attribute_values(2, "Out Attribute 2", "Out", "TEST")
    script_if.set_class_marker("A", "red", "In")
    
def script_control(script_if):
    script_if.reset_script_changes()
    script_logic(script_if)
    script_if.run_script()
