import pandas as pd

def aggregate_clonotypes(df, 
                         grouping_cols = ['v_call', 'j_call', 'junction'],
                         count_col = 'duplicate_count'):
    df = df.copy()
    df = df.reset_index()
    drg = df.groupby(grouping_cols)
    df['total'] = drg[count_col].transform('sum')
    df['max_count'] = drg[count_col].transform('max')
    df = df.reset_index()
    df = df[df[count_col] == df['max_count']]
    df[count_col] = df['total']
    df = df.drop(columns=['total', 'max_count'])
    df = df.sort_values(by = count_col, ascending=False)
    return df