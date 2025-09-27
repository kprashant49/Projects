import pandas as pd

# Load excel into dataframe
df = pd.read_excel("test_file.xlsx")

# Add is_new_key column
df["is_new_key"] = df["Key"] != df["Key"].shift()

# Add new_key_rows column (only fill when a new key appears)
df["new_key_rows"] = df["Key"].where(df["is_new_key"])

# df["max_in_key"] = df.groupby("Key")["Value"].transform("max")
# df["min_in_key"] = df.groupby("Key")["Value"].transform("min")

# Compute max, min, and sum for each key
agg = df.groupby("Key")["Value"].agg(
    max_in_key="max",
    min_in_key="min",
    sum_in_key="sum"
)

# Merge back, but only fill where it's a new key
df = df.merge(agg, on="Key", how="left")
df.loc[~df["is_new_key"], ["max_in_key", "min_in_key", "sum_in_key"]] = None


print(df)

# Get first value for each unique key
# first_vals = df.groupby("Key")["Value"].first().reset_index()

# Add "next" value by shifting
# first_vals["next_key"] = first_vals["Key"].shift(-1)
# first_vals["next_value"] = first_vals["Value"].shift(-1)

# Example operation: difference
# first_vals["diff"] = first_vals["next_value"] - first_vals["Value"]

# print(first_vals)

