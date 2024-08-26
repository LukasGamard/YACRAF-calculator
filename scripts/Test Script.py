def script_logic(script_if):
    # Insert logic here
    print("Current view: " + script_if.get_current_view_name())
    
    print("Class types in all views: " + str(script_if.get_class_type_names()))
    print("Class types in first view: " + str(script_if.get_class_type_names("Setup 1")))
    
    print("Class instances of Attack event AND in all views: " + str(script_if.get_class_instance_names("Attack event AND")))
    print("Class instances of Attack event AND in first view: " + str(script_if.get_class_instance_names("Attack event AND", "Setup 1")))
    
    print("Attributes of Attack event AND: " + str(script_if.get_attribute_names("Attack event AND")))
    
    print("Input classes to Attack event AND: Top 1: " + str(script_if.get_input_class_names("Attack event AND", "Top 1")))
    
    attribute_value = script_if.get_attribute_values("Attack event AND", "Top 1", "Global difficulty")[0]
    print("Value of Global difficulty in Attack event AND: Top 1: " + str(attribute_value))
    print("Value of Global difficulty in Attack event AND: Top 1: " + script_if.convert_value_to_string(attribute_value))
    
    script_if.override_attribute_values("0 / 1 / 2", class_type="Attack event AND", class_instance="Top 1", attribute="Local difficulty")
    
    script_if.override_attribute_values("0 / 1 / 2", class_type="Attack event AND", class_instance="Top 1", attribute="Global difficulty")
    script_if.reset_override_attribute_values(class_type="Attack event AND", class_instance="Top 1", attribute="Global difficulty")
    
    script_if.set_class_marker("A", "red", class_type="Attack event AND", class_instance="Top 1")
    script_if.set_class_marker("B", "blue", class_type="Attack event AND", class_instance="Top 1")
    script_if.set_class_marker("C", "yellow", class_type="Attack event AND", class_instance="Left 1")
    script_if.set_class_marker("D", "green", class_type="Attack event AND", class_instance="Right 1")
    
    script_if.calculate_values()
    
def script_control(script_if):
    script_if.reset_script_changes()
    script_logic(script_if)
