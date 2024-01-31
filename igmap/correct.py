import pandas as pd


def aggregate_clonotypes(df, 
                         grouping_cols = ['v_call', 'j_call', 'junction'],
                         count_col = 'duplicate_count'):
    df = df.copy()
    df = df.reset_index(drop=True) # in case already grouped
    df['rank'] = df.index
    drg = df.groupby(grouping_cols)
    df['total'] = drg[count_col].transform('sum')
    df['max_count'] = drg[count_col].transform('max')
    df['min_rank'] = drg['rank'].transform('min') # resolve ambigous choices with same duplicate_count
    df = df.reset_index(drop = 'True')
    df = df[(df[count_col] == df['max_count']) & (df['rank'] == df['min_rank'])]
    df[count_col] = df['total']
    df = df.drop(columns=['min_rank', 'rank', 'total', 'max_count'])
    df = df.sort_values(by = count_col, ascending=False)
    return df


def fetch_clonotypes(df,
                     junction_col = 'junction',
                     clonotype_cols = ['v_call', 'j_call', 'junction'],
                     count_col = 'duplicate_count'):
    df = df.copy()
    df = df[df[junction_col] != '']
    df = df.groupby(clonotype_cols)[count_col].agg(['sum']).reset_index()
    df = df.rename(columns={'sum': count_col})
    df = df.sort_values(by = count_col, ascending = False)
    return df


class ClonotypeCounter:
    def __init__(self, v_call, j_call, junction, count):
        self.junction = junction
        self.v_call = v_call
        self.j_call = j_call
        self.count = count
        self.parent = junction

    def reassign_parent(self, v_call, j_call, junction, count, 
                        factor = 0.05, matchVJ = False):
        if not matchVJ or (v_call == self.v_call and j_call == self.j_call):
            if self.parent == self.junction and (self.count + 1) / (count + 1) < factor:
                self.parent = junction

    def __repr__(self):
        return str(self.__dict__)


def _make_counters(df,
                   junction_col = 'junction',
                   clonotype_cols = ['v_call', 'j_call', 'junction'],
                   count_col = 'duplicate_count'):
    df = df.sort_values(by = count_col, ascending = False)
    c_count_dict = {}
    c_count_list = []
    for _, row in df.iterrows():
        counter = ClonotypeCounter(*row[clonotype_cols], row[count_col])
        c_count_dict[row[junction_col]] = c_count_dict.get(row[junction_col], []) + [counter]
        c_count_list.append(counter)
    return (c_count_list, c_count_dict)


BASES_GAP = ['A', 'T', 'G', 'C', '']
BASES = ['A', 'T', 'G', 'C']


def get_variants(seq, gap = True):
    if gap:
        for i, bp in enumerate(seq):
            for bp_new in BASES_GAP:
                if bp != bp_new:
                    yield(seq[:i] + bp_new + seq[(i+1):])
                if bp_new:
                    yield(seq[:i+1] + bp_new + seq[(i+1):])
    else:
        for i, bp in enumerate(seq):
            for bp_new in BASES:
                if bp != bp_new:
                    yield(seq[:i] + bp_new + seq[(i+1):])


def _update_counters_inplace(c_count_list,
                             c_count_dict,
                             junction_col = 'junction'):
    for counter1 in c_count_list:
        for junction in get_variants(counter1.junction):
            for counter2 in c_count_dict.get(junction, []):
                counter2.reassign_parent(counter1.v_call, counter1.j_call, 
                                         counter1.junction, counter1.count)
    return pd.DataFrame.from_records([x.__dict__ for x in c_count_list]) \
        .rename(columns={'seq': junction_col})


# df should be produced by fetch_clonotypes
def correct_clonotypes(df,
                       junction_col = 'junction',
                       clonotype_cols = ['v_call', 'j_call', 'junction'],
                       count_col = 'duplicate_count'):
    (c_count_list, c_count_dict) = _make_counters(df, junction_col=junction_col,
                                                  clonotype_cols=clonotype_cols,
                                                  count_col=count_col)
    return _update_counters_inplace(c_count_list=c_count_list,
                                    c_count_dict=c_count_dict)


def correct_full(df,
                 junction_col = 'junction',
                 clonotype_cols = ['v_call', 'j_call', 'junction'],
                 count_col = 'duplicate_count'):
    df = aggregate_clonotypes(df,
                              grouping_cols=clonotype_cols,
                              count_col=count_col)
    clns = fetch_clonotypes(df, 
                            junction_col=junction_col,
                            clonotype_cols=clonotype_cols,
                            count_col=count_col)
    corr = correct_clonotypes(clns,
                 junction_col=junction_col,
                 clonotype_cols=clonotype_cols,
                 count_col=count_col)
    corr = corr.drop(columns=['count']).drop_duplicates() # count is un-aggregated duplicate count
    merged = df.merge(corr, 
                      left_on=clonotype_cols, 
                      right_on=clonotype_cols,
                      how='left').fillna('')
    res = aggregate_clonotypes(merged, grouping_cols='parent')
    return res.drop(columns = 'parent')