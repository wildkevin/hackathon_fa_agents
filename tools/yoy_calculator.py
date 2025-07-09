"""Year-over-Year (YoY) calculation plugin for financial analysis.

This module provides tools for calculating year-over-year growth rates
and percentage changes for financial metrics.
"""

from typing import Annotated, Dict, Any
from semantic_kernel.functions import kernel_function
import json


class YoYCalculatorPlugin:
    """
    A plugin for calculating Year-over-Year (YoY) growth rates and changes.
    
    This plugin provides tools for financial analysis, specifically for
    calculating percentage changes between different time periods.
    """

    @kernel_function(
        name="calc_yoy",
        description="Calculate Year-over-Year (YoY) growth rate for financial metrics"
    )
    def calc_yoy(
        self,
        json_data: Annotated[str, "JSON string containing financial metrics with year data"],
        current_year: Annotated[str, "The current year to compare (e.g., '2024')"] = "2024",
        previous_year: Annotated[str, "The previous year to compare against (e.g., '2023')"] = "2023"
    ) -> Annotated[str, "JSON string with YoY calculations added"]:
        """
        Calculate Year-over-Year growth rate for financial metrics.
        
        Args:
            json_data: JSON string containing financial metrics with year data
            current_year: The current year to compare
            previous_year: The previous year to compare against
            
        Returns:
            JSON string with YoY calculations added
            
        Example:
            Input: '[{"Metric": "Revenue", "2023": "1000", "2024": "1200"}]'
            Output: '[{"Metric": "Revenue", "2023": "1000", "2024": "1200", "YoY_Growth": "20.0%"}]'
        """
        try:
            # Parse the JSON data
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            # Ensure data is a list
            if not isinstance(data, list):
                data = [data]
            
            # Calculate YoY for each metric
            for item in data:
                if isinstance(item, dict) and current_year in item and previous_year in item:
                    try:
                        current_value = float(str(item[current_year]).replace(',', ''))
                        previous_value = float(str(item[previous_year]).replace(',', ''))
                        
                        if previous_value != 0:
                            yoy_growth = ((current_value - previous_value) / previous_value) * 100
                            item["YoY_Growth"] = f"{yoy_growth:.1f}%"
                            item["YoY_Change"] = current_value - previous_value
                        else:
                            item["YoY_Growth"] = "N/A (Previous year was 0)"
                            item["YoY_Change"] = current_value
                    except (ValueError, TypeError):
                        item["YoY_Growth"] = "N/A (Invalid data)"
                        item["YoY_Change"] = "N/A"
                else:
                    if isinstance(item, dict):
                        item["YoY_Growth"] = f"N/A (Missing {current_year} or {previous_year} data)"
                        item["YoY_Change"] = "N/A"
            
            return json.dumps(data, indent=2)
            
        except json.JSONDecodeError:
            return json.dumps([{"error": "Invalid JSON format"}], indent=2)
        except Exception as e:
            return json.dumps([{"error": f"Calculation error: {str(e)}"}], indent=2)

    @kernel_function(
        name="calculate_growth_rate",
        description="Calculate growth rate between two values"
    )
    def calculate_growth_rate(
        self,
        current_value: Annotated[float, "Current period value"],
        previous_value: Annotated[float, "Previous period value"]
    ) -> Annotated[str, "Growth rate as percentage string"]:
        """
        Calculate growth rate between two values.
        
        Args:
            current_value: Current period value
            previous_value: Previous period value
            
        Returns:
            Growth rate as percentage string
            
        Example:
            >>> plugin = YoYCalculatorPlugin()
            >>> result = plugin.calculate_growth_rate(1200.0, 1000.0)
            >>> print(result)
            20.0%
        """
        if previous_value == 0:
            return "N/A (Previous value was 0)"
        
        growth_rate = ((current_value - previous_value) / previous_value) * 100
        return f"{growth_rate:.1f}%"

    @kernel_function(
        name="calculate_compound_growth",
        description="Calculate compound annual growth rate (CAGR)"
    )
    def calculate_compound_growth(
        self,
        beginning_value: Annotated[float, "Beginning value"],
        ending_value: Annotated[float, "Ending value"],
        number_of_years: Annotated[int, "Number of years"]
    ) -> Annotated[str, "CAGR as percentage string"]:
        """
        Calculate compound annual growth rate (CAGR).
        
        Args:
            beginning_value: Beginning value
            ending_value: Ending value
            number_of_years: Number of years
            
        Returns:
            CAGR as percentage string
            
        Example:
            >>> plugin = YoYCalculatorPlugin()
            >>> result = plugin.calculate_compound_growth(1000.0, 1500.0, 3)
            >>> print(result)
            14.5%
        """
        if beginning_value <= 0 or number_of_years <= 0:
            return "N/A (Invalid input values)"
        
        cagr = (pow(ending_value / beginning_value, 1 / number_of_years) - 1) * 100
        return f"{cagr:.1f}%"