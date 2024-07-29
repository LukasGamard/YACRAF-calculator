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

DEFENSE_MECHANISM_NAME = "Defense mechanism"
LOSS_EVENT_NAME = "Loss event"
LOSS_EVENT_INSTANCES = []
LOSS_EVENT_MAGNITUDE_ATTRIBUTE = "Magnitude"

def disable_all_other_defenses(script_if, defenses_to_disable, defense_to_exclude):
    for defense_name in defenses_to_disable:
        if defense_name != defense_to_exclude:
            script_if.override_attribute_values(0, class_type=DEFENSE_MECHANISM_NAME, class_instance=defense_name)
            
def calculate_total_magnitude(script_if):
    script_if.calculate_values()
    
    total_magnitude = 0
    
    for loss_event_instance in LOSS_EVENT_INSTANCES:
        total_magnitude += script_if.get_attribute_value(LOSS_EVENT_NAME, loss_event_instance, LOSS_EVENT_MAGNITUDE_ATTRIBUTE)
        
    return total_magnitude
    
def script_logic(script_if):
    remaining_defenses_names = script_if.get_class_instance_names(DEFENSE_MECHANISM_NAME)
    priority_of_defenses = []
    
    original_magnitude = calculate_total_magnitude(script_if)
    
    while len(remaining_defenses_names) > 0:
        current_lowest_magnitude = None
        current_best_defense = None
        
        for defense_name in remaining_defenses_names:
            script_if.reset_override_attribute_values()
            disable_all_other_defenses(script_if, remaining_defenses_names, defense_name)
            total_magnitude = calculate_total_magnitude(script_if)
            
            if current_lowest_magnitude == None or total_magnitude < current_lowest_magnitude:
                current_lowest_magnitude = total_magnitude
                current_best_defense = defense_name
                
        priority_of_defenses.append((current_best_defense, current_lowest_magnitude))
        
    print("Priority of defense mechanisms:")
    print(f"No defenses: {original_magnitude}")
    
    for i, defense_and_magnitude in enumerate(priority_of_defenses):
        defense_name, magnitude = defense_and_magnitude
        print(f"{i}. {defense_name}: {magnitude}")
        
def script_control(script_if):
    script_if.reset_script_changes()
    script_logic(script_if)
