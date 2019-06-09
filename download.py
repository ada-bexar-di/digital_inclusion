import requests
import pandas as pd
import zipfile
import io
import os

def tract_map():

    print('Downloading FCC tract_map')

    x = requests.get('https://www.fcc.gov/sites/default/files/tract_map_dec_2016.zip')
    z = zipfile.ZipFile(io.BytesIO(x.content))
    return pd.read_csv(z.open('tract_map_dec_2016.csv'))


def census_shape():

    print('Downloading Census Shape File')

    return pd.read_csv('http://bigbytes.mobyus.com/bigbytes/tableau/census_tract_shapefiles_all.csv')

def bexar_census_blocks():

    print('Downloading Bexar County Census Block Data')

    url = 'https://eroyall.carto.com:443/api/v2/sql?q='
    query = 'select tract, blockgroup'
    file = ' from public.bexar_county_census_blocks'
    x = requests.get(url+query+file)
    return pd.DataFrame(x.json()['rows'])



def make_data_folder():


    if os.path.isdir("./Data"):
        print('Data folder already created')
        print('Downloading FCC Data')
    else:
        print('Creating directory to store project data')


        # define the name of the directory to be created
        path = "./Data"

        try:
            os.mkdir(path)
        except OSError:
            print ("Creation of the directory %s failed" % path)
        else:
            print ("Successfully created the directory %s " % path)

def merge_fcc(bexar_blocks,tract_map,census_shape):

    bexar_blocks.tract = bexar_blocks.tract.astype('int')
    blocks_all = census_shape

    blocks_all = blocks_all.rename({'GEOID': 'tract'}, axis=1)

    tract_map = tract_map.rename({'tractcode': 'tract'}, axis=1)

    bexar_blocks_all = bexar_blocks.merge(blocks_all, on='tract', how='inner')

    blocks = bexar_blocks_all.merge(tract_map, on='tract', how='inner')
    return blocks



make_data_folder()
df = merge_fcc(bexar_blocks = bexar_census_blocks(),census_shape=census_shape(),tract_map=tract_map())
print('Saving CSV to ./Data')
df.to_csv('Data/FCC_data.csv')
