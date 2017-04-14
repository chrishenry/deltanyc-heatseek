#!/usr/bin/env python

import argparse
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
Taxbills Rent Stabilization joined count import
"""

description = "Taxbills Rent Stabilization"

table_name = "rent_stabilization"

primary_key = "ucbbl"

dtype_dict = {
    "borough": "object",
    "ucbbl": "int32",
    "2007uc": "float64", "2007est": "object", "2007dhcr": "object", "2007abat": "object",
    "2008uc": "float64", "2008est": "object", "2008dhcr": "object", "2008abat": "object",
    "2009uc": "float64", "2009est": "object", "2009dhcr": "object", "2009abat": "object",
    "2010uc": "float64", "2010est": "object", "2010dhcr": "object", "2010abat": "object",
    "2011uc": "float64", "2011est": "object", "2011dhcr": "object", "2011abat": "object",
    "2012uc": "float64", "2012est": "object", "2012dhcr": "object", "2012abat": "object",
    "2013uc": "float64", "2013est": "object", "2013dhcr": "object", "2013abat": "object",
    "2014uc": "float64", "2014est": "object", "2014dhcr": "object", "2014abat": "object",
    "2015uc": "float64", "2015est": "object", "2015dhcr": "object", "2015abat": "object",
    "cd": "float64",
    "ct2010": "object",
    "cb2010": "object",
    "council": "float64",
    "zipcode": "object",
    "address": "object",
    "ownername": "object",
    "numbldgs": "float64",
    "numfloors": "float64",
    "unitsres": "float64",
    "unitstotal": "float64",
    "yearbuilt": "float64",
    "condono": "float64",
    "lon": "float64",
    "lat": "float64"
}

keep_cols = [
    "ucbbl",
    "2007uc",
    "2007est",
    "2007dhcr",
    "2007abat",
    "2008uc",
    "2008est",
    "2008dhcr",
    "2008abat",
    "2009uc",
    "2009est",
    "2009dhcr",
    "2009abat",
    "2010uc",
    "2010est",
    "2010dhcr",
    "2010abat",
    "2011uc",
    "2011est",
    "2011dhcr",
    "2011abat",
    "2012uc",
    "2012est",
    "2012dhcr",
    "2012abat",
    "2013uc",
    "2013est",
    "2013dhcr",
    "2013abat",
    "2014uc",
    "2014est",
    "2014dhcr",
    "2014abat",
    "2015uc",
    "2015est",
    "2015dhcr",
    "2015abat"
]

truncate_columns = []
date_time_columns = []


def main():
    args = get_common_arguments('Import joined Rent Stabilization data.')

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)


def import_csv(args):
    csv_dir = os.path.join(BASE_DIR, table_name)
    mkdir_p(csv_dir)

    csv_file = os.path.join(csv_dir, "joined.csv")

    if not os.path.isfile(csv_file) or args.BUST_DISK_CACHE:
        log.info("DL-ing joined taxbills data")
        download_file("http://taxbills.nyc/joined.csv", csv_file)
    else:
        log.info("Joined taxbills exists, moving on...")

    pickle = csv_dir + '/taxbills.pkl'

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
                )


def sql_cleanup(args):
    log.info('SQL cleanup...')

    sql = make_primary(table_name, primary_key)
    run_sql(sql, args.TEST_MODE)


if __name__ == "__main__":
    main()
