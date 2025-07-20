# pylint: disable=line-too-long,useless-suppression

import json
import datetime
from typing import Any, Callable, Set, Dict, List, Optional, Annotated
import re
import numpy as np
import pandas as pd
import math
import numexpr

# These are the user-defined functions that can be called by the agent.

def calc_formula(
        expression: Annotated[str, "A mathematical expression to be evaluated"]
) -> Annotated[str, "The evaluated result for the expression"]:
    """
    Calculate a mathematical expression using Python's numexpr library.

    Args:
        expression: A single-line mathematical expression to be evaluated. Example: "37593 * 67" for "37593 times 67".

    Returns:
        The evaluated result for the expression, formatted as "expression = result".

    # Example:
    #     >>> result = calc_formula("2 + 2")
    #     >>> print(result)
    #     '2 + 2 = 4.00'
    """
    local_dict = {"pi": math.pi, "e": math.e}
    raw_exp = expression.strip()
    expression_clean = re.sub(r'(?<!:)//.*|(?<!:)#.*', '', raw_exp)
    try:
        result = str(
            format(
                numexpr.evaluate(
                    expression_clean,
                    global_dict={},  # restrict access to globals
                    local_dict=local_dict  # add common mathematical functions
                ), '.2f'
            )
        )
        return expression_clean + " = " + result
    except ZeroDivisionError:
        return expression_clean + " = 0"


def calc_yoy(data: str) -> str:
    """
    Calculate the Year-over-Year (YOY) value for each metric.
    :param data: The value for each metric in three years;.
    :return: YOY results and material change information as a JSON string.
    """
    data = json.loads(data)
    df = pd.DataFrame(data)
    cols = df.columns.tolist()
    years = sorted([item for item in cols if re.fullmatch(r'\d{4}', item)])
    for y in years:
        df[y] = df[y].astype(float)
    # calculate the YOY by last two years
    year_1st = years[0]
    year_2nd = years[1]
    year_3rd = years[2]
    df["YOY"] = (df[year_3rd] - df[year_2nd]) / np.abs(df[year_2nd])
    df["YOY_lag1"] = (df[year_2nd] - df[year_1st]) / np.abs(df[year_1st])
    df['abs_YOY'] = df['YOY'].abs()
    df = df.sort_values(['abs_YOY'], ascending=[False])
    mc = df[df['abs_YOY'] >= 0.05]
    df = df.drop(columns=['abs_YOY'])
    mc = mc.drop(columns=['abs_YOY'])
    results = df.to_dict(orient='records')
    mc = mc.to_dict(orient='records')
    return json.dumps({"YOY": results, "MC": mc})


user_functions: Set[Callable[..., Any]] = {
    calc_formula,
    calc_yoy
}


if __name__ == '__main__':
    # Test the calc_formula function
    print(calc_formula("2 + 2"))
    print(calc_formula("37593 * 67"))
    print(calc_formula("3.14 * 2"))

    # Test the calc_yoy function
    test_data = json.dumps(
        [{"Metric": "Inventory", "2022": "2339", "2023": "2510", "2024": "2632"},
        {"Metric": "Cash", "2022": "2345", "2023": "2465", "2024": "346"}])
    print(calc_yoy(test_data))