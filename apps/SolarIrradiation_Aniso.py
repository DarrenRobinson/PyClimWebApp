##########################################################################################
# PyClim was developed by Prof. Darren Robinson (University of Sheffield, 2019).         #
# PyClim produces a range of graphs and statistics to support the analysis of climate    #
# data, to support architectural / engineering / technology students to develop their    #
# early-stage bioclimatic design concepts.                                               #
##########################################################################################

#This module creates solar irradiation surface plots, either for an isotropic or for an
#anisotropic sky.
#A prior version also calculated a quotient of the two, to demonstrate the importance of
#modelling anisotropy.

#imports the basic libraries
import math

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from .ClimAnalFunctions import (cai2, declin_angle2, groundref, igbeta2,
                               solar_altitude2, solar_azimuth2, time_diff2,
                               timeshift)

pi = math.pi

##########################################################################################
#THIS SURFACE PLOT CALCULATION WOULD PROBABLY BE 'MUCH' QUICKER USING A GLOBAL RADIANCE 
#DISTRIBUTION MODEL. THE DISTRIBUTION ONLY NEEDS TO BE CALCULATED ONCE. ONLY THE PATCH
#VIEW FACTORS NEED TO BE RE-CALCULATED. THIS WILL NEED A MECHANISM TO ESTIMATE THE VIEW
#FACTOR FOR CUTS THROUGH PATCHES FROM A PROGRESSIVELY TILTED PLANE. 
##########################################################################################

def app(app, epw, ui, timeshift=timeshift, groundref=groundref):
    st.write("# "+app['title'])

    DiffuseOnly = st.sidebar.checkbox("DiffuseOnly", value=False, help="If TRUE then only diffuse irradiation is calculated; otherwise direct is also included")
    isotropic = st.sidebar.checkbox("isotropic", value=False, help="If TRUE then simpler calculations are used for an isotropic sky")
    groundref = st.sidebar.number_input("groundref", 0.0, 1.0, groundref, 0.5)
    timeshift = st.sidebar.slider("Timeshift", -0.5, 0.5, timeshift, 0.5, help="This is to handle timing conventions relating to climate data collection")

    #This is to access the headers from the epw file
    lat = epw.lat * pi / 180

    #this popuates global and diffuse lists with the corresponding solar data
    global_list = epw.dataframe['Global Horizontal Radiation'].to_numpy()
    diffuse_list = epw.dataframe['Diffuse Horizontal Radiation'].to_numpy()
    
    #This is where the daily and hourly solar quantities are calculated
    day_list = np.array(range(1,366))
    dec_list = declin_angle2(day_list)
    timediff_list = time_diff2(day_list, False, epw.lng, epw.timezone, timeshift)
    day_list_repeat = np.repeat(day_list, 24)
    dec_list_repeat = np.repeat(dec_list, 24)
    hours = np.tile(np.array(range(1,25)), 365)
    timediff_list_repeat = np.repeat(timediff_list, 24)
    jhour_x_time = np.add(hours, timediff_list_repeat)
    solalt_list = solar_altitude2(day_list_repeat, jhour_x_time, lat, dec_list_repeat)
    solaz_list = solar_azimuth2(day_list_repeat, jhour_x_time, lat, solalt_list, dec_list_repeat)

    tilt = 0
    wallaz = 0
    counter = 1
    annualirrad_list = np.array([])
    for i in range(360):
        cai_list = cai2(wallaz*pi/180, tilt*pi/180, solalt_list, solaz_list)
        igbeta_list = igbeta2(day_list_repeat, cai_list, global_list, diffuse_list, solalt_list, tilt*pi/180, isotropic, DiffuseOnly, groundref)
        annualirrad_list = np.append(annualirrad_list, np.sum(igbeta_list))
        tilt = tilt + 10 if ((counter % 36) == 0) else tilt
        wallaz = wallaz + 10 if wallaz < 350 else 0
        counter += 1

    # FirstSweep = True
    # day_list = []
    # dec_list = []
    # timediff_list = []
    # cumhour=0
    # globalirradbeta=0
    # hour_list = []
    # solalt_list = []
    # solaz_list = []
    # cai_list = []
    # file_list = []
    # global_list = []
    # diffuse_list = []
    # day_global_list = []
    # day_diffuse_list = []
    # igbeta_list = []
    # annualirrad_list = []
        
    #This is where the daily and hourly solar quantities are calculated
    # for tilt in range(0,95,10):
    #     for wallaz in range(0,360,10):
            # for i in range(1,366):
                # if FirstSweep: #no need to re-calculate sun-positions
                #     day_list.append(i)
                #     dec_list.append(declin_angle(i))
                #     timediff_list.append(time_diff(i,False,epw.longitude,epw.timezone,timeshift))
                    #This populates a list of daily SR, SS times, for the solar availability plots
                # for j in range(1,25):
                #     cumhour=cumhour+1
                    # if FirstSweep: #no need to re-calculate sun-positions
                    #     solalt_list.append(solar_altitude(i,j+timediff_list[i-1],lat, dec_list[i-1]))
                    #     solaz_list.append(solar_azimuth(i,j+timediff_list[i-1],lat,solalt_list[cumhour-1], dec_list[i-1]))
                    # cai_list.append(cai(wallaz*pi/180,tilt*pi/180,solalt_list[cumhour-1],solaz_list[cumhour-1]))
                    # igbeta_list.append(igbeta(i, cai_list[cumhour-1],global_list[cumhour-1],diffuse_list[cumhour-1],solalt_list[cumhour-1],tilt*pi/180, isotropic, DiffuseOnly, groundref))
                    # globalirradbeta = globalirradbeta + igbeta_list[cumhour-1]    
            
            # annualirrad_list.append(globalirradbeta)

            # FirstSweep = False
            # globalirradbeta=0
            # cumhour=0
            # cai_list.clear()
            # igbeta_list.clear()

    if isotropic:
        #This creates a 2D irradiation surface plot
        xlist = np.linspace(0, 350, 36)
        ylist = np.linspace(0, 90, 10) #Note: theer need to be 19 subdivisions (here and for Z) for 5o bins of altitude
        X, Y = np.meshgrid(xlist, ylist)
        fig, ax = plt.subplots(1,1, figsize=(16,8), tight_layout=True)
        #this part converts the list into an array and reshapes it, to match the x,y dimensions
        Z = np.array(annualirrad_list)*10**-6
        Z = Z.reshape(10,36)
        cp = ax.contourf(X, Y, Z, 16, cmap='plasma', alpha=1.0) #NB: 16 sets number of division; alpha sets opacity; 'magma', 'jet' and 'viridis' are also good cmaps
        fig.colorbar(cp, label = 'Solar irradiation, MWh/m\u00b2') # Adds a colorbar
        fig_title = 'Annual Solar Irradiation Surface Plot: Isotropic Sky'
        ax.set_title(fig_title)
        ax.set_xlabel('Collector azimuth, deg')
        ax.set_ylabel('Collector tilt, deg')
    else:
        #This creates a 2D irradiation surface plot
        xlist = np.linspace(0, 350, 36)
        ylist = np.linspace(0, 90, 10) #Note: theer need to be 19 subdivisions (here and for Z) for 5o bins of altitude
        X, Y = np.meshgrid(xlist, ylist)
        fig, ax = plt.subplots(1,1, figsize=(16,8), tight_layout=True)
        #this part converts the list into an array and reshapes it, to match the x,y dimensions
        Zprime = np.array(annualirrad_list)*10**-6
        Zprime = Zprime.reshape(10,36)
        cp = ax.contourf(X, Y, Zprime, 16, cmap='plasma', alpha=1.0) #NB: 16 sets number of division; alpha sets opacity; 'magma', 'jet' and 'viridis' are also good cmaps
        fig.colorbar(cp, label = 'Solar irradiation, MWh/m\u00b2') # Adds a colorbar    
        fig_title = 'Annual Solar Irradiation Surface Plot'
        ax.set_title(fig_title)
        ax.set_xlabel('Collector azimuth, deg')
        ax.set_ylabel('Collector tilt, deg')

    graph, href = ui.base64_to_link_and_graph(fig, fig_title, 'jpg', 800, 400)
    st.write(graph, href, unsafe_allow_html=True)