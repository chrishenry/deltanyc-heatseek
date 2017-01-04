#!/usr/bin/env python

import argparse
import os
import os.path
import sys
import logging

from utils import *

mkdir_p(BASE_DIR)

logging.basicConfig(format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stdout,
    level=logging.INFO)
log = logging.getLogger(__name__)

"""
DOB Violations import
"""

DOB_VIOLATIONS_KEY = 'dob_violations'

vio_dob_dtype_dict = {
        'ISN_DOB_BIS_VIOL':       'int64',
        'BORO':       'object',
        'BIN':       'float64',
        'BLOCK':       'object',
        'LOT':       'object',
        'ISSUE_DATE':       'object',
        'VIOLATION_TYPE_CODE':       'object',
        'VIOLATION_NUMBER':       'object',
        'HOUSE_NUMBER':       'object',
        'STREET':       'object',
        'DISPOSITION_DATE':       'object',
        'DISPOSITION_COMMENTS':       'object',
        'DEVICE_NUMBER':       'object',
        'DESCRIPTION':       'object',
        'ECB_NUMBER':       'object',
        'NUMBER':       'object',
        'VIOLATION_CATEGORY':       'object',
        'VIOLATION_TYPE':       'object'
        }


vio_dob_df_keep_cols = [
        'ISN_DOB_BIS_VIOL',
        'BORO',
        'BIN',
        'BLOCK',
        'LOT',
        'ISSUE_DATE',
        'VIOLATION_TYPE_CODE',
        'VIOLATION_NUMBER',
        'HOUSE_NUMBER',
        'STREET',
        'DISPOSITION_DATE',
        'DISPOSITION_COMMENTS',
        'DEVICE_NUMBER',
        'DESCRIPTION',
        'ECB_NUMBER',
        'NUMBER',
        'VIOLATION_CATEGORY',
        'VIOLATION_TYPE'
        ]

vio_dob_truncate_columns = ['description', 'ecb_number', 'number']

vio_dob_date_time_columns = ['issue_date', 'disposition_date']

def main(argv):

    parser = argparse.ArgumentParser(description='Import dob violations dataset.')
    parser = add_common_arguments(parser)
    args = parser.parse_args()

    print args

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)


def import_csv(args):

    dob_violations_dir = os.path.join(BASE_DIR, DOB_VIOLATIONS_KEY)
    mkdir_p(dob_violations_dir)

    dob_violations_csv = os.path.join(dob_violations_dir, "dob_violations.csv")

    if not os.path.isfile(dob_violations_csv) or args.BUST_DISK_CACHE:
        log.info("DL-ing DOB violations")
        download_file(
                "https://data.cityofnewyork.us/api/views/3h2n-5cm9/rows.csv?accessType=DOWNLOAD",
                dob_violations_csv)
    else:
        log.info("DOB Violations exists, moving on...")

    vio_dob_description = 'DOB Violations'
    vio_dob_pickle = dob_violations_dir + '/df_dob_violations.pkl'
    vio_dob_sep_char = ","
    vio_dob_table_name = "dob_violations"
    vio_dob_load_pickle = args.LOAD_PICKLE
    vio_dob_save_pickle = args.SAVE_PICKLE
    vio_dob_db_action = args.DB_ACTION
    vio_dob_chunk_size = 5000
    vio_max_col_len = 255
    vio_date_format = "%Y%m%d"

    hpd_csv2sql(
                vio_dob_description,
                dob_violations_csv,
                vio_dob_sep_char,
                vio_dob_table_name,
                vio_dob_dtype_dict,
                vio_dob_load_pickle,
                vio_dob_save_pickle,
                vio_dob_pickle,
                vio_dob_db_action,
                vio_dob_truncate_columns,
                vio_dob_date_time_columns,
                vio_dob_chunk_size,
                vio_dob_df_keep_cols,
                vio_max_col_len,
                vio_date_format
               )


def sql_cleanup(args):
    conn = connect()
    cursor = conn.cursor()

    SQL = '''  

    UPDATE dob_violations SET street = regexp_replace( street, ' AVE$|-AVE$| -AVE$', ' AVENUE');
    UPDATE dob_violations SET street = regexp_replace( street, '\.', '', 'g');
    UPDATE dob_violations SET street = array_to_string(regexp_matches(street, '(.*)(\d+)(?:TH|RD|ND|ST)( .+)'), '') WHERE street ~ '.*(\d+)(?:TH|RD|ND|ST)( .+).*';
    UPDATE dob_violations SET street = regexp_replace( street, ' LA$', ' LANE', 'g');
    UPDATE dob_violations SET street = regexp_replace( street, ' LN$', ' LANE', 'g');
    UPDATE dob_violations SET street = regexp_replace( street, ' PL$', ' PLACE', 'g');
    UPDATE dob_violations SET street = regexp_replace( street, ' ST$| STR$', ' STREET', 'g');
    UPDATE dob_violations SET street = regexp_replace( street, ' RD$', ' ROAD', 'g');
    UPDATE dob_violations SET street = regexp_replace( street, ' PKWY$', 'PARKWAY', 'g');
    UPDATE dob_violations SET street = regexp_replace( street, ' PKWY ', ' PARKWAY ', 'g');
    UPDATE dob_violations SET street = regexp_replace( street, ' BLVD$', ' BOULEVARD', 'g');
    UPDATE dob_violations SET street = regexp_replace( street, ' BLVD ', ' BOULEVARD ', 'g');
    UPDATE dob_violations SET street = regexp_replace( street, ' BLVD', ' BOULEVARD ', 'g');
    UPDATE dob_violations SET street = regexp_replace( street, '^E ', 'EAST ');
    UPDATE dob_violations SET street = regexp_replace( street, '^W ', 'WEST ');
    UPDATE dob_violations SET street = regexp_replace( street, '^N ', 'NORTH ');
    UPDATE dob_violations SET street = regexp_replace( street, '^S ', 'SOUTH ');
    UPDATE dob_violations SET street = regexp_replace( street, '^BCH ', 'BEACH ', 'g');
    UPDATE dob_violations SET boro = regexp_replace(boro, '1', 'MN', 'g');
    UPDATE dob_violations SET boro = regexp_replace(boro, '3', 'BK', 'g');
    UPDATE dob_violations SET boro = regexp_replace(boro, '5', 'SI', 'g');
    UPDATE dob_violations SET boro = regexp_replace(boro, '4', 'QN', 'g');
    UPDATE dob_violations SET boro = regexp_replace(boro, '2', 'BR', 'g'); 
    SELECT concat(trim(dob_violations.boroid),dob_violations.block,dob_violations.lot as bbl from dob_violations;
    ALTER TABLE dob_violations CHANGE bbl bigint(13) NULL DEFAULT NULL;
    ALTER TABLE `dob_violations` ADD INDEX(bbl);

    '''

    for result in cursor.execute(SQL,multi = True):
        pass
    
    conn.commit()
    cursor.close()
    conn.close()
    # TODO(ryan, alex): actual cleanup
    log.info('SQL cleanup...')


if __name__ == "__main__":
    main(sys.argv[:1])
