import pandas as pd
import requests
import os
import mysql.connector
from sqlalchemy import create_engine
import json
from pandas.io.json import json_normalize
from slugify import slugify

r = requests.get("http://landlordwatchlist.com/search.js")
data = json.loads(r.text.split(";")[0].replace("var markers = ", ''))
df = json_normalize(data)

cols = [slugify(unicode(i.strip().replace(" ","_").replace("#","num"))) for i in df.columns]
df.columns = cols

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

user = os.environ['POSTGRES_USER']
host = os.environ['POSTGRES_HOST']
pw = os.environ['POSTGRES_PASSWORD']
db = os.environ['POSTGRES_DATABASE']

engine = create_engine('postgresql://{0}:{1}@{2}/{3}'.format(user, pw, host, db))
df.to_sql(name='pubadv_worst_landlords', con=engine, if_exists = 'replace', index=False, chunksize=2500)