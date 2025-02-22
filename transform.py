import re
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd


b19013_cols = {'HD01_VD01' : 'income_median'}
b01002_cols = {'HD01_VD02': 'age_median'}
b02001_cols = {'HD01_VD02': 'White', 'HD01_VD03':'African_American','HD01_VD04':'Native_American','HD01_VD05':'Asian',
    'HD01_VD06':'Hawaiian_Pac_Islander', 'HD01_VD01':'pop_tot'}

b03003_cols={'HD01_VD01':'pop_tot', 'HD01_VD03':'Hispanic/Latino'}

b19001_cols = ['blockgroup',
         'income_0-19k',
         'income_20-24k',
         'income_25-39k',
         'income_40-64k',
         'income_65k+']


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

    # Adds additional columns binning/summing income ranges per Maggie recommendation:
    df['income_0-19k'] = df['lessthan_10k'] + df['10k-14k'] + df['15k-19k']
    df['income_20-24k'] = df['20k-24k']
    df['income_25-39k'] = df['25k-29k'] + df['30k-34k'] + df['35k-39k']
    df['income_40-64k'] = df['40k-44k'] + df['45k-49k'] + df['50k-59k']
    df['income_65k+'] = df['60k-74k'] + df['75k-99k'] + df['100k-124k'] + df['125k-149k'] + df['150k-199k'] + df['greaterthan_200k']

    for col in df.columns[-5:]:
        df[col+'_p'] =  df[col]/df['pop_tot']

    return df[['blockgroup']+list(df.columns[-5:])]



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

def transform_B03003(df):

    df = drop_moe(geo_fix(df))
    df = df[1:]
    df = df.rename(columns=b03003_cols)
    df = df[['blockgroup']+list(b03003_cols.values())]
    for col in df.columns:
        df[col] = df[col].astype('int')
    return df

def b03003_percents(df):
    cols = ['pop_tot','Hispanic/Latino']
    df['Hispanic/Latino_p'] = df['Hispanic/Latino']/df['pop_tot']

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

def b02001_percents(df):
    cols = ['White',
         'African_American',
         'Native_American',
         'Asian',
         'Hawaiian_Pac_Islander'
         ]
    for col in cols:
        df[col+'_p'] = df[col]/df['pop_tot']

def transform_B01001(df):

    df = df[1:]
    df = drop_moe(df.drop(columns=['GEO.id','GEO.display-label']).rename(columns={'GEO.id2':'blockgroup'}))
    df.rename(columns={'HD01_VD01':'pop_tot'},inplace=True)
    for col in df.columns:
        df[col] = df[col].astype('int')
    df['male_age_bin_0-19'] = df.iloc[:,3:8].sum(axis=1)
    df['male_age_bin_20-29'] = df.iloc[:,8:12].sum(axis=1)
    df['males_age_bin_30-44'] = df.iloc[:,12:15].sum(axis=1)
    df['male_age_bin_45-59'] = df.iloc[:,15:18].sum(axis=1)
    df['male_age_bin_60+'] = df.iloc[:,18:26].sum(axis=1)

    df['female_age_bin_0-19'] = df.iloc[:,27:32].sum(axis=1)
    df['female_age_bin_20-29'] = df.iloc[:,32:36].sum(axis=1)
    df['females_age_bin_30-44'] = df.iloc[:,36:39].sum(axis=1)
    df['female_age_bin_45-59'] = df.iloc[:,39:42].sum(axis=1)
    df['female_age_bin_60+'] = df.iloc[:,42:50].sum(axis=1)


    for col in df.columns[-10:]:
        df[col+'_p'] = df[col] / df['pop_tot']

    return df[['blockgroup']+list(df.columns[-10:])]




def load_census(filepath=''):

    if filepath == '':
        print('Please specify a filepath for the census csvs')
        return None

    if filepath[-1] is not '/':
        filepath += '/'

    b01002 = transform_B01002(pd.read_csv(filepath+'ACS_16_5YR_B01002_with_ann.csv'))
    b02001 = transform_B02001(pd.read_csv(filepath+'ACS_16_5YR_B02001_with_ann.csv'))
    b19013 = transform_B19013(pd.read_csv(filepath+'ACS_16_5YR_B19013_with_ann.csv'))
    b19001 = transform_B19001(pd.read_csv(filepath+'ACS_16_5YR_B19001_with_ann.csv'))
    b01001 = transform_B01001(pd.read_csv(filepath+'ACS_16_5YR_B01001_with_ann.csv'))
    b03003 = transform_B03003(pd.read_csv(filepath+'ACS_16_5YR_B03003_with_ann.csv'))

    return pd.merge(pd.merge(pd.merge(pd.merge(b01001,b02001),b19013),b19001),b03003)


def transform_FCC(df):
    return pd.DataFrame(
        {'pcat_all_mean': df.groupby('blockgroup')['pcat_all'].mean()
        ,'pcat_10x1_mean': df.groupby('blockgroup')['pcat_10x1'].mean()
        ,'pcat_all_median': df.groupby('blockgroup')['pcat_all'].median()
        ,'pcat_10x1_median': df.groupby('blockgroup')['pcat_10x1'].median()
         }
    )

def load_FCC(filepath=''):
    if filepath == '':
        print('Please specify a filepath for the census csvs')
        return None

    if filepath[-1] is not '/':
        filepath += '/'

    return transform_FCC(pd.read_csv(filepath+'FCC_data.csv')).reset_index()


def merge_FCC(filepath=''):
    if filepath == '':
        print('Please specify a filepath for the FCC csv')
        return None

    if filepath[-1] is not '/':
        filepath += '/'

    FCC = load_FCC(filepath)
    census = load_census(filepath)
    b02001_percents(census)
    b03003_percents(census)

    b02001_columns = ['White', 'African_American','Native_American','Asian',
        'Hawaiian_Pac_Islander']

    census = census.drop(columns=b02001_columns)


    return pd.merge(census,FCC)


def load_all(filepath=''):

        if filepath == '':
            print('Please specify a filepath for the census csvs')
            return None

        if filepath[-1] is not '/':
            filepath += '/'

        df = merge_FCC(filepath)
        return df.drop(columns=['pcat_all_mean','pcat_all_median', 'Hispanic/Latino'])
