from collections import namedtuple
import re


Cdr3Markup = namedtuple('Cdr3Markup',
                        'sequence v_sequence_end j_sequence_start cdr3_sequence_start cdr3_sequence_end')


CYS_CODON = re.compile('TG[TC]')
STOP_CODON = re.compile('T(?:AA|AG|GA)')
FGXG_CODON = re.compile('T(?:GG|TT|TC)GG....GG')


def find_inframe_patterns(seq, pattern):
    bad_frames = {x.start() % 3 for x in STOP_CODON.finditer(seq)}
    positions = [x.start() for x in pattern.finditer(seq)]
    return [x for x in positions if x % 3 not in bad_frames]


def find_cdr3nt_simple(seq, vend=-1, jstart=-1):
    if vend < 0:
        vend = len(seq)
    if jstart <= 0:
        jstart = 1
    cys = min(find_inframe_patterns(seq[:vend], CYS_CODON), default=-1)
    phe = jstart + \
        max(find_inframe_patterns(seq[(jstart-1):], FGXG_CODON), default=-1)
    if cys < 0 or phe <= cys:
        return Cdr3Markup(seq, vend, jstart, -1, -1)
    else:
        return Cdr3Markup(seq, vend, jstart, cys + 4, phe - 1)


# 0123456789012345678901234567890123456789012345678901234567890123456789012345
# 0000000000111111111122222222223333333333444444444455555555556666666666777777
#                        |                                        |
# AGACAGCAGCTTCTACATCTGCAGTGCTAGAGAGTCGACTAGCGATCCAAAAAATGAGCAGTTCTTCGGGCCAGGG
#                        |                                        |
#
# cdr3_sequence_start : last base after C plus 1 : 23
# cdr3_sequence_end : first base of F/W : 64

seq = 'AGACAGCAGCTTCTACATCTGCAGTGCTAGAGAGTCGACTAGCGATCCAAAAAATGAGCAGTTCTTCGGGCCAGGG'
v_sequence_end = 33
j_sequence_start = 53
print(find_cdr3nt_simple(seq))
print(find_cdr3nt_simple(seq, v_sequence_end, j_sequence_start))

# 0123456789012345678901234567890123456789012345678901234567890123456789012345
# 0000000000111111111122222222223333333333444444444455555555556666666666777777
#                                           |   |
# GGCTGATTATTACTGCAGTTCATATAGAGGCAGCGCCACTTTCGAGGTGGTGTTCGGCGGAGGGACCAAGGTGACC
#                                           |   |
# GGCTGATTATTACTGCAGTTCATATAGAGGCAGCGCCACTTTC   |
#                                               GTGGTGTTCGGCGGAGGGACCAAGGTGACC
seq = 'GGCTGATTATTACTGCAGTTCATATAGAGGCAGCGCCACTTTCGAGGTGGTGTTCGGCGGAGGGACCAAGGTGACC'
v_sequence_end = 43
j_sequence_start = 47
print(find_cdr3nt_simple(seq))
print(find_cdr3nt_simple(seq, v_sequence_end, j_sequence_start))
