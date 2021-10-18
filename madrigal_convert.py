#hdf5_convert.py by Ian Kelley
#converts madrigal los TEC file to a csv or pkl using pandas, can be read again easily using pandas
#specify path for files in path

import h5py
import numpy as np
import pandas as pd
import os
import gc

def convert(filename):
    f = h5py.File(filename, 'r')
    data = f['Data']['Table Layout'][0:25000000]
    d = {"ut_time" : data['ut1_unix'], "gps_site" : data['gps_site'], "sat_id" : data['sat_id'], "gdlat" : data['gdlat'], "glon" : data['glon'], "tec" : data['tec'], "dtec" : data['dtec'], "elm" : data['elm']}
    print("dict created from dataset")
    del data
    gc.collect()
    df = pd.DataFrame(d)
    print("dataframe created from dict")
    del d
    gc.collect()
    df['datetime'] = pd.to_datetime(df.ut_time, unit='s')
    del df['ut_time']
    df['site'] = df.gps_site.str.decode('utf-8')
    del df['gps_site']
    #df['vtec'] = df.tec * np.sqrt(1 - ((6371 * np.cos(np.deg2rad(df.elm)) / 6721)**2))
    df['log_tec'] = np.log10(df['tec'])
    #df['log_vtec'] = np.log10(df['vtec'])
    return df

if __name__ == "__main__":
    filename = 'los_20170528.003.h5.hdf5'
    path = '/home/ikelley/TEC/'
    # for all files in the directory data_files = [f for f in os.listdir(path) if f.endswith('.hdf5')]
    #for filename in data_files:
    if True:
        print("converting " + filename)
        df = convert(path + filename)
        #df.to_csv(path + filename[0:12] + '.csv')
        df.to_pickle(path + filename[0:12] + '_0.pkl')
        print("sucessfully converted into .pkl")



