import os
import pandas as pd
from datetime import datetime

def transform_df_a(df):
    """
    Transform a data
    """
    df = df.copy()
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
        .join(product_sampling_pct.add_prefix('Status_').add_suffix(' %'))
        .join(tat_pivot.add_prefix('TAT_'))
        .join(tat_pct.add_prefix('TAT_').add_suffix(' %')))

    final_df = final_df.reset_index()

    cols_to_drop = [
        "Status_Grand Total %",
        "TAT_Grand Total %"
    ]

    final_df = final_df.drop(
        columns=[c for c in cols_to_drop if c in final_df.columns]
    )

    # ----------------------------------------
    # Format TAT % columns as percentage strings
    # ----------------------------------------
    tat_pct_cols = [
        c for c in final_df.columns
        if c.startswith("TAT_") and c.endswith(" %")
    ]

    for col in tat_pct_cols:
        final_df[col] = final_df[col].round(0).astype(int).astype(str) + "%"

    # ----------------------------------------
    # Format Status % columns as percentage strings
    # ----------------------------------------
    status_pct_cols = [
        c for c in final_df.columns
        if c.startswith("Status_") and c.endswith(" %")
    ]

    for col in status_pct_cols:
        final_df[col] = final_df[col].round(0).astype(int).astype(str) + "%"

    return final_df

def transform_df_b_1(df):
    """
    Builds Working Hours vs Process summary with TAT buckets,
    subtotals, grand total, and row-wise percentages.
    """

    df = df.copy()
    df["Process"] = df["Processed By"].str.strip().str.lower()
    df["Process"] = df["Process"].apply(lambda x: "Auto" if "auto" in x else "Regular")

    df = df.copy()
    df["WorkingHours"] = df["Working Hours"].str.strip().str.lower()
    df["WorkingHours"] = df["WorkingHours"].apply(lambda x: "Working Hours" if "9:30" in x else "Non Working Hours")

    df['tat_bucket'] = pd.cut(
        df['TAT In Minutes'],
        bins=[-1, 15, 30, float('inf')],
        labels=['<15 Min', '<30 Min', '>=30 Min']
    )

    base_pivot = pd.pivot_table(
        df,
        index=["WorkingHours", "Process"],
        columns="tat_bucket",
        values="TAT In Minutes",
        aggfunc="count",
        fill_value=0
    )

    base_pivot["Grand Total"] = base_pivot.sum(axis=1)
    subtotals = (base_pivot.groupby(level=0).sum())
    subtotals.index = [f"{idx} Total" for idx in subtotals.index]

    final_rows = []

    for wh in base_pivot.index.get_level_values(0).unique():
        final_rows.append(base_pivot.loc[wh])
        final_rows.append(subtotals.loc[f"{wh} Total"].to_frame().T)

    final_df2 = pd.concat(final_rows)

    grand_total = pd.DataFrame(base_pivot.sum()).T
    grand_total.index = ["Grand Total"]

    final_df2 = pd.concat([final_df2, grand_total])

    pct_df = (
        final_df2[["<15 Min", "<30 Min", ">=30 Min"]]
        .div(final_df2["Grand Total"], axis=0)
        .mul(100)
        .round(0)
    )
    pct_df = pct_df.astype(int).astype(str) + "%"

    pct_df.columns = ["<15 MIN %", "<30 MIN %", ">=30 MIN %"]

    final_df2 = pd.concat([final_df2, pct_df], axis=1)
    final_df2 = final_df2.reset_index()
    final_df2 = final_df2.rename(columns={"index": "Process-WorkingHours_TAT"})

    return final_df2


def transform_df_b_2(df):
    """
    Builds Working Days counts.
    """

    df = df.copy()
    df["Day wise Count of cases"] = df["Day"].apply(
        lambda x: "Holiday" if x.strip().lower() == "sunday" else "Regular"
    )

    day_type_counts = (
        df["Day wise Count of cases"]
        .value_counts()
        .reset_index()
    )

    day_type_counts.columns = ["Day wise Count of cases", "Counts"]

    grand_total = pd.DataFrame({
        "Day wise Count of cases": ["Grand Total"],
        "Counts": [day_type_counts["Counts"].sum()]
    })

    day_type_counts = pd.concat([day_type_counts, grand_total], ignore_index=True)

    return day_type_counts


def transform_df_c(df):
    """
    Transform c data
    """
    df = df.copy()
    return df

def transform_df_d(df):
    """
    Transform d data
    """
    df = df.copy()
    return df

def transform_df_e(df):
    """
    Transform e data
    """
    df = df.copy()

    # FIX Reprocessed FIRST (remove .0)
    df['Reprocessed'] = df['Reprocessed'].astype('Int64').astype(str)

    # add grand total row
    df.loc['Grand Total', ['Count of Cases', 'Total']] = (
        df[['Count of Cases', 'Total']].sum()
    )

    # keep numeric columns as integers
    df[['Count of Cases', 'Total']] = df[['Count of Cases', 'Total']].astype('Int64')

    # set label explicitly
    df.loc['Grand Total', 'Reprocessed'] = 'Grand Total'

    return df

def transform_df_f(df):
    """
    Transform f data
    """
    df = df.copy()
    return df

def transform_df_g(df):
    """
    Transform g data
    """
    df = df.copy()

    df["Final_Trigger"] = (df["Final_Trigger"]
        .str.replace(r"\{.*?\}", "", regex=True)  # remove {anything}
        .str.replace(r"\s{2,}", " ", regex=True)  # collapse extra spaces
        .str.strip())

    agg = (df.groupby(["Final_Severity", "RuleID", "Final_Trigger"])
        .size()
        .reset_index(name="Count of Trigger"))

    top10 = (agg.sort_values(["Final_Severity", "Count of Trigger"],
            ascending=[True, False]
        ).groupby("Final_Severity").head(10))

    final_rows = []

    for severity, group in top10.groupby("Final_Severity", sort=False):
        # Severity header row
        final_rows.append({
            "RuleID": "",
            "Final_Trigger": severity,
            "Count of Trigger": ""
        })

        # Actual trigger rows
        for _, row in group.iterrows():
            final_rows.append({
                "RuleID": row["RuleID"],
                "Final_Trigger": row["Final_Trigger"],
                "Count of Trigger": row["Count of Trigger"]
            })

    final_df = pd.DataFrame(final_rows)

    return final_df

def get_export_file_path(client_name: str, prefix: str):
    """
    Builds export directory and filename.
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(project_root, "Exported Files")
    os.makedirs(export_dir, exist_ok=True)

    safe_client_name = client_name.replace(" ", "_")
    date_str = datetime.now().strftime("%Y%m%d")

    file_name = f"{prefix}_{safe_client_name}_{date_str}.xlsx"
    return os.path.join(export_dir, file_name)



def export_dataframes_to_excel(dfs: dict, client_name: str):
    """
    Exports multiple DataFrames to a single Excel file.
    """
    file_path = get_export_file_path(
        client_name=client_name,
        prefix="analytics_output"
    )

    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

    return file_path


def export_single_dataframe_to_excel(df, client_name: str):
    """
    Export a single DataFrame (raw data) to Excel.
    """
    file_path = get_export_file_path(
        client_name=client_name,
        prefix="raw_data"
    )

    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Raw_Data", index=False)

    return file_path

