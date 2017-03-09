import calendar
import clean_utils
import datetime
import luigi
import luigi_utils
import os
import tempfile
import utils

class DownloadHPDViolations():
    base_url = 'http://www1.nyc.gov/assets/hpd/downloads/misc/'
    base_out = '/root/heatseek/hpd_violations/'
    zip_filename_format = 'Violations{date:%Y%m%d}'
    txt_filename_format = 'Violation{date:%Y%m%d}'
    bad_zip_filename_date = datetime.date(2015, 3, 1)
    v2_start_date = datetime.date(2013, 5, 1)

    @classmethod
    def is_v2(cls, date):
        return date > cls.v2_start_date

    @classmethod
    def getHPDViolationDownloadTask(cls, date):
        if date != cls.bad_zip_filename_date:
            zip_filename = cls.zip_filename_format.format(date=date) + '.zip'
        else:
            zip_filename = cls.txt_filename_format.format(date=date) + '.zip'

        txt_date = date - datetime.timedelta(days=1)
        txt_filename = cls.txt_filename_format.format(date=txt_date) + '.txt'

        zip_url = cls.base_url + zip_filename
        zipout = cls.base_out + zip_filename

        return luigi_utils.DownloadUnzipTask(url=zip_url,
                zipout=zipout,
                zipfiles=[txt_filename],
                zipfilesout=[cls.base_out + txt_filename])


class ImportHPDViolationUpdate(luigi.Task):
    date = luigi.MonthParameter()

    table_name = 'hpd_violations'

    # Commented-out lines are present in latest drops but not original
    dtype_dict = {
            'ViolationID': 'object',
            'BuildingID': 'object',
            'RegistrationID': 'object',
            'Boro': 'object',
            'HouseNumber': 'object',
            'LowHouseNumber': 'object',
            'HighHouseNumber': 'object',
            'StreetName': 'object',
            'StreetCode': 'object',
            'Zip': 'object',
            'Block': 'object',
            'Lot': 'object',
            'Class': 'object',
            'InspectionDate': 'object',
            'OriginalCertifyByDate': 'object',
            'OriginalCorrectByDate': 'object',
            'NewCertifyByDate': 'object',
            'NewCorrectByDate': 'object',
            'CertifiedDate': 'object',
            'OrderNumber': 'object',
            'NOVID': 'object',
            'NOVDescription': 'object',
            'NOVIssuedDate': 'object',
            'CurrentStatus': 'object',
            'CurrentStatusDate': 'object'
            # 'BoroID': 'object',
            # 'Apartment': 'object',
            # 'Story': 'object',
            # 'ApprovedDate': 'object',
            # 'CurrentStatusID': 'int64',
            }

    date_time_columns = [
            'inspectiondate',
            # 'approveddate',
            'originalcertifybydate',
            'originalcorrectbydate',
            'newcertifybydate',
            'newcorrectbydate',
            'certifieddate',
            'novissueddate',
            'currentstatusdate'
            ]

    truncate_columns = [
            'novdescription',
            'currentstatus'
            ]

    keep_cols = [
            'ViolationID',
            'BuildingID',
            'RegistrationID',
            'Boro',
            'HouseNumber',
            'LowHouseNumber',
            'HighHouseNumber',
            'StreetName',
            'StreetCode',
            'Zip',
            'Block',
            'Lot',
            'Class',
            'InspectionDate',
            'OriginalCertifyByDate',
            'OriginalCorrectByDate',
            'NewCertifyByDate',
            'NewCorrectByDate',
            'CertifiedDate',
            'OrderNumber',
            'NOVID',
            'NOVDescription',
            'NOVIssuedDate',
            'CurrentStatus',
            'CurrentStatusDate'
            ]

    pickle_file = os.path.join(DownloadHPDViolations.base_out,
            'df_violations.pkl')

    args = luigi_utils.CmdArgsClass(DB_ACTION='append', TEST_MODE=False,
            BUST_DISK_CACHE=False, LOAD_PICKLE=False, SAVE_PICKLE=False,
            dataset='filtered')

    def requires(self):
        # Require the raw download
        tasks = {'download':
                DownloadHPDViolations.getHPDViolationDownloadTask(self.date)}

        # Require the previous month if there is one
        # TODO(rdlester): figure out how to parse pre v2
        if DownloadHPDViolations.v2_start_date < self.date:
            year = self.date.year
            prev_month = self.date.month - 1

            if prev_month == 0:
                year -= 1
                prev_month = 12

            tasks['prev'] = ImportHPDViolationUpdate(
                datetime.date(year, prev_month, day=1))

        return tasks

    def output(self):
        return luigi_utils.HeatseekDB(self.table_name, str(self.date))

    def run(self):
        utils.hpd_csv2sql(
                'Import HPD Violation update from ' + str(self.date),
                self.args,
                self.input()['download'][0].path,
                self.table_name,
                self.dtype_dict,
                self.truncate_columns,
                self.date_time_columns,
                self.keep_cols,
                self.pickle_file,
                sep_char='|'
                )

        self.output().create_marker_table()
        self.output().touch()


class CleanHPDViolations(luigi.Task):
    date = luigi.MonthParameter()

    def requires(self):
        return ImportHPDViolationUpdate(self.date)

    def output(self):
        return luigi_utils.HeatseekDB(ImportHPDViolationUpdate.table_name,
                'clean ' + str(self.date))

    def run(self):
        table_name = ImportHPDViolationUpdate.table_name
        sql = clean_utils.clean_addresses(table_name, 'streetname') + \
                clean_utils.clean_boro(table_name, 'boro',
                        clean_utils.full_name_boro_replacements()) + \
                clean_utils.add_boroid(table_name, 'boro') + \
                clean_utils.clean_bbl(ImportHPDViolationUpdate.table_name,
                        'boroid', 'block', 'lot')
        clean_utils.run_sql(sql, test_mode=False)


class GetUpdatesHPDViolations(luigi.WrapperTask):
    def requires(self):
        now_date = datetime.date.today()
        yield CleanHPDViolations(datetime.date(now_date.year, now_date.month,
            day=1))
