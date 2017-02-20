#!/usr/bin/env python

import os.path
import sys
import logging

from clean_utils import *
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

description = 'DOB Violations'

table_name = "dob_violations"

dtype_dict = {
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

truncate_columns = ['description', 'ecb_number', 'number']

date_time_columns = ['issue_date', 'disposition_date']

keep_cols = [
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


def main():
    args = get_common_arguments('Import dob violations dataset.')

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)


def import_csv(args):
    csv_dir = os.path.join(BASE_DIR, table_name)
    mkdir_p(csv_dir)

    csv_file = os.path.join(csv_dir, "dob_violations.csv")

    if not os.path.isfile(csv_file) or args.BUST_DISK_CACHE:
        log.info("DL-ing DOB violations")
        download_file(
                "https://data.cityofnewyork.us/api/views/3h2n-5cm9/rows.csv?accessType=DOWNLOAD",
                csv_file)
    else:
        log.info("DOB Violations exists, moving on...")

    pickle = csv_dir + '/df_dob_violations.pkl'
    chunk_size = 5000
    max_col_len = 255
    date_format = "%Y%m%d"

    hpd_csv2sql(
                description,
                args,
                csv_file,
                table_name,
                dtype_dict,
                truncate_columns,
                date_time_columns,
                keep_cols,
                pickle,
                chunk_size,
                max_col_len,
                date_format=date_format,
               )


def sql_cleanup(args):
    log.info('SQL cleanup...')

    # clean_bbl must go before clean_boro!
    sql = clean_addresses(table_name, "street") + \
            clean_bbl(table_name, "boro", "block", "lot") + \
            clean_boro(table_name, "boro", bbl_code_boro_replacements())
    print(sql)

    run_sql(sql, args.TEST_MODE)


if __name__ == "__main__":
    main()
