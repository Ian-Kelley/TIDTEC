import datetime as dt
import cartopy.crs as ccrs
import pandas as pd
import numpy as np


def get_df():
    df1 = pd.read_pickle('los_20140326.pkl')
    #print('df1 load')
    #df2 = pd.read_pickle('los_20170907_early.pkl')
    #print('df2 load')
    #df = pd.concat([df1, df2])
    #del df1
    #del df2
    return df1


def clean_df(df, start, end, extent):
    df = df[df['datetime'] > start]
    df = df[df['datetime'] < end]
    df = df[df['elm'] > 30]
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
    start = dt.datetime(2014, 3, 26)
    end = start + dt.timedelta(hours = 24)
    extent = [20, 70, -145, -60]
    df = get_df()
    print('df loaded')
    df = clean_df(df, start, end, extent)
    print('df cleaned')
    df = detrend_df(df)
    print('df detrended')
    df.to_pickle('20140326_1.pkl')