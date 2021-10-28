import matplotlib.pyplot as plt
import datetime as dt
import cartopy.crs as ccrs
import pandas as pd
from cartopy.feature.nightshade import Nightshade


def plot_still(time, df, frame_code):
    plt.close()
    tecmap = plt.figure(figsize=(16, 10))
    ax = plt.axes(projection = ccrs.PlateCarree())
    ax.coastlines(color='black', zorder=1)
    ax.gridlines()
    ax.set_extent([-140, -60, 20, 70], ccrs.PlateCarree())
    ax.add_feature(Nightshade(time, alpha=0.15))
    ax.set_title(str(time), size=30)
    part = df[df['datetime'] == time]
    if(len(part.tec)) < 1000:#reurn if not enough points
        return frame_code
    mesh = ax.scatter(part.glon, part.gdlat, c=part.tec, transform=ccrs.PlateCarree(), vmin=0, vmax=50, cmap='plasma', s=40, alpha=.7)
    cbar = plt.colorbar(mesh, fraction=0.046, pad=0.04)
    cbar.set_label('TECu')
    plt.savefig(f'{frame_code:03d}' + '.png')
    plt.close()
    return frame_code + 1

def plot_series(df, start, end, cadence):
    frame_num = int((end - start) / cadence)
    frame_attempt = 0
    frame_code = 0
    while(frame_attempt < frame_num):
        time = start + (frame_attempt * cadence)
        frame_attempt = frame_attempt + 1
        frame_code = plot_still(time, df, frame_code)

if __name__ == "__main__":
    #change these
    start = dt.datetime(2015, 1, 7, 21)
    end = dt.datetime(2015, 1, 7, 23)
    cadence = dt.timedelta(seconds = 30) 
    df = pd.read_pickle('los_20150107.pkl')
    df = df.where(df['elm'] > 30).dropna()
    plot_series(df, start, end, cadence)


