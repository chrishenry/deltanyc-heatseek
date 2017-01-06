#!/usr/bin/env python

import argparse
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
HPD Buildings import
"""

hpd_complaints_KEY = 'hpd_complaints'

cmp_dtype_dict = {
    'ComplaintID':         'int64',
    'BuildingID':          'int64',
    'BoroughID':           'int64',
    'Borough':            'object',
    'HouseNumber':        'object',
    'StreetName':         'object',
    'Zip':               'float64',
    'Block':               'int64',
    'Lot':                 'int64',
    'Apartment':          'object',
    'CommunityBoard':      'int64',
    'ReceivedDate':       'object',
    'StatusID':            'int64',
    'Status':             'object',
    'StatusDate':         'object'
}

cmp_df_keep_cols = [
    'ComplaintID',
    'BuildingID',
    'BoroughID',
    'Borough',
    'HouseNumber',
    'StreetName',
    'Zip',
    'Block',
    'Lot',
    'Apartment',
    'CommunityBoard',
    'ReceivedDate',
    'StatusID',
    'Status',
    'StatusDate',
]

cmp_date_time_columns = ['statusdate','receiveddate']

cmp_truncate_columns = ''

table_name = 'hpd_complaints'


def main(argv):
    parser = argparse.ArgumentParser(description='Import hpd complaints.')
    parser = add_common_arguments(parser)
    args = parser.parse_args()

    print args

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)


def import_csv(args):
    hpd_complaints_dir = os.path.join(BASE_DIR, hpd_complaints_KEY)
    mkdir_p(hpd_complaints_dir)

    hpd_complaints_csv = os.path.join(hpd_complaints_dir, "hpd_complaints.csv")

    if not os.path.isfile(hpd_complaints_csv) or args.BUST_DISK_CACHE:
        log.info("DL-ing HPD Complaints")
        download_file("https://data.cityofnewyork.us/api/views/uwyv-629c/rows.csv?accessType=DOWNLOAD", hpd_complaints_csv)
    else:
        log.info("HPD Complaints exists, moving on...")

    cmp_description = "HPD Complaints"
    cmp_input_csv_url = hpd_complaints_csv
    cmp_sep_char = ","
    cmp_pickle = os.path.join(hpd_complaints_dir, 'df_complaints.pkl')
    cmp_load_pickle = args.LOAD_PICKLE
    cmp_save_pickle = args.SAVE_PICKLE
    cmp_db_action = args.DB_ACTION
    cmp_chunk_size = 5000

    hpd_csv2sql(
                cmp_description,
                cmp_input_csv_url,
                cmp_sep_char,
                table_name,
                cmp_dtype_dict,
                cmp_load_pickle,
                cmp_save_pickle,
                cmp_pickle,
                cmp_db_action,
                cmp_truncate_columns,
                cmp_date_time_columns,
                cmp_chunk_size,
                cmp_df_keep_cols
               )


def sql_cleanup(args):
    log.info('SQL cleanup...')

    sql = clean_addresses(table_name, "streetname") + \
            clean_boro(table_name, "borough", full_name_boro_replacements()) + \
            clean_bbl(table_name, "boroughid", "block", "lot")

    run_sql(sql)


if __name__ == "__main__":
    main(sys.argv[:1])
