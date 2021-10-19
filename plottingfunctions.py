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

