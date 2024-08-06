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

# script_if.get_attribute_names(class_type, view=None)
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

import numpy as np

DEFENSE_MECHANISM_NAME = "Defense mechanism"
DEFEMSE_MECHANISM_ATTRIBUTE_IMPACT = "Impact"
LOSS_EVENT_NAME = "Loss event"
LOSS_EVENT_ATTRIBUTE_RISK = "Risk"

def disable_all_other_defenses(script_if, defenses_to_disable, defense_to_exclude=None):
    script_if.reset_override_attribute_values()
    
    for defense_name in defenses_to_disable:
        if defense_name != defense_to_exclude:
            script_if.override_attribute_values("0 / 0 / 0", class_type=DEFENSE_MECHANISM_NAME, class_instance=defense_name, attribute=DEFEMSE_MECHANISM_ATTRIBUTE_IMPACT)
            
def calculate_total_risk(script_if):
    script_if.calculate_values()
    
    total_risk = 0
    
    for loss_event_instance in script_if.get_class_instance_names(LOSS_EVENT_NAME, "Setup 1"):
        risk = script_if.get_attribute_value(LOSS_EVENT_NAME, loss_event_instance, LOSS_EVENT_ATTRIBUTE_RISK)
        
        # If a distribution, add the mean risk
        if isinstance(risk, list):
            total_risk += sum(risk) / len(risk)
            
        # A single value
        else:
            total_risk += risk
            
    return total_risk
    
def script_logic(script_if):
    # Insert logic here
    remaining_defenses_names = script_if.get_class_instance_names(DEFENSE_MECHANISM_NAME)
    priority_of_defenses = []
    
    disable_all_other_defenses(script_if, remaining_defenses_names)
    original_risk = calculate_total_risk(script_if)
    
    while len(remaining_defenses_names) > 0:
        current_lowest_risk = None
        current_best_defense = None
        
        for defense_name in remaining_defenses_names:
            
            disable_all_other_defenses(script_if, remaining_defenses_names, defense_name)
            total_risk = calculate_total_risk(script_if)
            
            if current_lowest_risk == None or total_risk < current_lowest_risk:
                current_lowest_risk = total_risk
                current_best_defense = defense_name
                
        remaining_defenses_names.remove(current_best_defense)
        
        priority_of_defenses.append((current_best_defense, current_lowest_risk))
        
    print("Priority of defense mechanisms:")
    print(f"No defenses: {original_risk}")
    
    for i, defense_and_risk in enumerate(priority_of_defenses):
        defense_name, risk = defense_and_risk
        print(f"{i}. {defense_name}: {risk}")
        
    script_if.reset_script_changes()
    
def script_control(script_if):
    script_if.update_setup_structure()
    script_if.reset_script_changes()
    script_logic(script_if)
