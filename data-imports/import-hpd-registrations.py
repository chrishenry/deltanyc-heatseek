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

def sql_cleanup(args):
    conn = connect()
    cursor = conn.cursor()

    SQL = '''  

    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, ' AVE$|-AVE$| -AVE$', ' AVENUE');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, '\.', '', 'g');
    UPDATE hpd_registrations SET streetname = array_to_string(regexp_matches(streetname, '(.*)(\d+)(?:TH|RD|ND|ST)( .+)'), '') WHERE streetname ~ '.*(\d+)(?:TH|RD|ND|ST)( .+).*';
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, ' LA$', ' LANE', 'g');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, ' LN$', ' LANE', 'g');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, ' PL$', ' PLACE', 'g');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, ' ST$| STR$', ' STREET', 'g');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, ' RD$', ' ROAD', 'g');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, ' PKWY$', 'PARKWAY', 'g');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, ' PKWY ', ' PARKWAY ', 'g');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, ' BLVD$', ' BOULEVARD', 'g');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, ' BLVD ', ' BOULEVARD ', 'g');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, ' BLVD', ' BOULEVARD ', 'g');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, '^BCH ', 'BEACH ', 'g');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, '^E ', 'EAST ');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, '^W ', 'WEST ');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, '^N ', 'NORTH ');
    UPDATE hpd_registrations SET streetname = regexp_replace( streetname, '^S ', 'SOUTH '); 
    UPDATE hpd_registrations SET boro = regexp_replace(boro, 'MANHATTAN', 'MN', 'g');
    UPDATE hpd_registrations SET boro = regexp_replace(boro, 'BROOKLYN', 'BK', 'g');
    UPDATE hpd_registrations SET boro = regexp_replace(boro, 'STATEN ISLAND', 'SI', 'g');
    UPDATE hpd_registrations SET boro = regexp_replace(boro, 'QUEENS', 'QN', 'g');
    UPDATE hpd_registrations SET boro = regexp_replace(boro, 'BRONX', 'BR', 'g');
    SELECT concat(trim(hpd_registrations.boroid),trim(LPAD(hpd_registrations.block, 5, '0')),trim(LPAD(hpd_registrations.lot, 4, '0'))) as bbl from hpd_registrations;
    ALTER TABLE hpd_registrations CHANGE bbl bigint(13) NULL DEFAULT NULL;
    ALTER TABLE `hpd_registrations` ADD INDEX(bbl);

    '''

    for result in cursor.execute(SQL,multi = True):
        pass
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main(sys.argv[:1])
