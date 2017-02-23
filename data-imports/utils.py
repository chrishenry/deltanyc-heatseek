import argparse
import datetime
import glob
import os
import sys
import logging
import pandas as pd
import pickle
import sqlalchemy
import wget
import zipfile

from slugify import slugify
from sqlalchemy import create_engine

BASE_DIR = os.path.join(os.path.expanduser('~'), "heatseek")

def get_common_arguments(description, extra_args=None):
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("--load-pickle",
            action='store_true',
            dest='LOAD_PICKLE',
            help='Save a pickled version of the data during processing.')
    parser.add_argument("--save-pickle",
            action='store_true',
            dest='SAVE_PICKLE',
            help='Save a pickled version of the data during processing.')
    parser.add_argument('--bust-disk-cache',
            action='store_true',
            dest='BUST_DISK_CACHE',
            help='Forces re-download of data files.')
    parser.add_argument('--update-db',
            action='store_const',
            dest='DB_ACTION',
            default='replace',
            const='append',
            help='"append" to the database if the table already exists instead of "replace".')
    parser.add_argument('--skip-import',
            action='store_true',
            dest='SKIP_IMPORT',
            help='Skips the CSV->SQL import.')
    parser.add_argument('--test-mode',
            action='store_true',
            dest='TEST_MODE')

    if extra_args:
        for arg, kwargs in extra_args.iteritems():
            parser.add_argument(arg, **kwargs)

    args = parser.parse_args()

    print(args)

    return args


def mkdir_p(my_path):
    try:
        os.stat(my_path)
    except:
        os.mkdir(my_path)


def connect(test_mode=False):
    """ Returns a SQLAlchemy.Engine with a connection pool for the configured database.
    """
    user = os.environ['MYSQL_USER']
    host = os.environ['MYSQL_HOST']
    password = os.environ['MYSQL_PASSWORD']
    database = os.environ['MYSQL_DATABASE'] if not test_mode else 'heatseek_test'

    conn_str = "mysql+mysqlconnector://{0}:{1}@{2}/{3}".format(user, password, host, database)
    return create_engine(conn_str, echo=False)


def guess_sqlcol(dfparam, max_col_len):
    """ Returns a map from columns of |dfparam| to SQL types.
    """
    ## GUESS AT SQL COLUMN TYPES FROM DataFrame dtypes.

    dtypedict = {}
    for i, j in zip(dfparam.columns, dfparam.dtypes):
        if "object" in str(j):
            # big field length for HPD violations description
            dtypedict.update({i: sqlalchemy.types.NVARCHAR(length=max_col_len)})

        if "datetime" in str(j):
            dtypedict.update({i: sqlalchemy.types.DateTime()})

        if "float" in str(j):
            # big precision for LAT/LONG fields
            dtypedict.update({i: sqlalchemy.types.Float(precision=20, asdecimal=True)})

        if "int" in str(j):
            dtypedict.update({i: sqlalchemy.types.BigInteger()})

    return dtypedict


def hpd_csv2sql(description, args, input_csv_url, table_name, dtype_dict,
        truncate_columns, date_time_columns, keep_cols, pickle_file, sql_chunk_size=2500,
        max_col_len=255, date_format=None, csv_chunk_size=None, sep_char=","):
    """ Clean up housing data and import into a sql database.

        description - tag used for logging
        args - CLI args obtained from get_common_arguments()
        input_csv_url - URL or filepath to CSV file
        table_name - name of the SQL table to create / modify
        dtype_dict - dict from column name to its datatype
        truncate_columns - list of string-type columns to truncate
        date_time_columns - list of date-type columns
        keep_cols - list of columns to keep in the database
        pickle_file - filename of pickle to save/load.
            should be a format in a unique folder if csv_chunk_size is specified.
        sql_chunk_size - num of rows to send to sql in each operation
        max_col_len - length to truncate cells in truncate_columns to
        date_format - expected format of dates in the table
        csv_chunk_size - if defined, the number of rows to process from the CSV at a time.
    """
    logging.basicConfig(format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stdout,
        level=logging.DEBUG)
    log = logging.getLogger(__name__)

    log.info("Beginning {} Import {}".format(description, datetime.datetime.now()))

    if args.TEST_MODE:
        csv_chunk_size = 1000

    # CSV chunking requested
    if csv_chunk_size is not None:

        # attempt to load split pickles
        if args.LOAD_PICKLE and os.path.isfile(pickle_file.format(0)):
            log.info("Flagged load of Pickles with format: {}".format(pickle_file))

            pickle_dir = os.path.dirname(pickle_file)

            # copy db_action out of args struct for modification while looping over csv chunks
            db_action = args.DB_ACTION

            for filename in os.listdir(pickle_dir):
                with open(os.path.join(pickle_dir, filename), 'r') as picklefile:
                    log.info("Begin OPEN {} Pickle: {}".format(filename, datetime.datetime.now()))
                    df = pickle.load(picklefile)
                    send_df_to_sql(df, log, description, table_name, db_action,
                            sql_chunk_size, max_col_len, args.TEST_MODE)
                    db_action = "append"  # only first sql import should replace!

            return

        # stream csv into chunked dataframes
        log.info("Streaming {} CSV fields from {} ...".format(
            len(keep_cols), input_csv_url))

        csv_chunks = pd.read_csv(input_csv_url, sep=sep_char, dtype=dtype_dict,
                encoding='utf8', chunksize=csv_chunk_size, usecols=keep_cols)

        # set up folder to save chunks to if pickling
        if args.SAVE_PICKLE:
            mkdir_p(os.path.dirname(pickle_file))

        # copy db_action out of args struct for modification while looping over csv chunks
        db_action = args.DB_ACTION

        chunk_num = 0
        for df in csv_chunks:
            log.info("Processing chunk {}".format(chunk_num))

            chunk_pickle_file = pickle_file.format(chunk_num)
            df = process_df(df, log, description, args.SAVE_PICKLE, chunk_pickle_file,
                    truncate_columns, date_time_columns, date_format, max_col_len)

            if chunk_num > 0:
                db_action = "append"

            send_df_to_sql(df, log, description, table_name, db_action,
                    sql_chunk_size, max_col_len, args.TEST_MODE)

            chunk_num += 1

            if args.TEST_MODE:
                break

        return

    # Load the entire CSV in one shot
    if args.LOAD_PICKLE and os.path.isfile(pickle_file): #IF FLAGGED TO LOAD PICKLE AS TRUE
        log.info("Flagged load of PICKLE: {} = True".format(pickle_file))

        with open(pickle_file, 'r') as picklefile:
            log.info("Begin OPEN {} Pickle: {}".format(pickle_file, datetime.datetime.now()))
            df = pickle.load(picklefile)

    else:
        log.info("Reading {} CSV fields from {} ... This may take a while...".format(
            len(keep_cols), input_csv_url))

        df = pd.read_csv(input_csv_url, sep=sep_char, dtype=dtype_dict, encoding='utf8',
                usecols=keep_cols)

        log.debug("This is what we've read in from the URL: {}".format(df.columns))

        df = process_df(df, log, description, args.SAVE_PICKLE, pickle_file, truncate_columns,
                date_time_columns, date_format, max_col_len)

    send_df_to_sql(df, log, description, table_name, args.DB_ACTION, sql_chunk_size,
            max_col_len, args.TEST_MODE)


def process_df(df, log, description, save_pickle, pickle_file, truncate_columns,
            date_time_columns, date_format, max_col_len):
    """ Cleans up a DataFrame: truncates strings, converts dates, saves pickle.
    """
    ## LET'S SEE IF THERE ARE COLUMNS TO TRUNCATE
    ## CLEAN COLUMN NAMES
    cols = [slugify(unicode(i.strip().replace(" ","_").replace("#","num"))) for i in df.columns]

    df.columns = cols

    log.debug("We've slugified, let's have another look: {}".format(df.columns))

    ## TRIM COLUMN DATA TO MAX_LENGTH
    log.info("... and truncate the {} known to be long".format(len(truncate_columns)))
    for i in truncate_columns:
        df[i] = df[i].str[:max_col_len]

    ## CONVERT DATETIME COLS TO DATETIME
    log.info("Lastly .. let's convert the {} Dates to Dates".format(len(date_time_columns)))
    for i in date_time_columns:
        log.info("Starting Date: {}".format(i))
        # http://pandas.pydata.org/pandas-docs/stable/generated/pandas.to_datetime.html
        # errors coerce will result invalid data set to NULL in MySQL
        df[i] = pd.to_datetime(df[i], format=date_format, infer_datetime_format=True, errors='coerce')

    if save_pickle:
        log.info("Why don't we save our hard work with {} for next time".format(pickle_file))
        with open(pickle_file, 'w') as picklefile:
            log.info("Begin writing {} Pickle: {}".format(description, datetime.datetime.now()))
            pickle.dump(df, picklefile)
        log.info("Finish writing {} Pickle: {}".format(description, datetime.datetime.now()))

    return df


def send_df_to_sql(df, log, description, table_name, db_action, sql_chunk_size, max_col_len,
        test_mode):
    """ Imports a DataFrame into a SQL database.
    """
    log.info("Let's now try to send it to the DB")
    outputdict = guess_sqlcol(df, max_col_len)  #Guess at SQL columns based on DF dtypes
    log.debug("Show us the DB column guesses\n {}".format(outputdict))
    log.info("Begin Upload {} SQL".format(description))
    log.info("Let's see if we should replace or append our table ... {}".format(db_action))

    if db_action == 'replace':
        action = db_action
    else:
        action = 'append'

    conn = connect(test_mode)

    log.info("We're going with db_action = {}".format(action))
    log.info("Sending our df to {}".format(table_name))
    df.to_sql(name=table_name, con=conn, if_exists=action,
            index=False, chunksize=sql_chunk_size, dtype=outputdict)

    log.info("Completed {} Import".format(description))
    log.info("Imported: {} rows".format(df.shape[0]))


def download_file(url, local_filename):
    """ Downloads a file from |url| to the file with path |local_filename|.
    """
    wget.download(url, out=local_filename)
    return local_filename


def unzip(filename, directory_to_extract_to):
    """ Unzips |filename| to |directory_to_extract_to|.
    """
    zip_ref = zipfile.ZipFile(filename, 'r')
    zip_ref.extractall(directory_to_extract_to)
    zip_ref.close()


def simple_concat_csv(directory, dest_file):
    """ Concats a set of CSV files to a single CSV file.
    """
    #in path provided, look for anything with a '.csv' extension and save it to this variable
    all_files = glob.glob(directory + "/*.csv")
    with open(dest_file, 'w') as outfile:
        with open(all_files[0], 'rb') as header_file:
            outfile.write(header_file.next())

        for fname in all_files:
            with open(fname) as infile:
                infile.next()
                for line in infile:
                    outfile.write(line)
