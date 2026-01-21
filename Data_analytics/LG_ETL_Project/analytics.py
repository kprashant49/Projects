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
    df_new = df[['Product', 'ApplicationStatus']].copy()
    df_new['cnt'] = 1

    product_sampling = pd.pivot_table(
        df_new,
        index='Product',
        columns='ApplicationStatus',
        values='cnt',
        aggfunc='sum',
        fill_value=0,
        margins=True,  # adds Grand Total
        margins_name='Grand Total'
    )

    product_sampling2 = pd.pivot_table(
        df_new,
        index='Product',
        columns='ApplicationStatus',
        values='cnt',
        aggfunc='sum',
        fill_value=0,
        margins=True,
        margins_name='Grand Total'
    )

    # calculate percentage WITHOUT Grand Total
    product_sampling_pct = product_sampling2.div(product_sampling.drop(columns='Grand Total').sum(axis=1),axis=0).mul(100).round(2)

    df['tat_bucket'] = pd.cut(
        df['TAT In Minutes'],
        bins=[-1, 15, 30, float('inf')],
        labels=['<15 Min', '<30 Min', '>=30 Min']
    )

    tat_pivot = pd.pivot_table(
        df,
        index='Product',
        columns='tat_bucket',
        values='TAT In Minutes',
        aggfunc='count',
        fill_value=0,
        margins=True,
        margins_name='Grand Total'
    )

    tat_pct = tat_pivot.div(tat_pivot.drop(columns='Grand Total').sum(axis=1),axis=0).mul(100).round(2)

    final_df = (product_sampling.add_prefix('Status_')
        .join(product_sampling_pct.add_prefix('Status_').add_suffix(' (%)'))
        .join(tat_pivot.add_prefix('TAT_'))
        .join(tat_pct.add_prefix('TAT_').add_suffix(' (%)')))

    final_df = final_df.reset_index()

    cols_to_drop = [
        "Status_Grand Total (%)",
        "TAT_Grand Total (%)"
    ]

    final_df = final_df.drop(
        columns=[c for c in cols_to_drop if c in final_df.columns]
    )

    return final_df

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