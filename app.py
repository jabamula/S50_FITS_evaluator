# This application looks on Seestar S50 FITS files that are debayered and plate solved.
# The program will ask the user to choose the files.
# It will get the Right Ascension and Declination coordinates from the center of the file First File and make a scatter plot of all files in the FOV of the image.
# It will also calculate the difference in pixel values from the first file and plot the movement of the image as pixels.
#
# Jari Backman, 2024
from datetime import datetime
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates 
from pathlib import Path
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilenames
from astropy.io import fits
from astropy.wcs import WCS
import csv
import warnings

# silence filter warnings due to older fits code
warnings.filterwarnings('ignore', message='.*datfix.*', append=True)

# function for converting decimal degrees (DD) to degrees, minutes, seconds (DMS) coordinates
def dd_to_dms(dd):
    mnt,sec = divmod(dd*3600,60)
    deg,mnt = divmod(mnt,60)
    deg = int(deg);
    mnt = int(mnt);
    return deg,mnt,sec;

# center coordinates in the image
x, y = 540, 960

# defining the data frame
df = pd.DataFrame()

# show an "Open" dialog box and return the path to the selected file
seestar = askopenfilenames(title = "Open FIT file(s) - In Chronological Order!!")

# name of csv file
file_name = "object_coordinates.csv"

# go through each object
for fitsfile in seestar:
    # get the file name from full path
    seestarfile = Path(fitsfile).stem

    # open the fits file
    f = fits.open(Path(fitsfile))
                         
    # get the given object RA, Dec
    ra_set = fits.getval(fitsfile, 'RA')
    dec_set = fits.getval(fitsfile, 'DEC')

    # read the FITS header
    mywcs = WCS(f[0].header)
    
    # get the ra, dec in the center of the image
    ra, dec = mywcs.all_pix2world([[x, y]], 0)[0]

    # convert to hexadecimal dd, mm, ss
    ra_h, ra_min, ra_sec = dd_to_dms(ra)
    dec_d, dec_min, dec_sec = dd_to_dms(dec)
    ra_sed = f"{ra_h:02}:{ra_min:02}:{int(ra_sec):02}"
    dec_sed = f"{dec_d:02}:{dec_min:02}:{int(dec_sec):02}"

    # convert to hexadecimal hh, mm, ss
    ra_h, ra_min, ra_sec = dd_to_dms(ra / 15)
    dec_d, dec_min, dec_sec = dd_to_dms(dec)
    ra_sex = f"{ra_h:02}:{ra_min:02}:{int(ra_sec):02}"
    dec_sex = f"{dec_d:02}:{dec_min:02}:{int(dec_sec):02}"

    # calculate the pixel distance center
    if fitsfile == seestar[0]:
        dpix_ra = 0
        dpix_dec = 0
        dpi_ra = 0
        dpi_dec = 0
        dpix = 0
        dpi = 0
        time_start = round((dt.datetime.strptime(fits.getval(fitsfile,'DATE-OBS')[11:], "%H:%M:%S.%f") - dt.datetime(1900,1,1)).total_seconds(),1)
        time = 0
        dtime = 0
    else:
         # timing of the observation and delta time between observations
        time_act = round((dt.datetime.strptime(fits.getval(fitsfile,'DATE-OBS')[11:], "%H:%M:%S.%f") - dt.datetime(1900,1,1)).total_seconds(),1)
        time = time_act - time_start
        dtime = time - my_data['time'].item()
        
        # cumulative step from the beginning
        dpix_ra = (df['RA_desim'][0:1].item() - ra) / 2.37 * 3600
        dpix_dec = -(df['DEC_desim'][0:1].item() - dec) / 2.37 * 3600
        
        # consecutive steps
        dpi_ra = (my_data['RA_desim'].item() - ra) / 2.37 * 3600
        dpi_dec = -(my_data['DEC_desim'].item() - dec) / 2.37 * 3600
        
        # calculate the total movement in pixels from file to file
        dx = (df['RA_desim'][0:1].item() - ra) / 2.37 * 3600
        dy = (df['DEC_desim'][0:1].item() - dec) / 2.37 * 3600
        dpix = (abs(dx)**2 + abs(dy)**2)**0.5
        
        # calculate the total movement in pixels from file to file
        dx = (my_data['RA_desim'].item() - ra) / 2.37 * 3600
        dy = (my_data['DEC_desim'].item() - dec) / 2.37 * 3600
        dpi = (abs(dx)**2 + abs(dy)**2)**0.5

    # data to be added to the csv file
    my_data = pd.DataFrame({'          Observation file':[seestarfile], 
                            'time':[round(time, 1)],  
                            'dtime':[round(dtime, 1)], 
                            'RA_desim':[round(ra, 5)], 'DEC_desim':[round(dec, 5)], 
                            'RA_sexad':[ra_sed], 'DEC_sexad':[dec_sed], 
                            'RA_sexah':[ra_sex], 'DEC_sexah':[dec_sex], 
                            ' Xtot':[round(dpix_ra, 1)], ' Ytot':[round(dpix_dec, 1)], 
                            'Pixel total':[round(dpix,1)],
                            '    X':[round(dpi_ra, 1)], '    Y':[round(dpi_dec, 1)], 
                            'Pixel single':[round(dpi,1)]})
    # append data to data frame
    df = pd.concat([df, my_data], ignore_index=True)
    
# save the data to csv file
df.to_csv(file_name, index=False)
print('Results are written to ', file_name)
print('RA dispersion: ', round((max(df['RA_desim'])- min(df['RA_desim'])) * 60, 2), ' arc min')
print('DEC dispersion: ', round((max(df['DEC_desim'])- min(df['DEC_desim'])) * 60, 2), ' arc min')

# start graphing, define the plot layout
fig = plt.figure(figsize=(12.9, 9.5))  # 1290 x 965 px, 1 inch = 100 px

# text box style in graphics
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

# graph 1: RA vs Dec
xmin = df['RA_desim'][0:1].item() + 0.3611
xmax = df['RA_desim'][0:1].item() - 0.3611
ymin = df['DEC_desim'][0:1].item() - 0.6347
ymax = df['DEC_desim'][0:1].item() + 0.6347

ax1 = fig.add_subplot(121)  
ax1.scatter(df['RA_desim'], df['DEC_desim'], c='b', marker='.')
ax1.set_xlim(xmin,  xmax)
ax1.set_ylim(ymin, ymax)
ax1.set_xlabel('RA (arcminutes)')
ax1.set_ylabel('Dec (arcminutes)')
ax1.set_title('Image center coordinate wandering - ' + fits.getval(fitsfile, 'OBJECT') + ' - '  + fits.getval(fitsfile,'DATE-OBS')[:10])
ax1.set_facecolor("whitesmoke")
ax1.text(
    0.015, 0.99,
    f'RA Width = {xmin-xmax:.1f} arc min\nDEC Height = {ymax-ymin:.1f} arc min',
    fontsize=12,
    va='top', ha='left',
    transform=ax1.transAxes, bbox=props)
ax1.text(
    1, 0, 
    f'JB {datetime.now().year}', 
    fontsize=8, 
    va='bottom', ha='right', 
    transform=ax1.transAxes)

# graph 2: X vs Y
xmin = min(df[' Xtot'])
xmax = max(df[' Xtot'])
ymin = min(df[' Ytot'])
ymax = max(df[' Ytot'])

ax2 = fig.add_subplot(122)  
#ax2.plot(df['    X'], df['    Y'], color='red', linestyle='dashed', marker='.')
ax2.scatter(df[' Xtot'], df[' Ytot'], c='r', marker='o')
ax2.set_xlim(xmin,  xmax)
ax2.set_ylim(ymin,  ymax)
ax2.set_xlabel('X (pixels)')
ax2.set_ylabel('Y (pixels)')
ax2.set_title('Pixel center wandering - ' + fits.getval(fitsfile, 'OBJECT') + ' - ' + fits.getval(fitsfile,'DATE-OBS')[:10])
ax2.set_facecolor("whitesmoke")
ax2.text(
    0.015, 0.99,
    f'Pixel X Width = {xmax-xmin:.1f} \nPixel Y Height = {ymax-ymin:.1f}',
    fontsize=12,
    va='top', ha='left',
    transform=ax2.transAxes, bbox=props)
ax2.text(
    1, 0, 
    f'JB {datetime.now().year}', 
    fontsize=8, 
    va='bottom', ha='right', 
    transform=ax2.transAxes)

# tight layout, show the two first graphs parallel
plt.tight_layout()

# graph 3: movement of pixels from image to image
fig, ax3 = plt.subplots(figsize=(12.9, 7.25))  # This takes all the width
ax3.scatter(df['time'],df['Pixel single'], c='r', marker='o')  
ax3.plot(df['time'],df['Pixel total'], c='r', marker='x', linestyle='dashdot')  
ax3.set_xlabel('Seconds from start') 
ax3.set_ylabel('Wandering (pixels)')
ax3.set_title(fits.getval(fitsfile, 'OBJECT') + ' - Seestar Movement in Time in Pixels  - ' + fits.getval(fitsfile,'DATE-OBS')[:10])
ax3.set_facecolor("whitesmoke")
ax3.legend(['From previous point', 'From start'])
# ax3.legend.get_frame().set_facecolor('wheat')
ax3.text(
    1, 0, 
    f'JB {datetime.now().year}', 
    fontsize=8, 
    va='bottom', ha='right', 
    transform=ax3.transAxes)

# show the plot
plt.show()