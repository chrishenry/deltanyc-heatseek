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
HPD Complaints Problems import
"""

description = 'HPD Complaints problems'

table_name = 'hpd_complaints_problems'

dtype_dict = {
'ProblemID':             'int64',
'ComplaintID':           'int64',
'UnitTypeID':            'int64',
'UnitType':             'object',
'SpaceTypeID':           'int64',
'SpaceType':            'object',
'TypeID':                'int64',
'Type':                 'object',
'MajorCategoryID':       'int64',
'MajorCategory':        'object',
'MinorCategoryID':       'int64',
'MinorCategory':        'object',
'CodeID':                'int64',
'Code':                 'object',
'StatusID':              'int64',
'Status':               'object',
'StatusDate':           'object',
'StatusDescription':    'object',
}

date_time_columns = ['statusdate']

truncate_columns = [
        'statusdescription',
        'majorcategoryid',
        ]

keep_cols = [
    'ProblemId',
    'ComplaintId',
    'UnitTypeId',
    'UnitType',
    'SpaceTypeId',
    'SpaceType',
    'TypeId',
    'Type',
    'MajorCategoryId',
    'MajorCategory',
    'MinorCategoryId',
    'MinorCategory',
    'CodeId',
    'Code',
    'StatusId',
    'Status',
    'StatusDate',
    'StatusDescription'
]


def main():
    args = get_common_arguments('Import ' + description)

    if not args.SKIP_IMPORT:
        import_csv(args)

    # No sql cleanup for problems...

def import_csv(args):
    csv_dir = os.path.join(BASE_DIR, table_name)
    mkdir_p(csv_dir)
    csv_file = os.path.join(csv_dir, "hpd_complaints.csv")

    if not os.path.isfile(csv_file) or args.BUST_DISK_CACHE:
        log.info("DL-ing HPD Complaints")
        download_file('https://data.cityofnewyork.us/api/views/a2nx-4u46/rows.csv?accessType=DOWNLOAD', csv_file)
    else:
        log.info("HPD Complaints exists, moving on...")

    pickle = os.path.join(csv_dir, 'df_complaints_problems.pkl')
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


if __name__ == "__main__":
    main()
