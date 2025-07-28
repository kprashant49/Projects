import pandas as pd
import logging
from collections import defaultdict
from Snowflake_connection import get_snowflake_connection
from snowflake.connector.pandas_tools import write_pandas

# ---- Snowflake Table Names ----
INPUT_TABLE = "prd.analytics.marts_retail"
OLD_ALLOCATION_TABLE = "prd.analytics.allocation_retail"
FOS_MAPPER_TABLE = "prd.analytics.pai_emp_pincode_mapper"
OUTPUT_TABLE = "prd.analytics.auto_allocation_result"
# -------------------------------

def setup_logging():
    logging.basicConfig(filename='allocation_engine.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def query_to_df(query):
    conn = get_snowflake_connection()
    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def get_input_data():
    query = f"SELECT AGREEMENTID, MAILINGZIPCODE FROM {INPUT_TABLE}"
    return query_to_df(query)

def get_previous_allocation():
    query = f"SELECT AGREEMENTID, AWS_CODE FROM {OLD_ALLOCATION_TABLE} WHERE MAILINGZIPCODE = '411021'"
    return query_to_df(query)

def get_fos_mapper():
    query = f"SELECT MAILINGZIPCODE, AWS_CODE, FOS_NAME FROM {FOS_MAPPER_TABLE}"
    return query_to_df(query)

def create_output_table_if_not_exists(conn):
    create_sql = f"""
    CREATE OR REPLACE TABLE {OUTPUT_TABLE} (
        AGREEMENTID STRING,
        MAILINGZIPCODE STRING,
        AWS_CODE STRING,
        Allocation_Status STRING,
        FOS_mapping_count NUMBER
    );
    """
    cursor = conn.cursor()
    cursor.execute(create_sql)
    cursor.close()
    logging.info("Verified or created output table.")

def write_df_to_snowflake(df, table_name):
    conn = get_snowflake_connection()
    try:
        create_output_table_if_not_exists(conn)
        success, nchunks, nrows, _ = write_pandas(conn, df, table_name.split('.')[-1], schema=table_name.split('.')[1])
        logging.info(f"Data written to {table_name}: {nrows} rows")
    except Exception as e:
        logging.error(f"Failed to write to Snowflake: {e}")
        raise
    finally:
        conn.close()

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

def Allocation_Rule_Engine():
    setup_logging()
    logging.info("Starting Allocation Rule Engine (Snowflake mode)")

    df_new = get_input_data()
    df_old = get_previous_allocation()
    fos_mapper = get_fos_mapper()

    df_priority1, df_unmapped = map_priority1(df_new, df_old)
    existing_counts = df_priority1['AWS_CODE'].value_counts().to_dict()
    df_priority2 = map_priority2(df_unmapped.copy(), fos_mapper, existing_counts)

    combined = pd.concat([df_priority1, df_priority2], ignore_index=True)
    combined['AGREEMENTID'] = pd.Categorical(combined['AGREEMENTID'], categories=df_new['AGREEMENTID'], ordered=True)
    result = combined.sort_values('AGREEMENTID')

    write_df_to_snowflake(result, OUTPUT_TABLE)
    logging.info("Exported results to Snowflake successfully.")

if __name__ == "__main__":
    Allocation_Rule_Engine()
