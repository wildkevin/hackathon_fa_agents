from typing import Any, Callable, Set, Annotated
import math
import numexpr
import re


def calculator(
    expression: Annotated[str, "A mathematical expression to be evaluated"]
) -> Annotated[str, "The evaluated result for the expression"]:
    """
    Calculate a mathematical expression using Python's numexpr library.
    
    This function safely evaluates mathematical expressions including:
    - Basic arithmetic: +, -, *, /, **
    - Mathematical constants: pi, e
    - Functions: sin, cos, tan, log, sqrt, etc.
    
    Args:
        expression: A single-line mathematical expression to be evaluated.
                   Examples: "2 + 2", "37593 * 67", "sin(pi/2)", "sqrt(16)"
    
    Returns:
        The evaluated result formatted as "expression = result"
    
    Examples:
        >>> calculator("2 + 2")
        '2 + 2 = 4.00'
        
        >>> calculator("37593 * 67")
        '37593 * 67 = 2518731.00'
        
        >>> calculator("sin(pi/2)")
        'sin(pi/2) = 1.00'
        
        >>> calculator("sqrt(16)")
        'sqrt(16) = 4.00'
        
        >>> calculator("10 / 0")
        '10 / 0 = 0'
    """
    # Define mathematical constants
    local_dict = {"pi": math.pi, "e": math.e}
    
    # Clean the expression by removing comments
    raw_exp = expression.strip()
    expression_clean = re.sub(r'(?<!:)//.*|(?<!:)#.*', '', raw_exp)
    
    try:
        result = str(
            format(
                numexpr.evaluate(
                    expression_clean,
                    global_dict={},  # Restrict access to globals for security
                    local_dict=local_dict  # Add mathematical functions and constants
                ), '.2f'
            )
        )
        return f"{expression_clean} = {result}"
    except ZeroDivisionError:
        return f"{expression_clean} = 0"
    except Exception as e:
        return f"Error evaluating '{expression_clean}': {str(e)}"


# Set of available user functions
user_functions: Set[Callable[..., Any]] = {
    calculator
}