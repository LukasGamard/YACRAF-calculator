def mark_easiest_previous_attack(script_if, view, attack_event_type, attack_event_instance, color, value_index=None):
    input_classes = script_if.get_input_class_names(attack_event_type, attack_event_instance, input_class_type="Attack event AND", view=view) + \
                    script_if.get_input_class_names(attack_event_type, attack_event_instance, input_class_type="Attack event OR", view=view)
    
    current_global_difficulties = script_if.get_attribute_values(attack_event_type, attack_event_instance, "Global difficulty", view)
    
    if len(current_global_difficulties) > 1:
        print(f"Warning: Multiple attributes found when searching for {attack_event_type} and {attack_event_instance}, using the attribute value of the first encountered")
        
    # Find unique path for each individual value displayed by the attribute
    for i in range(len(current_global_difficulties[0])):
        if value_index == None or i == value_index:
            script_if.set_class_marker(i+1, color, class_type=attack_event_type, class_instance=attack_event_instance, view=view)
            
            current_easiest_previous_attack = None
            current_lowest_difficulty = None
            
            for input_class_name, input_class_instance in input_classes:
                global_difficulties = script_if.get_attribute_values(input_class_name, input_class_instance, "Global difficulty", view)
                
                if len(global_difficulties) > 1:
                    print(f"Warning: Multiple attributes found when searching for {input_class_name} and {input_class_instance}, using the attribute value of the first encountered")
                    
                global_difficulty = global_difficulties[0]
                
                if current_lowest_difficulty == None or global_difficulty[i] < current_lowest_difficulty:
                    current_easiest_previous_attack = (input_class_name, input_class_instance)
                    current_lowest_difficulty = global_difficulty[i]
                    
            if current_easiest_previous_attack != None:
                mark_easiest_previous_attack(script_if, view, current_easiest_previous_attack[0], current_easiest_previous_attack[1], color, i)
                
def script_logic(script_if):
    # Insert logic here
    script_if.calculate_values()
    
    view = script_if.get_current_view_name()
    
    num_input_to_per_instance = {} # How many attack events each attack event is connected to, Key: Tuple (class_type, class_instance), Value: number attack events that takes it as input
    colors = ("red", "light blue", "green", "yellow", "orange", "magenta", "gray")
    
    for attack_event_type in ("Attack event AND", "Attack event OR"):
        for attack_event_instance in script_if.get_class_instance_names(attack_event_type, view=view):
            if (attack_event_type, attack_event_instance) not in num_input_to_per_instance:
                num_input_to_per_instance[(attack_event_type, attack_event_instance)] = 0
                
            for input_class_names in script_if.get_input_class_names(attack_event_type, \
                                                                     attack_event_instance, \
                                                                     input_class_type="Attack event AND", \
                                                                     view=view) + \
                                     script_if.get_input_class_names(attack_event_type, \
                                                                     attack_event_instance, \
                                                                     input_class_type="Attack event OR", \
                                                                     view=view):
                
                if input_class_names not in num_input_to_per_instance:
                    num_input_to_per_instance[input_class_names] = 1
                else:
                    num_input_to_per_instance[input_class_names] += 1
                    
    current_end_point = 0
    
    for class_names, num_input_to in num_input_to_per_instance.items():
        if num_input_to == 0:
            input_class_type, input_class_instance = class_names
            
            mark_easiest_previous_attack(script_if, view, input_class_type, input_class_instance, colors[current_end_point])
            current_end_point += 1
            
def script_control(script_if):
    script_if.reset_script_changes()
    script_logic(script_if)
