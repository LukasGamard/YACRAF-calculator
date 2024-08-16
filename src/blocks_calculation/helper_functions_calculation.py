import numpy as np
import sys
from helper_functions_general import convert_value_to_string, convert_string_to_value
from config import *
        
def check_input_value_types(symbol_calculation_type, input_attributes):
    """
    Checks that all the value types of all input attributes are allowed for the specific mathematical operation (calculation type)
    """
    if symbol_calculation_type == None:
        print(f"Error: Found calculation type {symbol_calculation_type}")
        return False
        
    elif symbol_calculation_type == SYMBOL_CALCULATION_TYPE_QUALITATIVE:
        return False
    
    # Allowed input value types when sampling triangle distributions
    elif symbol_calculation_type == SYMBOL_CALCULATION_TYPE_TRIANGLE:
        # Need to be exactly two input attributes
        if len(input_attributes) > 2:
            print(f"Error: More than 2 connected input attributes to input block with calculation type {symbol_calculation_type}")
            return False
            
        # All input values types must be triangle distributions
        for input_attribute in input_attributes:
            if input_attribute.get_symbol_value_type() != SYMBOL_VALUE_TYPE_TRIANGLE:
                print(f"Error: All connected input attributes did not have value type {input_attribute.get_symbol_value_type()} for calculation type {symbol_calculation_type}")
                return False
                
    # Check that all input attributes are of the same value type, unless it is multiplication
    if symbol_calculation_type != SYMBOL_CALCULATION_TYPE_MULTIPLICATION:
        for i in range(1, len(input_attributes)):
            if input_attributes[i].get_symbol_value_type() != input_attributes[i-1].get_symbol_value_type():
                print(f"Error: All connected input attributes did not have the same value type for input block with calculation type {symbol_calculation_type}")
                return False
                
    return True
    
def find_configuration_attribute_index(configuration_attributes, setup_attribute):
    """
    Returns the index of the attribute in a class whose configuration attribute has the specified setup attribute
    """
    for i, configuration_attribute in enumerate(configuration_attributes):
        if setup_attribute.has_configuration_attribute(configuration_attribute):
            return i
            
    return None
    
def apply_input_scalars(input_value, configuration_input_scalar, setup_input_scalars):
    """
    Applies input scalars from both the configuration and the setup
    """
    # Configuration input scalar is a single number
    if configuration_input_scalar != None:
        input_value *= configuration_input_scalar
        
    # Setup input scalar(s) is either a single number or a distribution
    if setup_input_scalars != None:
        if len(input_value) == 1 or len(setup_input_scalars) == 1 or len(input_value) == len(setup_input_scalars):
            # The number of values based on the one with the largest amount
            input_value = np.ones(max(len(input_value), len(setup_input_scalars))) * input_value * setup_input_scalars
            
        else:
            print(f"Error: The input value {input_value} and input scalar {setup_input_scalars} could not be multiplied, as at least one needs to be of length 1 or both of the same length")
            
    return input_value
    
def extract_input_values(symbol_calculation_type, input_configuration_attributes, input_setup_attributes, configuration_input_scalar=None, setup_input_scalars_per_attribute=None):
    """
    Returns the values that a setup attribute takes as input from connected setup classes
    """
    input_values = []
    input_symbol_value_type = ""
    
    # Sampling of triangle distribution need exactly two inputs, set default inputs
    if symbol_calculation_type == SYMBOL_CALCULATION_TYPE_TRIANGLE:
        input_values = [np.zeros(3), np.zeros(3)]
              
    for i, input_setup_attribute in enumerate(input_setup_attributes):
        input_symbol_value_type = input_setup_attribute.get_symbol_value_type()
        setup_input_scalars = setup_input_scalars_per_attribute[i]
        
        # Get currently active value
        if input_setup_attribute.has_override_value():
            input_value = input_setup_attribute.get_override_value()
        else:
            input_value = input_setup_attribute.get_value()
                    
        # There is a currently active value
        if input_value != None:
            if input_symbol_value_type == SYMBOL_VALUE_TYPE_NUMBER:
                try:
                    input_value = convert_string_to_value(input_value)
                    
                except:
                    print(f"Error: Could not cast {input_value} to float for {input_symbol_value_type} at attribute {input_setup_attribute.get_name()}")
                    return None
                    
                input_values.append(apply_input_scalars(np.array(input_value), configuration_input_scalar, setup_input_scalars))
                
            elif input_symbol_value_type == SYMBOL_VALUE_TYPE_TRIANGLE:
                try:
                    current_input_values = convert_string_to_value(input_value)
                    
                except:
                    print(f"Error: Could not cast the elements of {input_values} to float for {input_symbol_value_type} at attribute {input_setup_attribute.get_name()}")
                    return None
                    
                # Need to be exactly three values for triangle distribution
                if len(current_input_values) != 3:
                    print(f"Error: Not three values in {input_value} for {input_symbol_value_type} at attribute {input_setup_attribute.get_name()}")
                    return None
                    
                current_input_values = apply_input_scalars(np.array(current_input_values), configuration_input_scalar, setup_input_scalars)
                
                # Find and replace default input
                if symbol_calculation_type == SYMBOL_CALCULATION_TYPE_TRIANGLE:
                    input_values[find_configuration_attribute_index(input_configuration_attributes, input_setup_attribute)] = current_input_values
                else:
                    input_values.append(current_input_values)
            else:
                print(f"Error: Did not recognize the value type {input_symbol_value_type} at attribute {input_setup_attribute.get_name()}")
                return None
                                   
    return input_values
    
def calculate_output_value(symbol_calculation_type, input_values):
    """
    Calculate the output value considering specified input values and calculation type
    """
    # Mean calculation
    if symbol_calculation_type == SYMBOL_CALCULATION_TYPE_MEAN:
        output_value = np.mean(np.stack(input_values), axis=0)
        
    # AND calculation
    elif symbol_calculation_type == SYMBOL_CALCULATION_TYPE_AND:
        output_value = np.sum(np.stack(input_values), axis=0)
        
    # OR calculation
    elif symbol_calculation_type == SYMBOL_CALCULATION_TYPE_OR:
        output_value = np.min(np.stack(input_values), axis=0)
        
    # Multiplication calculation
    elif symbol_calculation_type == SYMBOL_CALCULATION_TYPE_MULTIPLICATION:
        output_value = np.ones(1)
        
        for input_value in input_values:
            # Found a value that is not a scalar, need to change the format of the output value
            if len(output_value) == 1 and len(input_value) > 1:
                output_value = np.ones(len(input_value)) * output_value
                
            output_value *= input_value
            
    # Comparing samples from two triangle distributions
    elif symbol_calculation_type == SYMBOL_CALCULATION_TYPE_TRIANGLE:
        sampled_values = []
        
        for input_value in input_values:
            a, b, c = input_value
            
            # If all values are equal, make one slightly different to avoid errors
            if a == b == c:
                a -= 1e-10
                
            # Sample current triangle distribution
            sampled_values.append(np.random.triangular(a, b, c, settings.get_num_samples()))
            
        # Compare samples
        output_value = [np.array(np.sum(sampled_values[0] > sampled_values[1]) / settings.get_num_samples())]
        
    else:
        print(f"Error: Did not recognized calculation type {symbol_calculation_type}")
        return None
        
    return output_value
    
def combine_values(symbol_calculation_type, symbol_value_type, input_configuration_attributes, input_setup_attributes, *, configuration_input_scalar=None, setup_input_scalars_per_attribute=None):
    """
    Returns a string of the combined and calculated output value based on input values from connected input attributes and the specified mathematical operations
    """
    if not check_input_value_types(symbol_calculation_type, input_setup_attributes):
        return None
        
    input_values = extract_input_values(symbol_calculation_type, input_configuration_attributes, input_setup_attributes, configuration_input_scalar=configuration_input_scalar, setup_input_scalars_per_attribute=setup_input_scalars_per_attribute)
    
    if input_values == None:
        print("Error: Could not extract input values")
        return None
        
    # Default values if no inputs
    if len(input_values) == 0:
        if symbol_value_type == SYMBOL_VALUE_TYPE_NUMBER:
            output_value = np.zeros(1)
            
        elif symbol_value_type == SYMBOL_VALUE_TYPE_TRIANGLE:
            output_value = np.zeros(3)
            
        else:
            print(f"Error: Did not recognized calculation type {symbol_calculation_type}")
            return None
            
    else:
        output_value = calculate_output_value(symbol_calculation_type, input_values)
        
    for check_symbol_value_type, check_text, check_num_values in ACTIVE_VALUE_TYPE_SYMBOLS_CONFIGS:
        if check_symbol_value_type == symbol_value_type:
            if check_num_values != None and check_num_values != len(output_value):
                print(f"Error: Found {len(output_value)} values, where value type {symbol_value_type} expected {check_num_values}")
                
            break
            
    return convert_value_to_string(output_value)
