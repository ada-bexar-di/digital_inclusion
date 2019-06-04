import re
from sklearn.cluster import KMeans
import numpy as np
<<<<<<< HEAD
import pandas as pd
=======
import pandas as pd
>>>>>>> 89e15b0f247a1271afdb29658f6b0ee8a2a5a994

b19013_cols = {'HD01_VD01' : 'income_median'}
b01002_cols = {'HD01_VD02': 'age_median'}
b02001_cols = {'HD01_VD02': 'white', 'HD01_VD03':'African_American','HD01_VD04':'Native_American','HD01_VD05':'Asian',
    'HD01_VD06':'Hawaiian_Pac_Islander', 'HD01_VD01':'pop_tot'}


def geo_fix(df):
    df = df.copy()
    colnames = {'GEO.id2':'blockgroup'}
    df = df.drop(columns=['GEO.id','GEO.display-label']).rename(columns=colnames)

    return df

def drop_moe(df):
    return df[['blockgroup']+[col for col in df.columns[1:] if int(col[2:4]) == 1]]


def transform_B19001(df,drop_lowpop = True,add_percents=True):
    #Drops Non-important GEOid
    #Renames GEO.id2 to blockgroup (useful for merging)
    colnames = {'GEO.id2':'blockgroup'}
    df = df.drop(columns=['GEO.id','GEO.display-label']).rename(columns=colnames)

    #Removes Margin of Error Fields
    df =df[['blockgroup']+[col for col in df.columns[1:] if int(col[2:4]) == 1]]

    #Drop Descriptions:
    descp = df[0:1]
    df = df[1:]

    #Rename Column names to more descriptive words
    columnnames = {'HD01_VD01':'pop_tot', 'HD01_VD02':'lessthan_10k','HD01_VD17':'greaterthan_200k'}


    # Each of the rest of the column names follow a pattern that looks like $10,000 - $14,000
    # This regular expression captures that range
    colnums = {col:re.findall(r'\$(\d+),000 to \$(\d+)', str(descp[col])) for col in descp.columns[3:-1] }
    # Colnums is a dict of single element lists, containing a tupple that looks like this
    # ('10','14') which indicates a salary range of 10k-14k


    for key in colnums:
        columnnames[key] = f'{colnums[key][0][0]}k-{colnums[key][0][1]}k'
    #This Generates Range Strings for column names which can now be added to df
    df.rename(columns=columnnames,inplace=True)

    #Converts all columns to ints
    for col in df.columns:
        df[col] = df[col].astype('int')


    if drop_lowpop:

        df = df[df['pop_tot'] > 99]


    if add_percents:
        for col in df.columns[2:]:
            df[col+'_p'] = df[col]/df['pop_tot']

    return df



def cluster_B19001(df):
    df = transform_B19001(df)
    X = list(df.columns[18:])
    model = KMeans(n_clusters=3, random_state=123)
    model.fit(df[X])
    df['Income_Cluster'] = model.predict(df[X])
    return df



def transform_B19013(df):

    df = drop_moe(geo_fix(df))
    df = df[1:]
    df = df.rename(columns=b19013_cols)
    df = df[['blockgroup']+list(b19013_cols.values())]
    df.replace('250,000+','250000',inplace=True)
    df.replace('-',np.NaN,inplace=True)
    df.dropna(inplace=True)
    df['income_median'] = df.income_median.astype('int')
    df['blockgroup'] = df.blockgroup.astype('int')
    return df

def transform_B01002(df):
    df = drop_moe(geo_fix(df))
    df = df[1:]
    df = df.rename(columns= b01002_cols)
    df = df[['blockgroup']+list(b01002_cols.values())]
    df.age_median.replace('-',np.NaN,inplace=True)
    df.dropna(inplace=True)
    df['age_median'] = df.age_median.astype('float')
    df['blockgroup'] = df.blockgroup.astype('int')
    return df

def transform_B02001(df):
    df = drop_moe(geo_fix(df))
    df = df[1:]
    df = df.rename(columns=b02001_cols)
    df = df[['blockgroup']+list(b02001_cols.values())]
    for col in df.columns:
        df[col] = df[col].astype('int')
    return df


def merge_3(df1,df2,df3):
    return pd.merge(pd.merge(df1,df2),df3)



def load_cesus(filepath=''):

    if filepath == '':
        print('Please specify a filepath for the census csvs')
        return None

    if filepath[-1] is not '/':
        filepath += '/'

    b01002 = transform_B01002(pd.read_csv(filepath+'ACS_16_5YR_B01002_with_ann.csv'))
    b02001 = transform_B02001(pd.read_csv(filepath+'ACS_16_5YR_B02001_with_ann.csv'))
    b19013 = transform_B19013(pd.read_csv(filepath+'ACS_16_5YR_B19013_with_ann.csv'))

    return pd.merge(pd.merge(b01002,b02001),b19013)
