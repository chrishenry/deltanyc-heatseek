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

table_name = 'aep_list'

def main(argv):
    parser = argparse.ArgumentParser(description='Import Alternative Enforcement Program dataset.')
    parser = add_common_arguments(parser)
    args = parser.parse_args()

    print args

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)


def import_csv(args):
    log.info('Importing pre-created AEP csv...')
    data_file = 'data/AEP_LIST.csv'
    df = pd.read_csv(data_file)

    conn = connect()

    df.to_sql(name=table_name, con=conn, if_exists=args.DB_ACTION,
            index=False, chunksize=2500)


def sql_cleanup(args):
    log.info('Cleaning database...')
    # TODO


if __name__ == '__main__':
    main(sys.argv[:1])
