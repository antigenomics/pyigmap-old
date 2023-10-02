import os
from shutil import which
from sys import platform

CORES = os.cpu_count()
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


if platform == 'linux' or platform == 'linux2':
    ZCAT_CMD = 'zcat'
    VIDJIL_CMD = 'vidjil-algo_linux'
    IGBLAST_CMD = 'igblastn_linux'
elif platform == 'darwin':
    ZCAT_CMD = 'gzcat'
    VIDJIL_CMD = 'vidjil-algo_darwin'
    IGBLAST_CMD = 'igblastn_darwin'
elif platform == 'win32':
    raise 'Cannot run on Windows'


def CAT_CMD(fname):
    if isinstance(fname, list):
        # TODO warn if extension don't match
        fname = ' '.join(fname)
    if fname.endswith('.gz'):
        return ZCAT_CMD + ' ' + fname
    else:
        return 'cat ' + fname


if not which('parallel'):
    raise 'Requires GNU Parallel to work'


EXT_PATH = os.path.abspath(SCRIPT_PATH + '/external')
BIN_PATH = EXT_PATH + '/bin'
if os.path.exists(BIN_PATH + '/vidjil-algo'):
    VIDJIL_CMD = BIN_PATH + '/vidjil-algo'
else:
    VIDJIL_CMD = BIN_PATH + '/' + VIDJIL_CMD
if os.path.exists(BIN_PATH + '/igblastn'):
    IGBLAST_CMD = BIN_PATH + '/igblastn'
else:
    IGBLAST_CMD = BIN_PATH + '/' + IGBLAST_CMD
VIDJIL_DATA_PATH = EXT_PATH + '/vidjil-germline'
IGBLAST_DATA_PATH = EXT_PATH