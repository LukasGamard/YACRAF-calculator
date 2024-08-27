import numpy as np

def disable_all_other_defenses(script_if, defenses_to_disable, defense_to_exclude=None):
    script_if.reset_override_attribute_values()
    
    for defense_name in defenses_to_disable:
        if defense_name != defense_to_exclude:
            current_value = script_if.get_attribute_values("Defense mechanism", defense_name, "Impact")[0]
            override_value = " / ".join(["0"] * len(current_value))
            
            script_if.override_attribute_values(override_value, \
                                                class_type="Defense mechanism", \
                                                class_instance=defense_name, \
                                                attribute="Impact")
            
def calculate_total_risk(script_if):
    script_if.calculate_values()
    
    total_risk = 0
    
    for loss_event_instance in script_if.get_class_instance_names("Loss event"):
        risks = script_if.get_attribute_values("Loss event", loss_event_instance, "Risk")
        
        for risk in risks:
            total_risk += sum(risk) / len(risk)
            
    return total_risk
    
def script_logic(script_if):
    # Insert logic here
    remaining_defenses_names = script_if.get_class_instance_names("Defense mechanism")
    priority_of_defenses = []
    
    disable_all_other_defenses(script_if, remaining_defenses_names)
    original_total_risk = calculate_total_risk(script_if)
    current_total_risk = original_total_risk
    
    while len(remaining_defenses_names) > 0:
        current_best_return_on_security_investment = None
        current_best_defense = None
        current_risk = None
        
        for defense_name in remaining_defenses_names:
            disable_all_other_defenses(script_if, remaining_defenses_names, defense_name)
            total_risk = calculate_total_risk(script_if)
            defense_mechanism_costs = script_if.get_attribute_values("Defense mechanism", defense_name, "Cost")
            
            if len(defense_mechanism_costs) > 1:
                print(f"Warning: Multiple attributes found when searching for {defense_name}, using the attribute value of the first encountered")
                
            defense_mechanism_cost = sum(defense_mechanism_costs[0]) / len(defense_mechanism_costs[0])
            return_on_security_investment = (current_total_risk - total_risk - defense_mechanism_cost) / defense_mechanism_cost
            
            if current_best_return_on_security_investment == None or return_on_security_investment > current_best_return_on_security_investment:
                current_best_return_on_security_investment = return_on_security_investment 
                current_best_defense = defense_name
                current_risk = total_risk
                
        remaining_defenses_names.remove(current_best_defense)
        
        priority_of_defenses.append((current_best_defense, current_best_return_on_security_investment))
        current_total_risk = current_risk
        
    print("Priority of defense mechanisms based on return on security investment:")
    
    for i, defense_and_return in enumerate(priority_of_defenses):
        defense_name, return_on_security_investment = defense_and_return
        return_on_security_investment *= 100
        print(f"{i+1}. {defense_name}: {return_on_security_investment} %")
        
    script_if.reset_script_changes()
    
def script_control(script_if):
    script_if.reset_script_changes()
    script_logic(script_if)
