def single_plot(time, df):
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import datetime as dt
    fig = plt.figure(figsize = (12, 7))
    part = df[df['datetime'] == time]
    if len(part) < 10000:
        part = df[df['datetime'] == time + dt.timedelta(seconds = 30)]
    ax = fig.add_subplot(1, 1, 1, projection="fovcarto",coords="geo", plot_date=time,map_projection=ccrs.Orthographic(central_longitude=-100, central_latitude=60))
    ax.set_extent([-130, -70, 30, 65])
    ax.set_title(time.strftime('%H:%M UT'), size=20)
    mesh = ax.scatter(part.glon, part.gdlat, c=part['30min_detrend'], transform=ccrs.PlateCarree(), vmin=-1, vmax=1, cmap='plasma', s=8, zorder=0)
    pos = ax.get_position()
    ax.grid_on()
    cbar = plt.colorbar(mesh, fraction=0.04, pad=0.04)
    cbar.set_label('TECu')
    ax.coastlines()
    ax.add_dn_terminator()

    return ax

def get_outline(radar, beam):
    import numpy as np
    import pydarn
    import matplotlib.path
    import rad_fov
    from scipy import interpolate
    hdw = pydarn.read_hdw_file(radar)
    rf = rad_fov.CalcFov(hdw=hdw, ngates=60)
    lons, lats = rf.lonFull, rf.latFull
    beam_lons = np.concatenate((lons[beam-1], np.flip(lons[beam])))
    beam_lats = np.concatenate((lats[beam-1], np.flip(lats[beam])))
    coords = np.vstack((beam_lons, beam_lats)).T
    path = matplotlib.path.Path(coords, closed=True)   
    
    #interpolation
    nrange = np.concatenate((np.arange(len(beam_lons) / 2), np.flip(np.arange(len(beam_lons) / 2))))
    #testing
    nrange_lats = np.concatenate((np.arange(len(beam_lats) / 2), np.flip(np.arange(len(beam_lats) / 2))))
    if (nrange != nrange_lats).all():
        raise UserWarning('different ranges calcuated from lat and lon verticies') 
    interp = interpolate.LinearNDInterpolator((beam_lons, beam_lats), nrange)

    return path, interp

def vel_ts(tec_df, radar, beam, startrange, endrange, start, end):
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import pandas as pd
    import numpy as np
    path, interp = get_outline(radar, beam)
    tec_df['contained'] = path.contains_points(np.vstack((tec_df.glon, tec_df.gdlat)).T) 
    part = tec_df.where(tec_df['contained'] == 1).dropna()
    part = part.where(startrange < part.nrange)
    part = part.where(part.nrange < endrange).dropna()
    fig, axs = plt.subplots(1, 1, constrained_layout=True, figsize=(9, 2.7))
    axs.scatter(part.datetime, part['30min_detrend'], s=.25, marker='s', c='k')
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    formatter = mdates.ConciseDateFormatter(locator)
    axs.xaxis.set_major_locator(locator)
    axs.xaxis.set_major_formatter(formatter)
    plt.title('Detrended TEC between ' + str(startrange) + ' and ' + str(endrange) +'km')
    axs.set_ylim([-5, 5])
    axs.set_xlim([start, end])
    grouped = part.set_index('datetime').groupby(pd.Grouper(freq='s')).mean().dropna()
    axs.plot(grouped.index, grouped['30min_detrend'], c='r')

def powerplot(filename, maxrange=60):
    import pandas as pd
    import matplotlib.pyplot as plt
    rad_df = pd.read_pickle(filename)
    rad_df.slist = rad_df.slist * 45
    code = filename[-9:-6]
    fig, axs = plt.subplots(1, 1, constrained_layout=True, figsize=(10, 3))
    beam_num = int(rad_df.bmnum.unique()[0])
    fig.suptitle(code.upper() + ' Beam #' + str(beam_num), fontsize=16)
    plt.scatter(rad_df.time, rad_df.slist, c = rad_df.p_l, vmin = 0, vmax=40, cmap='jet', marker = 's', s=3)
    cbar = plt.colorbar()
    cbar.set_label('Power, dB')

def threeplot(radar, beam, rad_df, tec_df, start, end):
    import matplotlib.pyplot as plt
    import numpy as np
    import matplotlib.dates as mdates
    fig, axs = plt.subplots(3, 1, constrained_layout=True, figsize=(10, 9))

    #plotting TEC data only
    path, interp = get_outline(radar, beam)
    tec_df['contained'] = path.contains_points(np.vstack((tec_df.glon, tec_df.gdlat)).T) 
    part = tec_df.where(tec_df['contained'] == 1).dropna()
    part['nrange'] = 45*interp(part.glon, part.gdlat)  
    a1 = axs[0].scatter(part.datetime, part.nrange, c=part['30min_detrend'], vmin=-5, vmax=5, marker='s', alpha=.3, s=2, cmap='plasma') 
    cbar = fig.colorbar(a1, ax=axs[0]) 
    cbar.set_alpha(1)
    cbar.set_label('dTEC, TECU') 

    #for plotting radar data
    beam_num = int(rad_df.bmnum.unique()[0])
    rad_df.slist = rad_df.slist * 45
    rad = axs[1].scatter(rad_df.time, rad_df.slist, c = rad_df.p_l, vmin = 0, vmax=40, cmap='jet', marker = 's', s=3)
    cbar = fig.colorbar(rad, ax=axs[1]) 

    #plotting both at once
    axs[2].scatter(part.datetime, part.nrange, c=part['30min_detrend'], vmin=-5, vmax=5, marker='s', alpha=.3, s=2, cmap='plasma')
    axs[2].scatter(rad_df.time, rad_df.slist, c = rad_df.p_l, vmin = 0, vmax=40, cmap='jet', marker = 's', s=3)

    #format the figure
    #matplotlib.rcParams['figure.dpi'] = 100 
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7) 
    formatter = mdates.ConciseDateFormatter(locator)
    for ax in axs: 
        ax.xaxis.set_major_locator(locator) 
        ax.xaxis.set_major_formatter(formatter) 
        ax.set_xlim([start, end]) 
        ax.set_ylim([0, 2700]) 
        ax.set_ylabel('Range, km')