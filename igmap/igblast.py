from .misc import CAT_CMD, FQ2FA_CMD, CORES, IGBLAST_CMD, IGBLAST_DATA_PATH

class IgBlastWrapper:
    species_glossary = {'hs': 'human',
                        'human' : 'human',
                        'homo-sapiens' : 'human',
                        'mus': 'mouse',
                        'mouse': 'mouse',
                        'mus-musculus': 'mouse'}
    
    receptor_glossary = {
        'IG': 'Ig',
        'ig': 'Ig',
        'Ig': 'Ig',
        'TR': 'TCR',
        'TCR': 'TCR',
        'tr': 'tr',
        'tcr': 'TCR'
    }
    
    def __init__(self,
                 germline='human',
                 receptor='TCR',
                 cores=CORES,
                 n=-1):
        self.species = self.species_glossary[germline]
        self.receptor = self.receptor_glossary[receptor]
        params = [f'-germline_db_V {IGBLAST_DATA_PATH}/database/{self.species}.V',
                  f'-germline_db_D {IGBLAST_DATA_PATH}/database/{self.species}.D',
                  f'-germline_db_J {IGBLAST_DATA_PATH}/database/{self.species}.J',
                  f'-organism {self.species}',
                  f'-auxiliary_data {IGBLAST_DATA_PATH}/optional_file/{self.species}_gl.aux',
                  f'-ig_seqtype {self.receptor} -show_translation -outfmt 19 -num_threads {cores}']
        # TODO build mouse C germline
        if self.species is 'human':
            params.append(f'-c_region_db {IGBLAST_DATA_PATH}/database/ncbi_{self.species}_c_genes')        
        params = ' '.join(params)
        self.igblast_cmd = f'{IGBLAST_CMD} {params}'
        self.cores = cores
        self.n = n

    def run_cmd(self,
                input,
                output):
        input_cmd = f'{CAT_CMD(input)} | {FQ2FA_CMD}'
        if self.n > 0:
            input_cmd = f'{input_cmd} | head -n {self.n * 2}'
        return f'{input_cmd} | {self.igblast_cmd} -num_threads {self.cores} > {output}'