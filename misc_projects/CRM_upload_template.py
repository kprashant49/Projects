import pandas as pd
import random
from random import randint
from datetime import date, timedelta
today = date.today()
import mysql.connector
import string
import json
alphabets = list(string.ascii_uppercase)

# filepath = r"C:\Users\kpras\Desktop\AutomatedBorrowerUploadTemplate.xlsx"
# df = pd.read_excel(filepath,sheet_name='Sheet1', engine = 'openpyxl')
# headers = df.columns.tolist()

headers_static = ['PAI_A/c_Number', 'Principal Outstanding', 'Interest Outstanding', 'Charges Outstanding',
                  'Total EMI Overdue', 'Total O/S', 'Total Overdue', 'Other Charges', 'SMA/Bucket', 'Current DPD',
                  'AUM', 'EMI Amount', 'EMI Date', 'Tenure', 'Effective_Interest_Rate', 'Sanctioned Amount',
                  'Sanctioned Date', 'NPA Date', 'Loan Ac Classification In F.I.', 'Disbursement_Date', 'Maturity_Date',
                  'Loan_Amount_At_Inception', 'Due_Date', 'Term_Remaining', 'Last_Payment_Date',
                  'Last_Principal_Payment_Amount', 'Last_Interest_Payment_Amount', 'Last_Charges_Amount', 'LTV',
                  'Type_of_loan', 'Product', 'Payment Link', 'Risk', 'Stage', 'Product Category', 'Opening DPD',
                  'Disb Amount', 'CBC (Cheque Bounce Charges)', 'Loan Maturity Date', 'Loan Status',
                  'Penal Rate Of Interest', 'No Of Installment Paid', 'Type Of EMI', 'Legal Charges',
                  'Latest Legal Status', 'Legal Status', 'Email', 'Contact Number', 'Alternate Contact Number',
                  'CUSTOMER_TYPE', 'INCORPORATION_DATE', 'INDUSTRY_CODE', 'REGISTRATION_NUMBER', 'DATE_OF_BIRTH',
                  'FATHER_NAME', 'MOTHER_NAME', 'HUSBAND_NAME', 'FIRST_NAME', 'MIDDLE_NAME', 'LAST_NAME', 'FULL_NAME',
                  'GENDER', 'MARITAL_STATUS_CODE', 'NATIONALITY', 'SALUTATION', 'Company Name', 'Company(office) Address',
                  'Company(office) Address City', 'Company(office) Address State', 'Company(office) Address Pin code',
                  'Address_Type', 'Address_Tag', 'Address 1', 'Address 2', 'Address 3', 'Landmark', 'City', 'State',
                  'Pincode', 'Co-ordinates_Lattitue', 'Co-ordinates_Longitutde', 'Address_Verified', 'Distance from Median',
                  'Median', 'KYC TYPE 1', 'KYC Number 1', 'KYC TYPE 2', 'KYC Number 2', 'KYC for POI', 'KYC for POA',
                  'Lead Id', 'Customer Id', 'Code', 'Borrower Status', 'Borrower District', 'Country', 'Area',
                  'Borrower Gst No', 'Borrower Company Name Classification', 'Street', 'Date Of Death', 'PTP Date',
                  'Description', 'Last Borrower Contact No. Contacted', 'Constitution', 'RERERENCE 1 NAME',
                  'REFERENCE 1 ADDRESS', 'REFERENCE 1 CONTACT', 'REFERENCE 1 EMAIL', 'RERERENCE 2 NAME',
                  'REFERENCE 2 ADDRESS', 'REFERENCE 2 CONTACT', 'REFERENCE 2 EMAIL', 'Collateral Type', 'Valuation_Amount',
                  'Registration date', 'Registration number', 'Vehicle Make', 'Vehicle Model', 'Manufacture Year',
                  'Registration Year', 'Engine Number', 'Chassis Number', 'Building Type', 'Completion Year',
                  'Collateral Address 1', 'Collateral Address 2', 'Collateral Landmark', 'Collateral City',
                  'Collateral State', 'Collateral Pincode', 'Communication Address is Collateral', 'Type of Property Sub',
                  'Property District', 'Dealer/Builder Name', 'Contacted Person Relationship With Borrower', 'Vehicle Type',
                  'Co-Borrower FIRST_NAME', 'Co-Borrower MIDDLE_NAME', 'Co-Borrower LAST_NAME', 'Co-Borrower FULL_NAME',
                  'Co-Borrower GENDER', 'Co-Borrower MARITAL_STATUS_CODE', 'Co-Borrower NATIONALITY', 'Co-Borrower SALUTATION',
                  'Co-Borrower Email', 'Co-Borrower Contact Number', 'Co-Borrower Alternate Contact Number',
                  'Co-Borrower Company Name', 'Co-Borrower Company(office) Address', 'Co-Borrower Company(office) Address City',
                  'Co-Borrower Company(office) Address State', 'Co-Borrower Company(office) Address Pin code',
                  'Co-Borrower DATE_OF_BIRTH', 'Co-Borrower FATHER_NAME', 'Co-Borrower MOTHER_NAME', 'Co-Borrower HUSBAND_NAME',
                  'Co-Borrower CUSTOMER_TYPE', 'Co-Borrower INCORPORATION_DATE', 'Co-Borrower INDUSTRY_CODE',
                  'Co-Borrower REGISTRATION_NUMBER', 'Co-Borrower Address_Type', 'Co-Borrower Address_Tag', 'Co-Borrower Address 1',
                  'Co-Borrower Address 2', 'Co-Borrower Address 3', 'Co-Borrower Landmark', 'Co-Borrower City', 'Co-Borrower State',
                  'Co-Borrower Pincode', 'Co-Borrower Co-ordinates_Lattitue', 'Co-Borrower Co-ordinates_Longitutde',
                  'Co-Borrower Address_Verified', 'Co-Borrower Distance from Median', 'Co-Borrower Median', 'Co-Borrower KYC TYPE 1',
                  'Co-Borrower KYC Number 1', 'Co-Borrower KYC TYPE 2', 'Co-Borrower KYC Number 2', 'Co-Borrower KYC for POI',
                  'Co-Borrower KYC for POA', 'Co-Borrower District', 'Co-Borrower Gst No.', 'Constitution (Only for Co-borrower)',
                  'Financial Institution Name(ORG)', 'Financial Institution Name(ORG) Id', 'Financial Institution Contact Mail Id',
                  'Financial Institution Soucing Branch Name', 'Financial Institution Contact Address', 'Financial Institution Contact No',
                  'Financial Institution Contact Person Name', 'Financial Institution Contact Person No',
                  'Financial Institution Contact Person Email Id', 'FI Allocation / Assignment Date', 'FI Allocation / Assignment End Date',
                  'Financial Institution Branch  State', 'Financial Institution Branch  District', 'Financial Institution Branch  City',
                  'Financial Institution Branch  Pincode', 'MRA/ MSA Provided By FI', 'MRA / MSA Period Start Date', 'MRA / MSA Period End Date',
                  'PAI Zonal Manager Name', 'PAI Zone Name', 'PAI Regional Manager Name', 'PAI Region Name', 'PAI Hub Name', 'PAI Branch Name',
                  'PAI Spoke Location Name', 'PAI Business Sourcing Staff Name', 'PAI Business Sourcing Staff Emp Code',
                  'PAI Business Sourcing Date', 'Name Of Contacted', 'Guarantor First Name', 'Guarantor Middle Name', 'Guarantor Last Name',
                  'Guarantor Full Name', 'Guarantor Gender', 'Guarantor MaritalStatus', 'Guarantor Contact Number','Guarantor Alternate Contact Number',
                  'Guarantor Date of Birth','Guarantor Address_Type', 'Guarantor Address_Tag',
                  'Guarantor Address 1', 'Guarantor Address 2', 'Guarantor Address 3', 'Guarantor Landmark', 'Guarantor City',
                  'Guarantor State', 'Guarantor Pincode', 'Guarantor Co-ordinates_Lattitue', 'Guarantor Co-ordinates_Longitutde',
                  'Guarantor Address_Verified', 'Guarantor Distance from Median', 'Guarantor Median', 'Guarantor KYC TYPE 1',
                  'Guarantor KYC Number 1', 'Guarantor KYC TYPE 2', 'Guarantor KYC Number 2', 'Guarantor KYC for POI',
                  'Guarantor KYC for POA', 'Guarantor District', 'Guarantor Gst No.']

headers_static_pmt = ['Lead Id','Borrowers Code','Payment Detail Name','Payment Detail Allocated Agent','Payment Detail Allocated Agent Id',
                      'Payment Detail Bank/Client LAN','Payment Detail Payment Amount','Payment Detail Payment Mode','Payment Detail Deposit Date',
                      'Payment Detail Receipting  Transaction Date','Payment Detail CRM System LAN','Payment Detail Status','State','Borrower State',
                      'Payment Detail Transaction of Receipting','Payment Detail Date Of Modification / Deletion','Payment Detail Reasons For Modification / Deletion',
                      'Financial Institution Contact Address','Financial Institution Contact Mail Id','Financial Institution Contact No',
                      'Financial Institution Contact Person Email Id','Financial Institution Contact Person Name','Financial Institution Contact Person No',
                      'Financial Institution Soucing Branch Name','Payment Detail Financial Institution Name(ORG)','Payment Detail Financial Institution Name(ORG) Id',
                      'Payment Detail OTS / NON OTS / EMI Payment','NPA Date','Principal Outstanding','Loan Product','Type Of Loan',
                      'Payment Detail User / Telecaller  / Field Agent Name','SMA/Bucket','Loan Ac Classification In F.I.','FI Allocation / Assignment Date',
                      'FI Allocation / Assignment End Date','Payment Detail Pepper Receipting  Date','Payment Detail Created By','Payment Detail Created By Id']

df_template = pd.DataFrame(columns=headers_static)
df_template_pmt = pd.DataFrame(columns=headers_static_pmt)

Bank = "HDFC"
Count = 10
Collateral = 'Car'
Co_borrower = 'Yes'
Guarantor = 'Yes'

df_borrowers = []
POS = []
IOS = []
EMI_OS = []
TOS = []
DPD = []
EMI_DT = []
TENOR = []
ROI = []
PAN = []
PAN_CB = []
PAN_G = []
UID = []
UID_CB = []
UID_G = []
RTO = []
APR = []
APR_DT = []
DISB_DT = []
MAT_DT = []
LAST_DT = []
TERM_REM = []
LTV = []
TERM_PAID = []
PHONE = []
PHONE_CB = []
PHONE_G = []
PHONE2 = []
PHONE2_CB = []
PHONE2_G = []
DOB = []
DOB_CB = []
DOB_G = []
LEAD = []
MFG_REG_YEAR = []
ENG = []
CHA = []
REF1_PNE = []
REF2_PNE = []
PMT_DT = []

for i in range(Count):
    borrower = Bank + str(randint(1000000, 9999999))
    df_borrowers.append(borrower)
    pos = randint(10000, 99999)
    POS.append(pos)
    ios = randint(1000, 9999)
    IOS.append(ios)
    tos = pos+ios
    TOS.append(tos)
    EMI_OS.append(tos)
    dpd = randint(1, 90)
    DPD.append(dpd)
    emi_date = today - timedelta(days=dpd)
    emi_date_str = emi_date.strftime('%Y-%m-%d')
    EMI_DT.append(emi_date_str)
    tenor = randint(60, 180)
    TENOR.append(tenor)
    roi = randint(11, 18)
    ROI.append(roi)
    apr = randint(100000, 999999)
    APR.append(apr)
    apr_days = randint(365, 745)
    apr_date = today - timedelta(days=apr_days)
    apr_date_str = apr_date.strftime('%Y-%m-%d')
    APR_DT.append(apr_date_str)
    mfg_reg_year = apr_date.year
    MFG_REG_YEAR.append(mfg_reg_year)
    disb_date = apr_date + timedelta(days=30)
    disb_date_str = disb_date.strftime('%Y-%m-%d')
    DISB_DT.append(disb_date_str)
    mat_date = disb_date + timedelta(days=(tenor*12))
    mat_date_str = mat_date.strftime('%Y-%m-%d')
    MAT_DT.append(mat_date_str)
    last_date = emi_date + timedelta(days=-30)
    last_date_str = last_date.strftime('%Y-%m-%d')
    LAST_DT.append(last_date_str)
    term_rem = (mat_date - today).days / 12
    term_rem = round(term_rem, 0)
    TERM_REM.append(term_rem)
    term_paid = (today - disb_date).days / 12
    term_paid = round(term_paid, 0)
    TERM_PAID.append(term_paid)
    phone = randint(100000000,999999999)
    phone = "9" + str(phone)
    PHONE.append(phone)
    phone_cb = randint(100000000,999999999)
    phone_cb = "9" + str(phone_cb)
    PHONE_CB.append(phone_cb)
    phone_g = randint(100000000, 999999999)
    phone_g = "9" + str(phone_g)
    PHONE_G.append(phone_g)
    phone2 = randint(100000000, 999999999)
    phone2 = "9" + str(phone2)
    PHONE2.append(phone2)
    phone2_cb = randint(100000000, 999999999)
    phone2_cb = "9" + str(phone2_cb)
    PHONE2_CB.append(phone2_cb)
    phone2_g = randint(100000000, 999999999)
    phone2_g = "9" + str(phone2_g)
    PHONE2_G.append(phone2_g)
    ltv = randint(50, 90)
    LTV.append(ltv)
    dob_days = randint(25, 50)
    dob = today - timedelta(days=(dob_days * 365))
    dob_str = dob.strftime('%Y-%m-%d')
    DOB.append(dob_str)
    dob_days_cb = randint(25, 50)
    dob_cb = today - timedelta(days=(dob_days_cb * 365))
    dob_str_cb = dob_cb.strftime('%Y-%m-%d')
    DOB_CB.append(dob_str_cb)
    dob_days_g = randint(25, 50)
    dob_g = today - timedelta(days=(dob_days_g * 365))
    dob_str_g = dob_g.strftime('%Y-%m-%d')
    DOB_G.append(dob_str_g)
    lead = randint(100000,999999)
    LEAD.append(lead)
    pan_letter1 = random.choice(alphabets)
    pan_letter2 = random.choice(alphabets)
    pan_letter3 = random.choice(alphabets)
    pan_letter4 = random.choice(alphabets)
    pan_letter5 = random.choice(alphabets)
    pan_num = randint(1000, 9999)
    pan_no = pan_letter1 + pan_letter2 + pan_letter3 + "P" + pan_letter4 + str(pan_num) + pan_letter5
    PAN.append(pan_no)
    pan_letter_cb1 = random.choice(alphabets)
    pan_letter_cb2 = random.choice(alphabets)
    pan_letter_cb3 = random.choice(alphabets)
    pan_letter_cb4 = random.choice(alphabets)
    pan_letter_cb5 = random.choice(alphabets)
    pan_num_cb = randint(1000, 9999)
    pan_no_cb = pan_letter_cb1 + pan_letter_cb2 + pan_letter_cb3 + "P" + pan_letter_cb4 + str(pan_num_cb) + pan_letter_cb5
    PAN_CB.append(pan_no_cb)
    pan_letter_g1 = random.choice(alphabets)
    pan_letter_g2 = random.choice(alphabets)
    pan_letter_g3 = random.choice(alphabets)
    pan_letter_g4 = random.choice(alphabets)
    pan_letter_g5 = random.choice(alphabets)
    pan_num_g = randint(1000, 9999)
    pan_no_g = pan_letter_g1 + pan_letter_g2 + pan_letter_g3 + "P" + pan_letter_g4 + str(pan_num_g) + pan_letter_g5
    PAN_G.append(pan_no_g)
    uid_num = randint(1000, 9999)
    uid = "XXXXXXXX"+str(uid_num)
    UID.append(uid)
    uid_num_cb = randint(1000, 9999)
    uid_cb = "XXXXXXXX" + str(uid_num_cb)
    UID_CB.append(uid_cb)
    uid_num_g = randint(1000, 9999)
    uid_g = "XXXXXXXX" + str(uid_num_g)
    UID_G.append(uid_g)
    rto_series1 = random.choice(alphabets)
    rto_series2 = random.choice(alphabets)
    rto_number = randint(1000, 9999)
    rto_number_str = str(rto_series1) + str(rto_series2) + str(rto_number)
    RTO.append(rto_number_str)
    eng_letter1 = random.choice(alphabets)
    eng_letter2 = random.choice(alphabets)
    eng_letter3 = random.choice(alphabets)
    eng_letter4 = random.choice(alphabets)
    eng_letter5 = random.choice(alphabets)
    eng_letter6 = random.choice(alphabets)
    eng_num = randint(1000000, 9999999)
    eng_no = eng_letter1 + eng_letter2 + eng_letter3 + str(eng_num) + eng_letter4 + eng_letter5 + eng_letter6
    ENG.append(eng_no)
    cha_letter1 = random.choice(alphabets)
    cha_letter2 = random.choice(alphabets)
    cha_letter3 = random.choice(alphabets)
    cha_letter4 = random.choice(alphabets)
    cha_letter5 = random.choice(alphabets)
    cha_letter6 = random.choice(alphabets)
    cha_num = randint(1000000, 9999999)
    cha_no = cha_letter1 + cha_letter2 + cha_letter3 + str(cha_num) + cha_letter4 + cha_letter5 + cha_letter6
    CHA.append(cha_no)
    ref1_phone = randint(100000000,999999999)
    ref1_phone = "9" + str(ref1_phone)
    REF1_PNE.append(ref1_phone)
    ref2_phone = randint(100000000, 999999999)
    ref2_phone = "9" + str(ref2_phone)
    REF2_PNE.append(ref2_phone)
    pmt_date = today - timedelta(days=1)
    pmt_date_str = pmt_date.strftime('%Y-%m-%d')
    PMT_DT.append(pmt_date_str)

# Variable headers
df_template['PAI_A/c_Number'] = df_borrowers
df_template['Principal Outstanding'] = POS
df_template['Interest Outstanding'] = IOS
df_template['Total EMI Overdue'] = EMI_OS
df_template['Total O/S'] = TOS
df_template['Total Overdue'] = TOS
df_template['Current DPD'] = DPD
df_template['EMI Date'] = EMI_DT
df_template['EMI Amount'] = TOS
df_template['Tenure'] = TENOR
df_template['Effective_Interest_Rate'] = ROI
df_template['Sanctioned Amount'] = APR
df_template['Sanctioned Date'] = APR_DT
df_template['Disbursement_Date'] = DISB_DT
df_template['Maturity_Date'] = MAT_DT
df_template['Loan_Amount_At_Inception'] = APR
df_template['Due_Date'] = EMI_DT
df_template['Last_Payment_Date'] = LAST_DT
df_template['Term_Remaining'] = TERM_REM
df_template['Last_Principal_Payment_Amount'] = POS
df_template['Last_Interest_Payment_Amount'] = IOS
df_template['LTV'] = LTV
df_template['Opening DPD'] = DPD
df_template['Disb Amount'] = APR
df_template['Loan Maturity Date'] = MAT_DT
df_template['No Of Installment Paid'] = TERM_PAID
df_template['Contact Number'] = PHONE
df_template['Alternate Contact Number'] = PHONE2
df_template['DATE_OF_BIRTH'] = DOB
df_template['KYC Number 1'] = PAN
df_template['KYC Number 2'] = UID
df_template['Lead Id'] = LEAD
df_template['Last Borrower Contact No. Contacted'] = PHONE

# Hard-coded headers
df_template.loc[:,'Last_Charges_Amount'] = 0
df_template.loc[:,'Charges Outstanding'] = 0
df_template.loc[:,'Other Charges'] = 0
df_template.loc[:,'AUM'] = 0
df_template.loc[:,'CBC (Cheque Bounce Charges)'] = 0
df_template.loc[:,'Loan Status'] = 'Active'
df_template.loc[:,'Penal Rate Of Interest'] = 0
df_template.loc[:,'Type Of EMI'] = 'Monthly'
df_template.loc[:,'Legal Charges'] = 0
df_template.loc[:,'Latest Legal Status'] = 'NA'
df_template.loc[:,'Legal Status'] = 'NA'
df_template.loc[:,'CUSTOMER_TYPE'] = 'Individual'
df_template.loc[:,'INDUSTRY_CODE'] = 'Manufacturing'
df_template.loc[:,'GENDER'] = 'Male'
df_template.loc[:,'MARITAL_STATUS_CODE'] = 'Married'
df_template.loc[:,'NATIONALITY'] = 'Indian'
df_template.loc[:,'SALUTATION'] = 'Mr'
df_template.loc[:,'Address_Type'] = 'Home'
df_template.loc[:,'Address_Tag'] = 'Residential'
df_template.loc[:,'Address_Verified'] = 'No'
df_template.loc[:,'KYC TYPE 1'] = 'PAN'
df_template.loc[:,'KYC TYPE 2'] = 'Aadhaar'
df_template.loc[:,'KYC for POI'] = 'Yes'
df_template.loc[:,'KYC for POA'] = 'Yes'
df_template.loc[:,'Code'] = 'Individual'
df_template.loc[:,'Borrower Status'] = 'Active'
df_template.loc[:,'Country'] = 'India'
df_template.loc[:,'Constitution'] = 'Individual'

def sma(dpd):
    if dpd >= 60:
        return 'SMA2'
    elif dpd >= 30 and dpd < 60:
        return 'SMA1'
    else:
        return 'SMA0'
df_template['Loan Ac Classification In F.I.'] = df_template['Current DPD'].apply(sma)
df_template['SMA/Bucket'] = df_template['Loan Ac Classification In F.I.'].str[-1:]

with open('db_config.json') as f:
    config = json.load(f)

conn = mysql.connector.connect(
    host=config["host"],
    user=config["user"],
    password=config["password"],
    database=config["database"]
)

cursor = conn.cursor()
query_names = f"SELECT First_Name, Middle_Name, Surname FROM sample_indian_names"
cursor.execute(query_names)
rows_names = cursor.fetchall()
sampled_rows_names = random.choices(rows_names, k=Count)

first_names = [row[0] for row in sampled_rows_names]
middle_names = [row[1] for row in sampled_rows_names]
surnames = [row[2] for row in sampled_rows_names]
full_names = [f"{row[0]} {row[1]} {row[2]}" for row in sampled_rows_names]
father_names = [f"{row[1]} {row[2]}" for row in sampled_rows_names]
email = [f"{row[0]}.{row[2]}{randint(1, 90)}@gmail.com" for row in sampled_rows_names]

query_addresses = f"Select officename, regionname, divisionname, district, statename, pincode FROM pincode_master"
cursor.execute(query_addresses)
rows_address  = cursor.fetchall()
sampled_rows_address = random.choices(rows_address, k=Count)

address1 = [row[0] for row in sampled_rows_address]
address2 = [row[1] for row in sampled_rows_address]
address3 = [row[2] for row in sampled_rows_address]
city = [row[3] for row in sampled_rows_address]
state = [row[4] for row in sampled_rows_address]
pincode = [row[5] for row in sampled_rows_address]

df_city = pd.DataFrame(city, columns=['CITY_UT'])
df_state = pd.DataFrame(state, columns=['STATE'])
df_regd = pd.concat([df_city, df_state], axis=1)

query_companies = f"Select CompanyName FROM company_names"
cursor.execute(query_companies)
rows_companies  = cursor.fetchall()
sampled_rows_companies = random.choices(rows_companies, k=Count)

companies = [row[0] for row in sampled_rows_companies]

query_ref1_names = f"SELECT Full_Name FROM sample_indian_names"
cursor.execute(query_ref1_names)
rows_ref1_names = cursor.fetchall()
sampled_rows_ref1_names = random.choices(rows_ref1_names, k=Count)

ref1_names = [row[0] for row in sampled_rows_ref1_names]
ref1_email = [f"{name.replace(' ', '')}{randint(1, 90)}@gmail.com" for name in ref1_names]

query_ref1_addresses = f"Select officename, regionname, divisionname, district, statename, pincode FROM pincode_master"
cursor.execute(query_ref1_addresses)
rows_ref1_address  = cursor.fetchall()
sampled_rows_ref1_address = random.choices(rows_ref1_address, k=Count)

ref1_address = [f"{row[0]} {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}" for row in sampled_rows_ref1_address]

query_ref2_names = f"SELECT Full_Name FROM sample_indian_names"
cursor.execute(query_ref2_names)
rows_ref2_names = cursor.fetchall()
sampled_rows_ref2_names = random.choices(rows_ref2_names, k=Count)

ref2_names = [row[0] for row in sampled_rows_ref2_names]
ref2_email = [f"{name.replace(' ', '')}{randint(1, 90)}@gmail.com" for name in ref2_names]

query_ref2_addresses = f"Select officename, regionname, divisionname, district, statename, pincode FROM pincode_master"
cursor.execute(query_ref2_addresses)
rows_ref2_address  = cursor.fetchall()
sampled_rows_ref2_address = random.choices(rows_ref2_address, k=Count)

ref2_address = [f"{row[0]} {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}" for row in sampled_rows_ref2_address]

# Co-borrower details

cursor = conn.cursor()
query_names_cb = f"SELECT First_Name, Middle_Name, Surname FROM sample_indian_names"
cursor.execute(query_names_cb)
rows_names_cb = cursor.fetchall()
sampled_rows_names_cb = random.choices(rows_names_cb, k=Count)

first_names_cb = [row[0] for row in sampled_rows_names_cb]
middle_names_cb = [row[1] for row in sampled_rows_names_cb]
surnames_cb = [row[2] for row in sampled_rows_names_cb]
full_names_cb = [f"{row[0]} {row[1]} {row[2]}" for row in sampled_rows_names_cb]
father_names_cb = [f"{row[1]} {row[2]}" for row in sampled_rows_names_cb]
email_cb = [f"{row[0]}.{row[2]}{randint(1, 90)}@gmail.com" for row in sampled_rows_names_cb]

query_addresses_cb = f"Select officename, regionname, divisionname, district, statename, pincode FROM pincode_master"
cursor.execute(query_addresses_cb)
rows_address_cb  = cursor.fetchall()
sampled_rows_address_cb = random.choices(rows_address_cb, k=Count)

address1_cb = [row[0] for row in sampled_rows_address_cb]
address2_cb = [row[1] for row in sampled_rows_address_cb]
address3_cb = [row[2] for row in sampled_rows_address_cb]
city_cb = [row[3] for row in sampled_rows_address_cb]
state_cb = [row[4] for row in sampled_rows_address_cb]
pincode_cb = [row[5] for row in sampled_rows_address_cb]

query_companies_cb = f"Select CompanyName FROM company_names"
cursor.execute(query_companies_cb)
rows_companies_cb  = cursor.fetchall()
sampled_rows_companies_cb = random.choices(rows_companies_cb, k=Count)

companies_cb = [row[0] for row in sampled_rows_companies_cb]

# Guarantor details

cursor = conn.cursor()
query_names_g = f"SELECT First_Name, Middle_Name, Surname FROM sample_indian_names"
cursor.execute(query_names_g)
rows_names_g = cursor.fetchall()
sampled_rows_names_g = random.choices(rows_names_g, k=Count)

first_names_g = [row[0] for row in sampled_rows_names_g]
middle_names_g = [row[1] for row in sampled_rows_names_g]
surnames_g = [row[2] for row in sampled_rows_names_g]
full_names_g = [f"{row[0]} {row[1]} {row[2]}" for row in sampled_rows_names_g]

query_addresses_g = f"Select officename, regionname, divisionname, district, statename, pincode FROM pincode_master"
cursor.execute(query_addresses_g)
rows_address_g  = cursor.fetchall()
sampled_rows_address_g = random.choices(rows_address_g, k=Count)

address1_g = [row[0] for row in sampled_rows_address_g]
address2_g = [row[1] for row in sampled_rows_address_g]
address3_g = [row[2] for row in sampled_rows_address_g]
city_g = [row[3] for row in sampled_rows_address_g]
state_g = [row[4] for row in sampled_rows_address_g]
pincode_g = [row[5] for row in sampled_rows_address_g]

if Co_borrower == 'Yes':

    df_template['Co-Borrower FULL_NAME'] = full_names_cb
    df_template['Co-Borrower FIRST_NAME'] = first_names_cb
    df_template['Co-Borrower MIDDLE_NAME'] = middle_names_cb
    df_template['Co-Borrower LAST_NAME'] = surnames_cb
    df_template['Co-Borrower FATHER_NAME'] = father_names_cb
    df_template['Co-Borrower Email'] = email_cb
    df_template['Co-Borrower Address 1'] = address1_cb
    df_template['Co-Borrower Address 2'] = address2_cb
    df_template['Co-Borrower Address 3'] = address3_cb
    df_template['Co-Borrower Landmark'] = address3_cb
    df_template['Co-Borrower City'] = city_cb
    df_template['Co-Borrower District'] = city_cb
    df_template['Co-Borrower State'] = state_cb
    df_template['Co-Borrower Pincode'] = pincode_cb
    df_template['Co-Borrower Company(office) Address'] = df_template['Co-Borrower Address 1'] + " " + df_template['Co-Borrower Address 2'] + " " + \
                                             df_template['Co-Borrower Address 3']
    df_template['Co-Borrower Company(office) Address City'] = city_cb
    df_template['Co-Borrower Company(office) Address State'] = state_cb
    df_template['Co-Borrower Company(office) Address Pin code'] = pincode_cb
    df_template['Co-Borrower Company Name'] = companies_cb
    df_template['Co-Borrower Contact Number'] = PHONE_CB
    df_template['Co-Borrower Alternate Contact Number'] = PHONE2_CB
    df_template['Co-Borrower DATE_OF_BIRTH'] = DOB_CB
    df_template['Co-Borrower KYC Number 1'] = PAN_CB
    df_template['Co-Borrower KYC Number 2'] = UID_CB
    df_template.loc[:, 'Co-Borrower CUSTOMER_TYPE'] = 'Individual'
    df_template.loc[:, 'Co-Borrower INDUSTRY_CODE'] = 'Manufacturing'
    df_template.loc[:, 'Co-Borrower GENDER'] = 'Male'
    df_template.loc[:, 'Co-Borrower MARITAL_STATUS_CODE'] = 'Married'
    df_template.loc[:, 'Co-Borrower NATIONALITY'] = 'Indian'
    df_template.loc[:, 'Co-Borrower SALUTATION'] = 'Mr'
    df_template.loc[:, 'Co-Borrower Address_Type'] = 'Home'
    df_template.loc[:, 'Co-Borrower Address_Tag'] = 'Residential'
    df_template.loc[:, 'Co-Borrower Address_Verified'] = 'No'
    df_template.loc[:, 'Co-Borrower KYC TYPE 1'] = 'PAN'
    df_template.loc[:, 'Co-Borrower KYC TYPE 2'] = 'Aadhaar'
    df_template.loc[:, 'Co-Borrower KYC for POI'] = 'Yes'
    df_template.loc[:, 'Co-Borrower KYC for POA'] = 'Yes'
    df_template.loc[:, 'Constitution (Only for Co-borrower)'] = 'Individual'

if Guarantor == 'Yes':

    df_template['Guarantor Full Name'] = full_names_g
    df_template['Guarantor First Name'] = first_names_g
    df_template['Guarantor Middle Name'] = middle_names_g
    df_template['Guarantor Last Name'] = surnames_g
    df_template['Guarantor Address 1'] = address1_g
    df_template['Guarantor Address 2'] = address2_g
    df_template['Guarantor Address 3'] = address3_g
    df_template['Guarantor Landmark'] = address3_g
    df_template['Guarantor City'] = city_g
    df_template['Guarantor District'] = city_g
    df_template['Guarantor State'] = state_g
    df_template['Guarantor Pincode'] = pincode_g
    df_template['Guarantor Contact Number'] = PHONE_G
    df_template['Guarantor Alternate Contact Number'] = PHONE2_G
    df_template['Guarantor Date of Birth'] = DOB_G
    df_template['Guarantor KYC Number 1'] = PAN_G
    df_template['Guarantor KYC Number 2'] = UID_G
    df_template.loc[:, 'Guarantor Gender'] = 'Male'
    df_template.loc[:, 'Guarantor MaritalStatus'] = 'Married'
    df_template.loc[:, 'Guarantor Address_Type'] = 'Indian'
    df_template.loc[:, 'Guarantor Address_Type'] = 'Home'
    df_template.loc[:, 'Guarantor Address_Tag'] = 'Residential'
    df_template.loc[:, 'Guarantor Address_Verified'] = 'No'
    df_template.loc[:, 'Guarantor KYC TYPE 1'] = 'PAN'
    df_template.loc[:, 'Guarantor KYC TYPE 2'] = 'Aadhaar'
    df_template.loc[:, 'Guarantor KYC for POI'] = 'Yes'
    df_template.loc[:, 'Guarantor KYC for POA'] = 'Yes'

if Collateral == 'Car':

    query_rto = f"SELECT REGISTRATION_NUMBER, upper(CITY_UT) as CITY_UT, upper(STATE) as STATE FROM rto_data where length(REGISTRATION_NUMBER) <= 4"
    cursor.execute(query_rto)
    rto_rows  = cursor.fetchall()

    df_rto = pd.DataFrame(rto_rows, columns=['REGISTRATION_NUMBER', 'CITY_UT', 'STATE'])
    df_rto_no = df_regd.merge(df_rto, on=['CITY_UT', 'STATE'], how='left')
    df_rto_no = df_rto_no.fillna("BH21")
    df_passing =  df_rto_no[['REGISTRATION_NUMBER']]
    df_passing = df_passing.copy()

    df_passing['SERIAL_NUMBER'] = RTO
    df_passing['Combined'] = df_passing.astype(str).agg(''.join, axis=1)

    query_cars = f"SELECT Make, Model FROM cars_data"
    cursor.execute(query_cars)
    cars_rows  = cursor.fetchall()

    sampled_rows = random.choices(cars_rows, k=Count)
    make = [row[0] for row in sampled_rows]
    model = [row[1] for row in sampled_rows]

    df_template = df_template.reset_index(drop=True)
    df_passing = df_passing.reset_index(drop=True)
    df_template['Registration number'] = df_passing['Combined']

    df_template['Vehicle Make'] = make
    df_template['Vehicle Model'] = model
    df_template.loc[:,'Collateral Type'] = 'Car'
    df_template.loc[:, 'Vehicle Type'] = 'Car'
    df_template['Registration date'] = APR_DT
    df_template['Valuation_Amount'] = APR
    df_template['Manufacture Year'] = MFG_REG_YEAR
    df_template['Registration Year'] = MFG_REG_YEAR
    df_template['Engine Number'] = ENG
    df_template['Chassis Number'] = CHA
    df_template.loc[:, 'Type_of_loan'] = 'Vehicle'
    df_template.loc[:, 'Product'] = 'Vehicle Loan'
    df_template.loc[:, 'Product Category'] = 'Secured'

elif Collateral == 'Home':

    df_template.loc[:, 'Collateral Type'] = 'Home'
    df_template.loc[:, 'Building Type'] = 'Apartment'
    df_template.loc[:, 'Communication Address is Collateral'] = 'Yes'
    df_template.loc[:, 'Type of Property Sub'] = 'Apartment'
    df_template.loc[:, 'Dealer/Builder Name'] = 'NA'
    df_template['Completion Year'] = MFG_REG_YEAR
    df_template['Collateral Address 1'] = address1
    df_template['Collateral Address 2'] = address2
    df_template['Collateral Landmark'] = address3
    df_template['Collateral City'] = city
    df_template['Collateral State'] = state
    df_template['Collateral Pincode'] = pincode
    df_template['Property District'] = city
    df_template.loc[:, 'Type_of_loan'] = 'Home'
    df_template.loc[:, 'Product'] = 'Home Loan'
    df_template.loc[:, 'Product Category'] = 'Secured'

else:

    df_template.loc[:, 'Type_of_loan'] = 'Personal'
    df_template.loc[:, 'Product'] = 'Personal Loan'
    df_template.loc[:, 'Product Category'] = 'Unsecured'

cursor.close()
conn.close()

df_template['FULL_NAME']=full_names
df_template['FIRST_NAME']=first_names
df_template['MIDDLE_NAME']=middle_names
df_template['LAST_NAME']=surnames
df_template['FATHER_NAME']=father_names
df_template['Email']=email

df_template['Address 1']=address1
df_template['Address 2']=address2
df_template['Address 3']=address3
df_template['City']=city
df_template['Borrower District']=city
df_template['Area']=city
df_template['Landmark']=city
df_template['State']=state
df_template['Pincode']=pincode

df_template['Company(office) Address']=df_template['Address 1']+" "+df_template['Address 2']+" "+df_template['Address 3']
df_template['Company(office) Address City']=city
df_template['Company(office) Address State']=state
df_template['Company(office) Address Pin code']=pincode

df_template['Company Name']=companies

df_template['RERERENCE 1 NAME']=ref1_names
df_template['REFERENCE 1 ADDRESS']=ref1_address
df_template['REFERENCE 1 CONTACT']=REF1_PNE
df_template['REFERENCE 1 EMAIL']=ref1_email

df_template['RERERENCE 2 NAME']=ref2_names
df_template['REFERENCE 2 ADDRESS']=ref2_address
df_template['REFERENCE 2 CONTACT']=REF2_PNE
df_template['REFERENCE 2 EMAIL']=ref2_email

df_template.to_excel(r"C:\Users\kpras\Desktop\CRM_borrower_upload_template_py.xlsx", index=False)

df_template_pmt['Lead Id'] = df_borrowers
df_template_pmt['Payment Detail Bank/Client LAN'] = df_borrowers
df_template_pmt['Payment Detail Name'] = full_names
df_template_pmt['Payment Detail Payment Amount'] = TOS
df_template_pmt['Payment Detail Deposit Date'] = PMT_DT
df_template_pmt['Payment Detail Receipting  Transaction Date'] = PMT_DT

df_template_pmt.loc[:,'Payment Detail Payment Mode'] = 'UPI'
df_template_pmt.loc[:,'Payment Detail Status'] = 'Received'
df_template_pmt.loc[:,'Payment Detail OTS / NON OTS / EMI Payment'] = 'EMI Payment'
df_template_pmt.loc[:,'Payment Detail Financial Institution Name(ORG)'] = Bank

df_template_pmt.to_excel(r"C:\Users\kpras\Desktop\CRM_payment_upload_template_py.xlsx", index=False)