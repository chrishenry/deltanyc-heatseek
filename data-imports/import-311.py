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

CALL_311_KEY = '311-complaints'

call_311_dtype_dict = {
        'Unique Key':'int64',
        'Created Date':'object',
        'Closed Date':'object',
        'Agency':'object',
        'Agency Name':'object',
        'Complaint Type':'object',
        'Descriptor':'object',
        'Location Type':'object',
        'Incident Zip':'object',
        'Incident Address':'object',
        'Street Name':'object',
        'Cross Street 1':'object',
        'Cross Street 2':'object',
        'Intersection Street 1':'object',
        'Intersection Street 2':'object',
        'Address Type':'object',
        'City':'object',
        'Landmark':'object',
        'Facility Type':'object',
        'Status':'object',
        'Due Date':'object',
        'Resolution Description':'object',
        'Resolution Action Updated Date':'object',
        'Community Board':'object',
        'Borough':'object',
        'X Coordinate (State Plane)':'float64',
        'Y Coordinate (State Plane)':'float64',
        'Park Facility Name':'object',
        'Park Borough':'object',
        'School Name':'object',
        'School Number':'object',
        'School Region':'object',
        'School Code':'object',
        'School Phone Number':'object',
        'School Address':'object',
        'School City':'object',
        'School State':'object',
        'School Zip':'object',
        'School Not Found':'object',
        'School or Citywide Complaint':'object',
        'Vehicle Type':'object',
        'Taxi Company Borough':'object',
        'Taxi Pick Up Location':'object',
        'Bridge Highway Name':'object',
        'Bridge Highway Direction':'object',
        'Road Ramp':'object',
        'Bridge Highway Segment':'object',
        'Garage Lot Name':'object',
        'Ferry Direction':'object',
        'Ferry Terminal Name':'object',
        'Latitude':'float64',
        'Longitude':'float64',
        'Location':'object'
}

call_311_df_keep_cols = [
    "Unique Key",
    "Created Date",
    "Closed Date",
    "Agency",
    "Complaint Type",
    "Descriptor",
    "Incident Zip",
    "Incident Address",
    "Street Name",
    "Cross Street 1",
    "Cross Street 2",
    "Intersection Street 1",
    "Intersection Street 2",
    "City",
    "Status",
    "Due Date",
    "Resolution Description",
    "Resolution Action Updated Date",
    "Borough",
    "Latitude",
    "Longitude",
    "Location"
]


def main(argv):

    parser = argparse.ArgumentParser(description='Import 311 complaints dataset.')
    parser = add_common_arguments(parser)
    args = parser.parse_args()

    print args

    call_311_dir = os.path.join(BASE_DIR, CALL_311_KEY)
    mkdir_p(call_311_dir)

    call_311_csv = os.path.join(call_311_dir, '311-full.csv')

    if not os.path.isfile(call_311_csv) or args.BUST_DISK_CACHE:
        log.info("DL-ing 311 complaints")
        download_file("https://nycopendata.socrata.com/api/views/erm2-nwe9/rows.csv?accessType=DOWNLOAD", call_311_csv)
    else:
        log.info("311 complaints exist, moving on...")

    call_311_description = "311_complaints"
    call_311_pickle = os.path.join(call_311_dir, 'split', '311-chunk-{}.pkl')
    call_311_sep_char = ","
    call_311_table_name = "call_311"
    call_311_load_pickle = args.LOAD_PICKLE
    call_311_save_pickle = args.SAVE_PICKLE
    call_311_db_action = 'replace' ## if not = 'replace' then 'append'
    call_311_truncate_columns = ['resolution_description']
    call_311_date_time_columns = ['created_date','closed_date','due_date', 'resolution_action_updated_date']
    call_311_sql_chunk_size = 2500
    call_311_csv_chunk_size = 250000

    hpd_csv2sql(
            call_311_description,
            call_311_csv,
            call_311_sep_char,
            call_311_table_name,
            call_311_dtype_dict,
            call_311_load_pickle,
            call_311_save_pickle,
            call_311_pickle,
            call_311_db_action,
            call_311_truncate_columns,
            call_311_date_time_columns,
            call_311_sql_chunk_size,
            call_311_df_keep_cols,
            csv_chunk_size=call_311_csv_chunk_size
            )
    
def sql_cleanup(args):
    conn = connect()
    cursor = conn.cursor()

    SQL = '''  
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, ' AVE$|-AVE$| -AVE$', ' AVENUE');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, '\.', '', 'g');
    UPDATE call_311 SET incident_address = array_to_string(regexp_matches(incident_address, '(.*)(\d+)(?:TH|RD|ND|ST)( .+)'), '') WHERE incident_address ~ '.*(\d+)(?:TH|RD|ND|ST)( .+).*';
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, ' LA$', ' LANE', 'g');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, ' LN$', ' LANE', 'g');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, ' PL$', ' PLACE', 'g');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, ' ST$| STR$', ' STREET', 'g');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, ' RD$', ' ROAD', 'g');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, ' PKWY$', 'PARKWAY', 'g');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, ' PKWY ', ' PARKWAY ', 'g');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, ' BLVD$', ' BOULEVARD', 'g');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, ' BLVD ', ' BOULEVARD ', 'g');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, ' BLVD', ' BOULEVARD ', 'g');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, '^BCH ', 'BEACH ', 'g');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, '^E ', 'EAST ');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, '^W ', 'WEST ');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, '^N ', 'NORTH ');
    UPDATE call_311 SET incident_address = regexp_replace( incident_address, '^S ', 'SOUTH '); 
    UPDATE call_311 SET borough = regexp_replace(borough, 'MANHATTAN', 'MN', 'g');
    UPDATE call_311 SET borough = regexp_replace(borough, 'BROOKLYN', 'BK', 'g');
    UPDATE call_311 SET borough = regexp_replace(borough, 'STATEN ISLAND', 'SI', 'g');
    UPDATE call_311 SET borough = regexp_replace(borough, 'QUEENS', 'QN', 'g');
    UPDATE call_311 SET borough = regexp_replace(borough, 'BRONX', 'BR', 'g');
    UPDATE call_311 SET borough = regexp_replace(borough, 'Unspecified', '', 'g');

    '''

    for result in cursor.execute(SQL,multi = True):
        pass
    
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main(sys.argv[:1])
