import h5py
import datetime as dt
import pandas as pd
import gc
import os

def quick_convert(filename, filename2, start, end):
    f = h5py.File(filename, 'a')
    if filename != filename2:
        f['ext link'] = h5py.ExternalLink(os.getcwd() + filename2, filename2)
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
    size = int(data.size)
    return size


def clean_df(df, start, end, extent, detrend_period=30, elev_cutoff=30):
    detrend_period = detrend_period * 2
    #throw out tec not in geographic range
    df = df[df['gdlat'] > extent[0]]
    df = df[df['gdlat'] < extent[1]]
    df = df[df['glon'] > extent[2]]
    df = df[df['glon'] < extent[3]]

    #make a new "code" containing unique satellite / reciever pairs
    df['code'] = (df['gps_site'].str.decode('UTF-8') + '_' + df['sat_id'].astype(int).astype(str))
    df = df.drop(columns = ['gps_site', 'sat_id'])
    #resort the data into timeseries based on satellite / reciever pairs
    df = df.sort_values(by=['code', 'datetime'])
    #30 min rolling average subtracted
    #df['30min_detrend'] = df['tec'] - df.rolling(detrend_period, center=True, min_periods=int(2*(detrend_period / 3))).mean().tec

    #throw out data not in time range
    df = df[df['datetime'] > start]
    df = df[df['datetime'] < end]
    #impose elevation cutoff since oblique paths through ionosphere are less certian.  
    #30 is plenty, but throws out data
    df = df[df['elm'] > elev_cutoff] 
    return df

if __name__ == "__main__":
    
    #change these
    start = dt.datetime(2017, 9, 7, 21)
    extent = [35, 45, -115, -85]


    filename = 'los_' + str(start.year) + str(start.month).zfill(2) + str(start.day).zfill(2) + '.004.h5'#this may have to be changed if there are extra versions of file
    print('hdf5 source file is ' + str(os.path.getsize(filename)/1000000000.0) + ' Gb')
    end = start + dt.timedelta(hours=8)
    filename2 = filename
    if end.date != start.date:
        filename2 = 'los_' + str(start.year) + str(start.month).zfill(2) + str(end.day).zfill(2) + '.004.h5'#this may have to be changed if there are extra versions of file
    #MAKE SURE TO SAVE THIS FILE BEFORE RUNNING
    #conversion script
    time1 = dt.datetime.utcnow()
    len = get_len(filename2)
    print(len)
    df = quick_convert(filename, filename2, 0, len)#this line will work faster if only a subset is used.  For example for 0-3 UT, we only need the first part of 
    # #the file, so we can do quick_convert(filename, 0, int(len / 4)), which only reads the first 1/4 of a 5-10 GB file and speeds things up
    print('df converted')

    df = clean_df(df, start, end, extent, detrend_period=30)
    print('df cleaned')

    
    df.to_pickle(filename.partition(".")[0] + '.pkl')
    print('new python pkl file is ' + str(os.path.getsize(filename.partition(".")[0] + '_long.pkl')/1000000000.0) + ' Gb')
    timer = dt.datetime.utcnow() - time1
    print('conversion lasted ' + str(timer))

 