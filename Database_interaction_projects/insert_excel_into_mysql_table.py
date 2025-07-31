import pandas as pd
import pymysql
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, DateTime
import json
with open('db_config.json') as f:
    config = json.load(f)

host=config["host"]
user=config["user"]
password=config["password"]
database=config["database"]

# Create SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}?charset=utf8mb4")
metadata = MetaData()

# Define Table Schema
tracker_table = Table(
    "tracker_data_new", metadata,
    Column("S_no", Integer),
    Column("Zone", String(255)),
    Column("Branch", String(255)),
    Column("State", String(255)),
    Column("Month", String(255)),
    Column("Vehicle_Business_Category", String(255)),
    Column("Sourcing_Channel", String(255)),
    Column("Dealership_Name", String(255)),
    Column("Dealer_Code", String(255)),
    Column("Customer_Name", String(255)),
    Column("Ckross_id", String(255)),
    Column("Loan_Account_Number", String(255), primary_key=True),
    Column("Approved_Loan_Amount", Integer),
    Column("Net_Disbursed_Amount", Integer),
    Column("Disbursement_Date", DateTime)
)

# Create Table (if not exists)
metadata.create_all(engine)

# Load Excel file into Pandas
file_path = "D:\\Projects\\Database_interaction_projects\\tracker_data.xlsx"  # Update this path
df = pd.read_excel(file_path, engine='openpyxl', dtype=str)

# Fix column names (replace special characters)
df.columns = (
    df.columns
    .str.strip()
    .str.replace(r"[ /.-]", "_", regex=True)  # Replace spaces, slashes (/), dots (.), dashes (-) with "_"
    .str.replace(r"[^a-zA-Z0-9_]", "", regex=True)  # Remove any other special characters
)

# Define column mapping (Excel -> MySQL)
column_mapping = {
    "S_no": "S_no",
    "Zone": "Zone",
    "Branch": "Branch",
    "State": "State",
    "Month": "Month",
    "Vehicle_Business_Category": "Vehicle_Business_Category",
    "Sourcing_Channel": "Sourcing_Channel",
    "Dealership_Name": "Dealership_Name",
    "Dealer_Code": "Dealer_Code",
    "Customer_Name": "Customer_Name",
    "ckross_id": "Ckross_id",
    "Loan_Account_Number": "Loan_Account_Number",
    "Approved_Loan_Amount": "Approved_Loan_Amount",
    "Net_Disbursed_Amount": "Net_Disbursed_Amount",
    "Disbursement_Date": "Disbursement_Date"
}

# Rename DataFrame columns based on mapping
df = df.rename(columns=column_mapping, errors="ignore")

# Select only the required columns in the correct order
expected_columns = list(column_mapping.values())  # Get MySQL table columns
df = df[expected_columns].copy()  # Keep only expected columns

# Convert numeric columns
df["S_no"] = pd.to_numeric(df["S_no"], errors="coerce")
df["Approved_Loan_Amount"] = pd.to_numeric(df["Approved_Loan_Amount"], errors="coerce")
df["Net_Disbursed_Amount"] = pd.to_numeric(df["Net_Disbursed_Amount"], errors="coerce")

# Convert date columns

df["Disbursement_Date"] = pd.to_datetime(df["Disbursement_Date"], errors="coerce")

# ------------------------------------------Other date fixes-------------------------------------------
# Remove spaces
# df["Disbursement_Date"] = df["Disbursement_Date"].astype(str).str.strip()
# df["Disbursement_Date"] = pd.to_datetime(df["Disbursement_Date"], errors="coerce")
# If Excel serial numbers are found, apply the fix
# df.loc[df["Disbursement_Date"].astype(str).str.isnumeric(), "Disbursement_Date"] = \
#    pd.to_datetime(df["Disbursement_Date"], origin="1899-12-30", unit="D", errors="coerce")
# df["Disbursement_Date"] = pd.to_datetime(df["Disbursement_Date"], format="%d/%m/%Y", errors="coerce")
# -----------------------------------------------------------------------------------------------------

# Insert data into MySQL
df.to_sql(name="tracker_data_new", con=engine, if_exists='append', index=False)

print("Data inserted successfully!")
