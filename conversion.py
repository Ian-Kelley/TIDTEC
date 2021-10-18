import h5py
import numpy as np
import pandas as pd
import os
import gc


def quick_convert(filename, start, end):
    f = h5py.File(filename, 'r')
    data = f['Data']['Table Layout'][start:end]
    d = {"ut_time" : data['ut1_unix'], "gdlat" : data['gdlat'], "glon" : data['glon'], "tec" : data['tec'],  "dtec" : data['dlos_tec'], "elm" : data['elm'], "gps_site" : data['gps_site'], "sat_id" : data['sat_id']}
    print("dict created from dataset")
    del data
    gc.collect()
    print("dataset deleted")
    df = pd.DataFrame(d)
    print("dataframe created from dict")
    del d
    gc.collect()
    print("dict deleted")
    df['datetime'] = pd.to_datetime(df.ut_time, unit='s')
    del df['ut_time']
    return df.round(2)

def get_len(filename):
    f = h5py.File(filename, 'r')
    data = f['Data']['Table Layout']
    size = int(data.size / 2)
    return size

if __name__ == '__main__':
    filename = 'los_20140326.001.h5'
    df = quick_convert(filename, 0, -1)
    print('df converted')
    df.to_pickle(filename[0:12] + '.pkl')



 