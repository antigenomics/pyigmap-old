import argparse
import os
import sys

from igmap.pgen import PgenModel

from .vidjil import VidjilWrapper, read_vidjil
from .misc import CORES


def main():
    parser = argparse.ArgumentParser(
        prog='igmap',
        description='Mapping raw reads to V(D)J rearrangements',
        epilog='')

    parser.add_argument('-t', '--threads',
                        default=CORES,
                        type=int,
                        nargs=1,
                        help=f'Number of threads, defaults to {CORES} you have')
    parser.add_argument('-n', '--nreads',
                        default=-1,
                        type=int,
                        nargs=1,
                        help=f'Number of reads to process (defaults to -1, all)')
    parser.add_argument('-s', '--species',
                        default='human',
                        choices=['human', 'mouse'],
                        nargs=1,
                        help='Species alias')
    parser.add_argument('-m', '--mode',
                        required=True,
                        choices=['rnaseq', 'target'],
                        help='Analysis mode')
    parser.add_argument('-i', '--input',
                        required=True,
                        nargs='+',
                        help='Input, single fastq[.gz], or pair for paired-end, or several files')
    parser.add_argument('-o', '--output',
                        required=True,
                        help='Path to the output directory')
    parser.add_argument('-b', '--basename',
                        default='igmap',
                        help='Basename of analysis report, to be appended to path; defaults to "igmap"')
    options = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    input = ' '.join([os.path.abspath(x) for x in options.input])
    output = options.output
    os.makedirs(output, exist_ok=True)
    if options.mode == 'rnaseq':
        run_rnaseq(options, input, output, options.basename)
    else:
        raise 'Unsupported mode'


def run_rnaseq(options, input, output, basename):
    print(f'Running RNA-Seq analysis for {options}')
    vw = VidjilWrapper(species=options.species,
                       cores=options.threads,
                       n=options.nreads)
    os.system(vw.run_cmd(input, output))
    df = read_vidjil(path=output + '/result.tsv',
                     concise=True, only_functional=True)
    PgenModel().calc_pgen_df(df=df, species=options.species) # filter spurious rearrangements
    df.to_csv(f'{output}/{basename}.tsv', sep='\t', index=False)    


if __name__ == '__main__':
    main()
