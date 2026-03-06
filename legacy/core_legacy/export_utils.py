"""Export utilities: CSV, Excel, LaTeX and research-ready tables."""
import pandas as pd
from typing import Dict


def export_csv_summary(summary_dict: Dict[str, pd.DataFrame], path: str):
    for name, df in summary_dict.items():
        df.to_csv(f"{path}_{name}.csv")


def export_excel_workbook(summary_dict: Dict[str, pd.DataFrame], filepath: str):
    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        for sheet_name, df in summary_dict.items():
            df.to_excel(writer, sheet_name=sheet_name)


def dataframe_to_latex(df: pd.DataFrame, caption: str = '', label: str = '') -> str:
    return df.to_latex(index=False, caption=caption, label=label)
