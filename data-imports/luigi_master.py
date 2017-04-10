from collections import namedtuple
import copy
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
standard_args = CmdArgsClass(TEST_MODE=False, BUST_DISK_CACHE=True,
        LOAD_PICKLE=False, SAVE_PICKLE=False, DB_ACTION='replace',
        dataset='filtered')

class HeatseekDB(luigi.contrib.mysqldb.MySqlTarget):
    """ Wrapper MySqlTarget that obtains connection info from env.
    """
    def __init__(self, update_id):
        super(HeatseekDB, self).__init__(
                os.environ['MYSQL_HOST'], os.environ['MYSQL_DATABASE'],
                os.environ['MYSQL_USER'], os.environ['MYSQL_PASSWORD'],
                'imports', update_id)

class RunImportScript(luigi.Task):
    def module(self):
        return NotImplementedError('Import script not provided')

    def sql_cleanup(self):
        """ Override for scripts that do not run cleanup.
        """
        return True

    def output(self):
        return HeatseekDB(self.module().__name__)

    def run(self):
        module = self.module()
        module.import_csv(standard_args)
        if self.sql_cleanup():
            module.sql_cleanup(standard_args)
        self.output().create_marker_table()
        self.output().touch()

class Import311(RunImportScript):
    def module(self):
        return import_311

class ImportAEP(RunImportScript):
    def module(self):
        return import_aep

class ImportDOBPermits(RunImportScript):
    def module(self):
        return import_dob_permits

class ImportDOBViolations(RunImportScript):
    def module(self):
        return import_dob_violations

class ImportHPDBuildings(RunImportScript):
    def module(self):
        return import_hpd_buildings

class ImportHPDComplaints(RunImportScript):
    def module(self):
        return import_hpd_complaints

class ImportHPDComplaintsProblems(RunImportScript):
    def module(self):
        return import_hpd_complaints_problems

    def sql_cleanup(self):
        return False

class ImportHPDLitigations(RunImportScript):
    def module(self):
        return import_hpd_litigations

class ImportHPDRegistrations(RunImportScript):
    def module(self):
        return import_hpd_registrations

class ImportHPDRegistrationContact(RunImportScript):
    def module(self):
        return import_hpd_registration_contact

class ImportPluto(RunImportScript):
    def module(self):
        return import_pluto

class ImportRentStab(RunImportScript):
    def module(self):
        return import_rent_stab

class ImportWorstLandlords(RunImportScript):
    def module(self):
        return import_worst_landlords

class ImportAll(luigi.WrapperTask):
    def requires(self):
        yield Import311()
        yield ImportAEP()
        yield ImportDOBPermits()
        yield ImportDOBViolations()
        yield ImportHPDBuildings()
        yield ImportHPDComplaints()
        yield ImportHPDComplaintsProblems()
        yield ImportHPDLitigations()
        yield ImportHPDRegistrations()
        yield ImportHPDRegistrationContact()
        yield ImportPluto()
        yield ImportRentStab()
        yield ImportWorstLandlords()
