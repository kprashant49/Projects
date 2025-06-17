import pandas as pd
from collections import defaultdict

# Input tables
table_a = pd.DataFrame({
    'id_a': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'A13', 'A14', 'A15'],
    'common_key': ['X', 'X', 'Y', 'Y', 'Y', 'Y', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z']
})

table_b = pd.DataFrame({
    'id_b': ['B1', 'B2', 'B3', 'B4', 'B5'],
    'common_key': ['X', 'X', 'Y', 'Z', 'Z']
})

# Pre-existing mapping counts
existing_counts = {
    'B1': 2,
    'B2': 0,
    'B3': 0,
    'B4': 5,
    'B5': 8
}

# Default to 0 if not in existing_counts
assignment_counter = defaultdict(int, existing_counts)

result = []

# Group A by common_key and assign to least-loaded B for that key
for idx, row in table_a.iterrows():
    key = row['common_key']

    # Get all matching B rows for this key
    b_group = table_b[table_b['common_key'] == key]['id_b'].tolist()

    # Find the B with minimum total load (existing + assigned)
    min_b = min(b_group, key=lambda b: assignment_counter[b])

    # Assign and update count
    assignment_counter[min_b] += 1

    result.append({
        'index': idx,
        'id_a': row['id_a'],
        'common_key': key,
        'id_b': min_b,
        'b_mapping_count': assignment_counter[min_b]
    })

# Final DataFrame sorted like table_a
mapped_df = pd.DataFrame(result).set_index('index').sort_index().reset_index(drop=True)

print(table_a)
print(table_b)
print(mapped_df)
