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

import os
from datetime import datetime

def export_dataframes_to_excel(dfs: dict, filename_prefix="analytics_output"):
    """
    Exports multiple DataFrames to a single Excel file.

    dfs: {
        "SheetName1": df1,
        "SheetName2": df2,
        ...
    }
    """

    base_dir = os.path.dirname(os.path.abspath(__file__))
    date_str = datetime.now().strftime("%Y%m%d")

    file_path = os.path.join(
        base_dir,
        f"{filename_prefix}_{date_str}.xlsx"
    )

    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

    return file_path
