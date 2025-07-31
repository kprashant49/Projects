import pandas as pd

# Example DataFrame
df = pd.DataFrame({
    'B': [1, 2],
    'A': [3, 4],
    'C': [5, 6],
    'D': [7, 8],
    'E': [9, 10]
})

print(df)
# Custom column order
column_order = ['A','B','C']  # Desired sequence

# Columns present in both the DataFrame and the standard list
main_cols = [col for col in column_order if col in df.columns]

# Columns not in the standard list
remaining_cols = [col for col in df.columns if col not in column_order]

# Split into two DataFrames
df_main = df[main_cols]
df_remaining = df[remaining_cols]

print(df_main)
print(df_remaining)
