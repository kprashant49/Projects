import pandas as pd

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
    """
    if ('TransactionNarration' not in df.columns # or 'Status'not in df.columns
        ):
        raise KeyError("Input file must contain 'Narration' columns")

    mapping = {
        'BBPS': 'Bill Payment',
        'CSH WDL': 'Cash Withdrawal',
        'INSTALLMENT': 'EMI',
        'InsodIntRcvry': 'Interest Recovery',
        'IWR  CHRG': 'Inward Remittance Charge',
        'BL-ONLINE DISBURSEMENT': 'Loan',
        'medicine': 'Medical',
        'NFT RTN': 'NEFT Return',
        'NFT/RTN': 'NEFT Return',
        'RENTAL': 'Rent Payments',
        'SALARY': 'SALARY',
        'I nt.Pd': 'Interest',
        'I nt.Coll': 'Interest',
        'Petrol': 'Fuel',
        'CHQ DEP RET': 'CHQ Bounce',
        'CHQ Issued Bounce': 'CHQ Bounce',
        'ECS DR RTN': 'CHQ Bounce',
        'RETURNED': 'CHQ Bounce',
        'TPT-RETURN': 'CHQ Bounce',
        'CHQ RET': 'CHQ Bounce',
        'ACH DEBIT RETURN': 'CHQ Bounce',
        'EMI RTN': 'CHQ Bounce',
        'CHQ DEP': 'Cheque Deposit',
        'REJECT': 'CHQ Bounce',
        'TO TRANSFER': 'Transfer To'
    }

    def categorize(narration):
        if pd.isna(narration):
            return 'Other'
        for key, category in mapping.items():
            if key.lower() in narration.lower():
                return category
        return 'Other'

    df['Category'] = df['TransactionNarration'].apply(categorize)

    return df
