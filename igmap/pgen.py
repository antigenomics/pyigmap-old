import math
import os
import olga.load_model as load_model
import olga.generation_probability as pgen
from .misc import IGOR_DATA_PATH


class PgenModel:
    species_glossary = {'hs': 'human',
                        'human' : 'human',
                        'homo-sapiens' : 'human',
                        'mus': 'mouse',
                        'mouse': 'mouse',
                        'mus-musculus': 'mouse'}
    locus_glossary = {'TRA': 'T_alpha', 'TRB': 'T_beta',
                      'IGH': 'B_heavy', 'IGK': 'B_kappa', 'IGL': 'B_lambda'}

    def __init__(self):
        self.models = dict()

    def calc_pgen(self, cdr3_nt, species='human', locus='TRB'):
        mdl = self.get_olga_model(species, locus)
        if mdl:
            pgen = mdl.compute_nt_CDR3_pgen(cdr3_nt)
            if pgen > 0:
                return math.log10(pgen)
        return math.nan

    def calc_pgen_df(self, df, species='human'):
        df['pgen'] = math.nan
        for i, row in df.iterrows():
            locus = row['locus']
            cdr3_nt = row['junction']
            row['pgen'] = self.calc_pgen(
                species=species, locus=locus, cdr3_nt=cdr3_nt)
            df.loc[i] = row            

    def get_olga_model(self, species='human', locus='TRB'):
        locus = locus[0:3]
        ss = self.species_glossary.get(species)
        ll = self.locus_glossary.get(locus)
        key = f'{ss}_{ll}'        
        mdl = self.models.get(key)
        if not mdl:
            params_file_name = f'{IGOR_DATA_PATH}/{key}/model_params.txt'
            marginals_file_name = f'{IGOR_DATA_PATH}/{key}/model_marginals.txt'
            V_anchor_pos_file = f'{IGOR_DATA_PATH}/{key}/V_gene_CDR3_anchors.csv'
            J_anchor_pos_file = f'{IGOR_DATA_PATH}/{key}/J_gene_CDR3_anchors.csv'
            if all([os.path.isfile(f) for f in [params_file_name, 
                                                marginals_file_name, 
                                                V_anchor_pos_file,
                                                J_anchor_pos_file]]):
                if locus in {'TRB', 'TRD', 'IGH'}:
                    generative_model = load_model.GenerativeModelVDJ()
                    generative_model.load_and_process_igor_model(marginals_file_name)
                    genomic_data = load_model.GenomicDataVDJ()
                    genomic_data.load_igor_genomic_data(
                        params_file_name, V_anchor_pos_file, J_anchor_pos_file)
                    mdl = pgen.GenerationProbabilityVDJ(generative_model, genomic_data)
                else:  
                    generative_model = load_model.GenerativeModelVJ()
                    generative_model.load_and_process_igor_model(marginals_file_name)
                    genomic_data = load_model.GenomicDataVJ()
                    genomic_data.load_igor_genomic_data(
                        params_file_name, V_anchor_pos_file, J_anchor_pos_file)                  
                    mdl = pgen.GenerationProbabilityVJ(generative_model, genomic_data)
                self.models[key] = mdl
        return mdl
