#!/usr/bin/env python

import argparse
import json
import logging
import os
import os.path
import pickle
import requests
import sys
from pandas.io.json import json_normalize
from slugify import slugify

from utils import *

mkdir_p(BASE_DIR)

logging.basicConfig(format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stdout,
    level=logging.INFO)
log = logging.getLogger(__name__)

table_name = 'pubadv_worst_landlords'

data_dir = os.path.join(BASE_DIR, 'worst-landlords')
mkdir_p(data_dir)

data_file = os.path.join(data_dir, 'worst-landlords.json')

def main(argv):
    parser = argparse.ArgumentParser(description='Import worst landlords list.')
    parser = add_common_arguments(parser)
    args = parser.parse_args()

    print args

    if not args.SKIP_IMPORT:
        import_data(args)

    sql_cleanup(args)


def import_data(args):
    if not os.path.isfile(data_file) or args.BUST_DISK_CACHE:
        log.info("DL-ing worst landlords list")
        r = requests.get("http://landlordwatchlist.com/search.js")
        with open(data_file, 'wb') as f:
            f.write(r.text.split(";")[0].replace("var markers = ", ''))
    else:
        log.info("Worst landlords list exists, moving on...")

    pickle_file = os.path.join(data_dir, 'worst-landlords.pkl')

    if not args.BUST_DISK_CACHE and args.LOAD_PICKLE:
        log.info('Loading pickle...')
        with open(pickle_file, 'rb') as f:
            df = pickle.load(f)
    else:
        df = process_data(args)

    log.info('Sending to database...')
    conn = connect()
    df.to_sql(name=table_name, con=conn, if_exists=args.DB_ACTION,
            index=False, chunksize=2500)


def process_data(args):
    log.info("Reading data...")
    with open(data_file, 'rb') as f:
        data = json.load(f)
    df = json_normalize(data)

    log.info("Slugifying column names...")
    cols = [slugify(unicode(i.strip().replace(" ","_").replace("#","num"))) for i in df.columns]
    df.columns = cols

    log.info("Convert integer columns to int SQL type...")
    int_cols = [
        'a_units',
        'bin',
        'b_units',
        'buildingid',
        'dof',
        'landlordid',
        'rank',
        'units',
        'zip',
        'a',
        'b',
        'c',
        'dob',
        'dob_hpd',
        'exclude',
        'i',
        'lat', #FLOAT
        'lng', #FLOAT
        'num',
        'score', #FLOAT
        'worstlandlord'
    ]
    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    if args.SAVE_PICKLE:
        log.info('Saving a pickle...')
        with open(pickle_file, 'wb') as f:
            pickle.dump(df, f)

    return df


def sql_cleanup(args):
    log.info('Cleaning the data...')
    # TODO: cleaning


if __name__ == '__main__':
    main(sys.argv[:1])
