# pylint: disable=line-too-long,useless-suppression

import json
import datetime
from typing import Any, Callable, Set, Dict, List, Optional
import re
import numpy as np
import pandas as pd

# These are the user-defined functions that can be called by the agent.

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
    calc_yoy
}
