import os
import os.path
import pandas as pd
import mysql.connector
import sqlalchemy
from sqlalchemy import create_engine
import datetime
import pickle
import logging
from slugify import slugify
import requests
import glob
import psycopg2

BASE_DIR = os.path.expanduser('~')+"/Heatseek/"

try:
    os.stat(BASE_DIR)
except:
    os.mkdir(BASE_DIR)

LOG_FILE = BASE_DIR+'db_import_postgres.log'

logging.basicConfig(format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    filename=LOG_FILE, 
    level=logging.INFO)

log = logging.getLogger(__name__)
print "This notebook will log to {}".format(LOG_FILE)
log.info("This notebook will log to {}".format(LOG_FILE))

import os
import mysql.connector
from sqlalchemy import create_engine

user = os.environ['POSTGRES_USER']
host = os.environ['POSTGRES_HOST']
pw = os.environ['POSTGRES_PASSWORD']
db = os.environ['POSTGRES_DATABASE']

# try:
#     conn_str = psycopg2.connect("dbname='heatseek' user='postgres' host='localhost'")
# except:
#     print "I am unable to connect to the database"

# #conn_str = "mysql+mysqlconnector://{0}:{1}@{2}/{3}".format(user, pw, host, db)
# engine = create_engine(conn_str, echo=False)
engine = create_engine('postgresql://{0}:{1}@{2}/{3}'.format(user,pw,host,db))

def guess_sqlcol(dfparam, max_col_len): 
    
## GUESS AT SQL COLUMN TYPES FROM DataFrame dtypes. 
    
    dtypedict = {}
    for i,j in zip(dfparam.columns, dfparam.dtypes):
        if "object" in str(j):
            dtypedict.update({i: sqlalchemy.types.VARCHAR(length=max_col_len)}) ##big field length for HPD violations description

        if "datetime" in str(j):
            dtypedict.update({i: sqlalchemy.types.DateTime()})

        if "float" in str(j):
            dtypedict.update({i: sqlalchemy.types.Float(precision=20, asdecimal=True)}) ##big precision for LAT/LONG fields

        if "int" in str(j):
            dtypedict.update({i: sqlalchemy.types.BigInteger()})

    return dtypedict


def hpd_csv2sql(description, input_csv_url, sep_char,\
            table_name, dtype_dict, load_pickle, \
                pickle_file, db_action, truncate_columns, date_time_columns,\
               chunk_size, keep_cols, max_col_len=255, date_format=None):
    
    log.info("Beginning {} Import {}".format(description,datetime.datetime.now()))
    
    if load_pickle == True: #IF FLAGGED TO LOAD PICKLE AS TRUE
        log.info("Flagged load of PICKLE: {} = True".format(pickle_file))
        
        with open(pickle_file, 'r') as picklefile:
            log.info("Begin OPEN {} Pickle: {}".format(pickle_file, datetime.datetime.now()))
            log.info("Great we have a pickle file...Loading from {}".format(pickle_file))
            df = pickle.load(picklefile)

    else: 
        log.info("Reading CSV from {} .. This may take a while...".format(input_csv_url))
        
        #SWITCHING TO URL DIRECTLY, CAN'T CHECK FOR LOCAL FILE ANYMORE
        df = pd.read_csv(input_csv_url, sep=sep_char, dtype=dtype_dict, encoding='utf8')

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

        ## CONVERT DTETIME COLS TO DATETIME
        log.info("Lastly .. let's convert the {} Dates to Dates".format(len(date_time_columns)))
        for i in date_time_columns:
            log.info("Starting Date: {}".format(i))
            try: 
                df[i] = pd.to_datetime(df[i],format=date_format)
            except: 
                df[i] = pd.to_datetime('19000101')
                
    if (load_pickle == False):
        log.info("Why don't we save our hard work with {} for next time".format(pickle_file))
        with open(pickle_file, 'w') as picklefile:
            log.info("Begin writing {} Pickle: {}".format(description,datetime.datetime.now()))
            pickle.dump(df, picklefile)

        
    log.info("Let's now try to send it to the DB")
    outputdict = guess_sqlcol(df, max_col_len)  #Guess at SQL columns based on DF dtypes
    log.debug("Show us the DB columnm guesses\n {}".format(outputdict))
    log.info("Begin Upload {} SQL".format(description, datetime.datetime.now()))
    log.info("Let's see if we should replace or append our table ... {}".format(db_action))

    if db_action == 'replace': 
        
        action = db_action 

    else:
        
        action = 'append'
    
    log.info("We're going with db_action = {}".format(action))
    log.info("Sending our df to {}".format(table_name))
    df.to_sql(name=table_name, con=engine, if_exists = action,\
              index=False, chunksize=chunk_size, dtype = outputdict)

    log.info("Completed {} Import".format(description, datetime.datetime.now()))
    log.info("Imported: {} rows".format(df.shape[0]))

## SET UP TEST DIR

test_dir = BASE_DIR + 'TEST'

try:
    os.stat(test_dir)
except:
    os.mkdir(test_dir)

TEST_dtype_dict = {
    'ISN_DOB_BIS_VIOL':       'int64',
    'BORO':       'object',
    'BIN':       'float64',
    'BLOCK':       'object',
    'LOT':       'object',
    'ISSUE_DATE':       'object',
    'VIOLATION_TYPE_CODE':       'object',
    'VIOLATION_NUMBER':       'object',
    'HOUSE_NUMBER':       'object',
    'STREET':       'object',
    'DISPOSITION_DATE':       'object',
    'DISPOSITION_COMMENTS':       'object',
    'DEVICE_NUMBER':       'object',
    'DESCRIPTION':       'object',
    'ECB_NUMBER':       'object',
    'NUMBER':       'object',
    'VIOLATION_CATEGORY':       'object',
    'VIOLATION_TYPE':       'object'
}


TEST_date_time_columns = ['issue_date', 'disposition_date']

TEST_df_keep_cols = [
    'isn_dob_bis_viol',
    'boro',
    'bin',
    'block',
    'lot',
    'issue_date',
    'violation_type_code',
    'violation_number',
    'house_number',
    'street',
    'disposition_date',
    'disposition_comments',
    'device_number',
    'description',
    'ecb_number',
    'number',
    'violation_category',
    'violation_type'
]

TEST_description = 'TEST Violations'
TEST_input_csv_url = 'https://data.cityofnewyork.us/resource/dvnq-fhaa.csv?isn_dob_bis_viol=1676992'  
TEST_pickle = test_dir + '/df_TEST_violations.pkl' 
TEST_sep_char = ","
TEST_table_name = "TEST_violations"
TEST_load_pickle = False
TEST_db_action = "replace"
TEST_truncate_columns = ['description', 'ecb_number', 'number']
TEST_chunk_size = 5000
TEST_max_column_size = 255
TEST_date_format = "%Y%m%d"

hpd_csv2sql(
            TEST_description,
            TEST_input_csv_url, 
            TEST_sep_char,
            TEST_table_name, 
            TEST_dtype_dict, 
            TEST_load_pickle,   
            TEST_pickle,
            TEST_db_action, 
            TEST_truncate_columns, 
            TEST_date_time_columns, 
            TEST_chunk_size,
            TEST_df_keep_cols,
            TEST_max_column_size,
            TEST_date_format
           )


## SET UP DOB DIR

dob_dir = BASE_DIR + 'DOB'

try:
    os.stat(dob_dir)
except:
    os.mkdir(dob_dir)

vio_dob_dtype_dict = {
    'ISN_DOB_BIS_VIOL':       'int64',
    'BORO':       'object',
    'BIN':       'float64',
    'BLOCK':       'object',
    'LOT':       'object',
    'ISSUE_DATE':       'object',
    'VIOLATION_TYPE_CODE':       'object',
    'VIOLATION_NUMBER':       'object',
    'HOUSE_NUMBER':       'object',
    'STREET':       'object',
    'DISPOSITION_DATE':       'object',
    'DISPOSITION_COMMENTS':       'object',
    'DEVICE_NUMBER':       'object',
    'DESCRIPTION':       'object',
    'ECB_NUMBER':       'object',
    'NUMBER':       'object',
    'VIOLATION_CATEGORY':       'object',
    'VIOLATION_TYPE':       'object'
}


vio_dob_date_time_columns = ['issue_date', 'disposition_date']

vio_dob_df_keep_cols = [
    'isn_dob_bis_viol',
    'boro',
    'bin',
    'block',
    'lot',
    'issue_date',
    'violation_type_code',
    'violation_number',
    'house_number',
    'street',
    'disposition_date',
    'disposition_comments',
    'device_number',
    'description',
    'ecb_number',
    'number',
    'violation_category',
    'violation_type'
]

vio_dob_description = 'DOB Violations'
vio_dob_input_csv_url = 'https://data.cityofnewyork.us/api/views/3h2n-5cm9/rows.csv?accessType=DOWNLOAD'
vio_dob_pickle = dob_dir + '/df_dob_violations.pkl' 
vio_dob_sep_char = ","
vio_dob_table_name = "dob_violations"
vio_dob_load_pickle = True
vio_dob_db_action = "replace"
vio_dob_truncate_columns = ['description', 'ecb_number', 'number']
vio_dob_chunk_size = 5000
vio_max_col_len = 255
vio_date_format = "%Y%m%d"

## DONT NEED TO DOWNLOAD FILE, READ CSV WILL TAKE URL DIRECTLY    
    
hpd_csv2sql(
            vio_dob_description,
            vio_dob_input_csv_url, 
            vio_dob_sep_char,
            vio_dob_table_name, 
            vio_dob_dtype_dict, 
            vio_dob_load_pickle,   
            vio_dob_pickle,
            vio_dob_db_action, 
            vio_dob_truncate_columns, 
            vio_dob_date_time_columns, 
            vio_dob_chunk_size,
            vio_dob_df_keep_cols,
            vio_max_col_len,
            vio_date_format
           )    