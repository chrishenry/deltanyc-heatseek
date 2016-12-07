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
Taxbills Rent Stabilization joined count import
"""

TAXBILLS_KEY = 'taxbills_joined'

taxbills_dtype_dict = {
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

taxbills_keep_cols = [
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

taxbills_primary_key = "ucbbl"


def main(argv):

    parser = argparse.ArgumentParser(description='Import joined Rent Stabilization data.')
    parser = add_common_arguments(parser)
    args = parser.parse_args()

    print args

    taxbills_joined_dir = os.path.join(BASE_DIR, TAXBILLS_KEY)
    mkdir_p(taxbills_joined_dir)

    taxbills_joined_csv = os.path.join(taxbills_joined_dir, "joined.csv")

    if not os.path.isfile(taxbills_joined_csv) or args.BUST_DISK_CACHE:
        log.info("DL-ing joined taxbills data")
        download_file("http://taxbills.nyc/joined.csv", taxbills_joined_csv)
    else:
        log.info("Joined taxbills exists, moving on...")

    taxbills_description = "Taxbills Rent Stabilization"
    taxbills_pickle = taxbills_joined_dir + '/taxbills.pkl'
    taxbills_sep_char = ","
    taxbills_table_name = "rent_stabilization"
    taxbills_load_pickle = args.LOAD_PICKLE
    taxbills_save_pickle = args.SAVE_PICKLE
    taxbills_db_action = 'replace' ## if not = 'replace' then 'append'
    taxbills_truncate_columns = []
    taxbills_date_time_columns = []
    taxbills_chunk_size = 2500

    hpd_csv2sql(
                taxbills_description,
                taxbills_joined_csv,
                taxbills_sep_char,
                taxbills_table_name,
                taxbills_dtype_dict,
                taxbills_load_pickle,
                taxbills_save_pickle,
                taxbills_pickle,
                taxbills_db_action,
                taxbills_truncate_columns,
                taxbills_date_time_columns,
                taxbills_chunk_size,
                taxbills_keep_cols,
                primary_key=taxbills_primary_key
                )


if __name__ == "__main__":
    main(sys.argv[:1])
