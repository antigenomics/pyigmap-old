from sys import platform
from shutil import which
import os

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

def CAT_CMD(fname: str) -> str:
    if fname.endswith('.gz'):
        return ZCAT_CMD
    else:
        return 'cat'

if not which('parallel'):
    raise 'Requires GNU Parallel to work'

def PAR_CMD(cmd: str, cores: int) -> str:
    return f'parallel -j {cores} {cmd}'

EXT_PATH = SCRIPT_PATH + '/../external'
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