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
HPD Buildings import
"""

description = "HPD Complaints"

table_name = 'hpd_complaints'

dtype_dict = {
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

date_time_columns = ['statusdate','receiveddate']

truncate_columns = []

keep_cols = [
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


def main():
    args = get_common_arguments('Import hpd complaints.')

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)


def import_csv(args):
    csv_dir = os.path.join(BASE_DIR, table_name)
    mkdir_p(csv_dir)

    csv_file = os.path.join(csv_dir, "hpd_complaints.csv")

    if not os.path.isfile(csv_file) or args.BUST_DISK_CACHE:
        log.info("DL-ing HPD Complaints")
        download_file("https://data.cityofnewyork.us/api/views/uwyv-629c/rows.csv?accessType=DOWNLOAD", csv_file)
    else:
        log.info("HPD Complaints exists, moving on...")

    pickle = os.path.join(csv_dir, 'df_complaints.pkl')
    chunk_size = 5000

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
               )


def sql_cleanup(args):
    log.info('SQL cleanup...')

    sql = clean_addresses(table_name, "streetname") + \
            clean_boro(table_name, "borough", full_name_boro_replacements()) + \
            clean_bbl(table_name, "boroughid", "block", "lot")

    run_sql(sql)


if __name__ == "__main__":
    main()
