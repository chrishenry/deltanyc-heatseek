#!/usr/bin/env python

import os.path
import sys
import logging

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

description = 'PLUTO'

table_name = "pluto_nyc"

dtype_dict = {
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

truncate_columns = []

date_time_columns = ['appdate']

keep_cols = [
    'Borough',
    'Block',
    'Lot',
    'CD',
    'CT2010',
    'CB2010',
    'SchoolDist',
    'Council',
    'ZipCode',
    'FireComp',
    'PolicePrct',
    'HealthArea',
    'SanitBoro',
    'SanitDistrict',
    'SanitSub',
    'Address',
    'ZoneDist1',
    'ZoneDist2',
    'ZoneDist3',
    'ZoneDist4',
    'Overlay1',
    'Overlay2',
    'SPDist1',
    'SPDist2',
    'SPDist3',
    'LtdHeight',
    'SplitZone',
    'BldgClass',
    'LandUse',
    'Easements',
    'OwnerType',
    'OwnerName',
    'LotArea',
    'BldgArea',
    'ComArea',
    'ResArea',
    'OfficeArea',
    'RetailArea',
    'GarageArea',
    'StrgeArea',
    'FactryArea',
    'OtherArea',
    'AreaSource',
    'NumBldgs',
    'NumFloors',
    'UnitsRes',
    'UnitsTotal',
    'LotFront',
    'LotDepth',
    'BldgFront',
    'BldgDepth',
    'Ext',
    'ProxCode',
    'IrrLotCode',
    'LotType',
    'BsmtCode',
    'AssessLand',
    'AssessTot',
    'ExemptLand',
    'ExemptTot',
    'YearBuilt',
    'YearAlter1',
    'YearAlter2',
    'HistDist',
    'Landmark',
    'BuiltFAR',
    'ResidFAR',
    'CommFAR',
    'FacilFAR',
    'BoroCode',
    'BBL',
    'CondoNo',
    'Tract2010',
    'XCoord',
    'YCoord',
    'ZoneMap',
    'ZMCode',
    'Sanborn',
    'TaxMap',
    'EDesigNum',
    'APPBBL',
    'APPDate',
    'PLUTOMapID'
]


def main():
    args = get_common_arguments('Import Pluto dataset.')

    if not args.SKIP_IMPORT:
        import_csv(args)

    sql_cleanup(args)


def import_csv(args):
    csv_dir = os.path.join(BASE_DIR, table_name)
    mkdir_p(csv_dir)

    local_pluto_file = os.path.join(csv_dir, 'pluto.zip')
    csv_file = os.path.join(csv_dir, "pluto.csv")

    if not os.path.isfile(local_pluto_file) or args.BUST_DISK_CACHE:
        log.info("DL-ing Pluto")
        download_file("http://www1.nyc.gov/assets/planning/download/zip/data-maps/open-data/nyc_pluto_16v2%20.zip", local_pluto_file)
    else:
        log.info("Pluto exists, moving on...")

    if not os.path.isfile(csv_file) or args.BUST_DISK_CACHE:
        sys.stdout.write("\rUnzipping Pluto archive....")
        unzip(local_pluto_file, csv_dir)
        sys.stdout.flush()
        sys.stdout.write("\rUnzipping Pluto archive....done.\n")

        sys.stdout.write("\rConcatenating Pluto boro csvs....")
        pluto_csv_files_dir = os.path.join(csv_dir, "BORO_zip_files_csv")
        pandas_concat_csv(pluto_csv_files_dir, csv_file)
        sys.stdout.flush()
        sys.stdout.write("\rConcatenating Pluto boro csvs....done.\n")
    else:
        sys.stdout.write("\rUsing previously concat'ed files....\n")

    pickle = os.path.join(dir, 'df_NYC.pkl')
    chunk_size = 5000
    max_column_size = 255
    date_format = "%m/%d/%Y"

    hpd_csv2sql(
                description,
                args,
                csv_file,
                table_name,
                dtype_dict,
                truncate_columns,
                date_time_columns,
                keep_cols,
                pickle,
                chunk_size,
                max_column_size,
                date_format=date_format,
               )


def sql_cleanup(args):
    log.info('SQL cleanup...')

    sql = clean_addresses(table_name, "address") + \
        clean_boro(table_name, "borough", full_name_boro_replacements())

    run_sql(sql)


if __name__ == "__main__":
    main()
