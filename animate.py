import matplotlib.pyplot as plt
import datetime as dt
import cartopy.crs as ccrs
import h5py
import pandas as pd
import numpy as np
from cartopy.feature.nightshade import Nightshade
from IPython.display import Video
import matplotlib.animation as animation
from cartopy.io.img_tiles import OSM
import cartopy.io.img_tiles as cimgt
from matplotlib.tri import Triangulation, UniformTriRefiner
import os




def plot_still(time, df, i, frame_code):
    #central = 180 - (time.hour * 15 + time.minute * .25 + time.second * .0041667)
    tecmap = plt.figure(figsize=(16, 10))
    ax = plt.axes(projection = ccrs.PlateCarree())
    ax.coastlines(color='black', zorder=1)
    ax.gridlines()
    ax.set_extent([-140, -60, 20, 70], ccrs.PlateCarree())
    ax.add_feature(Nightshade(time, alpha=0.15))
    ax.set_title(str(time), size=30)
    part = df[df['datetime'] == time]
    if(len(part.tec)) < 25000:#reurn if not enough points
        return frame_code
    tri = Triangulation(part.glon, part.gdlat)
    tri = UniformTriRefiner(tri)
    levels = np.arange(0., 2., .005)
    mesh = ax.scatter(part.glon, part.gdlat, c=part.tec, transform=ccrs.PlateCarree(), vmin=0, vmax=30, cmap='jet', s=5, alpha=1)
    #mesh = ax.scatter(tri, part.log_tec, transform=ccrs.PlateCarree(), levels=levels, cmap='jet')#, vmin=0, vmax=25, alpha=0.5, s=100, cmap='jet')
    
    cbar = plt.colorbar(mesh, fraction=0.046, pad=0.04)
    cbar.set_label('log 10 TECu')
    plt.savefig(f'{frame_code:03d}' + '.png')
    plt.close()
    return frame_code + 1

def plot_series(df):
	start = dt.datetime(2017, 9, 8, 0)
	cadence = dt.timedelta(seconds = 30)
	frame_num = 15
	frame_attempt = 0
	frame_code = 0
	while frame_attempt < frame_num:
    		time = start + frame_attempt * cadence
    		frame_attempt = frame_attempt + 1
    		frame_code = plot_still(time, df, frame_attempt, frame_code)

if __name__ == "__main__":
    df = pd.read_pickle('los_20170908.pkl')
    df = df.where(df['elm'] > 30).dropna()
    plot_series(df)
