import numpy as np
from config import *
        
def check_input_value_types(symbol_calculation_type, input_attributes):
    if symbol_calculation_type == SYMBOL_CALCULATION_TYPE_TRIANGLE:
        if len(input_attributes) != 2:
            return False
            
        for input_attribute in input_attributes:
            if input_attribute.get_symbol_value_type() != SYMBOL_VALUE_TYPE_TRIANGLE:
                return False
                
    input_attributes_list = list(input_attributes)
    
    for i in range(1, len(input_attributes_list)):
        if input_attributes_list[i].get_symbol_value_type() != input_attributes_list[i-1].get_symbol_value_type():
            return False
            
    return True
            
def extract_input_values(input_attributes):
    input_values = []
    input_symbol_value_type = ""
    
    for input_attribute in input_attributes:
        input_symbol_value_type = input_attribute.get_symbol_value_type()
        
        if input_attribute.has_override_value():
            input_value = input_attribute.get_override_value()
        else:
            input_value = input_attribute.get_value()
            
        if input_value != None:
            if input_symbol_value_type == SYMBOL_VALUE_TYPE_NUMBER:
                try:
                    input_value_int = float(str(input_value).strip())
                    
                except:
                    print(f"Error: Could not cast {input_value} to float for {input_symbol_value_type}")
                    return None
                    
                input_values.append(np.array([input_value_int]))
                
            elif input_symbol_value_type == SYMBOL_VALUE_TYPE_TRIANGLE:
                try:
                    current_input_values = [int(value.strip()) for value in input_value.split("/")]
                    
                except:
                    print(f"Error: Could not cast the elements of {input_values} to int for {input_symbol_value_type}")
                    return None
                    
                if len(current_input_values) != 3:
                    print(f"Error: Not three values in {input_values} for {input_symbol_value_type}")
                    return None
                    
                input_values.append(np.array(current_input_values))
                
            else:
                print(f"Error: Did not recognize the value type {input_symbol_value_type}")
                return None
            
    return input_values
    
def combine_values(symbol_calculation_type, symbol_value_type, input_attributes):
    if not check_input_value_types(symbol_calculation_type, input_attributes):
        print("Error: Incorrect input")
        return None
        
    input_values = extract_input_values(input_attributes)
    
    if input_values == None:
        print("Error: Could not extract input values")
        return None
        
    # Default values if no inputs
    if len(input_values) == 0:
        if symbol_calculation_type in (SYMBOL_CALCULATION_TYPE_MEAN, SYMBOL_CALCULATION_TYPE_AND, SYMBOL_CALCULATION_TYPE_OR):
            output_values = [0]
            
        elif symbol_calculation_type == SYMBOL_CALCULATION_TYPE_TRIANGLE:
            output_values = [0, 0, 0]
            
        else:
            print(f"Error: Did not recognized calculation type {symbol_calculation_type}")
            return None
    else:
        # Mean calculation
        if symbol_calculation_type == SYMBOL_CALCULATION_TYPE_MEAN:
            output_values = np.mean(np.stack(input_values), axis=0)
            
        # AND calculation
        elif symbol_calculation_type == SYMBOL_CALCULATION_TYPE_AND:
            output_values = np.sum(np.stack(input_values), axis=0)
            
        # OR calculation
        elif symbol_calculation_type == SYMBOL_CALCULATION_TYPE_OR:
            output_values = np.max(np.stack(input_values), axis=0)
            
        # Multiplication calculation
        elif symbol_calculation_type == SYMBOL_CALCULATION_TYPE_MULTIPLICATION:
            output_values = np.prod(np.stack(input_values), axis=0)
            
        # Comparing samples from two triangle distributions
        elif symbol_calculation_type == SYMBOL_CALCULATION_TYPE_TRIANGLE:
            sampled_values = []
            
            for input_value in input_values:
                sampled_values.append(np.random.triangular(input_value[0], input_value[1], input_value[2], SAMPLES_TRIANGLE_DISTRIBUTION))
                
            output_values = str(float(np.sum(sampled_values[0] > sampled_values[1])) / SAMPLES_TRIANGLE_DISTRIBUTION)
            
        else:
            print(f"Error: Did not recognized calculation type {symbol_calculation_type}")
            return None
            
    # Format output
    if symbol_value_type == SYMBOL_VALUE_TYPE_NUMBER:
        output_values = str(float(output_values[0]))
        
    elif symbol_value_type == SYMBOL_VALUE_TYPE_TRIANGLE:
        output_values = " / ".join([str(float(output_value)) for output_value in output_values])
        
    else:
        print(f"Error: Did not recognized value type {symbol_value_type}")
        return None
        
    return output_values
