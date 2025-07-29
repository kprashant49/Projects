import pandas as pd
import logging
import configparser
from collections import defaultdict
from Snowflake_connection import get_snowflake_connection, load_config
from snowflake.connector.pandas_tools import write_pandas

# ---- Snowflake Table Names ----
INPUT_TABLE = "PRD.ANALYTICS.MARTS_RETAIL_IDFC"
OLD_ALLOCATION_TABLE = "RAW.MIS_DATA.IDFC_RETAIL_ALLOCATION_JUNE"
FOS_MAPPER_TABLE = "RAW.MIS_DATA.EMP_PINCODE_MAPPER"
OUTPUT_TABLE = "RAW.MIS_DATA.AUTO_ALLOCATION_OUTPUT"
# -------------------------------

def setup_logging():
    logging.basicConfig(filename='allocation_engine.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def query_to_df(query, config):
    conn = get_snowflake_connection(config)
    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()

def get_input_data(config):
    query = f"SELECT AGREEMENTID, MAILINGZIPCODE FROM {INPUT_TABLE}"
    return query_to_df(query,config)

def get_previous_allocation(config):
    query = f"SELECT AGREEMENTID, AWS_CODE FROM {OLD_ALLOCATION_TABLE}"
    return query_to_df(query,config)

def get_fos_mapper(config):
    query = f"SELECT MAILINGZIPCODE, AWS_CODE, FOS_NAME FROM {FOS_MAPPER_TABLE}"
    return query_to_df(query,config)

def create_output_table_if_not_exists(conn):
    create_sql = f"""
    CREATE OR REPLACE TABLE {OUTPUT_TABLE} (
        AGREEMENTID STRING,
        MAILINGZIPCODE STRING,
        AWS_CODE STRING,
        ALLOCATION_STATUS STRING,
        FOS_MAPPING_COUNT NUMBER
    );
    """
    cursor = conn.cursor()
    cursor.execute(create_sql)
    cursor.close()
    logging.info("Verified or created output table.")

def write_df_to_snowflake(df, table_name, config):
    conn = get_snowflake_connection(config)
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
    df_priority1.rename(columns={'_merge': 'ALLOCATION_STATUS'}, inplace=True)
    df_priority1['FOS_MAPPING_COUNT'] = df_map.groupby('AWS_CODE').cumcount() + 1
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
                'ALLOCATION_STATUS': 'OGL',
                'FOS_MAPPING_COUNT': None
            })
            continue

        min_fos = min(fos_group, key=lambda x: assignment_counter[x])
        assignment_counter[min_fos] += 1

        result.append({
            'index': idx,
            'AGREEMENTID': row['AGREEMENTID'],
            'MAILINGZIPCODE': key,
            'AWS_CODE': min_fos,
            'ALLOCATION_STATUS': 'Assigned by rule_engine',
            'FOS_MAPPING_COUNT': assignment_counter[min_fos]
        })

    return pd.DataFrame(result).set_index('index').sort_index().reset_index(drop=True)

def Allocation_Rule_Engine():
    setup_logging()
    logging.info("Starting Allocation Rule Engine (Snowflake mode)")
    config = load_config('config.ini')

    df_new = get_input_data(config)
    df_old = get_previous_allocation(config)
    fos_mapper = get_fos_mapper(config)

    df_priority1, df_unmapped = map_priority1(df_new, df_old)
    existing_counts = df_priority1['AWS_CODE'].value_counts().to_dict()
    df_priority2 = map_priority2(df_unmapped.copy(), fos_mapper, existing_counts)

    combined = pd.concat([df_priority1, df_priority2], ignore_index=True)
    combined['AGREEMENTID'] = pd.Categorical(combined['AGREEMENTID'], categories=df_new['AGREEMENTID'], ordered=True)
    result = combined.sort_values('AGREEMENTID')

    write_df_to_snowflake(result, OUTPUT_TABLE, config)
    logging.info("Exported results to Snowflake successfully.")

if __name__ == "__main__":
    Allocation_Rule_Engine()
