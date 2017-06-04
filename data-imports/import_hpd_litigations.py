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
    level=logging.DEBUG)
log = logging.getLogger(__name__)

"""
HPD Litigations import
"""

description = "HPD Litigations"

table_name = 'hpd_litigations'

dtype_dict = {
    'LitigationID':       'int64',
    'BuildingID':         'int64',
    'BoroID':             'int64',
    'Boro':              'object',
    'HouseNumber':       'object',
    'StreetName':        'object',
    'Zip':              'object',
    'Block':              'int64',
    'Lot':                'int64',
    'CaseType':          'object',
    'CaseOpenDate':      'object',
    'CaseStatus':       'object',
    'CaseJudgement':     'object'
}

date_time_columns = ['caseopendate']

truncate_columns = []

keep_cols = [
    'LitigationID',
    'BuildingID',
    'BoroID',
    'Boro',
    'HouseNumber',
    'StreetName',
    'Zip',
    'Block',
    'Lot',
    'CaseType',
    'CaseOpenDate',
    'CaseStatus',
    'CaseJudgement',
]


def main():
    args = get_common_arguments('Import hpd litigations.')

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)


def import_csv(args):
    csv_dir = os.path.join(BASE_DIR, table_name)
    mkdir_p(csv_dir)

    csv_file = os.path.join(csv_dir, "hpd_litigations.csv")

    if not os.path.isfile(csv_file) or args.BUST_DISK_CACHE:
        log.info("DL-ing HPD Litigations")
        download_file("https://data.cityofnewyork.us/api/views/59kj-x8nc/rows.csv?accessType=DOWNLOAD", csv_file)
    else:
        log.info("HPD Litigations exists, moving on...")

    pickle = os.path.join(csv_dir, 'df_litigations.pkl')
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
            clean_boro(table_name, "boro", full_name_boro_replacements()) + \
            clean_bbl(table_name, "boroid", "block", "lot")

    run_sql(sql, args.TEST_MODE)


if __name__ == "__main__":
    main()
