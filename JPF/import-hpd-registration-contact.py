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

HPD_REGISTRATION_KEY = 'hpd_registration_contact'

rcn_dtype_dict = {
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

rcn_df_keep_cols = [
    'registrationcontactid',
    'registrationid',
    'type',
    'corporationname',
    'contactdescription',
    'title',
    'firstname',
    'middleinitial',
    'lastname',
    'businesshousenumber',
    'businessstreetname',
    'businessapartment',
    'businesscity',
    'businessstate',
    'businesszip'
]

def main(argv):

    parser = argparse.ArgumentParser(description='Import hpd registration dataset.')
    parser = add_common_arguments(parser)
    args = parser.parse_args()

    print args

    hpd_creg_dir = os.path.join(BASE_DIR, HPD_REGISTRATION_KEY)
    mkdir_p(hpd_creg_dir)

    hpd_reg_csv = os.path.join(hpd_creg_dir, "hpd_creg.csv")

    if not os.path.isfile(hpd_reg_csv) or args.BUST_DISK_CACHE:
        log.info("DL-ing HPD Registrations")
        download_file("https://data.cityofnewyork.us/api/views/feu5-w2e2/rows.csv?accessType=DOWNLOAD", hpd_reg_csv)
    else:
        log.info("HPD Registrations exists, moving on...")

    rcn_truncate_columns = ''
    rcn_date_time_columns = ''

    rcn_description = "HPD RegistrationsContacts"
    rcn_input_csv_url = hpd_reg_csv
    rcn_sep_char = ","
    rcn_pickle = os.path.join(hpd_creg_dir, 'df_regCon.pkl')
    rcn_table_name = 'hpd_registration_contacts'
    rcn_load_pickle = args.LOAD_PICKLE
    rcn_save_pickle = args.SAVE_PICKLE
    rcn_db_action = 'replace' ## if not = 'replace' then 'append'
    rcn_chunk_size = 5000

    hpd_csv2sql(
                rcn_description,
                rcn_input_csv_url,
                rcn_sep_char,
                rcn_table_name,
                rcn_dtype_dict,
                rcn_load_pickle,
                rcn_save_pickle,
                rcn_pickle,
                rcn_db_action,
                rcn_truncate_columns,
                rcn_date_time_columns,
                rcn_chunk_size,
                rcn_df_keep_cols
            )

if __name__ == "__main__":
    main(sys.argv[:1])


