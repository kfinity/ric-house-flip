import json
import pandas as pd
import requests
import math

"""
e.g. service_url: 'https://services3.arcgis.com/TsynfzBSE6sXfoLq/ArcGIS/rest/services/Cadastral/FeatureServer/3'
"""
def to_df(service_url, in_params):
    
    url = service_url + '/query'
    
    # default resultRecordCount:
    pagelen = 1000
    
    params = dict(
        f='json',
        where='1=1',
        returnGeometry='true',
        spatialRel='esriSpatialRelIntersects',
        geometryType='esriGeometryEnvelope',
        inSR=None,
        outFields='*',
        orderByFields='OBJECTID ASC',
        outSR=None,
        resultOffset=0,
        resultRecordCount=pagelen
    )
    # load input params
    params.update(in_params)
    
    # used for test query
    testparams = params.copy()
    testparams.update(dict(resultRecordCount=10))
    
    # load a test query - first 10 results
    resp = requests.get(url=url, params=testparams)
    data = resp.json() 
    
    # get the list of valid columns from the first feature.
    cols = list(data['features'][0]['attributes'].keys())
    if params['returnGeometry']=='true':
        cols = cols + list(data['features'][0]['geometry'].keys())
    
    # find max row count
    max_count_params = dict(
        f='json',
        where='1=1',
        #returnCountOnly='true',
        returnIdsOnly='true' # special query param, returns ALL (no limit) OBJECTIDs
    )
    resp = requests.get(url=url, params=max_count_params)
    ids = resp.json() 
    
    # total count of objectIds
    pagelen = params['resultRecordCount']
    rowcount = len(ids['objectIds'])
    pages = math.ceil(rowcount / pagelen) 
    print(f"Rowcount: {rowcount}, pages: {pages}")
    
    # load all the data

    # create blank df
    df = pd.DataFrame(columns=cols)

    for i in range(0,pages): # set this to 1 or 2 for testing
        params['resultOffset'] = i*pagelen
        print(f"Request {str(i)}: {params['resultOffset']}")
        resp = requests.get(url=url, params=params)
        data = resp.json() 
        df2 = pd.json_normalize(data, record_path=['features'])
        df2.columns = cols
        df = df.append(df2, ignore_index=True)
    
    print(f"Final shape: {df.shape}")
    return df