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
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from apps.ClimAnalFunctions import * 

##########################################################################################
#THIS SURFACE PLOT CALCULATION WOULD PROBABLY BE 'MUCH' QUICKER USING A GLOBAL RADIANCE 
#DISTRIBUTION MODEL. THE DISTRIBUTION ONLY NEEDS TO BE CALCULATED ONCE. ONLY THE PATCH
#VIEW FACTORS NEED TO BE RE-CALCULATED. THIS WILL NEED A MECHANISM TO ESTIMATE THE VIEW
#FACTOR FOR CUTS THROUGH PATCHES FROM A PROGRESSIVELY TILTED PLANE. 
##########################################################################################

def app(file_name, title, ui_helper, file_list, lat, longitude, timezone):
    
    st.write("# "+title)

    DiffuseOnly = st.sidebar.checkbox("DiffuseOnly", value=False, help="If TRUE then only diffuse irradiation is calculated; otherwise direct is also included")
    isotropic = st.sidebar.checkbox("isotropic", value=False, help="If TRUE then simpler calculations are used for an isotropic sky")
    FirstSweep = True

    cumhour=0
    globalirradbeta=0
    day_list = []
    dec_list = []
    hour_list = []
    solalt_list = []
    solaz_list = []
    timediff_list = []
    cai_list = []
    # file_list = []
    global_list = []
    diffuse_list = []
    day_global_list = []
    day_diffuse_list = []
    igbeta_list = []
    annualirrad_list = []

    # with open(os.path.join(pathlib.Path(__file__).parent.absolute(), "Finningley.csv"), "r") as file: 
    #     for line in file:
    #         line = line.rstrip('\n')
    #         line = line.split(',')
    #         file_list.append(line)
    #     file.close()

    #This is to access the headers from the epw file
    lat = lat * pi / 180
    groundref = st.sidebar.number_input("groundref", 0.0, 1.0, 0.2, 0.5)
    timeshift = st.sidebar.slider("Timeshift", -0.5, 0.5, -0.5, 0.5, help="This is to handle timing conventions relating to climate data collection")




    #this popuates global and diffuse lists with the corresponding solar data
    for i in range (3,len(file_list)):
        global_list.append(float(file_list[i][5]))
        diffuse_list.append(float(file_list[i][6]))

    #This is where the daily and hourly solar quantities are calculated
    for tilt in range(0,95,10):
        for wallaz in range (0,360,10):
            for i in range(1,366):
                if FirstSweep == True: #no need to re-calculate sun-positions
                    day_list.append(i)
                    dec_list.append(declin_angle(i))
                    timediff_list.append(time_diff(i,False,longitude,timezone,timeshift))
                    #This populates a list of daily SR, SS times, for the solar availability plots
                for j in range(1,25):
                    cumhour=cumhour+1
                    if FirstSweep == True: #no need to re-calculate sun-positions
                        solalt_list.append(solar_altitude(i,j+timediff_list[i-1],lat, dec_list[i-1]))
                        solaz_list.append(solar_azimuth(i,j+timediff_list[i-1],lat,solalt_list[cumhour-1], dec_list[i-1]))
                    cai_list.append(cai(wallaz*pi/180,tilt*pi/180,solalt_list[cumhour-1],solaz_list[cumhour-1]))
                    igbeta_list.append(igbeta(i, cai_list[cumhour-1],global_list[cumhour-1],diffuse_list[cumhour-1],solalt_list[cumhour-1],tilt*pi/180, isotropic, DiffuseOnly, groundref))
                    globalirradbeta = globalirradbeta + igbeta_list[cumhour-1]    
            
            annualirrad_list.append(globalirradbeta)
            FirstSweep = False
            globalirradbeta=0
            cumhour=0
            cai_list.clear()
            igbeta_list.clear()

    if isotropic==True:
        #This creates a 2D irradiation surface plot
        xlist = np.linspace(0, 350, 36)
        ylist = np.linspace(0, 90, 10) #Note: theer need to be 19 subdivisions (here and for Z) for 5o bins of altitude
        X, Y = np.meshgrid(xlist, ylist)
        fig,ax=plt.subplots(1,1, figsize=(16,8))
        #this part converts the list into an array and reshapes it, to match the x,y dimensions
        Z = np.array(annualirrad_list)*10**-6
        Z = Z.reshape(10,36)
        cp = ax.contourf(X, Y, Z, 16, cmap='plasma', alpha=1.0) #NB: 16 sets number of division; alpha sets opacity; 'magma', 'jet' and 'viridis' are also good cmaps
        fig.colorbar(cp, label = 'Solar irradiation, MWh/m\u00b2') # Adds a colorbar
        fig_title = 'Annual Solar Irradiation Surface Plot: Isotropic Sky'
        ax.set_title(fig_title)
        ax.set_xlabel('Collector azimuth, deg')
        ax.set_ylabel('Collector tilt, deg')
        # plt.show()
        st.pyplot(fig)
        st.write(ui_helper.generate_fig_dl_link(fig, fig_title), unsafe_allow_html=True)

    else:
        #This creates a 2D irradiation surface plot
        xlist = np.linspace(0, 350, 36)
        ylist = np.linspace(0, 90, 10) #Note: theer need to be 19 subdivisions (here and for Z) for 5o bins of altitude
        X, Y = np.meshgrid(xlist, ylist)
        fig,ax=plt.subplots(1,1, figsize=(16,8))
        #this part converts the list into an array and reshapes it, to match the x,y dimensions
        Zprime = np.array(annualirrad_list)*10**-6
        Zprime = Zprime.reshape(10,36)
        cp = ax.contourf(X, Y, Zprime, 16, cmap='plasma', alpha=1.0) #NB: 16 sets number of division; alpha sets opacity; 'magma', 'jet' and 'viridis' are also good cmaps
        fig.colorbar(cp, label = 'Solar irradiation, MWh/m\u00b2') # Adds a colorbar    
        fig_title = 'Annual Solar Irradiation Surface Plot'
        ax.set_title(fig_title)
        ax.set_xlabel('Collector azimuth, deg')
        ax.set_ylabel('Collector tilt, deg')
        # plt.show()
        st.pyplot(fig)
        st.write(ui_helper.generate_fig_dl_link(fig, fig_title), unsafe_allow_html=True)
