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




def threeplot(radar, beam, rad_df, tec_df, start, end):
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    fig, axs = plt.subplots(3, 1, constrained_layout=True, figsize=(9, 8))
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
    cbar.set_label('SD Power, dB')

    #plotting both at once
    axs[2].scatter(part.datetime, part.nrange, c=part['30min_detrend'], vmin=-5, vmax=5, marker='s', alpha=.3, s=2, cmap='plasma')
    axs[2].scatter(rad_df.time, rad_df.slist, c = rad_df.p_l, vmin = 0, vmax=40, cmap='jet', marker = 's', s=3)

    #format the figure
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7) 
    formatter = mdates.ConciseDateFormatter(locator)

    for ax in axs: 
        ax.xaxis.set_major_locator(locator) 
        ax.xaxis.set_major_formatter(formatter) 
        ax.set_xlim([start, end]) 
        ax.set_ylim([0, 2700]) 
        ax.set_ylabel('Range, km')

def plot_still(time, df, frame_code, start):
    import warnings
    import datetime as dt
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import matplotlib
    warnings.filterwarnings('ignore')
    time = dt.datetime(2017, 9, 8, 1,30, 30)
    index = int((time - start).seconds / 60)
    fig = plt.figure(figsize = (25, 14))



    ax = fig.add_subplot(2, 2, 3, projection="fovcarto",coords="geo", plot_date=time,map_projection=ccrs.Orthographic(central_longitude=-100, central_latitude=60))
    ax.set_extent([-130, -70, 20, 60])
    ax.set_title('Fort Hays East/West', size=20)
    ax.grid_on()
    ax.coastlines()
    ax.add_dn_terminator()

    ax.rad='fhe'
    ax.overlay_radar()
    ax.overlay_fov()
    ax.overlay_radar_data(fhe[index], p_max=500, p_min=-500, add_colorbar=False, cmap='RdBu')

    ax.rad='fhw'
    ax.overlay_radar()
    ax.overlay_fov()
    ax.overlay_radar_data(fhw[index], p_max=500, p_min=-500, add_colorbar=False, cmap='RdBu')

    cmap = matplotlib.cm.RdBu
    norm = matplotlib.colors.Normalize(vmin=-500, vmax=500)
    cbar = plt.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax,fraction=0.04, pad=0.04) 
    cbar.set_label('Velocity, m/s')

    ax = fig.add_subplot(2, 2, 4, projection="fovcarto",coords="geo", plot_date=time,map_projection=ccrs.Orthographic(central_longitude=-100, central_latitude=60))
    ax.set_extent([-130, -70, 20, 60])
    ax.set_title('Christmas Valley East/West', size=20)
    ax.grid_on()
    ax.coastlines()
    ax.add_dn_terminator()

    ax.rad='cve'
    ax.overlay_fov()
    ax.overlay_radar_data(cve[index], p_max=500, p_min=-500, add_colorbar=False, cmap ='RdBu')

    ax.rad='cvw'
    ax.overlay_fov()
    ax.overlay_radar()
    ax.overlay_radar_data(cvw[index], p_max=500, p_min=-500, add_colorbar=False, cmap ='RdBu')



    cmap = matplotlib.cm.RdBu
    norm = matplotlib.colors.Normalize(vmin=-500, vmax=500)
    cbar = plt.colorbar(matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax,fraction=0.04, pad=0.04) 
    cbar.set_label('Velocity, m/s')
    
    #get tec based on time, use next 30 second time if not enough data 
    part = df[df['datetime'] == time]
    if len(part) < 10000:
        part = df[df['datetime'] == time + dt.timedelta(seconds = 30)]
    
    ax = fig.add_subplot(2, 2, 2, projection="fovcarto",coords="geo", plot_date=time,map_projection=ccrs.Orthographic(central_longitude=-100, central_latitude=60))
    ax.set_extent([-130, -70, 20, 60])
    ax.set_title('Raw GNSS TEC', size=20)
    mesh = ax.scatter(part.glon, part.gdlat, c=part['tec'], transform=ccrs.PlateCarree(), vmin=0, vmax=25, cmap='plasma', s=8, zorder=0, alpha=0.8)
    pos = ax.get_position()
    ax.grid_on()
    cbar = plt.colorbar(mesh, fraction=0.04, pad=0.04)
    cbar.set_label('TECu')
    ax.coastlines()
    ax.add_dn_terminator()

    ax = fig.add_subplot(2, 2, 1, projection="fovcarto",coords="geo", plot_date=time,map_projection=ccrs.Orthographic(central_longitude=-100, central_latitude=60))
    ax.set_extent([-130, -70, 20, 60])
    ax.set_title('30 min Detrended GNSS TEC', size=20)
    mesh = ax.scatter(part.glon, part.gdlat, c=part['30min_detrend'], transform=ccrs.PlateCarree(), vmin=-0.5, vmax=.5, cmap='winter', s=8, zorder=0, alpha=0.8)
    pos = ax.get_position()
    ax.grid_on()
    cbar = plt.colorbar(mesh, fraction=0.04, pad=0.04)
    cbar.set_label('TECu')
    ax.coastlines()
    ax.add_dn_terminator()

    fig.suptitle(time.strftime('%H:%M UT'), size=50)
    plt.show()