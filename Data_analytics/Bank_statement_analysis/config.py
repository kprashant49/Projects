import numpy as np

# ---------------- CONFIGURATION ----------------
INPUT_DIR = r"C:\Users\kpras\Desktop\Test_data\Banking_Project\Input"
OUTPUT_DIR = r"C:\Users\kpras\Desktop\Test_data\Banking_Project\Output"
LOG_FILE = r"C:\Users\kpras\Desktop\Test_data\Banking_Project\last_processed.txt"
LOG_DIR = r"C:\Users\kpras\Desktop\Test_data\Banking_Project\Logs"
SHEET_NAME = "Sheet1"  # For Excel input

# ---------------- CATEGORY LOGIC ----------------
def categorize_transactions(df):
    """
    Custom categorization logic.
    You can edit this function manually to change category rules.
    """
    if ('TransactionNarration' not in df.columns # or 'Status'
            not in df.columns):
        raise KeyError("Input file must contain 'Narration' columns")

    conditions = [
        (df['TransactionNarration'].str.contains('Bounce', case=False, na=False)),
        (df['TransactionNarration'].str.contains('IMPS', case=False, na=False)),
        (df['TransactionNarration'].str.contains('RTGS', case=False, na=False))
    ]
    choices = ['Bounce', 'IMPS', 'RTGS']

    df['Category'] = np.select(conditions, choices, default='Other')
    return df
