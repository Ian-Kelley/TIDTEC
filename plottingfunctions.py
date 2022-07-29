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
    date_time = date_time = time.strftime("%m/%d/%Y, %H:%M:%S")
    ax.set_title(date_time + ' UT', size=20)
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


def tecplot(radar, beam, tec_df, start, end):
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    fig, axs = plt.subplots(1, 1, constrained_layout=True, figsize=(9, 3))
    #plotting TEC data only
    path, interp = get_outline(radar, beam)
    tec_df['contained'] = path.contains_points(np.vstack((tec_df.glon, tec_df.gdlat)).T) 
    part = tec_df.where(tec_df['contained'] == 1).dropna()
    part['nrange'] = 45*interp(part.glon, part.gdlat)  
    a1 = axs[0].scatter(part.datetime, part.nrange, c=part['30min_detrend'], vmin=-5, vmax=5, marker='s', alpha=.3, s=2, cmap='plasma') 
    cbar = fig.colorbar(a1, ax=axs[0]) 
    cbar.set_alpha(1)
    cbar.set_label('dTEC, TECU') 



def threeplot(radar, beam, rad_df, tec_df, start, end, sensitivity=1, ylim=2700, plot_ground=False, plot_v=False, plots='all', savefig=False):
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib as mpl
    mpl.rcParams['figure.dpi'] = 200

    if plots=='all':
        fig, axs = plt.subplots(3, 1, constrained_layout=True, figsize=(8, 7))
    elif plots=='sd':
        fig, axs = plt.subplots(1, 1, constrained_layout=True, figsize=(9, 3))
    elif plots=='tec':
        fig, axs = plt.subplots(1, 1, constrained_layout=True, figsize=(9, 3))
    elif plots=='both':
        fig, axs = plt.subplots(2, 1, constrained_layout=True, figsize=(9, 5))

    if plots=='all' or plots=='tec' or plots=='both':
        #plotting TEC data only
        path, interp = get_outline(radar, beam)
        tec_df['contained'] = path.contains_points(np.vstack((tec_df.glon, tec_df.gdlat)).T) 
        part = tec_df.where(tec_df['contained'] == 1).dropna()
        part['nrange'] = 45*interp(part.glon, part.gdlat)  
        if plots=='tec':
            a1 = axs.scatter(part.datetime, part.nrange, c=part['30min_detrend'], vmin=-1 * sensitivity, vmax=sensitivity, marker='s', alpha=.5, s=3, cmap='plasma') 
            cbar = fig.colorbar(a1, ax=axs) 
        else:
            a1 = axs[0].scatter(part.datetime, part.nrange, c=part['30min_detrend'], vmin=-1 * sensitivity, vmax=sensitivity, marker='s', alpha=.5, s=3, cmap='plasma') 
            cbar = fig.colorbar(a1, ax=axs[0]) 
        cbar.set_alpha(1)
        cbar.set_label('dTEC, TECU') 

    if plots=='all' or plots=='sd' or 'both':
        #for plotting radar data
        rad_df = rad_df.where(rad_df.bmnum == beam).dropna()
        beam_num = int(rad_df.bmnum.unique()[0])
        rad_df.slist = rad_df.slist * 45
        #this next line will use ground range estimation from Bristow et al. 1994
        if plot_ground:
            Re = 6371#km radius of earth
            h = 250#km altitude of peak density
            rad_df.slist =Re * np.arcsin((((rad_df.slist ** 2) / 4) - (h**2)) ** 0.5  / Re)

        rad_df.slist = rad_df.slist 
        if plot_v:
            if plots=='sd':
                rad = axs.scatter(rad_df.time, rad_df.slist, c = rad_df.v, vmin = -500, vmax=500, cmap='RdBu', marker = 's', s=3)
                cbar = fig.colorbar(rad, ax=axs) 
                axs.set_facecolor('lightgray')
                
            else:
                rad = axs[1].scatter(rad_df.time, rad_df.slist, c = rad_df.v, vmin = -500, vmax=500, cmap='RdBu', marker = 's', s=3)
                cbar = fig.colorbar(rad, ax=axs[1]) 
                axs[1].set_facecolor('lightgray')
            cbar.set_label('SD Velocity, m/s')
            
        else:
            if plots=='sd':
                rad = axs.scatter(rad_df.time, rad_df.slist, c = rad_df.p_l, vmin = 0, vmax=40, cmap='jet', marker = 's', s=3)
                cbar = fig.colorbar(rad, ax=axs) 
            else:
                rad = axs[1].scatter(rad_df.time, rad_df.slist, c = rad_df.p_l, vmin = 0, vmax=40, cmap='jet', marker = 's', s=3)
                cbar = fig.colorbar(rad, ax=axs[1]) 
            cbar.set_label('SD Power, dB')

    if plots=='all':
        #plotting both at once
        axs[2].scatter(part.datetime, part.nrange, c=part['30min_detrend'], vmin=-1 * sensitivity, vmax=sensitivity, marker='s', alpha=1, s=2, cmap='plasma')
        if plot_v:
            axs[2].scatter(rad_df.time, rad_df.slist, c = rad_df.v, vmin = -500, vmax=500, cmap='RdBu', marker = 's', s=3, alpha=1)
        else:    
            axs[2].scatter(rad_df.time, rad_df.slist, c = rad_df.p_l, vmin = 0, vmax=40, cmap='jet', marker = 's', s=3, alpha=0.7)

    #format the figure
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7) 
    formatter = mdates.ConciseDateFormatter(locator)
    fig.suptitle(radar +' beam #' + str(beam),  fontsize="x-large")

    if plots=='sd' or plots=='tec':
        axs.xaxis.set_major_locator(locator) 
        axs.xaxis.set_major_formatter(formatter) 
        axs.set_xlim([start, end]) 
        axs.set_ylim([0, ylim]) 
        axs.set_ylabel('Range, km')
    else:
        for ax in axs: 
            ax.xaxis.set_major_locator(locator) 
            ax.xaxis.set_major_formatter(formatter) 
            ax.set_xlim([start, end]) 
            ax.set_ylim([0, ylim]) 
            ax.set_ylabel('Range, km')
    if savefig:
        fig.savefig(radar +' beam #' + str(beam) + ".pdf", bbox_inches='tight')
        fig.savefig(radar +' beam #' + str(beam) + ".png", bbox_inches='tight')

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