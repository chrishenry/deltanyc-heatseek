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
HPD Buildings import
"""

HPD_BUILDINGS_KEY = 'hpd_buildings'

bld_dtype_dict = {
    'BuildingID':              'int64',
    'BoroID':                  'int64',
    'Boro':                   'object',
    'HouseNumber':            'object',
    'LowHouseNumber':         'object',
    'HighHouseNumber':        'object',
    'StreetName':             'object',
    'Zip':                    'object',
    'Block':                   'int64',
    'Lot':                     'int64',
    'BIN':                   'float64',
    'CommunityBoard':          'int64',
    'CensusTract':           'float64',
    'ManagementProgram':      'object',
    'DoBBuildingClassID':    'float64',
    'DoBBuildingClass':       'object',
    'LegalStories':          'float64',
    'LegalClassA':           'float64',
    'LegalClassB':           'float64',
    'RegistrationID':          'int64',
    'LifeCycle':              'object',
    'RecordStatusID':          'int64',
    'RecordStatus':           'object'
}

bld_df_keep_cols = [
    'BuildingID',
    'BoroID',
    'Boro',
    'HouseNumber',
    'LowHouseNumber',
    'HighHouseNumber',
    'StreetName',
    'Zip',
    'Block',
    'Lot',
    'BIN',
    'CommunityBoard',
    'CensusTract',
    'ManagementProgram',
    'DoBBuildingClassID',
    'DoBBuildingClass',
    'LegalStories',
    'LegalClassA',
    'LegalClassB',
    'RegistrationID',
    'LifeCycle',
    'RecordStatusID',
    'RecordStatus'
]

bld_truncate_columns = ''

bld_date_time_columns = ''


def main(argv):

    parser = argparse.ArgumentParser(description='Import hpd buildings dataset.')
    parser = add_common_arguments(parser)
    args = parser.parse_args()

    print args

    hpd_buildings_dir = os.path.join(BASE_DIR, HPD_BUILDINGS_KEY)
    mkdir_p(hpd_buildings_dir)

    hpd_buildings_csv = os.path.join(hpd_buildings_dir, "hpd_buildings.csv")

    if not os.path.isfile(hpd_buildings_csv) or args.BUST_DISK_CACHE:
        log.info("DL-ing HPD Buildings")
        download_file("https://data.cityofnewyork.us/api/views/kj4p-ruqc/rows.csv?accessType=DOWNLOAD", hpd_buildings_csv)
    else:
        log.info("HPD Buildings exists, moving on...")

    bld_description = "HPD Buildings"
    bld_input_csv_url = hpd_buildings_csv
    bld_sep_char = ","
    bld_pickle = os.path.join(hpd_buildings_dir, 'df_buildings.pkl')
    bld_table_name = 'hpd_buildings'
    bld_load_pickle = args.LOAD_PICKLE
    bld_save_pickle = args.SAVE_PICKLE
    bld_db_action = 'replace' ## if not = 'replace' then 'append'
    bld_chunk_size = 5000

    hpd_csv2sql(
                bld_description,
                bld_input_csv_url,
                bld_sep_char,
                bld_table_name,
                bld_dtype_dict,
                bld_load_pickle,
                bld_save_pickle,
                bld_pickle,
                bld_db_action,
                bld_truncate_columns,
                bld_date_time_columns,
                bld_chunk_size,
                bld_df_keep_cols
               )

def sql_cleanup(args):
    conn = connect()
    cursor = conn.cursor()

    SQL = '''  

    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, ' AVE$|-AVE$| -AVE$', ' AVENUE');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, '\.', '', 'g');
    UPDATE hpd_buildings SET streetname = array_to_string(regexp_matches(streetname, '(.*)(\d+)(?:TH|RD|ND|ST)( .+)'), '') WHERE streetname ~ '.*(\d+)(?:TH|RD|ND|ST)( .+).*';
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, ' LA$', ' LANE', 'g');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, ' LN$', ' LANE', 'g');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, ' PL$', ' PLACE', 'g');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, ' ST$| STR$', ' STREET', 'g');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, ' RD$', ' ROAD', 'g');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, ' PKWY$', 'PARKWAY', 'g');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, ' PKWY ', ' PARKWAY ', 'g');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, ' BLVD$', ' BOULEVARD', 'g');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, ' BLVD ', ' BOULEVARD ', 'g');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, ' BLVD', ' BOULEVARD ', 'g');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, '^BCH ', 'BEACH ', 'g');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, '^E ', 'EAST ');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, '^W ', 'WEST ');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, '^N ', 'NORTH ');
    UPDATE hpd_buildings SET streetname = regexp_replace( streetname, '^S ', 'SOUTH '); 
    UPDATE hpd_buildings SET boro = regexp_replace(boro, 'MANHATTAN', 'MN', 'g');
    UPDATE hpd_buildings SET boro = regexp_replace(boro, 'BROOKLYN', 'BK', 'g');
    UPDATE hpd_buildings SET boro = regexp_replace(boro, 'STATEN ISLAND', 'SI', 'g');
    UPDATE hpd_buildings SET boro = regexp_replace(boro, 'QUEENS', 'QN', 'g');
    UPDATE hpd_buildings SET boro = regexp_replace(boro, 'BRONX', 'BR', 'g');
    SELECT concat(trim(hpd_buildings.boroid),trim(LPAD(hpd_buildings.block, 5, '0')),trim(LPAD(hpd_buildings.lot, 4, '0'))) as bbl from hpd_buildings;
    ALTER TABLE hpd_buildings CHANGE bbl bigint(13) NULL DEFAULT NULL;
    ALTER TABLE `hpd_buildings` ADD INDEX(bbl);

    '''

    for result in cursor.execute(SQL,multi = True):
        pass
    
    conn.commit()
    cursor.close()
    conn.close()
if __name__ == "__main__":
    main(sys.argv[:1])
