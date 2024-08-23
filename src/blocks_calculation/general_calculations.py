import numpy as np
from helper_functions_general import convert_value_to_string, convert_string_to_value

def combine_values(value_type, calculation_type, input_setup_attributes, setup_input_scalars_per_attribute, configuration_attribute, num_samples):
    calculated_value = value_type.default_value()
    input_values = []
    
    number_of_inputs = calculation_type.number_of_inputs()
    
    # Missing connected setup attributes for the given calculation type to be correctly calculated
    if number_of_inputs != None and len(input_setup_attributes) != number_of_inputs:
        return "-"
        
    for i, input_setup_attribute in enumerate(input_setup_attributes):
        input_value_type = input_setup_attribute.get_value_type()
        input_value_string = input_setup_attribute.get_current_value()
        
        if input_value_string == "-":
            return "-"
        
        value = input_value_type.extract_input_value(input_value_string)
        
        if value == None:
            return "ERROR"
            
        value = np.array(value)
        setup_input_scalars = setup_input_scalars_per_attribute[i]
        
        if setup_input_scalars != None:
            value = apply_setup_input_scalars(value, np.array(setup_input_scalars), input_value_type.allowed_number_of_scalars())
            
        input_values.append(value)
        
    if len(input_values) > 0:
        calculated_value = calculation_type.calculate_output_value(input_values, num_samples) * configuration_attribute.get_input_scalar() + configuration_attribute.get_input_offset()
        
    return convert_value_to_string(calculated_value)
    
def get_attribute_value_types(configuration_attributes):
    value_types = []
    
    for configuration_attribute in configuration_attributes:
        value_types.append(configuration_attribute.get_value_type())
        
    return value_types
    
def apply_setup_input_scalars(values, input_scalars, allowed_scalar_values):
    if len(input_scalars) in allowed_scalar_values:
        values *= input_scalars
    else:
        print(f"Warning: Could not apply input setup scalars {input_scalars} to {values}, expected a number of values equal to a value in {allowed_scalar_values}")
    return values
    
class ValueTypeString:
    @staticmethod
    def symbol():
        return None
        
    @staticmethod
    def explaination():
        return "Simple text (no calculations)"
        
    @staticmethod
    def default_text():
        return "Text"
        
    @staticmethod
    def correctly_connected(calculation_type, input_configuration_attributes):
        if calculation_type == CalculationTypeQualitative:
            return True
            
        elif calculation_type != None:
            print(f"Warning: Attribute value type \"Simple text\" does not support calculation type {calculation_type.symbol()}")
            return False
            
        return True
        
class ValueTypeNumber:
    @staticmethod
    def symbol():
        return "N"
        
    @staticmethod
    def explaination():
        return "Number (integer or float)"
        
    @staticmethod
    def default_text():
        return "Number"
        
    @staticmethod
    def default_value():
        return np.zeros(1)
        
    @staticmethod
    def allowed_number_of_scalars():
        return (1,)
        
    @staticmethod
    def correctly_connected(calculation_type, input_configuration_attributes):
        if calculation_type == CalculationTypeQualitative:
            return True
            
        elif calculation_type in (CalculationTypeSampleTriangle, CalculationTypeQualitative):
            return True
            
        for input_value_type in get_attribute_value_types(input_configuration_attributes):
            if input_value_type != ValueTypeNumber:
                print(f"Warning: Attribute value type N does not support {input_value_type.symbol()} as input")
                return False
                
        return True
        
    @staticmethod
    def extract_input_value(input_value_string):
        value = None
        
        try:
            value = [float(input_value_string)]
        except:
            print(f"Warning: Could not convert {input_value_string} to float for the attribute value type {ValueTypeNumber.symbol()}")
            
        return value
        
class ValueTypeTriangleDistribution:
    @staticmethod
    def symbol():
        return "T"
        
    @staticmethod
    def explaination():
        return "Triangle distribution (a / b / c)"
        
    @staticmethod
    def default_text():
        return "a / b / c"
        
    @staticmethod
    def default_value():
        return np.zeros(3)
        
    @staticmethod
    def allowed_number_of_scalars():
        return (1, 3)
        
    @staticmethod
    def correctly_connected(calculation_type, input_configuration_attributes):
        if calculation_type == CalculationTypeQualitative:
            return True
            
        elif calculation_type == CalculationTypeSampleTriangle:
            print(f"Warning: Attribute value type {ValueTypeTriangleDistribution.symbol()} does not support the calculation type {calculation_type.symbol()}")
            return False
            
        elif calculation_type == CalculationTypeMultiplication:
            for input_value_type in get_attribute_value_types(input_configuration_attributes):
                if input_value_type == ValueTypeTriangleDistribution:
                    return True
                    
            print(f"Warning: Attribute value type {ValueTypeTriangleDistribution.symbol()} with the calculation type {calculation_type.symbol()} requires at least one input to be of type {ValueTypeTriangleDistribution.symbol()}")
            return False
            
        return True
        
    @staticmethod
    def extract_input_value(input_value_string):
        value = None
        
        try:
            value = convert_string_to_value(input_value_string)
            
            if len(value) != 3:
                print(f"Warning: Did not find three values in {value}, derived from {input_value_string} for the attribute value type {ValueTypeTriangleDistribution.symbol()}")
                
        except:
            print(f"Warning: Could not convert each element delimited by \"/\" in {input_value_string} to float for the attribute value type {ValueTypeTriangleDistribution.symbol()}")
            
        return value
        
class CalculationType:
    @staticmethod
    def number_of_inputs():
        """
        Returns the number of inputs this calculation type requires, where the order of inputs also matters (the appearing number at each connection)
        Returns None if the inputs are not enumerated and their order does not matter
        """
        return None
        
    @staticmethod
    def correct_input_attribute_value_types(input_configuration_attributes):
        """
        Checks that the input attribute value types are valid for this calculation type
        """
        # Check that all input attribute value types are of the same type
        last_type = None
        
        for input_value_type in get_attribute_value_types(input_configuration_attributes):
            if last_type != None and last_type != input_value_type:
                print(f"Warning: All input attributes in configuration were not of the same value type, found {get_attribute_value_types(input_configuration_attributes)}")
                return False
                
            last_type = input_value_type
            
        return True
        
class CalculationTypeMean(CalculationType):
    @staticmethod
    def symbol():
        return "M"
        
    @staticmethod
    def explaination():
        return "Mean"
        
    @staticmethod
    def calculate_output_value(input_values, num_samples):
        return np.mean(np.stack(input_values), axis=0)
        
class CalculationTypeAND(CalculationType):
    @staticmethod
    def symbol():
        return "&"
        
    @staticmethod
    def explaination():
        return "AND (addition)"
        
    @staticmethod
    def calculate_output_value(input_values, num_samples):
        return np.sum(np.stack(input_values), axis=0)
        
class CalculationTypeOR(CalculationType):
    @staticmethod
    def symbol():
        return "|"
        
    @staticmethod
    def explaination():
        return "OR (minimum)"
        
    @staticmethod
    def calculate_output_value(input_values, num_samples):
        return np.min(np.stack(input_values), axis=0)
        
class CalculationTypeMultiplication(CalculationType):
    @staticmethod
    def symbol():
        return "*"
        
    @staticmethod
    def explaination():
        return "Multiplication"
        
    @staticmethod
    def correct_input_attribute_value_types(input_configuration_attributes):
        return True
        
    @staticmethod
    def calculate_output_value(input_values, num_samples):
        output_value = np.ones(1)
        
        for input_value in input_values:
            # Found a value that is not a scalar, need to change the format of the output value
            if len(output_value) == 1 and len(input_value) > 1:
                output_value = np.ones(len(input_value)) * output_value
                
            output_value *= input_value
            
        return output_value
        
class CalculationTypeDivision(CalculationType):
    @staticmethod
    def symbol():
        return "/"
        
    @staticmethod
    def explaination():
        return "Division between two values, (1) / (2)"
        
    @staticmethod
    def number_of_inputs():
        return 2
        
    @staticmethod
    def correct_input_attribute_value_types(input_configuration_attributes):
        value_types = get_attribute_value_types(input_configuration_attributes)
        
        if len(value_types) > CalculationTypeDivision.number_of_inputs():
            print(f"Warning: Calculation type {CalculationTypeDivision.symbol()} require exactly {CalculationTypeDivision.number_of_inputs()} input attributes in the configuration")
            return False
            
class CalculationTypeSampleTriangle(CalculationType):
    @staticmethod
    def symbol():
        return "T"
        
    @staticmethod
    def explaination():
        return "Sample two triangle distributions, ratio of (1) > (2)"
        
    @staticmethod
    def number_of_inputs():
        return 2
        
    @staticmethod
    def correct_input_attribute_value_types(input_configuration_attributes):
        # Only triangle distributions allowed as input, with at most two inputs
        if CalculationType.correct_input_attribute_value_types(input_configuration_attributes):
            if len(input_configuration_attributes) == 0:
                return True
                
            elif len(input_configuration_attributes) <= CalculationTypeSampleTriangle.number_of_inputs() and input_configuration_attributes[0].get_value_type() == ValueTypeTriangleDistribution:
                return True
                
            print(f"Warning: All input attributes for calculation type {CalculationTypeSampleTriangle.symbol()} need to be of value type {ValueTypeTriangleDistribution.symbol()} in the configuration")
                
        else:
            print(f"Warning: Calculation type {CalculationTypeSampleTriangle.symbol()} require exactly {CalculationTypeSampleTriangle.number_of_inputs()} input attributes in the configuration")
            
        return False
        
    @staticmethod
    def calculate_output_value(input_values, num_samples):
        sampled_values = []
        
        for input_value in input_values:
            a, b, c = input_value
            
            # If all values are equal, make one slightly different to avoid errors
            if a == b == c:
                a -= 1e-10
                
            # Sample current triangle distribution
            sampled_values.append(np.random.triangular(a, b, c, num_samples))
            
        # Compare samples
        return np.array([np.array(np.sum(sampled_values[0] > sampled_values[1]) / num_samples)])
        
class CalculationTypeQualitative(CalculationType):
    @staticmethod
    def symbol():
        return "Q"
        
    @staticmethod
    def explaination():
        return "Manual and qualitative evaluation"

