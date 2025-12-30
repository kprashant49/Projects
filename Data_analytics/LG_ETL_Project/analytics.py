def transform_sales(df):
    """
    Transform sales_table data
    """
    df = df.copy()
    # df["amount"] = df["amount"].astype(int)
    return df


def transform_customers(df):
    """
    Transform customer_table data
    """
    df = df.copy()
    # df["region"] = df["region"].str.upper()
    return df
