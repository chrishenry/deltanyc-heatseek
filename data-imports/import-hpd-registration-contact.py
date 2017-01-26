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
HPD Registration import
"""

description = "HPD RegistrationsContacts"

table_name = 'hpd_registration_contacts'

dtype_dict = {
    'RegistrationContactID':     'int64',
    'RegistrationID':            'int64',
    'Type':                     'object',
    'ContactDescription':       'object',
    'CorporationName':          'object',
    'Title':                    'object',
    'FirstName':                'object',
    'MiddleInitial':            'object',
    'LastName':                 'object',
    'BusinessHouseNumber':      'object',
    'BusinessStreetName':       'object',
    'BusinessApartment':        'object',
    'BusinessCity':             'object',
    'BusinessState':            'object',
    'BusinessZip':              'object'
}

truncate_columns = []

date_time_columns = []

keep_cols = [
    'RegistrationContactID',
    'RegistrationID',
    'Type',
    'ContactDescription',
    'CorporationName',
    'Title',
    'FirstName',
    'MiddleInitial',
    'LastName',
    'BusinessHouseNumber',
    'BusinessStreetName',
    'BusinessApartment',
    'BusinessCity',
    'BusinessState',
    'BusinessZip'
]


def main():
    args = get_common_arguments('Import hpd registration dataset.')

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)


def import_csv(args):
    csv_dir = os.path.join(BASE_DIR, table_name)
    mkdir_p(csv_dir)

    csv_file = os.path.join(csv_dir, "hpd_creg.csv")

    if not os.path.isfile(csv_file) or args.BUST_DISK_CACHE:
        log.info("DL-ing HPD Registrations")
        download_file("https://data.cityofnewyork.us/api/views/feu5-w2e2/rows.csv?accessType=DOWNLOAD", csv_file)
    else:
        log.info("HPD Registrations exists, moving on...")

    pickle = os.path.join(csv_dir, 'df_regCon.pkl')
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

    sql = clean_addresses(table_name, "businessstreetname")

    run_sql(sql, args.TEST_MODE)


if __name__ == "__main__":
    main()
