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

import sys

try: 
	process_file = sys.argv[1]
	print "Processing: ",process_file
except: 
	process_file = "ALL"
	print "Processing: ALL - TEST, DOB, HPD, PLUTO"
	

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
if process_file == "TEST" or process_file == "ALL":
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

if process_file == "DOB" or process_file == "ALL":
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
	vio_dob_load_pickle = False
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

	perm_dob_dtype_dict = {
	'borough':                                'object',
	'bin_num':                               'float64',
	'house_num':                              'object',
	'street_name':                            'object',
	'job_num':                               'float64',
	'job_doc._num':                          'float64',
	'job_type':                               'object',
	'self_cert':                              'object',
	'block':                                 'float64',
	'lot':                                    'object',
	'community_board':                        'object',
	'zip_code':                               'object',
	'bldg_type':                             'float64',
	'residential':                            'object',
	'special_district_1':                     'object',
	'special_district_2':                     'object',
	'work_type':                              'object',
	'permit_status':                          'object',
	'filing_status':                          'object',
	'permit_type':                            'object',
	'permit_sequence_num':                   'float64',
	'permit_subtype':                         'object',
	'oil_gas':                                'object',
	'site_fill':                              'object',
	'filing_date':                            'object',
	'issuance_date':                          'object',
	'expiration_date':                        'object',
	'job_start_date':                         'object',
	'permittees_first_name':                  'object',
	'permittees_last_name':                   'object',
	'permittees_business_name':               'object',
	'permittees_phone_num':                   'object',
	'permittees_license_type':                'object',
	'permittees_license_num':                 'object',
	'act_as_superintendent':                  'object',
	'permittees_other_title':                 'object',
	'hic_license':                            'object',
	'site_safety_mgrs_first_name':            'object',
	'site_safety_mgrs_last_name':             'object',
	'site_safety_mgr_business_name':          'object',
	'superintendent_first_and_last_name':     'object',
	'superintendent_business_name':           'object',
	'owners_business_type':                   'object',
	'non-profit':                             'object',
	'owners_business_name':                   'object',
	'owners_first_name':                      'object',
	'owners_last_name':                       'object',
	'owners_house_num':                       'object',
	'owners_house_street_name':               'object',
	'owners_house_city':                      'object',
	'owners_house_state':                     'object',
	'owners_house_zip_code':                  'object',
	'owners_phone_num':                       'object',
	'dobrundate':                             'object'}


	perm_dob_date_time_columns = ['filing_date', 'issuance_date', 'expiration_date', 'job_start_date', 'dobrundate']

	perm_dob_df_keep_cols = [
	    'borough',
	    'bin_num',
	    'house_num',
	    'street_name',
	    'job_num',
	    'job_doc_num',
	    'job_type',
	    'block',
	    'lot',
	    'zip_code',
	    'bldg_type',
	    'residential',
	    'work_type',
	    'permit_status',
	    'filing_status',
	    'permit_type',
	    'filing_date',
	    'issuance_date',
	    'expiration_date',
	    'job_start_date',
	    'dobrundate'
	]

	perm_dob_description = 'DOB Permits'
	perm_dob_input_csv_url = 'https://data.cityofnewyork.us/api/views/ipu4-2q9a/rows.csv?accessType=DOWNLOAD'  
	perm_dob_pickle = dob_dir + '/df_dob_permit.pkl' 
	perm_dob_sep_char = ","
	perm_dob_table_name = "dob_permits"
	perm_dob_load_pickle = False
	perm_dob_db_action = "replace"
	perm_dob_truncate_columns = ['borough']
	perm_dob_chunk_size = 2500

	hpd_csv2sql(
	            perm_dob_description,
	            perm_dob_input_csv_url, 
	            perm_dob_sep_char, 
	            perm_dob_table_name, 
	            perm_dob_dtype_dict, 
	            perm_dob_load_pickle,   
	            perm_dob_pickle,
	            perm_dob_db_action, 
	            perm_dob_truncate_columns, 
	            perm_dob_date_time_columns, 
	            perm_dob_chunk_size,
	            perm_dob_df_keep_cols
	           )
if process_file == "HPD" or process_file == "ALL":
	## SET UP HPD DIR

	hpd_dir = BASE_DIR + 'HPD'

	try:
	    os.stat(hpd_dir)
	except:
	    os.mkdir(hpd_dir)

	lit_dtype_dict = {
	    'LitigationID':       'int64',
	    'BuildingID':         'int64',
	    'BoroID':             'int64',
	    'Boro':              'object',
	    'HouseNumber':       'object',
	    'StreetName':        'object',
	    'Zip':              'float64',
	    'Block':              'int64',
	    'Lot':                'int64',
	    'CaseType':          'object',
	    'CaseOpenDate':      'object',
	    'CaseStatus':       'object',
	    'CaseJudgement':     'object'
	}


	lit_date_time_columns = ['caseopendate']

	lit_df_keep_cols = [
	    'litigationid',
	    'buildingid',
	    'boroid',
	    'boro',
	    'housenumber',
	    'streetname',
	    'zip',
	    'block',
	    'lot',
	    'casetype',
	    'caseopendate',
	    'casestatus',
	    'casejudgement'
	]

	lit_description = 'HPD Litigations'
	lit_input_csv_url = 'https://data.cityofnewyork.us/api/views/59kj-x8nc/rows.csv?accessType=DOWNLOAD'  
	lit_pickle = hpd_dir + '/df_hpd_litigations.pkl'
	lit_sep_char = ","
	lit_table_name = "hpd_litigations"
	lit_load_pickle = False
	lit_db_action = "replace"
	lit_truncate_columns = []
	lit_chunk_size = 5000
	lit_max_column_size = 255

	hpd_csv2sql(
	            lit_description,
	            lit_input_csv_url, 
	            lit_sep_char,
	            lit_table_name, 
	            lit_dtype_dict, 
	            lit_load_pickle,   
	            lit_pickle,
	            lit_db_action, 
	            lit_truncate_columns, 
	            lit_date_time_columns, 
	            lit_chunk_size,
	            lit_df_keep_cols,
	            lit_max_column_size
	           )

	vio_dtype_dict = {
	'ViolationID':                'int64',
	'BuildingID':                 'int64',
	'RegistrationID':             'int64',
	'BoroID':                     'int64',
	'Boro':                      'object',
	'HouseNumber':               'object',
	'LowHouseNumber':            'object',
	'HighHouseNumber':           'object',
	'StreetName':                'object',
	'StreetCode':                 'int64',
	'Zip':                      'float64',
	'Apartment':                 'object',
	'Story':                     'object',
	'Block':                      'int64',
	'Lot':                        'int64',
	'Class':                     'object',
	'InspectionDate':            'object',
	'ApprovedDate':              'object',
	'OriginalCertifyByDate':     'object',
	'OriginalCorrectByDate':     'object',
	'NewCertifyByDate':          'object',
	'NewCorrectByDate':          'object',
	'CertifiedDate':             'object',
	'OrderNumber':               'object',
	'NOVID':                    'float64',
	'NOVDescription':            'object',
	'NOVIssuedDate':             'object',
	'CurrentStatusID':            'int64',
	'CurrentStatus':             'object',
	'CurrentStatusDate':         'object'
	}    



	vio_date_time_columns = ['inspectiondate',
	'approveddate',
	'originalcertifybydate',
	'originalcorrectbydate',
	'newcertifybydate',
	'newcorrectbydate',
	'certifieddate',
	'novissueddate',
	'currentstatusdate'] 
	    
	vio_df_keep_cols = [
	    'violationid',
	    'buildingid',
	    'registrationid',
	    'boroid',
	    'boro',
	    'housenumber',
	    'lowhousenumber',
	    'highhousenumber',
	    'streetname',
	    'streetcode',
	    'zip',
	    'apartment',
	    'story',
	    'block',
	    'lot',
	    'class',
	    'inspectiondate',
	    'approveddate',
	    'originalcertifybydate',
	    'originalcorrectbydate',
	    'newcertifybydate',
	    'newcorrectbydate',
	    'certifieddate',
	    'ordernumber',
	    'novid',
	    'novdescription',
	    'novissueddate',
	    'currentstatusid',
	    'currentstatus',
	    'currentstatusdate'
	]
	vio_description = "HPD Violations"
	vio_input_csv_url = 'https://data.cityofnewyork.us/api/views/wvxf-dwi5/rows.csv?accessType=DOWNLOAD'
	vio_sep_char = ","
	vio_pickle = hpd_dir + '/df_violations.pkl'
	vio_table_name = 'hpd_violations'
	vio_load_pickle = False
	vio_db_action = 'replace' ## if not = 'replace' then 'append' 
	vio_truncate_columns = ['novdescription']
	vio_chunk_size = 5000
	vio_max_column_size = 255
	vio_date_format = "%m/%d/%Y"


	hpd_csv2sql(
	            vio_description,
	            vio_input_csv_url, 
	            vio_sep_char,
	            vio_table_name, 
	            vio_dtype_dict, 
	            vio_load_pickle,     # ATTEMPT TO LOAD PICKLE FILE (specfified above as 'pickle')
	            vio_pickle,
	            vio_db_action, # DB ACTiON set as REPLACE (rather than APPEND)
	            vio_truncate_columns, 
	            vio_date_time_columns, 
	            vio_chunk_size,
	            vio_df_keep_cols,
	            vio_max_column_size,
	            vio_date_format
	           )

	bld_dtype_dict = {
	'BuildingID':              'int64',
	'BoroID':                  'int64',
	'Boro':                   'object',
	'HouseNumber':            'object',
	'LowHouseNumber':         'object',
	'HighHouseNumber':        'object',
	'StreetName':             'object',
	'Zip':                    'object',
	'Block':                   'int64',
	'Lot':                     'int64',
	'BIN':                   'float64',
	'CommunityBoard':          'int64',
	'CensusTract':           'float64',
	'ManagementProgram':      'object',
	'DoBBuildingClassID':    'float64',
	'DoBBuildingClass':       'object',
	'LegalStories':          'float64',
	'LegalClassA':           'float64',
	'LegalClassB':           'float64',
	'RegistrationID':          'int64',
	'LifeCycle':              'object',
	'RecordStatusID':          'int64',
	'RecordStatus':           'object'
	}

	bld_df_keep_cols = [
	    'buildingid',
	    'boroid',
	    'boro',
	    'housenumber',
	    'lowhousenumber',
	    'highhousenumber',
	    'streetname',
	    'zip',
	    'block',
	    'lot',
	    'bin',
	    'communityboard',
	    'censustract',
	    'managementprogram',
	    'dobbuildingclassid',
	    'dobbuildingclass',
	    'legalstories',
	    'legalclassa',
	    'legalclassb',
	    'registrationid',
	    'lifecycle',
	    'recordstatusid',
	    'recordstatus'
	]

	bld_description = "HPD Buildings"
	bld_input_csv_url = 'https://data.cityofnewyork.us/api/views/kj4p-ruqc/rows.csv?accessType=DOWNLOAD'
	bld_sep_char = ","
	bld_pickle = hpd_dir + '/df_buildings.pkl'
	bld_table_name = 'hpd_buildings'
	bld_load_pickle = False
	bld_db_action = 'replace' ## if not = 'replace' then 'append' 
	bld_truncate_columns = ''
	bld_date_time_columns = ''
	bld_chunk_size = 5000


	hpd_csv2sql(
	            bld_description,
	            bld_input_csv_url, 
	            bld_sep_char,
	            bld_table_name, 
	            bld_dtype_dict, 
	            bld_load_pickle,    
	            bld_pickle,
	            bld_db_action, 
	            bld_truncate_columns, 
	            bld_date_time_columns, 
	            bld_chunk_size,
	            bld_df_keep_cols
	           )

	cmp_dtype_dict = {
	'ComplaintID':         'int64',
	'BuildingID':          'int64',
	'BoroughID':           'int64',
	'Borough':            'object',
	'HouseNumber':        'object',
	'StreetName':         'object',
	'Zip':               'float64',
	'Block':               'int64',
	'Lot':                 'int64',
	'Apartment':          'object',
	'CommunityBoard':      'int64',
	'ReceivedDate':       'object',
	'StatusID':            'int64',
	'Status':             'object',
	'StatusDate':         'object'
	}

	cmp_df_keep_cols = [
	    'complaintid',
	    'buildingid',
	    'boroughid',
	    'borough',
	    'housenumber',
	    'streetname',
	    'zip',
	    'block',
	    'lot',
	    'apartment',
	    'communityboard',
	    'receiveddate',
	    'statusid',
	    'status',
	    'statusdate'
	]

	cmp_date_time_columns = ['statusdate','receiveddate']

	cmp_truncate_columns = ''

	cmp_description = "HPD Complaints"
	cmp_input_csv_url = 'https://data.cityofnewyork.us/api/views/uwyv-629c/rows.csv?accessType=DOWNLOAD'
	cmp_sep_char = ","
	cmp_pickle = hpd_dir + '/df_complaints.pkl'
	cmp_table_name = 'hpd_complaints'
	cmp_load_pickle = False
	cmp_db_action = 'replace' ## if not = 'replace' then 'append' 
	cmp_chunk_size = 5000

	hpd_csv2sql(
	            cmp_description,
	            cmp_input_csv_url, 
	            cmp_sep_char,
	            cmp_table_name, 
	            cmp_dtype_dict, 
	            cmp_load_pickle,   
	            cmp_pickle,
	            cmp_db_action,
	            cmp_truncate_columns, 
	            cmp_date_time_columns, 
	            cmp_chunk_size,
	            cmp_df_keep_cols
	           )

	cpb_dtype_dict = {
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

	cpb_date_time_columns = ['statusdate']

	cpb_df_keep_cols = [
	    'problemid',
	    'complaintid',
	    'unittypeid',
	    'unittype',
	    'spacetypeid',
	    'spacetype',
	    'typeid',
	    'type',
	    'majorcategoryid',
	    'majorcategory',
	    'minorcategoryid',
	    'minorcategory',
	    'codeid',
	    'code',
	    'statusid',
	    'status',
	    'statusdate',
	    'statusdescription'
	]


	cpb_description = "HPD ComplaintProblems"
	cpb_input_csv_url = 'https://data.cityofnewyork.us/api/views/a2nx-4u46/rows.csv?accessType=DOWNLOAD'
	cpb_sep_char = ","
	cpb_pickle = hpd_dir + '/df_prob.pkl'
	cpb_table_name = 'hpd_complaintsProb'
	cpb_load_pickle = False
	cpb_db_action = 'replace'
	cpb_chunk_size = 5000
	cpb_truncate_columns = ['statusdescription']

	hpd_csv2sql(
	            cpb_description,
	            cpb_input_csv_url, 
	            cpb_sep_char,
	            cpb_table_name, 
	            cpb_dtype_dict, 
	            cpb_load_pickle,
	            cpb_pickle,
	            cpb_db_action,
	            cpb_truncate_columns, 
	            cpb_date_time_columns, 
	            cpb_chunk_size,
	            cpb_df_keep_cols
	           )

	reg_dtype_dict = {
	'RegistrationID':            'int64',
	'BuildingID':                'int64',
	'BoroID':                    'int64',
	'Boro':                     'object',
	'HouseNumber':              'object',
	'LowHouseNumber':           'object',
	'HighHouseNumber':          'object',
	'StreetName':               'object',
	'StreetCode':               'int64',
	'Zip':                     'float64',
	'Block':                     'int64',
	'Lot':                       'int64',
	'BIN':                     'float64',
	'CommunityBoard':            'int64',
	'LastRegistrationDate':     'object',
	'RegistrationEndDate':      'object'}

	reg_df_keep_cols = [
	    'registrationid',
	    'buildingid',
	    'boroid',
	    'boro',
	    'housenumber',
	    'lowhousenumber',
	    'highhousenumber',
	    'streetname',
	    'streetcode',
	    'zip',
	    'block',
	    'lot',
	    'bin',
	    'communityboard',
	    'lastregistrationdate',
	    'registrationenddate'
	]

	reg_date_time_columns = ['lastregistrationdate', 'registrationenddate']
	reg_truncate_columns = ''

	reg_description = "HPD Registrations"
	reg_input_csv_url = 'https://data.cityofnewyork.us/api/views/tesw-yqqr/rows.csv?accessType=DOWNLOAD'
	reg_sep_char = ","
	reg_pickle = hpd_dir + '/df_reg.pkl'
	reg_table_name = 'hpd_registrations'
	reg_load_pickle = False
	reg_db_action = 'replace' ## if not = 'replace' then 'append' 
	reg_chunk_size = 5000

	hpd_csv2sql(
	            reg_description,
	            reg_input_csv_url, 
	            reg_sep_char,
	            reg_table_name, 
	            reg_dtype_dict, 
	            reg_load_pickle,   
	            reg_pickle,
	            reg_db_action, 
	            reg_truncate_columns, 
	            reg_date_time_columns, 
	            reg_chunk_size,
	            reg_df_keep_cols
	           )

	rcn_dtype_dict = {
	'RegistrationContactID':     'int64',
	'RegistrationID':            'int64',
	'Type':                     'object',
	'ContactDescription':       'object',
	'CorporationName':          'object',
	'Title':                    'object',
	'FirstName':                'object',
	'MiddleInitial':            'object',
	'LastName':                 'object',
	'BusinessHouseNumber':      'object',
	'BusinessStreetName':       'object',
	'BusinessApartment':        'object',
	'BusinessCity':             'object',
	'BusinessState':            'object',
	'BusinessZip':              'object'
	    }

	rcn_df_keep_cols = [
	    'registrationcontactid',
	    'registrationid',
	    'type',
	    'contactdescription',
	    'corporationname',
	    'title',
	    'firstname',
	    'middleinitial',
	    'lastname',
	    'businesshousenumber',
	    'businessstreetname',
	    'businessapartment',
	    'businesscity',
	    'businessstate',
	    'businesszip'
	]

	rcn_truncate_columns = ''

	rcn_date_time_columns = ''

	rcn_description = "HPD RegistrationsContacts"
	rcn_input_csv_url = 'https://data.cityofnewyork.us/api/views/feu5-w2e2/rows.csv?accessType=DOWNLOAD'
	rcn_sep_char = ","
	rcn_pickle = hpd_dir + '/df_regCon.pkl'
	rcn_table_name = 'hpd_registrationContact'
	rcn_load_pickle = False
	rcn_db_action = 'replace' ## if not = 'replace' then 'append' 
	rcn_chunk_size = 5000

	hpd_csv2sql(
	            rcn_description,
	            rcn_input_csv_url, 
	            rcn_sep_char,
	            rcn_table_name, 
	            rcn_dtype_dict, 
	            rcn_load_pickle,
	            rcn_pickle,
	            rcn_db_action,
	            rcn_truncate_columns, 
	            rcn_date_time_columns, 
	            rcn_chunk_size,
	            rcn_df_keep_cols
	            )
if process_file == "PLUTO" or process_file == "ALL":
	## SET UP PLUTO DIR

	pluto_dir = BASE_DIR + 'PLUTO'

	try:
	    os.stat(pluto_dir)
	except:
	    os.mkdir(pluto_dir)

	path = pluto_dir #set a variable with the path name where the files are saved
	allFiles = glob.glob(path + "/*.csv") #in path provided, look for anything with a '.csv' extension and save it to this variable
	pluto_data = pd.DataFrame()
	pluto_list_ = []
	for file_ in allFiles: #iterate through all csv files and create a pandas df
	    pluto_df = pd.read_csv(file_,index_col=None, header=0)
	    pluto_list_.append(pluto_df) #append every df to a big list
	pluto_data = pd.concat(pluto_list_) #combine the big list into one big pandas df
	pluto_data = pluto_data.reset_index(drop=True)
	pluto_data.to_csv(path + '/pluto_nyc.csv', index=False)

	PLUTO_dtype_dict = {
	    'Borough':       'object',
	    'Block':       'int64',
	    'Lot':       'int64',
	    'CD':       'int64',
	    'CT2010':       'float64',
	    'CB2010':       'float64',
	    'SchoolDist':       'float64',
	    'Council':       'float64',
	    'ZipCode':       'float64',
	    'FireComp':       'object',
	    'PolicePrct':       'float64',
	    'HealthArea':       'float64',
	    'SanitBoro':       'float64',
	    'SanitDistrict':       'float64',
	    'SanitSub':       'object',
	    'Address':       'object',
	    'ZoneDist1':       'object',
	    'ZoneDist2':       'object',
	    'ZoneDist3':       'object',
	    'ZoneDist4':       'object',
	    'Overlay1':       'object',
	    'Overlay2':       'object',
	    'SPDist1':       'object',
	    'SPDist2':       'object',
	    'SPDist3':       'object',
	    'LtdHeight':       'object',
	    'SplitZone':       'object',
	    'BldgClass':       'object',
	    'LandUse':       'float64',
	    'Easements':       'int64',
	    'OwnerType':       'object',
	    'OwnerName':       'object',
	    'LotArea':       'int64',
	    'BldgArea':       'int64',
	    'ComArea':       'int64',
	    'ResArea':       'int64',
	    'OfficeArea':       'int64',
	    'RetailArea':       'int64',
	    'GarageArea':       'int64',
	    'StrgeArea':       'int64',
	    'FactryArea':       'int64',
	    'OtherArea':       'int64',
	    'AreaSource':       'int64',
	    'NumBldgs':       'int64',
	    'NumFloors':       'float64',
	    'UnitsRes':       'int64',
	    'UnitsTotal':       'int64',
	    'LotFront':       'float64',
	    'LotDepth':       'float64',
	    'BldgFront':       'float64',
	    'BldgDepth':       'float64',
	    'Ext':       'object',
	    'ProxCode':       'float64',
	    'IrrLotCode':       'object',
	    'LotType':       'float64',
	    'BsmtCode':       'float64',
	    'AssessLand':       'int64',
	    'AssessTot':       'int64',
	    'ExemptLand':       'int64',
	    'ExemptTot':       'int64',
	    'YearBuilt':       'int64',
	    'YearAlter1':       'int64',
	    'YearAlter2':       'int64',
	    'HistDist':       'object',
	    'Landmark':       'object',
	    'BuiltFAR':       'float64',
	    'ResidFAR':       'float64',
	    'CommFAR':       'float64',
	    'FacilFAR':       'float64',
	    'BoroCode':       'int64',
	    'BBL':       'int64',
	    'CondoNo':       'int64',
	    'Tract2010':       'int64',
	    'XCoord':       'float64',
	    'YCoord':       'float64',
	    'ZoneMap':       'object',
	    'ZMCode':       'object',
	    'Sanborn':       'object',
	    'TaxMap':       'float64',
	    'EDesigNum':       'object',
	    'APPBBL':       'float64',
	    'APPDate':       'object',
	    'PLUTOMapID':       'int64'
	}



	PLUTO_df_keep_cols = [
	    'borough',
	    'block',
	    'lot',
	    'cd',
	    'ct2010',
	    'cb2010',
	    'schooldist',
	    'council',
	    'zipcode',
	    'firecomp',
	    'policeprct',
	    'healtharea',
	    'sanitboro',
	    'sanitdistrict',
	    'sanitsub',
	    'address',
	    'zonedist1',
	    'zonedist2',
	    'zonedist3',
	    'zonedist4',
	    'overlay1',
	    'overlay2',
	    'spdist1',
	    'spdist2',
	    'spdist3',
	    'ltdheight',
	    'splitzone',
	    'bldgclass',
	    'landuse',
	    'easements',
	    'ownertype',
	    'ownername',
	    'lotarea',
	    'bldgarea',
	    'comarea',
	    'resarea',
	    'officearea',
	    'retailarea',
	    'garagearea',
	    'strgearea',
	    'factryarea',
	    'otherarea',
	    'areasource',
	    'numbldgs',
	    'numfloors',
	    'unitsres',
	    'unitstotal',
	    'lotfront',
	    'lotdepth',
	    'bldgfront',
	    'bldgdepth',
	    'ext',
	    'proxcode',
	    'irrlotcode',
	    'lottype',
	    'bsmtcode',
	    'assessland',
	    'assesstot',
	    'exemptland',
	    'exempttot',
	    'yearbuilt',
	    'yearalter1',
	    'yearalter2',
	    'histdist',
	    'landmark',
	    'builtfar',
	    'residfar',
	    'commfar',
	    'facilfar',
	    'borocode',
	    'bbl',
	    'condono',
	    'tract2010',
	    'xcoord',
	    'ycoord',
	    'zonemap',
	    'zmcode',
	    'sanborn',
	    'taxmap',
	    'edesignum',
	    'appbbl',
	    'appdate',
	    'plutomapid'
	]

	PLUTO_date_time_columns = ['appdate']
	PLUTO_description = 'PLUTO'
	PLUTO_input_csv_url = pluto_dir + '/pluto_nyc.csv'  
	PLUTO_pickle = pluto_dir + '/df_PLUTO_NYC.pkl' 
	PLUTO_sep_char = ","
	PLUTO_table_name = "pluto_nyc"
	PLUTO_load_pickle = False
	PLUTO_db_action = "replace"
	PLUTO_truncate_columns = []
	PLUTO_chunk_size = 5000
	PLUTO_max_column_size = 255
	PLUTO_date_format = "%m/%d/%Y"

	hpd_csv2sql(
	            PLUTO_description,
	            PLUTO_input_csv_url, 
	            PLUTO_sep_char,
	            PLUTO_table_name, 
	            PLUTO_dtype_dict, 
	            PLUTO_load_pickle,   
	            PLUTO_pickle,
	            PLUTO_db_action, 
	            PLUTO_truncate_columns, 
	            PLUTO_date_time_columns, 
	            PLUTO_chunk_size,
	            PLUTO_df_keep_cols,
	            PLUTO_max_column_size,
	            PLUTO_date_format
	           )

	
if process_file == '311' or process_file == 'ALL':
## SET UP 311 DIR

_311_dir = BASE_DIR + '311'

try:
    os.stat(_311_dir)
except:
    os.mkdir(_311_dir)

call_311_dtype_dict = {'Unique Key':'int64',
'Created Date':'object',
'Closed Date':'object',
'Agency':'object',
'Agency Name':'object',
'Complaint Type':'object',
'Descriptor':'object',
'Location Type':'object',
'Incident Zip':'object',
'Incident Address':'object',
'Street Name':'object',
'Cross Street 1':'object',
'Cross Street 2':'object',
'Intersection Street 1':'object',
'Intersection Street 2':'object',
'Address Type':'object',
'City':'object',
'Landmark':'object',
'Facility Type':'object',
'Status':'object',
'Due Date':'object',
'Resolution Description':'object',
'Resolution Action Updated Date':'object',
'Community Board':'object',
'Borough':'object',
'X Coordinate (State Plane)':'float64',
'Y Coordinate (State Plane)':'float64',
'Park Facility Name':'object',
'Park Borough':'object',
'School Name':'object',
'School Number':'object',
'School Region':'object',
'School Code':'object',
'School Phone Number':'object',
'School Address':'object',
'School City':'object',
'School State':'object',
'School Zip':'object',
'School Not Found':'object',
'School or Citywide Complaint':'float64',
'Vehicle Type':'object',
'Taxi Company Borough':'object',
'Taxi Pick Up Location':'object',
'Bridge Highway Name':'object',
'Bridge Highway Direction':'object',
'Road Ramp':'object',
'Bridge Highway Segment':'object',
'Garage Lot Name':'object',
'Ferry Direction':'object',
'Ferry Terminal Name':'object',
'Latitude':'float64',
'Longitude':'float64',
'Location':'object'}

call_311_df_keep_cols = [
    "unique_key",
    "created_date",
    "closed_date",
    "agency",
    "complaint_type",
    "descriptor",
    "incident_zip",
    "incident_address",
    "street_name",
    "cross_street_1",
    "cross_street_2",
    "intersection_street_1",
    "intersection_street_2",
    "city",
    "status",
    "due_date",
    "resolution_description",
    "resolution_action_updated_date",
    "borough",
    "latitude",
    "longitude",
    "location"
    ]

call_311_description = "311_xaa"
call_311_pickle = _311_dir + '/xaa_c.pkl'
call_311_input_csv_url = BASE_DIR + '311/Data Files/2016_Jan1-Nov14/xaa_c'
call_311_sep_char = ","
call_311_table_name = "call_311"
call_311_load_pickle = False
call_311_db_action = 'replace' ## if not = 'replace' then 'append' 
call_311_truncate_columns = ['resolution_description']
call_311_date_time_columns = ['created_date','closed_date','due_date', 'resolution_action_updated_date']
call_311_chunk_size = 2500

hpd_csv2sql(
            call_311_description,
            call_311_input_csv_url, 
            call_311_sep_char,
            call_311_table_name, 
            call_311_dtype_dict, 
            call_311_load_pickle,   
            call_311_pickle,
            call_311_db_action,
            call_311_truncate_columns, 
            call_311_date_time_columns, 
            call_311_chunk_size,
            call_311_df_keep_cols
            )
call_311_description = "311_xab"
call_311_pickle = _311_dir + '/xab_c.pkl'
call_311_input_csv_url = BASE_DIR + '311/Data Files/2016_Jan1-Nov14/xab_c'
call_311_db_action = 'append' ## if not = 'replace' then 'append' 

hpd_csv2sql(
            call_311_description,
            call_311_input_csv_url, 
            call_311_sep_char,
            call_311_table_name, 
            call_311_dtype_dict, 
            call_311_load_pickle,   
            call_311_pickle,
            call_311_db_action,
            call_311_truncate_columns, 
            call_311_date_time_columns, 
            call_311_chunk_size,
            call_311_df_keep_cols
            )

call_311_description = "311_xac"
call_311_pickle = _311_dir + '/xac_c.pkl'
call_311_input_csv_url = BASE_DIR + '311/Data Files/2016_Jan1-Nov14/xac_c'

hpd_csv2sql(
            call_311_description,
            call_311_input_csv_url, 
            call_311_sep_char,
            call_311_table_name, 
            call_311_dtype_dict, 
            call_311_load_pickle,   
            call_311_pickle,
            call_311_db_action,
            call_311_truncate_columns, 
            call_311_date_time_columns, 
            call_311_chunk_size,
            call_311_df_keep_cols
            )

call_311_description = "311_xad"
call_311_pickle = _311_dir + '/xad_c.pkl'
call_311_input_csv_url = BASE_DIR + '311/Data Files/2016_Jan1-Nov14/xad_c'

hpd_csv2sql(
            call_311_description,
            call_311_input_csv_url, 
            call_311_sep_char,
            call_311_table_name, 
            call_311_dtype_dict, 
            call_311_load_pickle,   
            call_311_pickle,
            call_311_db_action,
            call_311_truncate_columns, 
            call_311_date_time_columns, 
            call_311_chunk_size,
            call_311_df_keep_cols
            )

call_311_description = "311_xae"
call_311_pickle = _311_dir + '/xae_c.pkl'
call_311_input_csv_url = BASE_DIR + '311/Data Files/2016_Jan1-Nov14/xae_c'

hpd_csv2sql(
            call_311_description,
            call_311_input_csv_url, 
            call_311_sep_char,
            call_311_table_name, 
            call_311_dtype_dict, 
            call_311_load_pickle,   
            call_311_pickle,
            call_311_db_action,
            call_311_truncate_columns, 
            call_311_date_time_columns, 
            call_311_chunk_size,
            call_311_df_keep_cols
            )

call_311_description = "311_xaf"
call_311_pickle = _311_dir + '/xaf_c.pkl'
call_311_input_csv_url = BASE_DIR + '311/Data Files/2016_Jan1-Nov14/xaf_c'

hpd_csv2sql(
            call_311_description,
            call_311_input_csv_url, 
            call_311_sep_char,
            call_311_table_name, 
            call_311_dtype_dict, 
            call_311_load_pickle,   
            call_311_pickle,
            call_311_db_action,
            call_311_truncate_columns, 
            call_311_date_time_columns, 
            call_311_chunk_size,
            call_311_df_keep_cols
            )

call_311_description = "311_xag"
call_311_pickle = _311_dir + '/xag_c.pkl'
call_311_input_csv_url = BASE_DIR + '311/Data Files/2016_Jan1-Nov14/xag_c'


hpd_csv2sql(
            call_311_description,
            call_311_input_csv_url, 
            call_311_sep_char,
            call_311_table_name, 
            call_311_dtype_dict, 
            call_311_load_pickle,   
            call_311_pickle,
            call_311_db_action,
            call_311_truncate_columns, 
            call_311_date_time_columns, 
            call_311_chunk_size,
            call_311_df_keep_cols
            )

call_311_description = "311_xah"
call_311_pickle = _311_dir + '/xah_c.pkl'
call_311_input_csv_url = BASE_DIR + '311/Data Files/2016_Jan1-Nov14/xah_c'


hpd_csv2sql(
            call_311_description,
            call_311_input_csv_url, 
            call_311_sep_char,
            call_311_table_name, 
            call_311_dtype_dict, 
            call_311_load_pickle,   
            call_311_pickle,
            call_311_db_action,
            call_311_truncate_columns, 
            call_311_date_time_columns, 
            call_311_chunk_size,
            call_311_df_keep_cols
            )

call_311_description = "311_xai"
call_311_pickle = _311_dir + '/xai_c.pkl'
call_311_input_csv_url = BASE_DIR + '311/Data Files/2016_Jan1-Nov14/xai_c'


hpd_csv2sql(
            call_311_description,
            call_311_input_csv_url, 
            call_311_sep_char,
            call_311_table_name, 
            call_311_dtype_dict, 
            call_311_load_pickle,   
            call_311_pickle,
            call_311_db_action,
            call_311_truncate_columns, 
            call_311_date_time_columns, 
            call_311_chunk_size,
            call_311_df_keep_cols
            )
