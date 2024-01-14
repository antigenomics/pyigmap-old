import os
import pandas as pd
from .misc import CAT_CMD, CORES, VIDJIL_CMD, VIDJIL_DATA_PATH
from .utils import find_cdr3nt_simple, translate_cdr3


class VidjilWrapper:
    species_glossary = {'hs': 'homo-sapiens',
                        'human' : 'homo-sapiens',
                        'homo-sapiens' : 'homo-sapiens',
                        'mus': 'mus-musculus',
                        'mouse': 'mus-musculus',
                        'mus-musculus': 'mus-musculus'}
    # TODO: window parameters?
    # TODO: D and C genes
    def __init__(self,
                 species='homo-sapiens',
                 rnaseq=True,
                 cores=CORES,
                 n=-1):
        if os.path.isfile(species):
            self.species = species
        else:
            species = self.species_glossary[species]
            self.species = f'{VIDJIL_DATA_PATH}/{species}.g'
        self.vidjil_cmd = f'{VIDJIL_CMD} -g {self.species}'
        if rnaseq:
            self.vidjil_cmd = self.vidjil_cmd + ' -U'
        self.cores = cores
        self.n = n

    def detect_cmd(self,
                   input,
                   output):
        input_cmd = CAT_CMD(input)
        if self.n > 0:
            input_cmd = f'{input_cmd} | head -n {self.n * 4}'
        chunk_placeholder = '_p{#}'
        process_cmd = f'{self.vidjil_cmd} -c detect -o {output} -b {chunk_placeholder} -'
        return f'{input_cmd} | parallel -j {self.cores} --pipe -L 4 --round-robin "{process_cmd}"'

    def clones_cmd(self,
                   input,
                   output):
        input_cmd = CAT_CMD(input)
        return f'{input_cmd} | {self.vidjil_cmd} -c clones --all -o {output} -b result -'

    def run_cmd(self,
                input,
                output):
        return f'{self.detect_cmd(input, output)} && ' + \
            f'{self.clones_cmd(output + "/_p*.fa", output)} && ' + \
            f'rm -r {output}/_p*'


def read_vidjil(path, concise=False, only_functional=False):    
    df = pd.read_csv(path,
                     sep='\t',
                     low_memory=False,
                     usecols=lambda c: not c.startswith('Unnamed:'))
    df.dropna(subset=['v_call', 'j_call'], inplace=True)    
    df['v_sequence_end'] = df['v_sequence_end'].fillna(-1).astype(int)
    df['j_sequence_start'] = df['j_sequence_start'].fillna(-1).astype(int)
    for i, row in df.iterrows():
        seq = row['sequence']
        vend = row['v_sequence_end']
        jstart = row['j_sequence_start']
        markup = find_cdr3nt_simple(seq, vend, jstart)
        junction_aa = translate_cdr3(markup.junction)
        if junction_aa:
            cdr3_aa = junction_aa[1:-1]
        else:
            cdr3_aa = ''
        row['junction'] = markup.junction
        row['cdr3_sequence_start'] = markup.cdr3_sequence_start
        row['cdr3_sequence_end'] = markup.cdr3_sequence_end
        row['junction_aa'] = junction_aa
        row['cdr3aa'] = cdr3_aa
        df.loc[i] = row
    if only_functional:
        df = df[df['junction'] != '']
        df = df[~df["junction_aa"].str.contains('_')]
        df = df[~df["junction_aa"].str.contains('\*')]
        df = df[df['junction_aa'].str.startswith('C')]
        df = df[df['junction_aa'].str.endswith('F') | df['junction_aa'].str.endswith('W')]
    if concise:
        df['v_sequence_end'] = df['v_sequence_end'] - df['cdr3_sequence_start'] + 3
        #df['d_sequence_start'] = df['d_sequence_start'] - df['cdr3_sequence_start'] + 3
        #df['d_sequence_end'] = df['d_sequence_end'] - df['cdr3_sequence_start'] + 3
        df['j_sequence_start'] = df['j_sequence_start'] - df['cdr3_sequence_start'] + 3
        df = df.groupby(['locus',
                         'v_call', 'j_call',
                         'junction', 'junction_aa'], as_index=False)\
            .agg(duplicate_count=('duplicate_count', 'sum'),
                 molecule_count=('sequence', 'count'),
                 v_sequence_end=('v_sequence_end', 'max'),
                 j_sequence_start=('j_sequence_start', 'min'))
    df.sort_values('duplicate_count', inplace=True, ascending=False)
    df.fillna('', inplace=True)   
    return df