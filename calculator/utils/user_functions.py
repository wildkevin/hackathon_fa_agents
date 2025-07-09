from typing import Any, Callable, Set, Annotated, List, Union
import math
import numexpr
import re


def calculator(
    expressions: Annotated[Union[str, List[str]], "A mathematical expression or list of mathematical expressions to be evaluated"]
) -> Annotated[str, "The evaluated results for all expressions"]:
    """Calculate mathematical expressions using Python's numexpr library.
    
    This function safely evaluates mathematical expressions including:
    - Basic arithmetic: +, -, *, /, **
    - Mathematical constants: pi, e
    
    :param expressions (Union[str, List[str]]): A mathematical expression or list of mathematical expressions to be evaluated.
                   Examples: "2 + 2", ["2 + 2", "3 * 4"], "37593 * 67"
    :rtype: str
    
    :return: The evaluated results formatted as "expression = result" for each expression, separated by newlines.
    :rtype: str
    
    Examples:
        >>> calculator("2 + 2")
        '2 + 2 = 4.00'
        
        >>> calculator(["2 + 2", "3 * 4"])
        '2 + 2 = 4.00\n3 * 4 = 12.00'
        
        >>> calculator("37593 * 67")
        '37593 * 67 = 2518731.00'
    """
    # Convert single string to list for consistent processing
    if isinstance(expressions, str):
        expressions = [expressions]
    
    # Define mathematical constants
    local_dict = {"pi": math.pi, "e": math.e}
    
    results = []
    
    for expression in expressions:
        # Clean the expression by removing comments
        raw_exp = expression.strip()
        expression_clean = re.sub(r'(?<!:)//.*|(?<!:)#.*', '', raw_exp)
        
        try:
            result = str(
                format(
                    numexpr.evaluate(
                        expression_clean,
                        global_dict={},  # Restrict access to globals for security
                        local_dict=local_dict  # Add mathematical constants
                    ), '.2f'
                )
            )
            results.append(f"{expression_clean} = {result}")
        except ZeroDivisionError:
            results.append(f"{expression_clean} = 0")
        except Exception as e:
            results.append(f"Error evaluating '{expression_clean}': {str(e)}")
    
    return "\n".join(results)


# Set of available user functions
user_functions: Set[Callable[..., Any]] = {
    calculator
}