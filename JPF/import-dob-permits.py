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
DOB Permits import
"""

DOB_PERMITS_KEY = 'dob_permits'

perm_dob_dtype_dict = {
        'BOROUGH':                                'object',
        'Bin #':                               'float64',
        'House #':                              'object',
        'Street Name':                            'object',
        'Job #':                               'float64',
        'Job Doc. #':                          'float64',
        'Job Type':                               'object',
        'Self_Cert':                              'object',
        'Block':                                 'float64',
        'Lot':                                    'object',
        'Community Board':                        'object',
        'Zip Code':                               'object',
        'Bldg Type':                             'float64',
        'Residential':                            'object',
        'Special District 1':                     'object',
        'Special District 2':                     'object',
        'Work Type':                              'object',
        'Permit Status':                          'object',
        'Filing Status':                          'object',
        'Permit Type':                            'object',
        'Permit Sequence #':                   'float64',
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
        'Act As Superintendent':                  'object',
        'Permittee\'s Other Title':                 'object',
        'HIC License':                            'object',
        'Site Safety Mgr\'s First Name':            'object',
        'Site Safety Mgr\'s Last Name':             'object',
        'Site Safety Mgr Business Name':          'object',
        'Superintendent First And Last Name':     'object',
        'Superintendent Business Name':           'object',
        'Owner\'s Business Type':                   'object',
        'Non-profit':                             'object',
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


perm_dob_df_keep_cols = [
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


perm_dob_date_time_columns = [
        'filing_date',
        'issuance_date',
        'expiration_date',
        'job_start_date',
        'dobrundate'
        ]


perm_dob_truncate_columns = ['borough']


def main(argv):
    parser = argparse.ArgumentParser(description='Import hpd buildings dataset.')
    parser = add_common_arguments(parser)
    args = parser.parse_args()

    print args

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)


def import_csv(args):
    dob_permits_dir = os.path.join(BASE_DIR, DOB_PERMITS_KEY)
    mkdir_p(dob_permits_dir)

    dob_permits_csv = os.path.join(dob_permits_dir, "dob_permits.csv")

    if not os.path.isfile(dob_permits_csv) or args.BUST_DISK_CACHE:
        log.info("DL-ing DOB Permits")
        download_file(
                'https://data.cityofnewyork.us/api/views/ipu4-2q9a/rows.csv?accessType=DOWNLOAD',
                dob_permits_csv)
    else:
        log.info("DOB Permits exists, moving on...")

    perm_dob_description = 'DOB Permits'
    perm_dob_pickle = dob_permits_dir + '/df_dob_permit.pkl'
    perm_dob_sep_char = ","
    perm_dob_table_name = "dob_permits"
    perm_dob_load_pickle = args.LOAD_PICKLE
    perm_dob_save_pickle = args.SAVE_PICKLE
    perm_dob_db_action = "replace"
    perm_dob_chunk_size = 2500

    hpd_csv2sql(
            perm_dob_description,
            dob_permits_csv,
            perm_dob_sep_char,
            perm_dob_table_name,
            perm_dob_dtype_dict,
            perm_dob_load_pickle,
            perm_dob_save_pickle,
            perm_dob_pickle,
            perm_dob_db_action,
            perm_dob_truncate_columns,
            perm_dob_date_time_columns,
            perm_dob_chunk_size,
            perm_dob_df_keep_cols
            )


def sql_cleanup(args):
    # TODO(ryan, alex): actual sql cleanup.
    log.info('SQL cleanup...')


if __name__ == "__main__":
    main(sys.argv[:1])
