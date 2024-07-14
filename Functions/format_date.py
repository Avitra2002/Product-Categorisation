#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from datetime import datetime

def format_date(date_str):
    # Check if it's NaN or float first
    if pd.isna(date_str) or isinstance(date_str, float):
        return date_str  # Return NaN or float as-is
    
    # Convert to string and strip any whitespace
    date_str = str(date_str).strip()
    
    # Try to parse the date assuming it's in the format '22/4/2024 15:43'
    try:
        date_obj = datetime.strptime(date_str, '%d/%m/%Y %H:%M')
        formatted_date = date_obj.strftime('%d/%m/%Y')
        return formatted_date
    except ValueError:
        pass
    
    # Try to parse the date assuming it's in the format '22/04/24'
    try:
        date_obj = datetime.strptime(date_str, '%d/%m/%y')
        formatted_date = date_obj.strftime('%d/%m/%y')
        return formatted_date
    except ValueError:
        pass
    
    # Try to parse the date assuming it's in the format '22/04/2024'
    try:
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        formatted_date = date_obj.strftime('%d/%m/%y')
        return formatted_date
    except ValueError:
        pass

    # If all parsing attempts fail, raise an error
    raise ValueError(f"Date string '{date_str}' is not in a recognized format.")

