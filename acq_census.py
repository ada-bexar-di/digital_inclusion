import pandas as pd

def load_csv(filenum):
    a = 'aff_download/ACS_17_5YR_S'
    b = '_with_ann.csv'
    df = pd.read_csv(a+filenum+b)
    x = df.loc[0:0]
    return pd.concat([x,df[df['GEO.id2'].str.contains(('48029'))]],join='outer')

def fix_cols(df,filename):
    cols = list(df.columns[:3])
    for col in df.columns[3:]:
        col = col.split('_')
        col[0] = filename+'_'+col[0]
        col = '_'.join(col)
        cols.append(col)
    df.columns = cols
    return df

def get_many(formlist):

    df = pd.concat([fix_cols(load_csv(form),form) for form in formlist],axis=1,join='outer') #Joins all the listed CSVs into 1 big Dataframe
    df.drop(columns=['GEO.id2','GEO.id','GEO.display-label'],inplace=True) # Drops the many duplicate GEO.id fields
    return pd.concat([load_csv('0101')[['GEO.id2']],df],axis=1,join='outer') # returns the DF with 1 GEO.id field


def acquire()

    formlist = formlist = '0101 0601 0701 0801 0802 1002 1101 1201 1301 1401 1501 1502 1601 1602 1603 1701 1702 1810 1901 1902 1903 2001 2101 2201 2301'.split()
    return get_many(formlist)
