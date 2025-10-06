import pandas as pd
import numpy as np

filepath = r"C:\Users\kpras\Desktop\Test_data.xlsx"
df = pd.read_excel(filepath,sheet_name='Sheet1', engine = 'openpyxl')

df['Category'] = np.where(df['Narration'].str.contains('Bounce', case=False, na=False), 'Bounce',
                 np.where(df['Narration'].str.contains('IMPS', case=False, na=False), 'IMPS', 'Other')
)

# conditions = [
#     df['Narration'].str.contains('Bounce', case=False, na=False),
#     df['Narration'].str.contains('IMPS', case=False, na=False),
#     df['Narration'].str.contains('RTGS', case=False, na=False)
# ]
# choices = ['Bounce', 'IMPS', 'RTGS']
# df['Category'] = np.select(conditions, choices, default='Other')

print(df)

df.to_excel(fr"C:\Users\kpras\Desktop\Output.xlsx", index=False)