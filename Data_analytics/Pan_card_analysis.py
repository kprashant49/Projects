import pandas as pd
from statistics import mode

# file_path = r"C:\Users\PrashantKumar\OneDrive - Pepper India Resolution Private Limited\Desktop\Pan_Series_Analysis.xlsx"  # Issue date
file_path = r"C:\Users\PrashantKumar\OneDrive - Pepper India Resolution Private Limited\Desktop\Pan_issue_dob_analysis.xlsx" # Date of Birth
df = pd.read_excel(file_path, sheet_name="Sheet1", engine="openpyxl")

# df = df.dropna(subset=['PanIssuedate', 'One'])       # for Issue date with combi of only "One" column
# df = df.dropna(subset=['PanIssuedate', 'Series'])    # for Issue date with combi of "Series" column
df = df.dropna(subset=['Backdatedyear', 'Series_1'])               # for YOB/Series

# df['PanIssuedate'] = df['PanIssuedate'].astype(int)
df['Backdatedyear'] = df['Backdatedyear'].astype(int)

result = []
for category, group in df.groupby('Series_1'):
# for category, group in df.groupby('Series'):
    min_val = group['Backdatedyear'].min()
    max_val = group['Backdatedyear'].max()
    avg_val = round(group['Backdatedyear'].mean())
    median_val = int(group['Backdatedyear'].median())
    mode_val = group['Backdatedyear'].mode().tolist()
    # count_val = len(group)
    
    # try:
    #     mode_val = mode(group['PanIssuedate'])
    # except:
    #     mode_val = group['PanIssuedate'].mode().tolist()
    
    result.append({
        'Category': category,
        # 'Count': count_val,
        'Min': min_val,
        'Max': max_val,
        'Average': round(avg_val, 2),
        'Median': median_val,
        'Mode': mode_val
    })

stats_df = pd.DataFrame(result).set_index('Category')
trimmed = file_path.rstrip(".xlsx")
output_file = f"{trimmed}_stats.xlsx"

stats_df.to_excel(output_file, index=True)
print(stats_df)
