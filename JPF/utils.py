import datetime
import glob
import os
import sys
import logging
import mysql.connector
import pandas as pd
import pickle
import requests
import sqlalchemy
import zipfile

from slugify import slugify
from sqlalchemy import create_engine

BASE_DIR = os.path.join(os.path.expanduser('~'), "heatseek")

def add_common_arguments(parser):

    parser.add_argument("--save-pickle",
                action='store_const',
                dest='SAVE_PICKLE',
                const=True,
                help='Save a pickled version of the data during processing.')


    parser.add_argument('--bust-disk-cache',
                action='store_const',
                dest='BUST_DISK_CACHE',
                const=False,
                help='Whether to re-download data files.')

    parser.add_argument('--bust-picke-cache',
                action='store_const',
                dest='BUST_DISK_CACHE',
                const=False,
                help='Whether to re-pickle data files.')

    parser.add_argument('--update-or-replace-db',
                action='store_const',
                dest='BUST_DISK_CACHE',
                const='replace',
                help='Whether to update or outright replace data.')


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
               chunk_size, keep_cols, max_col_len=255, date_format=None):

    logging.basicConfig(format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stdout,
        level=logging.DEBUG)
    log = logging.getLogger(__name__)

    log.info("Beginning {} Import {}".format(description,datetime.datetime.now()))

    if load_pickle and os.path.isfile(pickle_file): #IF FLAGGED TO LOAD PICKLE AS TRUE
        log.info("Flagged load of PICKLE: {} = True".format(pickle_file))

        with open(pickle_file, 'r') as picklefile:
            log.info("Begin OPEN {} Pickle: {}".format(pickle_file, datetime.datetime.now()))
            df = pickle.load(picklefile)

            # Don't just save the pickle after reading it.
            save_pickle = False

    else:
        log.info("Reading CSV from {} .. This may take a while...".format(input_csv_url))

        df = pd.read_csv(input_csv_url, sep=sep_char, dtype=dtype_dict, encoding='utf8')
        # Pandas had a pretty serious problem with the types we expected.
        # df = pd.read_csv(input_csv_url, encoding='utf8')

        log.debug("This is what we've read in from the URL: {}".format(df.columns))

        ## LET'S SEE IF THERE ARE COLUMNS TO TRUNCATE
        ## CLEAN COLUMN NAMES
        cols = [slugify(unicode(i.strip().replace(" ","_").replace("#","num"))) for i in df.columns]

        df.columns = cols

        log.debug("We've slugified, let's have another look: {}".format(df.columns))

        ## KEEP ONLY THE COLUMNS OF INTEREST
        log.info("Let's just keep the important {} columns".format(len(keep_cols)))
        df = df[keep_cols]

        ## TRIM COLUMN DATA TO MAX_LENGTH
        log.info("... and truncate the {} known to be long".format(len(truncate_columns)))
        for i in truncate_columns:
            df[i] = df[i].str[:max_col_len]

        ## CONVERT DATETIME COLS TO DATETIME
        log.info("Lastly .. let's convert the {} Dates to Dates".format(len(date_time_columns)))
        for i in date_time_columns:
            log.info("Starting Date: {}".format(i))
            try:
                df[i] = pd.to_datetime(df[i],format=date_format)
            except:
                df[i] = pd.to_datetime('19000101')

    if save_pickle:
        log.info("Why don't we save our hard work with {} for next time".format(pickle_file))
        with open(pickle_file, 'w') as picklefile:
            log.info("Begin writing {} Pickle: {}".format(description,datetime.datetime.now()))
            pickle.dump(df, picklefile)
        log.info("Finish writing {} Pickle: {}".format(description,datetime.datetime.now()))


    log.info("Let's now try to send it to the DB")
    outputdict = guess_sqlcol(df, max_col_len)  #Guess at SQL columns based on DF dtypes
    log.debug("Show us the DB column guesses\n {}".format(outputdict))
    log.info("Begin Upload {} SQL".format(description, datetime.datetime.now()))
    log.info("Let's see if we should replace or append our table ... {}".format(db_action))

    if db_action == 'replace':
        action = db_action
    else:
        action = 'append'

    log.info("We're going with db_action = {}".format(action))
    log.info("Sending our df to {}".format(table_name))
    df.to_sql(name=table_name, con=connect(), if_exists=action,\
              index=False, chunksize=chunk_size, dtype=outputdict)

    log.info("Completed {} Import".format(description, datetime.datetime.now()))
    log.info("Imported: {} rows".format(df.shape[0]))


def download_file(url, local_filename):
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    total_length = r.headers.get('content-length')

    if total_length is None: # no content length header
        f.write(response.content)
    else:
        dl = 0
        total_length = int(total_length)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

                    dl += len(chunk)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                    sys.stdout.flush()

    sys.stdout.write("\n")

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


