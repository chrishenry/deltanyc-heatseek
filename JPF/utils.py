import datetime
import glob
import os
import sys
import logging
import mysql.connector
import pandas as pd
import pickle
import sqlalchemy
import wget
import zipfile

from slugify import slugify
from sqlalchemy import create_engine

BASE_DIR = os.path.join(os.path.expanduser('~'), "heatseek")

def add_common_arguments(parser):

    parser.add_argument("--load-pickle",
                action='store_true',
                dest='LOAD_PICKLE',
                default=False,
                help='Save a pickled version of the data during processing.')

    parser.add_argument("--save-pickle",
                action='store_true',
                dest='SAVE_PICKLE',
                default=False,
                help='Save a pickled version of the data during processing.')

    parser.add_argument('--bust-disk-cache',
                action='store_true',
                dest='BUST_DISK_CACHE',
                default=False,
                help='Whether to re-download data files.')

    parser.add_argument('--update-or-replace-db',
                action='store_const',
                dest='BUST_DISK_CACHE',
                const='replace',
                help='Whether to update or outright replace data.')

    return parser


def mkdir_p(my_path):
    try:
        os.stat(my_path)
    except:
        os.mkdir(my_path)


def connect():

    user = os.environ['MYSQL_USER']
    host = os.environ['MYSQL_HOST']
    pw = os.environ['MYSQL_PASSWORD']
    db = os.environ['MYSQL_DATABASE']

    conn_str = "mysql+mysqlconnector://{0}:{1}@{2}/{3}".format(user, pw, host, db)
    return create_engine(conn_str, echo=False)


def guess_sqlcol(dfparam, max_col_len):

    ## GUESS AT SQL COLUMN TYPES FROM DataFrame dtypes.

    dtypedict = {}
    for i,j in zip(dfparam.columns, dfparam.dtypes):
        if "object" in str(j):
            dtypedict.update({i: sqlalchemy.types.NVARCHAR(length=max_col_len)}) ##big field length for HPD violations description

        if "datetime" in str(j):
            dtypedict.update({i: sqlalchemy.types.DateTime()})

        if "float" in str(j):
            dtypedict.update({i: sqlalchemy.types.Float(precision=20, asdecimal=True)}) ##big precision for LAT/LONG fields

        if "int" in str(j):
            dtypedict.update({i: sqlalchemy.types.BigInteger()})

    return dtypedict



def hpd_csv2sql(description, input_csv_url, sep_char,\
            table_name, dtype_dict, load_pickle, save_pickle, \
                pickle_file, db_action, truncate_columns, date_time_columns,\
               sql_chunk_size, keep_cols, max_col_len=255, date_format=None, \
               csv_chunk_size=None):
    """ Clean up housing data and import into a sql database.

        description - tag used for logging
        dtype_dict - dict from column name to its datatype
        load_pickle - if True, uses a cached pickle of data if available
        save_pickle - if True, save a pickle of the data
        pickle_file - filename of pickle to save/load. should be a format in a unique folder if csv_chunk_size is specified.
        db_action - "replace", "append"
        truncate_columns - list of string-type columns to truncate
        date_time_columns - list of date-type columns
        sql_chunk_size - num of rows to send to sql in each operation
        keep_cols - list of columns to keep in the database
        max_col_len - length to truncate cells in truncate_columns to
        date_format - expected format of dates in the table
        csv_chunk_size - if defined, the number of rows to process from the CSV at a time.
    """

    logging.basicConfig(format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stdout,
        level=logging.DEBUG)
    log = logging.getLogger(__name__)

    log.info("Beginning {} Import {}".format(description,datetime.datetime.now()))

    # CSV chunking requested
    if csv_chunk_size is not None:

        # attempt to load split pickles
        if load_pickle and os.path.isfile(pickle_file.format(0)):
            log.info("Flagged load of Pickles with format: ".format(pickle_file))

            pickle_dir = os.path.dirname(pickle_file)

            for filename in os.listdir(pickle_dir):
                with open(os.path.join(pickle_dir, filename), 'r') as picklefile:
                    log.info("Begin OPEN {} Pickle: {}".format(filename, datetime.datetime.now()))
                    df = pickle.load(picklefile)
                    send_df_to_sql(df, log, description, table_name, db_action,\
                            sql_chunk_size, max_col_len)
                    db_action = "append"  # only first sql import should replace!

            return

        # stream csv into chunked dataframes
        log.info("Streaming {} CSV fields from {} ...".format(
            len(keep_cols), input_csv_url))

        csv_chunks = pd.read_csv(input_csv_url, sep=sep_char, dtype=dtype_dict,\
                encoding='utf8', chunksize=csv_chunk_size, usecols=keep_cols)

        # set up folder to save chunks to if pickling
        if save_pickle:
            mkdir_p(os.path.dirname(pickle_file))

        chunk_num = 0
        for df in csv_chunks:
            log.info("Processing chunk {}".format(chunk_num))

            chunk_pickle_file = pickle_file.format(chunk_num)
            df = process_df(df, log, description, save_pickle, chunk_pickle_file,\
                    truncate_columns, date_time_columns, keep_cols, date_format, max_col_len)

            if chunk_num > 0:
                db_action = "append"

            send_df_to_sql(df, log, description, table_name, db_action,\
                    sql_chunk_size, max_col_len)

            chunk_num += 1

        return

    # Load the entire CSV in one shot
    if load_pickle and os.path.isfile(pickle_file): #IF FLAGGED TO LOAD PICKLE AS TRUE
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

        df = process_df(df, log, description, save_pickle, pickle_file, truncate_columns,\
                date_time_columns, keep_cols, date_format, max_col_len)

    send_df_to_sql(df, log, description, table_name, db_action, sql_chunk_size, max_col_len)


def process_df(df, log, description, save_pickle, pickle_file, truncate_columns,\
            date_time_columns, keep_cols, date_format, max_col_len):
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
        try:
            df[i] = pd.to_datetime(df[i],format=date_format, infer_datetime_format=True)
        except:
            df[i] = pd.to_datetime('19000101')

    if save_pickle:
        log.info("Why don't we save our hard work with {} for next time".format(pickle_file))
        with open(pickle_file, 'w') as picklefile:
            log.info("Begin writing {} Pickle: {}".format(description,datetime.datetime.now()))
            pickle.dump(df, picklefile)
        log.info("Finish writing {} Pickle: {}".format(description,datetime.datetime.now()))

    return df


def send_df_to_sql(df, log, description, table_name, db_action, sql_chunk_size, max_col_len):
    log.info("Let's now try to send it to the DB")
    outputdict = guess_sqlcol(df, max_col_len)  #Guess at SQL columns based on DF dtypes
    log.debug("Show us the DB column guesses\n {}".format(outputdict))
    log.info("Begin Upload {} SQL".format(description, datetime.datetime.now()))
    log.info("Let's see if we should replace or append our table ... {}".format(db_action))

    if db_action == 'replace':
        action = db_action
    else:
        action = 'append'

    conn = connect()

    log.info("We're going with db_action = {}".format(action))
    log.info("Sending our df to {}".format(table_name))
    df.to_sql(name=table_name, con=conn, if_exists=action,\
              index=False, chunksize=sql_chunk_size, dtype=outputdict)

    if db_action == 'replace':
        conn.execute("ALTER TABLE %s ADD id INT PRIMARY KEY AUTO_INCREMENT;" % table_name)

    log.info("Completed {} Import".format(description, datetime.datetime.now()))
    log.info("Imported: {} rows".format(df.shape[0]))


def download_file(url, local_filename):
    # NOTE the stream=True parameter
    wget.download(url, out=local_filename)
    return local_filename


def unzip(filename, directory_to_extract_to):

    zip_ref = zipfile.ZipFile(filename, 'r')
    zip_ref.extractall(directory_to_extract_to)
    zip_ref.close()


def pandas_concat_csv(directory, dest_file):

    allFiles = glob.glob(directory + "/*.csv") #in path provided, look for anything with a '.csv' extension and save it to this variable
    pluto_data = pd.DataFrame()
    pluto_list_ = []
    for file_ in allFiles: #iterate through all csv files and create a pandas df
        pluto_df = pd.read_csv(file_,index_col=None, header=0)
        pluto_list_.append(pluto_df) #append every df to a big list
    pluto_data = pd.concat(pluto_list_) #combine the big list into one big pandas df
    pluto_data = pluto_data.reset_index(drop=True)
    pluto_data.to_csv(dest_file, index=False)


def simple_concat_csv(directory, dest_file):

    #in path provided, look for anything with a '.csv' extension and save it to this variable
    allFiles = glob.glob(directory + "/*.csv")
    with open(dest_file, 'w') as outfile:
        for fname in allFiles:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)


