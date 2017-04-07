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
DOB Permits import
"""

description = 'DOB Permits'

table_name = "dob_permits"

dtype_dict = {
        'BOROUGH':                                'object',
        'Bin #':                               'object',
        'House #':                              'object',
        'Street Name':                            'object',
        'Job #':                               'object',
        'Job doc. #':                          'object',
        'Job Type':                               'object',
        'Self_Cert':                              'object',
        'Block':                                 'object',
        'Lot':                                    'object',
        'Community Board':                        'object',
        'Zip Code':                               'object',
        'Bldg Type':                             'object',
        'Residential':                            'object',
        'Special District 1':                     'object',
        'Special District 2':                     'object',
        'Work Type':                              'object',
        'Permit Status':                          'object',
        'Filing Status':                          'object',
        'Permit Type':                            'object',
        'Permit Sequence #':                   'object',
        'Permit Subtype':                         'object',
        'Oil Gas':                                'object',
        'Site Fill':                              'object',
        'Filing Date':                            'object',
        'Issuance Date':                          'object',
        'Expiration Date':                        'object',
        'Job Start Date':                         'object',
        'Permittee\'s First Name':                  'object',
        'Permittee\'s Last Name':                   'object',
        'Permittee\'s Business Name':               'object',
        'Permittee\'s Phone #':                   'object',
        'Permittee\'s License Type':                'object',
        'Permittee\'s License #':                 'object',
        'Act as Superintendent':                  'object',
        'Permittee\'s Other Title':                 'object',
        'HIC License':                            'object',
        'Site Safety Mgr\'s First Name':            'object',
        'Site Safety Mgr\'s Last Name':             'object',
        'Site Safety Mgr Business Name':          'object',
        'Superintendent First And Last Name':     'object',
        'Superintendent Business Name':           'object',
        'Owner\'s Business Type':                   'object',
        'Non-Profit':                             'object',
        'Owner\'s Business Name':                   'object',
        'Owner\'s First Name':                      'object',
        'Owner\'s Last Name':                       'object',
        'Owner\'s House #':                       'object',
        'Owner\'s House Street Name':               'object',
        'Owner\'s House City':                      'object',
        'Owner\'s House State':                     'object',
        'Owner\'s House Zip Code':                  'object',
        'Owner\'s Phone #':                       'object',
        'DOBRunDate':                             'object'
        }

truncate_columns = ['borough']

date_time_columns = [
        'filing_date',
        'issuance_date',
        'expiration_date',
        'job_start_date',
        'dobrundate'
        ]

keep_cols = [
        'BOROUGH',
        'Bin #',
        'House #',
        'Street Name',
        'Job #',
        'Job doc. #',
        'Job Type',
        'Block',
        'Lot',
        'Zip Code',
        'Bldg Type',
        'Residential',
        'Work Type',
        'Permit Status',
        'Filing Status',
        'Permit Type',
        'Filing Date',
        'Issuance Date',
        'Expiration Date',
        'Job Start Date',
        'DOBRunDate'
        ]


def main():
    args = get_common_arguments('Import hpd buildings dataset.')

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)


def import_csv(args):
    csv_dir = os.path.join(BASE_DIR, table_name)
    mkdir_p(csv_dir)

    csv_file = os.path.join(csv_dir, "dob_permits.csv")

    if not os.path.isfile(csv_file) or args.BUST_DISK_CACHE:
        log.info("DL-ing DOB Permits")
        download_file(
                'https://data.cityofnewyork.us/api/views/ipu4-2q9a/rows.csv?accessType=DOWNLOAD',
                csv_file)
    else:
        log.info("DOB Permits exists, moving on...")

    pickle = csv_dir + '/df_dob_permit.pkl'
    chunk_size = 2500

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

    sql = clean_addresses(table_name, "street_name") + \
        clean_boro(table_name, "borough", full_name_boro_replacements()) + \
        add_boroid(table_name, "borough") + \
        clean_bbl(table_name, "boroughid", "block", "lot")

    run_sql(sql, args.TEST_MODE)


if __name__ == "__main__":
    main()
