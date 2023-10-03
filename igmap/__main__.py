import argparse
import os
import sys

from .vidjil import VidjilWrapper
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
                        default='hs',
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
                        help='Path to output file with output prefix')

    options = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    input = ' '.join([os.path.abspath(x) for x in options.input])
    out = split_path(options.output)
    if options.mode == 'rnaseq':
        run_rnaseq(options, input, out)
    else:
        raise 'Unsupported mode'
    
def split_path(path):
    abs_path = os.path.abspath(path)
    dir = os.path.dirname(abs_path)
    return (path, dir, os.path.basename(abs_path))

def run_rnaseq(options, input, out):
    # no need to create directories as vidjil does it automatically
    print(f'Running RNA-Seq analysis for {options}')
    species_glossary = {'hs' : 'homo-sapiens', 'homo-sapiens' : 'homo-sapiens'}
    vw = VidjilWrapper(species_glossary[options.species], 
                       cores=options.threads,
                       n=options.nreads)
    #print(out)
    os.system(vw.run_cmd(input, out[0]))

if __name__ == '__main__':
    main()