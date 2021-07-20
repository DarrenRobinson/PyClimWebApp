##########################################################################################
# PyClim was developed by Prof. Darren Robinson (University of Sheffield, 2019).         #
# PyClim produces a range of graphs and statistics to support the analysis of climate    #
# data, for architectural / engineering / technology students to develop their           #
# early-stage bioclimatic design concepts.                                               #
##########################################################################################

#THIS MODULE SIMPLY CREATES A POLAR WIND ROSE PLOT.
import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

from apps.ClimAnalFunctions import *  

def app(file_name, title, ui_helper, file_list, lat, longitude, timezone):
    st.write("# "+title)
    
    # Time filter helper
    # ui_helper.session_keys_init('windrose')
    ui_helper.time_filter('windrose')
    
    #in the future: provide the option to plot using the Beaufort scale

    ########################################################
    #The following control the format of the windrose
    ########################################################
    

    #This determines whether the radial axis goes from centre outwards or vice-versa
    invert_radialaxis=False
    #This sets the number of azimuthal sectors to plot
    numsectors = st.sidebar.slider('Number of sectors', 6, 32, 16, help="It determines the number of sectors for which data is plotted")
    #These set the lower and upper bounds of the colormap
    lower_percentile_limit  = st.sidebar.slider('Lower Percentile Limit', 0, 50, 10, help="The lower threshold for the bounds of the colormap: limits impact of outliers")
    upper_percentile_limit = st.sidebar.slider('Upper Percentile Limit', 51, 100, 80, help="The upper threshold for the bounds of the colormap: limits impact of outliers")
    #This determines whether temperature or wind speed is plotted
    PlotTemp_status = st.sidebar.radio("PlotTemp", ("Temperature", "Wind Speed"), help="If TRUE then a temperature-dependent rose will be produced; else speed-dependent")
    PlotTemp = True if (PlotTemp_status == "Temperature") else False
    #Wind speeds are potted at 1m/s intervals: TempInterval sets the temperature intervals
    TempInterval = st.sidebar.slider('Temperature Interval', 1.0, 5.0, 2.5, 0.5, help="Temperature spans a much broader range than wind speed, this is a way of limiting the number of radial divisions")

    #this reads climate data file
    winspeed_list= []
    windir_list = []
    temp_list = []
    # file_list = []

    # with open(os.path.join(pathlib.Path(__file__).parent.absolute(), result+".csv"), "r") as file: 
    #     for line in file:
    #         line = line.rstrip('\n')
    #         line = line.split(',')
    #         file_list.append(line)
    #     file.close()

    #this popuates lists with the corresponding data
    for i in range (3, len(file_list)):
        temp_list.append(float(file_list[i][3])/TempInterval)
        winspeed_list.append(float(file_list[i][7]))
        windir_list.append(float(file_list[i][8]))
    
    maxspeed = int(max(winspeed_list))
    maxtemp = int(max(temp_list))
    mintemp = int(min(temp_list))
    
    azimuth_list  = np.linspace(0, 360, (numsectors+1))
    zenith_list = np.linspace(0,maxspeed+1,(maxspeed+1))
    tempzen_list = np.linspace(mintemp,maxtemp+2,(maxtemp-mintemp+1)) 
    value_list = [[0 for i in range(numsectors+1)] for j in range(maxspeed+1)]
    tempval_list = [[0 for i in range(numsectors+1)] for j in range(maxtemp-mintemp+1)] 

    adjustment = -mintemp if mintemp > 0 else max(mintemp, -mintemp) # 1) A var is created for adjustment: temp will always start from 0 as the index number for row in tempval_list

    for j in range (0,len(file_list)-3):  
        sectornum = int(windir_list[j]/(360/numsectors))
        speednum=int(winspeed_list[j])
        tempnum=int(temp_list[j])
        zval = value_list[speednum][sectornum]

        try:
            ##
            # logic seems to break on this line when the range of temperature is positive (e.g. min:2 - max:30) as no temp is assigned to row with index 0 and the max temp exceeds the number of row by 1
            ##
            zpval = tempval_list[tempnum+adjustment][sectornum] # 2) An adjustment variable +ep is added here.
            # zpval = tempval_list[tempnum][sectornum] # Original line 
        except:
            st.write(maxtemp, mintemp)
            st.dataframe(tempval_list)
            st.write(tempnum, sectornum)

        value_list[speednum][sectornum] = zval+1
        tempval_list[tempnum+adjustment][sectornum] = zpval+1 # 3) An adjustment variable +ep is added here.
        # tempval_list[tempnum][sectornum] = zpval+1 # Original line 

    value_list[0][0]=0

    fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))

    azimuth_list = np.radians(azimuth_list)

    if PlotTemp == False:
        #NB: The jet cmap gives very good discrimination:
        cp = ax.pcolormesh(azimuth_list, zenith_list, value_list, cmap='jet') #'plasma', 'magma', 'jet' and 'viridis' are good cmaps
        
        ax.set_title('Annual Wind Rose: with wind speed in radial sectors \n')
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_ylim([int(np.percentile(winspeed_list,lower_percentile_limit)), int(np.percentile(winspeed_list,upper_percentile_limit))])
        
        if invert_radialaxis==True:
            ax.set_ylim(plt.ylim()[::-1])
        fig.colorbar(cp, label = 'Annual hours: wind approaching from \n ith direction at jth speed')
    else:
        cp = ax.pcolormesh(azimuth_list, tempzen_list, tempval_list, cmap='jet')
        
        ax.set_title('Annual Wind Rose: with temperature in radial sectors, in multiples of {0:1.1f} \n' .format(TempInterval))
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_ylim([int(np.percentile(temp_list,lower_percentile_limit)), int(np.percentile(temp_list,upper_percentile_limit))])
        
        if invert_radialaxis==True:
            ax.set_ylim(plt.ylim()[::-1])
    #    ax.set_yticklabels([])
        fig.colorbar(cp, label = 'Annual hours: wind approaching from \n ith direction at jth temperature')

    plt.tight_layout()
    # plt.show()
    st.pyplot(fig)
    fig_title = 'Wind Rose'
    st.write(ui_helper.generate_fig_dl_link(fig, fig_title), unsafe_allow_html=True)
