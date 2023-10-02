import re
from collections import namedtuple


Cdr3Markup = namedtuple(
    'Cdr3Markup', 'junction cdr3_sequence_start cdr3_sequence_end')


CYS_CODON = re.compile('TG[TC]')
STOP_CODON = re.compile('T(?:AA|AG|GA)')
FGXG_CODON = re.compile('T(?:GG|TT|TC)GG....GG')
FGXG_SHORT_CODON = re.compile('T(?:GG|TT|TC)GG')


def find_inframe_patterns(seq, pattern):
    bad_frames = {x.start() % 3 for x in STOP_CODON.finditer(seq)}
    positions = [x.start() for x in pattern.finditer(seq)]
    return [x for x in positions if x % 3 not in bad_frames]


def find_cdr3nt_simple(seq, vend=-1, jstart=-1, rescue_fgxg=True):
    if vend < 0:
        vend = len(seq)
    if jstart <= 0:
        jstart = 1
    cys = min(find_inframe_patterns(seq[:vend], CYS_CODON), default=-1)
    phe = find_inframe_patterns(seq[(jstart-1):], FGXG_CODON)
    if not phe and rescue_fgxg:
        phe = find_inframe_patterns(seq[(jstart-1):], FGXG_SHORT_CODON)
    phe = jstart + max(phe, default=-1)
    if cys < 0 or phe <= cys:
        return Cdr3Markup('', -1, -1)
    else:
        return Cdr3Markup(seq[cys:(phe + 2)], cys + 4, phe - 1)


CODONS = {'AAA': 'K', 'AAC': 'N', 'AAG': 'K', 'AAT': 'N',
          'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACT': 'T',
          'AGA': 'R', 'AGC': 'S', 'AGG': 'R', 'AGT': 'S',
          'ATA': 'I', 'ATC': 'I', 'ATG': 'M', 'ATT': 'I',
          'CAA': 'Q', 'CAC': 'H', 'CAG': 'Q', 'CAT': 'H',
          'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P',
          'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R',
          'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L',
          'GAA': 'E', 'GAC': 'D', 'GAG': 'E', 'GAT': 'D',
          'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A',
          'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G',
          'GTA': 'V', 'GTC': 'V', 'GTG': 'V', 'GTT': 'V',
          'TAA': '*', 'TAC': 'Y', 'TAG': '*', 'TAT': 'Y',
          'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S',
          'TGA': '*', 'TGC': 'C', 'TGG': 'W', 'TGT': 'C',
          'TTA': 'L', 'TTC': 'F', 'TTG': 'L', 'TTT': 'F'}


def translate(seq):
    return ''.join([CODONS.get(seq[i:(i + 3)], '_') for i in range(0, len(seq), 3)])


def translate_cdr3(seq, mid=-1):
    l = len(seq)
    if mid < 0:
        mid = l // 2
    shift = l % 3
    if shift == 0:
        pad = ''
    else:
        pad = '_' * (3 - shift)
    return translate(seq[:mid] + pad + seq[mid:])
