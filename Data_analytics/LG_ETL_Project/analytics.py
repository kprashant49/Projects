import os
import pandas as pd
from datetime import datetime

def transform_df_a(df):
    """
    Transform a data
    """
    df = df.copy()
    # df["amount"] = df["amount"].astype(int)
    return df

def transform_df_b(df):
    """
    Transform b data
    """
    df = df.copy()
    # df["region"] = df["region"].str.upper()
    return df

def transform_df_c(df):
    """
    Transform c data (for attachment)
    """
    df = df.copy()
    # df["created_at"] = df["created_at"].astype(str)
    return df

def transform_df_d(df):
    """
    Transform d data (for attachment)
    """
    df = df.copy()
    # df["created_at"] = df["created_at"].astype(str)
    return df

def export_dataframes_to_excel(dfs: dict, client_name: str):
    """
    Exports multiple DataFrames to a single Excel file under
    'Exported Files' folder in the project root.

    dfs: {
        "SheetName1": df1,
        "SheetName2": df2,
        ...
    }
    """

    # -------------------------
    # Resolve project root
    # -------------------------
    project_root = os.path.dirname(os.path.abspath(__file__))

    export_dir = os.path.join(project_root, "Exported Files")
    os.makedirs(export_dir, exist_ok=True)

    # -------------------------
    # Build filename
    # -------------------------
    safe_client_name = client_name.replace(" ", "_")
    date_str = datetime.now().strftime("%Y%m%d")

    file_name = f"analytics_output_{safe_client_name}_{date_str}.xlsx"
    file_path = os.path.join(export_dir, file_name)

    # -------------------------
    # Write Excel
    # -------------------------
    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

    return file_path