import pandas as pd

# Sample MultiIndex DataFrame
index = pd.MultiIndex.from_tuples([
    ('A', 'one'), ('A', 'two'), ('B', 'one'), ('B', 'two')
], names=['Group', 'Subgroup'])

data = [[1, 2], [3, 4], [5, 6], [7, 8]]
my_table = pd.DataFrame(data, index=index, columns=['Col1', 'Col2'])
print(my_table)

# Compute per-group subtotals
subtotals = []
for group, df in my_table.groupby(level=0):
    subtotal = df.sum().to_frame().T  # Compute sum for the group
    subtotal.index = pd.MultiIndex.from_tuples([(group, 'Total')], names=my_table.index.names)
    subtotals.append(df)  # Original group data
    subtotals.append(subtotal)  # Add subtotal row

# Combine group data + subtotals
result = pd.concat(subtotals)

# Compute Grand Total
grand_total = my_table.sum().to_frame().T
grand_total.index = pd.MultiIndex.from_tuples([('Grand Total', '')], names=my_table.index.names)

# Final result with Grand Total
result = pd.concat([result, grand_total])

print(result)
