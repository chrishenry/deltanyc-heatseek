from collections import namedtuple
import copy
import importlib
import import_311
import import_aep
import import_dob_permits
import import_dob_violations
import import_hpd_buildings
import import_hpd_complaints
import import_hpd_complaints_problems
import import_hpd_litigations
import import_hpd_registrations
import import_hpd_registration_contact
import import_pluto
import import_rent_stab
import import_worst_landlords
import luigi
import luigi.contrib.mysqldb
import os

CmdArgsClass = namedtuple('CmdArgsClass', ['TEST_MODE', 'BUST_DISK_CACHE',
    'LOAD_PICKLE', 'SAVE_PICKLE', 'DB_ACTION', 'dataset'])
standard_args = CmdArgsClass(TEST_MODE=False, BUST_DISK_CACHE=False,
        LOAD_PICKLE=False, SAVE_PICKLE=False, DB_ACTION='replace',
        dataset='filtered')

class ModuleParameter(luigi.Parameter):
    """ Luigi parameter of type Python module.
    """
    def parse(self, x):
        return importlib.import_module(x)

    def serialize(self, x):
        return x.__name__

class HeatseekDB(luigi.contrib.mysqldb.MySqlTarget):
    """ Wrapper MySqlTarget that obtains connection info from env.
    """
    def __init__(self, table, update_id):
        super(HeatseekDB, self).__init__(
                os.environ['MYSQL_HOST'], os.environ['MYSQL_DATABASE'],
                os.environ['MYSQL_USER'], os.environ['MYSQL_PASSWORD'],
                'imports', update_id)

class RunImportScript(luigi.Task):
    module = ModuleParameter()
    skip_sql_cleanup = luigi.BoolParameter()

    def output(self):
        return HeatseekDB(self.module.table_name, self.module.__name__)

    def run(self):
        self.module.import_csv(standard_args)
        if not self.skip_sql_cleanup:
            self.module.sql_cleanup(standard_args)
        self.output().create_marker_table()
        self.output().touch()

class ImportAll(luigi.WrapperTask):
    def requires(self):
        yield RunImportScript(module=import_311)
        yield RunImportScript(module=import_aep)
        yield RunImportScript(module=import_dob_permits)
        yield RunImportScript(module=import_dob_violations)
        yield RunImportScript(module=import_hpd_buildings)
        yield RunImportScript(module=import_hpd_complaints)
        yield RunImportScript(
                module=import_hpd_complaints_problems, skip_sql_cleanup=True)
        yield RunImportScript(module=import_hpd_litigations)
        yield RunImportScript(module=import_hpd_registrations)
        yield RunImportScript(module=import_hpd_registration_contact)
        yield RunImportScript(module=import_pluto)
        yield RunImportScript(module=import_rent_stab)
        yield RunImportScript(module=import_worst_landlords)
