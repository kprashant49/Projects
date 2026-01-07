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