"""
Utility functions for creating LangChain-compatible tools
"""

import inspect
from typing import get_type_hints
from langchain_core.tools import tool

def create_string_input_tool(func, tool_name: str = None):
    """
    Creates a string-input wrapper for any multi-parameter function.
    
    Args:
        func: The original function to wrap
        tool_name: Optional name for the tool (defaults to func.__name__ + "_string")
    
    Returns:
        A LangChain tool that accepts a single string input
    """
    # Get function info
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    param_names = list(sig.parameters.keys())
    
    def string_wrapper(input_string: str):
        """Parse string input and call the original function."""
        try:
            # Parse the input string
            values = [v.strip() for v in input_string.split(',')]
            
            if len(values) != len(param_names):
                return f"Error: Expected {len(param_names)} comma-separated values, got {len(values)}"
            
            # Convert values to correct types
            parsed_args = []
            for i, value_str in enumerate(values):
                param_name = param_names[i]
                target_type = type_hints.get(param_name, str)
                
                if target_type is float:
                    parsed_args.append(float(value_str))
                elif target_type is int:
                    parsed_args.append(int(float(value_str)))
                else:
                    parsed_args.append(value_str)
            
            # Call original function
            return func(*parsed_args)
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    # Set wrapper properties with improved documentation
    wrapper_name = tool_name or f"{func.__name__}_string"
    string_wrapper.__name__ = wrapper_name
    
    # Create example format
    example_values = []
    for param_name in param_names:
        target_type = type_hints.get(param_name, str)
        if target_type is float:
            example_values.append("0.0")
        elif target_type is int:
            example_values.append("1")
        else:
            example_values.append(f"value_{param_name}")
    
    example_format = ", ".join(example_values)
    
    string_wrapper.__doc__ = f"""Function expects values {', '.join(param_names)} as a string, separated by commas, like this:

{example_format}"""
    
    return tool(string_wrapper)
