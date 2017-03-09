from collections import namedtuple
import luigi.contrib.mysqldb
import os
import tempfile
import wget
import zipfile

CmdArgsClass = namedtuple('CmdArgsClass', ['TEST_MODE', 'BUST_DISK_CACHE',
    'LOAD_PICKLE', 'SAVE_PICKLE', 'DB_ACTION', 'dataset'])
standard_args = CmdArgsClass(TEST_MODE=False, BUST_DISK_CACHE=False,
        LOAD_PICKLE=False, SAVE_PICKLE=False, DB_ACTION='replace',
        dataset='filtered')

class HeatseekDB(luigi.contrib.mysqldb.MySqlTarget):
    """ Wrapper MySqlTarget that obtains connection info from env.
    """
    def __init__(self, table, update_id):
        super(HeatseekDB, self).__init__(
                os.environ['MYSQL_HOST'], os.environ['MYSQL_DATABASE_DATA'],
                os.environ['MYSQL_USER'], os.environ['MYSQL_PASSWORD'],
                table, update_id)


class DownloadUnzipTask(luigi.Task):
    """ Luigi task that downloads a zip file and extracts a given set of files.

    Task only outputs extracted files; zip file is deleted on completion.

    Args:
        url: URL of zip file to download.
        zipout: File path to write zip file to.
        zipfiles: Files to extract from the Zip.
        zipfilesout: File paths to extract files to.
    """

    url = luigi.Parameter()
    zipout = luigi.Parameter()
    zipfiles = luigi.ListParameter()
    zipfilesout = luigi.ListParameter()

    def output(self):
        return [luigi.LocalTarget(filename) for filename in self.zipfilesout]

    def run(self):
        outputs = self.output()
        wget.download(self.url, self.zipout)

        tmpdir = tempfile.mkdtemp()

        with zipfile.ZipFile(self.zipout, 'r') as zipout_zipfile:
            for filename in self.zipfiles:
                zipout_zipfile.extract(filename, tmpdir)

        for (filename, target) in zip(self.zipfiles, outputs):
            with target.temporary_path() as temp_output_path:
                os.rename(os.path.join(tmpdir, filename), temp_output_path)

        os.rmdir(tmpdir)
        os.remove(self.zipout)
