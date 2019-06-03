import re
from sklearn.cluster import KMeans


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
