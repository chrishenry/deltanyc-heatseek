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
HPD Registration import
"""

description = "HPD Registrations"

table_name = 'hpd_registrations'

dtype_dict = {
    'RegistrationID':            'int64',
    'BuildingID':                'int64',
    'BoroID':                    'int64',
    'Boro':                     'object',
    'HouseNumber':              'object',
    'LowHouseNumber':           'object',
    'HighHouseNumber':          'object',
    'StreetName':               'object',
    'StreetCode':               'int64',
    'Zip':                     'float64',
    'Block':                     'int64',
    'Lot':                       'int64',
    'BIN':                     'float64',
    'CommunityBoard':            'int64',
    'LastRegistrationDate':     'object',
    'RegistrationEndDate':      'object'
}

truncate_columns = []

date_time_columns = ['lastregistrationdate', 'registrationenddate']

keep_cols = [
    'RegistrationID',
    'BuildingID',
    'BoroID',
    'Boro',
    'HouseNumber',
    'LowHouseNumber',
    'HigHhouseNumber',
    'StreetName',
    'StreetCode',
    'Zip',
    'Block',
    'Lot',
    'BIN',
    'CommunityBoard',
    'LastRegistrationDate',
    'RegistrationEndDate'
]


def main():
    args = get_common_arguments('Import hpd registration dataset.')

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)

def import_csv(args):
    csv_dir = os.path.join(BASE_DIR, table_name)
    mkdir_p(csv_dir)

    csv_file = os.path.join(csv_dir, "hpd_reg.csv")

    if not os.path.isfile(csv_file) or args.BUST_DISK_CACHE:
        log.info("DL-ing HPD Registrations")
        download_file("https://data.cityofnewyork.us/api/views/tesw-yqqr/rows.csv?accessType=DOWNLOAD", csv_file)
    else:
        log.info("HPD Registrations exists, moving on...")

    pickle = os.path.join(csv_dir, 'df_reg.pkl')
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

    # Address cleaning breaks - erases all of some address name?
    # sql = clean_addresses(table_name, "streetname") + \
    sql = clean_boro(table_name, "boro", full_name_boro_replacements()) + \
            clean_bbl(table_name, "boroid", "block", "lot")

    run_sql(sql, args.TEST_MODE)


if __name__ == "__main__":
    main()
