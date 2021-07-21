##########################################################################################
# PyClim was developed by Prof. Darren Robinson (University of Sheffield, 2019).         #
# PyClim produces a range of graphs and statistics to support the analysis of climate    #
# data, to support architectural / engineering / technology students to develop their    #
# early-stage bioclimatic design concepts.                                               #
##########################################################################################

#////////////////////////////////////////////////////////////////////////////////////
# CREATE A CLASS TO CREATE THE CHART, AND PASS ARRAYS WITH THE DATA TO BE PLOTTED
#////////////////////////////////////////////////////////////////////////////////////

#This module creates a psychrometric chart for the plotting of climate data
#It also creates a second chart with data translated along the wet bulb line 
#to a defined fraction of the wbtd, to mimic adiabatic (evaporative) cooling.

#imports the basic libraries
import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

from apps.ClimAnalFunctions import * 

def app(app, epw, ui):
    st.write("# "+app['title'])
       
    filter_applied = ui.is_filter_applied(app['file_title'])
    daynum_list = [31,28,31,30,31,30,31,31,30,31,30,31]     # Default values if dataset is not filtered
    hour_range = 25                                         # Default values if dataset is not filtered
    if filter_applied:
        # Calculate number of days each month if dataset is filtered
        for i in range (1,13):
            daynum_list[i-1] = len(epw.dataframe[epw.dataframe['Month'] == i]['Day'].unique()) 
        # Calculate number of hours daily if dataset is filtered
        hour_range = (st.session_state.psychros_end_hour-st.session_state.psychros_start_hour+2) if (st.session_state.psychros_end_hour >= st.session_state.psychros_start_hour) else ((24-st.session_state.psychros_start_hour)+(st.session_state.psychros_end_hour-1)+2)




    # Time filter
    ui.time_filter(app['file_title'])

    # colour = st.sidebar.color_picker(color_picker_label, value='#0C791A', help="By default when applying filters, all data should be plotted in the same colour")
    colour = '#0C791A'

    # file_list = []
    temp_list = []
    rh_list = []
    g_list = []

    PlotMonthly = st.sidebar.checkbox("Plot Monthly", value=True, help="If FALSE then there is no distinction between data points for different months")
    PlotEvapCool = st.sidebar.checkbox("PlotEvapCool", value=True, help="Efficiency of the evaporative cooling process")
    
    min_temp = min(np.array(epw.file_list[3:])[:,3])
    # max_temp = max(np.array(epw.file_list[3:])[:,3])

    LLdbt = st.sidebar.number_input("LLdbt", min_value=float(min_temp), value=25.0, step=0.5, help="Temperature above which data points are shifted to mimic evaporative cooling") #lower limit of temperature: above which data is shifted
    MartinezLimit = True
    EvapCoolEff = st.sidebar.slider("EvapCoolEff", 0.0, 1.0, 0.7, help="If TRUE then a separate plot is produced with evaporative cooling mimicked") #Proportion of wbtd thar data s shifted to.
    Screen = False #so that wbt not t_screen is calculated  
    
    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    #READ IN THE CLIMATE DATA TO PLOT
    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    #this reads climate data file

    # numhours=0
    # with open(os.path.join(pathlib.Path(__file__).parent.absolute(), "Finningley.csv"), "r") as file: 
    #     for line in file:
    #         line = line.rstrip('\n')
    #         line = line.split(',')
    #         epw.file_list.append(line)
    #         numhours=numhours+1
    #     file.close()
    numhours = len(epw.file_list)

    #this popuates lists with the corresponding data
    for i in range (3, len(epw.file_list)):
        temp_list.append(float(epw.file_list[i][3]))
        rh_list.append(float(epw.file_list[i][4]))

    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    #NOW: CREATE THE PSYCHROMETRIC CHART
    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    fig = plt.figure(figsize=(12, 8), tight_layout=True)

    temp_x_list = []
    g_y_list = []

    for rh in range (10,110,10):
        for temp in range (-10,61):
            temp_x_list.append(temp)
            g_y_list.append(g(temp,rh))
        plt.plot(temp_x_list,g_y_list, lw=1, color='darkgray')
        temp_x_list.clear()
        g_y_list.clear()

    mc=0
    while mc<=0.03:
        mc=mc+0.005
        temp_x_list.append(tsat(mc))
        g_y_list.append(mc)
        temp_x_list.append(60)
        g_y_list.append(mc)
        plt.plot(temp_x_list,g_y_list, lw=1, color='darkgray')
        temp_x_list.clear()
        g_y_list.clear()

    for temp in range(-10,60,5):
        gsat=g_dry_wet(temp,temp)
        if gsat>=0.3:
            gsat=0.3
        temp_x_list.append(temp)
        g_y_list.append(0)
        temp_x_list.append(temp)
        g_y_list.append(gsat)
        plt.plot(temp_x_list,g_y_list, lw=1, color='darkgray')
        temp_x_list.clear()
        g_y_list.clear()

    for wbt in range (-10,40,5):
        for dbt in range (-10, 61, 1):
            mc = g_dry_wet(dbt,wbt)
            if dbt>=wbt:
                temp_x_list.append(dbt)
                g_y_list.append(mc)
        plt.plot(temp_x_list,g_y_list, lw=1, color='darkgray')
        temp_x_list.clear()
        g_y_list.clear()



    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    #NOW: PLOT THE DATA
    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


    if PlotMonthly==False:
        for plotpoints in range (0,len(temp_list)):
            g_list.append(g(temp_list[plotpoints],rh_list[plotpoints]))
        plt.scatter(temp_list,g_list, c='red', alpha=0.5, s=5)
    else:
        cumhour=0
        Colour_list = ['firebrick', 'salmon', 'darkorange', 'orange', 'gold', 'yellow', 'yellowgreen', 'green', 'olive', 'cyan', 'skyblue', 'blue']
        Month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        daynum_list = daynum_list
        # daynum_list = [31,28,31,30,31,30,31,31,30,31,30,31]
        hour_range = hour_range
        Monthly_g = []
        Monthly_t = []
        for month in range (1,13):
            for days in range (0, daynum_list[month-1]):
                for hours in range(1, hour_range):
                # for hours in range(1,25):
                    Monthly_g.append(g(temp_list[cumhour],rh_list[cumhour]))
                    Monthly_t.append(temp_list[cumhour])
                    cumhour=cumhour+1
            plt.scatter(
                Monthly_t, 
                Monthly_g, 
                c = colour if filter_applied else Colour_list[11-month], 
                label = '' if filter_applied else (Month_list[month-1]),
                s=6, 
                alpha=0.9
            )
            Monthly_t.clear()
            Monthly_g.clear()

    plt.ylim(0,0.03)
    plt.xlim(-10,60)
    plt.xlabel('Dry bulb temperature, $^o$C')
    plt.ylabel('Moisture content, kg/kg (dry air)')

    plt.axvline(x=60, color='lightgrey')
    #plt.axis('off')
    fig_title = 'Hourly climate data plotted on a psychrometric chart (raw weather data, not transformed)'
    plt.title(fig_title, loc='center')    
    plt.legend(loc = 'upper left', frameon=False)

    # plt.show()
    st.pyplot(fig)
    st.write(ui.generate_fig_dl_link(fig, fig_title), unsafe_allow_html=True)

    if PlotEvapCool == True:
        
        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        #RE-CREATE THE PSYCHROMETRIC CHART AND PLOT EVAP-COOLED DATA
        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

        fig = plt.figure(figsize=(12, 8), tight_layout=True)
        
        temp_x_list = []
        g_y_list = []
        for rh in range (10,110,10):
            for temp in range (-10,61):
                temp_x_list.append(temp)
                g_y_list.append(g(temp,rh))
            plt.plot(temp_x_list,g_y_list, lw=1, color='darkgray')
            temp_x_list.clear()
            g_y_list.clear()
        
        mc=0
        while mc<=0.03:
            mc=mc+0.005
            temp_x_list.append(tsat(mc))
            g_y_list.append(mc)
            temp_x_list.append(60)
            g_y_list.append(mc)
            plt.plot(temp_x_list,g_y_list, lw=1, color='darkgray')
            temp_x_list.clear()
            g_y_list.clear()
        
        for temp in range(-10,60,5):
            gsat=g_dry_wet(temp,temp)
            if gsat>=0.3:
                gsat=0.3
            temp_x_list.append(temp)
            g_y_list.append(0)
            temp_x_list.append(temp)
            g_y_list.append(gsat)
            plt.plot(temp_x_list,g_y_list, lw=1, color='darkgray')
            temp_x_list.clear()
            g_y_list.clear()
        
        for wbt in range (-10,40,5):
            for dbt in range (-10, 61, 1):
                mc = g_dry_wet(dbt,wbt)
                if dbt>=wbt:
                    temp_x_list.append(dbt)
                    g_y_list.append(mc)
            plt.plot(temp_x_list,g_y_list, lw=1, color='darkgray')
            temp_x_list.clear()
            g_y_list.clear()
        
        shifted_temp_list = []
        shifted_g_list = []
        
        for plotpoints in range (0,len(temp_list)):
            g_list.append(g(temp_list[plotpoints],rh_list[plotpoints]))
            tdry = temp_list[plotpoints]
            twet = twetrh(temp_list[plotpoints], rh_list[plotpoints], Screen)
            wbtd = tdry-twet
            
            if MartinezLimit==True:
                LLdbt = 29 + g_list[plotpoints] / -0.0055 #where -0.0055 = dy/dx of PDEC line
            
            if tdry>=LLdbt:
                tdry = tdry - (EvapCoolEff * wbtd)
                shifted_temp_list.append(tdry)
                shifted_g_list.append(g_dry_wet(tdry,twet))
            else:
                shifted_temp_list.append(temp_list[plotpoints])
                shifted_g_list.append(g_list[plotpoints])
        plt.scatter(shifted_temp_list, shifted_g_list, c='red', alpha=0.5, s=5)
        
        plt.ylim(0,0.03)
        plt.xlim(-10,60)
        plt.xlabel('Dry bulb temperature, $^o$C')
        plt.ylabel('Moisture content, kg/kg (dry air)')
        
        plt.axvline(x=60, color='lightgrey')
        #plt.axis('off')
        fig_title = 'Hourly climate data plotted on a psychrometric chart (data transformed to emulate direct evaporative cooling)'
        plt.title(fig_title, loc='center')
        
        # plt.show()
        st.pyplot(fig)

        st.write(ui.generate_fig_dl_link(fig, fig_title), unsafe_allow_html=True)
