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

hpd_complaints_KEY = 'hpd_complaints'

cmp_dtype_dict = {
    'ComplaintID':         'int64',
    'BuildingID':          'int64',
    'BoroughID':           'int64',
    'Borough':            'object',
    'HouseNumber':        'object',
    'StreetName':         'object',
    'Zip':               'float64',
    'Block':               'int64',
    'Lot':                 'int64',
    'Apartment':          'object',
    'CommunityBoard':      'int64',
    'ReceivedDate':       'object',
    'StatusID':            'int64',
    'Status':             'object',
    'StatusDate':         'object'
}

cmp_df_keep_cols = [
    'ComplaintID',
    'BuildingID',
    'BoroughID',
    'Borough',
    'HouseNumber',
    'StreetName',
    'Zip',
    'Block',
    'Lot',
    'Apartment',
    'CommunityBoard',
    'ReceivedDate',
    'StatusID',
    'Status',
    'StatusDate',
]

cmp_date_time_columns = ['statusdate','receiveddate']

cmp_truncate_columns = ''


def main(argv):

    parser = argparse.ArgumentParser(description='Import hpd complaints.')
    parser = add_common_arguments(parser)
    args = parser.parse_args()

    print args

    hpd_complaints_dir = os.path.join(BASE_DIR, hpd_complaints_KEY)
    mkdir_p(hpd_complaints_dir)

    hpd_complaints_csv = os.path.join(hpd_complaints_dir, "hpd_complaints.csv")

    if not os.path.isfile(hpd_complaints_csv) or args.BUST_DISK_CACHE:
        log.info("DL-ing HPD Complaints")
        download_file("https://data.cityofnewyork.us/api/views/uwyv-629c/rows.csv?accessType=DOWNLOAD", hpd_complaints_csv)
    else:
        log.info("HPD Complaints exists, moving on...")

    cmp_description = "HPD Complaints"
    cmp_input_csv_url = hpd_complaints_csv
    cmp_sep_char = ","
    cmp_pickle = os.path.join(hpd_complaints_dir, 'df_complaints.pkl')
    cmp_table_name = 'hpd_complaints'
    cmp_load_pickle = args.LOAD_PICKLE
    cmp_save_pickle = args.SAVE_PICKLE
    cmp_db_action = args.DB_ACTION
    cmp_chunk_size = 5000

    hpd_csv2sql(
                cmp_description,
                cmp_input_csv_url,
                cmp_sep_char,
                cmp_table_name,
                cmp_dtype_dict,
                cmp_load_pickle,
                cmp_save_pickle,
                cmp_pickle,
                cmp_db_action,
                cmp_truncate_columns,
                cmp_date_time_columns,
                cmp_chunk_size,
                cmp_df_keep_cols
               )

    # sql_cleanup([])

def sql_cleanup(args):

    conn = connect()

    SQL = '''
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, ' AVE$|-AVE$| -AVE$', ' AVENUE');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, '\.', '', 'g');
    UPDATE hpd_complaints SET streetname = array_to_string(regexp_matches(streetname, '(.*)(\d+)(?:TH|RD|ND|ST)( .+)'), '') WHERE streetname ~ '.*(\d+)(?:TH|RD|ND|ST)( .+).*';
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, ' LA$', ' LANE', 'g');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, ' LN$', ' LANE', 'g');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, ' PL$', ' PLACE', 'g');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, ' ST$| STR$', ' STREET', 'g');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, ' RD$', ' ROAD', 'g');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, ' PKWY$', 'PARKWAY', 'g');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, ' PKWY ', ' PARKWAY ', 'g');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, ' BLVD$', ' BOULEVARD', 'g');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, ' BLVD ', ' BOULEVARD ', 'g');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, ' BLVD', ' BOULEVARD ', 'g');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, '^BCH ', 'BEACH ', 'g');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, '^E ', 'EAST ');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, '^W ', 'WEST ');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, '^N ', 'NORTH ');
    UPDATE hpd_complaints SET streetname = regexp_replace( streetname, '^S ', 'SOUTH ');
    UPDATE hpd_complaints SET boro = regexp_replace(boro, 'MANHATTAN', 'MN', 'g');
    UPDATE hpd_complaints SET boro = regexp_replace(boro, 'BROOKLYN', 'BK', 'g');
    UPDATE hpd_complaints SET boro = regexp_replace(boro, 'STATEN ISLAND', 'SI', 'g');
    UPDATE hpd_complaints SET boro = regexp_replace(boro, 'QUEENS', 'QN', 'g');
    UPDATE hpd_complaints SET boro = regexp_replace(boro, 'BRONX', 'BR', 'g');
    SELECT concat(trim(hpd_complaints.boroid),trim(LPAD(hpd_complaints.block, 5, '0')),trim(LPAD(hpd_complaints.lot, 4, '0'))) as bbl from hpd_complaints;
    ALTER TABLE hpd_complaints CHANGE bbl bigint(13) NULL DEFAULT NULL;
    ALTER TABLE hpd_complaints ADD INDEX(bbl);
    '''

    for result in conn.execute(SQL, multi=True):
        print result

    conn.commit()


if __name__ == "__main__":
    main(sys.argv[:1])
