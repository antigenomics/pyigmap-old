import os
import pandas as pd
from .misc import CAT_CMD, CORES, IGBLAST_CMD, IGBLAST_DATA_PATH

class IgBlastWrapper:
    species_glossary = {'hs': 'human',
                        'human' : 'human',
                        'homo-sapiens' : 'human',
                        'mus': 'mouse',
                        'mouse': 'mouse',
                        'mus-musculus': 'mouse'}
    
    #os.environ['IGDATA'] = os.path.abspath('.')
    pass