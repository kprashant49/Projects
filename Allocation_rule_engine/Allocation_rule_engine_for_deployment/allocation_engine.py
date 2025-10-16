import pandas as pd
import mysql.connector
import logging
import json
from collections import defaultdict

# ---- File Paths ----
INPUT_FILE = r"C:\Users\kpras\Desktop\Test_data\Allocation.xlsx"
OUTPUT_FILE = r"C:\Users\kpras\\Desktop\Auto_allocation.xlsx"
CONFIG_FILE = r"D:\Projects\Allocation_rule_engine\Allocation_rule_engine_for_deployment\db_config.json"
# ----------------------

def setup_logging():
    logging.basicConfig(filename='allocation_engine.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def load_input_excel(path):
    try:
        return pd.read_excel(path, sheet_name='Sheet1', engine='openpyxl')[['AGREEMENTID', 'MAILINGZIPCODE']]
    except Exception as e:
        logging.error("Failed to read Excel file: %s", e)
        raise

def load_db_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        logging.error("Failed to load DB config: %s", e)
        raise

def connect_db(config):
    try:
        return mysql.connector.connect(**config)
    except mysql.connector.Error as e:
        logging.error("Database connection failed: %s", e)
        raise

def get_previous_allocation(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT AGREEMENTID, AWS_CODE FROM allocation_retail WHERE MAILINGZIPCODE = '411021'")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    return pd.DataFrame(rows, columns=columns)

def get_fos_mapper(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT MAILINGZIPCODE, AWS_CODE, FOS_NAME FROM pai_emp_pincode_mapper")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(rows, columns=columns)

def save_fos_mapping_counts(conn, df):
    """
    Saves total number of allocations per AWS_CODE into a summary table.
    Deallocated leads are excluded from counts.
    """
    try:
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fos_allocation_summary (
                AWS_CODE VARCHAR(50) PRIMARY KEY,
                TOTAL_ALLOCATIONS INT,
                LAST_UPDATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        # Only count active allocations (exclude Deallocated or OGL)
        active_df = df[~df['Allocation_Status'].isin(['Deallocated', 'OGL'])]
        fos_counts = df['AWS_CODE'].value_counts().reset_index()
        fos_counts.columns = ['AWS_CODE', 'TOTAL_ALLOCATIONS']

        # Insert or update
        for _, row in fos_counts.iterrows():
            cursor.execute("""
                INSERT INTO fos_allocation_summary (AWS_CODE, TOTAL_ALLOCATIONS)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE TOTAL_ALLOCATIONS = VALUES(TOTAL_ALLOCATIONS)
            """, (row['AWS_CODE'], int(row['TOTAL_ALLOCATIONS'])))

        conn.commit()
        logging.info("FOS allocation summary updated successfully (after deallocations).")

    except Exception as e:
        logging.error("Failed to save FOS allocation summary: %s", e)
        raise

def map_priority1(df_new, df_old):
    df_new['AGREEMENTID'] = df_new['AGREEMENTID'].astype(str)
    df_old['AGREEMENTID'] = df_old['AGREEMENTID'].astype(str)
    df_map = pd.merge(df_new, df_old, how='left', on='AGREEMENTID', indicator=True)
    df_priority1 = df_map[df_map['_merge'] == 'both'].copy()
    df_priority1['_merge'] = 'Assigned basis old allocation'
    df_priority1.rename(columns={'_merge': 'Allocation_Status'}, inplace=True)
    df_priority1['FOS_mapping_count'] = df_map.groupby('AWS_CODE').cumcount() + 1
    df_priority1['MAILINGZIPCODE'] = df_priority1['MAILINGZIPCODE'].astype(str)
    return df_priority1.dropna(), df_map[df_map['_merge'] == 'left_only'][df_new.columns]

def map_priority2(df_unmapped, fos_map, existing_counts):
    df_unmapped['MAILINGZIPCODE'] = df_unmapped['MAILINGZIPCODE'].astype(str).str.strip()
    fos_map['MAILINGZIPCODE'] = fos_map['MAILINGZIPCODE'].astype(str).str.strip()
    assignment_counter = defaultdict(int, existing_counts)
    result = []

    for idx, row in df_unmapped.iterrows():
        key = row['MAILINGZIPCODE']
        fos_group = fos_map[fos_map['MAILINGZIPCODE'] == key]['AWS_CODE'].tolist()

        if not fos_group:
            result.append({
                'index': idx,
                'AGREEMENTID': row['AGREEMENTID'],
                'MAILINGZIPCODE': key,
                'AWS_CODE': 'No FOS',
                'Allocation_Status': 'OGL',
                'FOS_mapping_count': None
            })
            continue

        min_fos = min(fos_group, key=lambda x: assignment_counter[x])
        assignment_counter[min_fos] += 1

        result.append({
            'index': idx,
            'AGREEMENTID': row['AGREEMENTID'],
            'MAILINGZIPCODE': key,
            'AWS_CODE': min_fos,
            'Allocation_Status': 'Assigned by rule_engine',
            'FOS_mapping_count': assignment_counter[min_fos]
        })

    return pd.DataFrame(result).set_index('index').sort_index().reset_index(drop=True)

def get_deallocated_leads(conn):
    """
    Fetches the list of AGREEMENTIDs to be deallocated.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT AGREEMENTID FROM deallocated_leads")
    rows = cursor.fetchall()
    return [r[0] for r in rows]

def allocation_rule_engine():
    setup_logging()
    logging.info("Starting Allocation Rule Engine")

    df_new = load_input_excel(INPUT_FILE)
    config = load_db_config(CONFIG_FILE)
    conn = connect_db(config)
    df_old = get_previous_allocation(conn)
    fos_mapper = get_fos_mapper(conn)
    deallocated_ids = get_deallocated_leads(conn)
    conn.close()

    df_priority1, df_unmapped = map_priority1(df_new, df_old)
    existing_counts = df_priority1['AWS_CODE'].value_counts().to_dict()
    df_priority2 = map_priority2(df_unmapped.copy(), fos_mapper, existing_counts)

    combined = pd.concat([df_priority1, df_priority2], ignore_index=True)
    combined['AGREEMENTID'] = pd.Categorical(combined['AGREEMENTID'], categories=df_new['AGREEMENTID'], ordered=True)
    result = combined.sort_values('AGREEMENTID')

    # Apply deallocation in reverse order
    result = apply_deallocation(result, deallocated_ids)

    # Save updated results
    result.to_excel(OUTPUT_FILE, index=False)
    logging.info("Exported results to %s", OUTPUT_FILE)
    print(f"Exported results to {OUTPUT_FILE}")

    # Update FOS allocation summary
    conn = connect_db(config)
    save_fos_mapping_counts(conn, result)
    conn.close()

def apply_deallocation(result_df, deallocated_ids):
    """
    Marks specified leads as deallocated in reverse order of allocation.
    Keeps FOS but marks status as 'Deallocated' and excludes from count.
    """
    # Only process if deallocation list exists
    if not deallocated_ids:
        logging.info("No leads to deallocate.")
        return result_df

    # Ensure order of removal = reverse order of allocation
    dealloc_df = result_df[result_df['AGREEMENTID'].isin(deallocated_ids)].copy()
    dealloc_df = dealloc_df.iloc[::-1]  # reverse order

    # Mark as deallocated
    result_df.loc[result_df['AGREEMENTID'].isin(deallocated_ids), 'Allocation_Status'] = 'Deallocated'
    result_df.loc[result_df['AGREEMENTID'].isin(deallocated_ids), 'FOS_mapping_count'] = None

    logging.info(f"Deallocated {len(deallocated_ids)} leads in reverse order.")
    return result_df


if __name__ == "__main__":
    allocation_rule_engine()
