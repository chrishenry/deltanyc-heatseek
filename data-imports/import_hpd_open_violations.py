#!/usr/bin/env python

import os
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
HPD Violations import
"""

description = "HPD Violations"

table_name = 'open_hpd_violations'

sep_char = '|'

max_col_len = 500

dtype_dict = {
    'ViolationID':                'int64',
    'BuildingID':                 'int64',
    'RegistrationID':             'int64',
    'BoroID':                     'int64',
    'Boro':                      'object',
    'HouseNumber':               'object',
    'LowHouseNumber':            'object',
    'HighHouseNumber':           'object',
    'StreetName':                'object',
    'StreetCode':                 'int64',
    'Zip':                      'float64',
    'Apartment':                 'object',
    'Story':                     'object',
    'Block':                      'int64',
    'Lot':                        'int64',
    'Class':                     'object',
    'InspectionDate':            'object',
    'ApprovedDate':              'object',
    'OriginalCertifyByDate':     'object',
    'OriginalCorrectByDate':     'object',
    'NewCertifyByDate':          'object',
    'NewCorrectByDate':          'object',
    'CertifiedDate':             'object',
    'OrderNumber':               'object',
    'NOVID':                    'float64',
    'NOVDescription':            'object',
    'NOVIssuedDate':             'object',
    'CurrentStatusID':            'int64',
    'CurrentStatus':             'object',
    'CurrentStatusDate':         'object'
}

truncate_columns = []

date_time_columns = [
    'inspectiondate',
    'approveddate',
    'originalcertifybydate',
    'originalcorrectbydate',
    'newcertifybydate',
    'newcorrectbydate',
    'certifieddate',
    'novissueddate',
    'currentstatusdate'
]

keep_cols = None


def main():
    args = get_common_arguments('Import hpd violations dataset.')

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)

def import_csv(args):
    csv_dir = os.path.join(BASE_DIR, table_name)
    mkdir_p(csv_dir)

    zip_file = os.path.join(csv_dir, "hpd_violations.zip")
    csv_file = os.path.join(csv_dir, "Violation20161031.txt")

    if not os.path.isfile(csv_file) or args.BUST_DISK_CACHE:
        log.info("DL-ing HPD Buildings")
        download_file("http://www1.nyc.gov/assets/hpd/downloads/misc/AllOpenViolations20161101.zip", zip_file)
        unzip(zip_file, csv_dir)
    else:
        log.info("HPD Buildings exists, moving on...")

    pickle = os.path.join(csv_dir, 'df_violations.pkl')

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
                max_col_len=max_col_len,
                sep_char=sep_char
               )

def sql_cleanup(args):
    log.info('SQL cleanup...')

    sql = clean_addresses(table_name, "streetname") + \
            clean_boro(table_name, "boro", full_name_boro_replacements()) + \
            clean_bbl(table_name, "boroid", "block", "lot")

    run_sql(sql, args.TEST_MODE)


if __name__ == "__main__":
    main()
