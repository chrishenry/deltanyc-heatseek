#!/usr/bin/env python

import argparse
import os
import os.path
import sys
import logging


from sqlalchemy import create_engine

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

HPD_REGISTRATION_KEY = 'hpd_registration'

reg_dtype_dict = {
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

reg_df_keep_cols = [
    'registrationid',
    'buildingid',
    'boroid',
    'boro',
    'housenumber',
    'lowhousenumber',
    'highhousenumber',
    'streetname',
    'streetcode',
    'zip',
    'block',
    'lot',
    'bin',
    'communityboard',
    'lastregistrationdate',
    'registrationenddate'
]

def main(argv):

    parser = argparse.ArgumentParser(description='Import hpd registration dataset.')
    parser = add_common_arguments(parser)
    args = parser.parse_args()

    print args

    hpd_reg_dir = os.path.join(BASE_DIR, HPD_REGISTRATION_KEY)
    mkdir_p(hpd_reg_dir)

    hpd_reg_csv = os.path.join(hpd_reg_dir, "hpd_reg.csv")

    if not os.path.isfile(hpd_reg_csv) or args.BUST_DISK_CACHE:
        log.info("DL-ing HPD Registrations")
        download_file("https://data.cityofnewyork.us/api/views/tesw-yqqr/rows.csv?accessType=DOWNLOAD", hpd_reg_csv)
    else:
        log.info("HPD Registrations exists, moving on...")

    reg_date_time_columns = ['lastregistrationdate', 'registrationenddate']
    reg_truncate_columns = ''

    reg_description = "HPD Registrations"
    reg_input_csv_url = hpd_reg_csv
    reg_sep_char = ","
    reg_pickle = os.path.join(hpd_reg_dir, 'df_reg.pkl')
    reg_table_name = 'hpd_registrations'
    reg_load_pickle = args.LOAD_PICKLE
    reg_save_pickle = args.SAVE_PICKLE
    reg_db_action = 'replace' ## if not = 'replace' then 'append'
    reg_chunk_size = 5000

    hpd_csv2sql(
                reg_description,
                reg_input_csv_url,
                reg_sep_char,
                reg_table_name,
                reg_dtype_dict,
                reg_load_pickle,
                reg_save_pickle,
                reg_pickle,
                reg_db_action,
                reg_truncate_columns,
                reg_date_time_columns,
                reg_chunk_size,
                reg_df_keep_cols
               )

if __name__ == "__main__":
    main(sys.argv[:1])


