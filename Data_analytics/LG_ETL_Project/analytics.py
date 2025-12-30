def transform_df_a(df):
    """
    Transform sales_table data
    """
    df = df.copy()
    # df["amount"] = df["amount"].astype(int)
    return df


def transform_df_b(df):
    """
    Transform customer_table data
    """
    df = df.copy()
    # df["region"] = df["region"].str.upper()
    return df
