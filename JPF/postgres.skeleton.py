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


