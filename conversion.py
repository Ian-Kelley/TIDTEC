import h5py
import datetime as dt
import pandas as pd
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



def clean_df(df, start, end, extent):
    df = df[df['datetime'] > start]
    df = df[df['datetime'] < end]
    df = df[df['elm'] > 30] #this line imposes an elevation cutoff, some say 30 degrees is ok, but this throws out a lot more data
    df = df[df['gdlat'] > extent[0]]
    df = df[df['gdlat'] < extent[1]]
    df = df[df['glon'] > extent[2]]
    df = df[df['glon'] < extent[3]]
    df['code'] = (df['gps_site'].str.decode('UTF-8') + '_' + df['sat_id'].astype(int).astype(str))
    df = df.drop(columns = ['gps_site', 'sat_id'])
    return df

def detrend_df(df):
    df = df.sort_values(by=['code', 'datetime'])
    df['30min_detrend'] = df['tec'] - df.rolling(60, center=True, min_periods=30).mean().tec
    return df


if __name__ == "__main__":
    #change these
    filename = 'los_20180826.001.h5'
    start = dt.datetime(2018, 8, 26)
    end = dt.datetime(2018, 8, 26, 6)
    extent = [20, 70, -145, -60]

    #conversion script
    len = get_len(filename)
    df = quick_convert(filename, 0, -1)#this line will work faster if only a subset is used.  For example for 0-3 UT, we only need the first part of 
    #the file, so we can do quick_convert(filename, 0, int(len / 4)), which only reads the first 1/4 of a 5-10 GB file and speeds things up
    print('df converted')
    df = clean_df(df, start, end, extent)
    print('df cleaned')
    df = detrend_df(df)
    print('df detrended')
    
    df.to_pickle(filename.partition(".")[0] + '.pkl')

 