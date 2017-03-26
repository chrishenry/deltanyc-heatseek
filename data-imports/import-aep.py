#!/usr/bin/env python

import sys
import logging

import pandas as pd

from clean_utils import *
from utils import *

mkdir_p(BASE_DIR)

logging.basicConfig(format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stdout,
    level=logging.INFO)
log = logging.getLogger(__name__)


###################
# CSV import config

table_name = 'aep_list'

def main():
    args = get_common_arguments('Import Alternative Enforcement Program dataset.')

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)


def import_csv(args):
    log.info('Importing pre-created AEP csv...')
    data_file = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../heatseek/AEP_LIST.csv'))
    df = pd.read_csv(data_file)

    conn = connect(args.TEST_MODE)

    df.to_sql(name=table_name, con=conn, if_exists=args.DB_ACTION,
            index=False, chunksize=2500)


def sql_cleanup(args):
    log.info('Cleaning database...')

    sql = clean_addresses(table_name, "full_addr") + \
        clean_boro(table_name, "borough", full_name_boro_replacements())
    run_sql(sql, args.TEST_MODE)


if __name__ == '__main__':
    main()
