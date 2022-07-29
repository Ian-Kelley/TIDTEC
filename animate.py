import matplotlib.pyplot as plt
import datetime as dt
import cartopy.crs as ccrs
import pandas as pd
from cartopy.feature.nightshade import Nightshade


def plot_still(time, df, frame_code):
    plt.close()
    tecmap = plt.figure(figsize=(16, 10))
    ax = plt.axes(projection = ccrs.Orthographic(central_longitude=-100, central_latitude=60))
    ax.coastlines(color='black', zorder=1)
    ax.gridlines()
    ax.set_extent([-130, -70, 20, 60])
    ax.add_feature(Nightshade(time, alpha=0.15))
    ax.set_title(str(time), size=30)
    part = df[df['datetime'] == time]
    if(len(part.tec)) < 10000:#reurn if not enough points
        return frame_code
    mesh = ax.scatter(part.glon, part.gdlat, c=part['30min_detrend'], transform=ccrs.PlateCarree(), vmin=1, vmax=-1, cmap='plasma', s=15)
    cbar = plt.colorbar(mesh, fraction=0.046, pad=0.04)
    cbar.set_label('detrend TECu')
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
    start = dt.datetime(2017, 9, 7, 23)
    end = start + dt.timedelta(hours=4)

    cadence = dt.timedelta(seconds = 30) 
    filename = 'los_' + str(start.year) + str(start.month).zfill(2) + str(start.day).zfill(2) + '.pkl'
    df = pd.read_pickle(filename)
    plot_series(df, start, end, cadence)
    #run ffmpeg 


