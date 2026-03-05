import os
import pandas as pd
import numpy as np
import json

def export_to_csv(data_dict, filename):
    """
    Utility function to export dict of metrics into a clean CSV table matching the research outputs.
    """
    filepath = os.path.join(os.path.dirname(__file__), 'v1_final_results', filename)
    df = pd.DataFrame([data_dict])
    df.to_csv(filepath, index=False)

def sanitize_json(data):
    """Recursively convert np.nan/pd.NA to None for valid JSON serialization."""
    if isinstance(data, dict):
        return {k: sanitize_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_json(v) for v in data]
    elif isinstance(data, float) and np.isnan(data):
        return None
    elif pd.isna(data):
        return None
    return data

def export_to_json(data_dict, filename):
    """
    Utility function to export a dict directly to cleanly formatted JSON.
    Applies strict NaN sanitization.
    """
    filepath = os.path.join(os.path.dirname(__file__), 'v1_final_results', filename)
    clean_data = sanitize_json(data_dict)
    with open(filepath, 'w') as f:
        json.dump(clean_data, f, indent=4)
