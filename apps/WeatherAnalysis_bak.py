##########################################################################################
# PyClim was developed by Prof. Darren Robinson (University of Sheffield, 2019).         #
# PyClim produces a range of graphs and statistics to support the analysis of climate    #
# data, to support architectural / engineering / technology students to develop their    #
# early-stage bioclimatic design concepts.                                               #
##########################################################################################

#This module creates a series of graphics / statistics: 1) temporal solar irradiance / 
#maps, 2) violin plots of key synoptic variables, 3) Monthly degree-day bar charts,
#4) inverse illuminance cumulative distribution function: determines light switch-off hours,
#5) wind speed / temperature frequency histograms, 6) ground temperature profile. 

#imports the basic libraries
from apps.ClimAnalFunctions import * 

def app(app, epw, ui, timeshift=timeshift):
    st.write("# "+app['title'])

    globaleff = False
    daynum_list = []
    dailymeantemp_list = []
    temp_matrix = []
    windspeed_matrix = []
    tground_matrix=[]
    depth_list = []
    Colour_list = []
    Diurnal_matrix = []
    rh_matrix = []
    SRtime_list = []
    SStime_list = []
    illuminance_list = []

    HDDbase = st.sidebar.slider("Heating Degree-day Base Temperature", 10.0, 18.0, 15.5, 0.5, help="Temperature below which heating is needed")
    CDDbase = st.sidebar.slider("Cooling Degree-day Base Temperature", 14.0, 22.0, 18.0, 0.5, help="Temperature above which cooling is needed")

    #Tground parameters
    Conductivity = st.sidebar.number_input("Soil Conductivity (W/(m.K))", 0.1, 3.0, 1.21, help="Soil conductivity (W/(m.K)): ground temperature profile")
    Density = st.sidebar.number_input("Soil Density (kg/m\u00b3)", 1000, 3000, 1960, help="Soil density (kg/m\u00b3): ground temperature profile")
    Cp = st.sidebar.number_input("Soil Specific Heat Capacity (J/(kg.K))", 500, 2000, 840, help="Soil specific heat capacity (J/(kg.K)): ground temperature profile")

    Rho=1.2 #kg/m3
    WindKineticEnergy=0
    AnnualIgh=0
    DiffuseFraction=0

    lat = epw.lat * pi / 180
    # file_format = ui.format_selector()
    
    rh_list = epw.dataframe['Relative Humidity'].to_numpy()
    temp_list = epw.dataframe['Dry Bulb Temperature'].to_numpy()
    global_list = epw.dataframe['Global Horizontal Radiation'].to_numpy()
    diffuse_list = epw.dataframe['Diffuse Horizontal Radiation'].to_numpy()
    windspeed_list = epw.dataframe['Wind Speed'].to_numpy()

    daynum_list = [31,28,31,30,31,30,31,31,30,31,30,31] 
    AnnualIgh = sum(global_list)/1000
    DiffuseFraction = sum(diffuse_list)/sum(global_list)

    day_list = np.array(range(1,366))
    dec_list = declin_angle2(day_list)
    SStime, SRtime = sunrise_time2(dec_list, lat, day_list)
    dT = time_diff2(day_list,True,epw.longitude,epw.timezone,timeshift)
    SStime_list = np.append(SStime_list, np.minimum(24,SStime+dT))
    SRtime_list = np.append(SRtime_list, np.maximum(1,SRtime+dT))

    day_list_repeat = np.repeat(day_list, 24)
    dec_list_repeat = np.repeat(dec_list, 24)
    k = np.tile(np.array(range(1,25)), 365)
    dT_repeat = np.repeat(dT, 24)
    solalt = solar_altitude2(day_list_repeat, k + dT_repeat, lat, dec_list_repeat)



    # begin_time = datetime.datetime.now()
    # def conditions_ibn(solalt, global_list, diffuse_list):
    #     if (solalt > 0) and (global_list > 0):
    #         return (global_list - diffuse_list)/np.sin(solalt)
    #     else:
    #         return 0

    # func_ibn = np.vectorize(conditions_ibn)

    # ibn = func_ibn(solalt, global_list, diffuse_list)
    # st.write(datetime.datetime.now() - begin_time)
    
    # begin_time = datetime.datetime.now()

    ibn = np.where(
        np.all([(solalt>0), (global_list>0)], axis=0), 
        (global_list - diffuse_list)/np.sin(solalt),
        0
    )
    # st.write(datetime.datetime.now() - begin_time)

    # if solalt>0 and global_list[24*(cumday-1)+k-1]>0:
    #     ibn = (global_list[24*(cumday-1)+k-1] - diffuse_list[24*(cumday-1)+k-1])/math.sin(solalt)
    #     if globaleff==True and diffuse_list[24*(cumday-1)+k-1]>0:
    #         illuminance = global_list[24*(cumday-1)+k-1]*LumEff(globaleff,cumday,solalt,diffuse_list[24*(cumday-1)+k-1],ibn)
    #     elif globaleff==False and diffuse_list[24*(cumday-1)+k-1]>0:
    #         illuminance = diffuse_list[24*(cumday-1)+k-1]*LumEff(globaleff,cumday,solalt,diffuse_list[24*(cumday-1)+k-1],ibn)
    # begin_time = datetime.datetime.now()

    def conditions_illuminance(global_list, globaleff, day_list_repeat, solalt, diffuse_list, ibn):
        if (solalt > 0) and (global_list > 0):
            if globaleff==True and diffuse_list>0:
                return global_list*LumEff(globaleff,day_list_repeat,solalt,diffuse_list,ibn)
            elif globaleff==False and diffuse_list>0:
                return diffuse_list*LumEff(globaleff,day_list_repeat,solalt,diffuse_list,ibn)
        return 0

    func_illuminance = np.vectorize(conditions_illuminance)

    illuminance = func_illuminance(global_list, globaleff, day_list_repeat, solalt, diffuse_list, ibn)
    # st.write(datetime.datetime.now() - begin_time)
    # begin_time = datetime.datetime.now()

    # illuminance = np.where(
    #     np.all([(solalt>0), (global_list>0)], axis=0), 
    #     np.where(
    #         np.all([(globaleff == True), (diffuse_list>0)], axis=0),
    #         global_list * LumEff2(globaleff, day_list_repeat, solalt, diffuse_list, ibn), 
    #         np.where(
    #             np.all([(globaleff == False), (diffuse_list>0)], axis=0),
    #             diffuse_list * LumEff2(globaleff, day_list_repeat, solalt, diffuse_list, ibn),
    #             0
    #         )
    #     ),
    #     0
    # )
    # st.write(datetime.datetime.now() - begin_time)

    illuminance_list = illuminance*10**-3

    WindKineticEnergy = np.sum(0.5*Rho*windspeed_list**3/1000)
    annualmeantemp = np.sum(temp_list/len(temp_list))

    MonthlyHDD_list = [0 for i in range(0,12)]
    MonthlyCDD_list = [0 for i in range(0,12)]
    TotalHDD = 0
    TotalCDD = 0

    prev = 0
    for i in range(1,13):
        limit = 24*daynum_list[i-1]+prev

        temp_matrix.append(temp_list[prev:limit])
        windspeed_matrix.append(windspeed_list[prev:limit])
        rh_matrix.append(rh_list[prev:limit])

        prev = limit

        daytempprofile = epw.dataframe[epw.dataframe['Month'] == i].groupby(['Day'])
        Diurnal_matrix.append((daytempprofile['Dry Bulb Temperature'].max() - daytempprofile['Dry Bulb Temperature'].min()).values.tolist())
        daymeantemp = daytempprofile['Dry Bulb Temperature'].mean()
        MonthlyCDD_list[i-1] = np.sum(np.where(daymeantemp > CDDbase, (daymeantemp - CDDbase), 0))
        TotalCDD += np.sum(np.where(daymeantemp > CDDbase, (daymeantemp - CDDbase), 0))
        MonthlyHDD_list[i-1] = np.sum(np.where(daymeantemp < HDDbase, (HDDbase - daymeantemp), 0))
        TotalHDD += np.sum(np.where(daymeantemp < HDDbase, (HDDbase - daymeantemp), 0))
        dailymeantemp_list = np.append(dailymeantemp_list, daymeantemp)
    
    #This part calculates ground temperature profiles. 
    maxmeandaytemp = max(dailymeantemp_list)
    minmeandaytemp = min(dailymeantemp_list)
    t_offset = np.where(dailymeantemp_list == minmeandaytemp)[0]+1
    # dailymeantemp_list = list(dailymeantemp_list)
    # t_offset = dailymeantemp_list.index(minmeandaytemp)+1
    amplitude = 0.5 * (maxmeandaytemp - minmeandaytemp)
    cum_monthmeandaynum = 0
    for i in range(1,13):
        tground_matrix.append([])
        cum_monthmeandaynum = cum_monthmeandaynum + daynum_list[i-1]
        # st.write(cum_monthmeandaynum)
        for depth in range (0,21):
            #need to populate a 2D list here with temps for month and depth
            #t_mean,t_swing,t_month,t_ref,depth
            tground_matrix[i-1].append(Tground(annualmeantemp,amplitude,cum_monthmeandaynum - daynum_list[i-1]/2,t_offset,depth, Conductivity, Density, Cp))
            if i==1:
                depth_list.append(depth)
    




    # globaleff = False
    # daynum_list = []
    # # temp_list = []
    # dailymeantemp_list = []
    # # rh_list = []
    # # global_list = []
    # # diffuse_list = []
    # # winspeed_list= []
    # # windir_list = []
    # temp_matrix = []
    # winspeed_matrix = []
    # tground_matrix=[]
    # depth_list = []
    # Colour_list = []
    # # Month_list=[]
    # daytempprofile = []
    # Diurnal_matrix = []
    # rh_matrix = []
    # SRtime_list = []
    # SStime_list = []
    # day_list = []
    # dec_list = []
    # illuminance_list = []

    # MonthlyHDD_list = []
    # MonthlyCDD_list = []
    # HDDbase = st.sidebar.slider("Heating Degree-day Base Temperature", 10.0, 18.0, 15.5, 0.5, help="Temperature below which heating is needed")
    # CDDbase = st.sidebar.slider("Cooling Degree-day Base Temperature", 14.0, 22.0, 18.0, 0.5, help="Temperature above which cooling is needed")

    # #Tground parameters
    # Conductivity = st.sidebar.number_input("Soil Conductivity (W/(m.K))", 0.1, 3.0, 1.21, help="Soil conductivity (W/(m.K)): ground temperature profile")
    # Density = st.sidebar.number_input("Soil Density (kg/m\u00b3)", 1000, 3000, 1960, help="Soil density (kg/m\u00b3): ground temperature profile")
    # Cp = st.sidebar.number_input("Soil Specific Heat Capacity (J/(kg.K))", 500, 2000, 840, help="Soil specific heat capacity (J/(kg.K)): ground temperature profile")
    # TotalHDD=0
    # TotalCDD=0
    # Rho=1.2 #kg/m3
    # WindKineticEnergy=0
    # AnnualIgh=0
    # DiffuseFraction=0

    # lat = epw.lat * pi / 180

    # temp_list = epw.dataframe['Dry Bulb Temperature'].values.tolist()
    # rh_list = epw.dataframe['Relative Humidity'].values.tolist()
    # global_list = epw.dataframe['Global Horizontal Radiation'].values.tolist()
    # diffuse_list = epw.dataframe['Diffuse Horizontal Radiation'].values.tolist()
    # winspeed_list = epw.dataframe['Wind Speed'].values.tolist()
    # # windir_list = epw.dataframe['Wind Direction'].values.tolist()

    # daynum_list = [31,28,31,30,31,30,31,31,30,31,30,31] 
    # AnnualIgh = sum(global_list)/1000
    # DiffuseFraction = sum(diffuse_list)/sum(global_list)

    # cumday=0
    # annualmeantemp=0
    # # meandaytemp=0
    # MonthlyHDD_list = [0 for i in range(0,12)]
    # MonthlyCDD_list = [0 for i in range(0,12)]
    
    
    # # temp_matrix2 = []
    # # winspeed_matrix2 = []
    # prev = 0
    # for i in range(1,13):
    #     limit = 24*daynum_list[i-1]+prev
    #     temp_matrix.append(temp_list[prev:limit])
    #     winspeed_matrix.append(winspeed_list[prev:limit])
    #     rh_matrix.append(rh_list[prev:limit])
    #     prev = limit
    
    # for i in range(1,13):
    #     # temp_matrix.append([])
    #     # winspeed_matrix.append([])
    #     Diurnal_matrix.append([])
    #     # rh_matrix.append([])
    #     for j in range(1,daynum_list[i-1]+1):
    #         cumday=cumday+1
    #         daymeantemp=0
    #         day_list.append(cumday)
    #         dec_list.append(declin_angle(cumday))
    #         SStime, SRtime = sunrise_time(dec_list[cumday-1],lat,cumday)
    #         dT = time_diff(cumday,True,epw.longitude,epw.timezone,timeshift)
    #         SStime_list.append(min(24,SStime+dT))
    #         SRtime_list.append(max(1,SRtime+dT))
    #         for k in range(1,25):
    #             # temp_matrix[i-1].append(temp_list[24*(cumday-1)+k-1])
    #             # winspeed_matrix[i-1].append(winspeed_list[24*(cumday-1)+k-1])
    #             # rh_matrix[i-1].append(rh_list[24*(cumday-1)+k-1])
    #             WindKineticEnergy=WindKineticEnergy+0.5*Rho*winspeed_list[24*(cumday-1)+k-1]**3/1000
    #             #Accrue monthly degree days
    #             #annual mean temp for ground temperature model
    #             annualmeantemp=annualmeantemp+temp_list[24*(cumday-1)+k-1]/len(temp_list)
    #             daymeantemp = daymeantemp + temp_list[24*(cumday-1)+k-1]/24
    #             daytempprofile.append(temp_list[24*(cumday-1)+k-1])
    #             #This populates an hour list of iluminance, for an iluminance availability plot
    #             ibn=0
    #             illuminance=0
    #             solalt = solar_altitude(cumday,k + dT,lat,dec_list[cumday-1])
    #             if solalt>0 and global_list[24*(cumday-1)+k-1]>0:
    #                 ibn = (global_list[24*(cumday-1)+k-1] - diffuse_list[24*(cumday-1)+k-1])/math.sin(solalt)
    #                 if globaleff==True and diffuse_list[24*(cumday-1)+k-1]>0:
    #                     illuminance = global_list[24*(cumday-1)+k-1]*LumEff(globaleff,cumday,solalt,diffuse_list[24*(cumday-1)+k-1],ibn)
    #                 elif globaleff==False and diffuse_list[24*(cumday-1)+k-1]>0:
    #                     illuminance = diffuse_list[24*(cumday-1)+k-1]*LumEff(globaleff,cumday,solalt,diffuse_list[24*(cumday-1)+k-1],ibn)
    #             illuminance_list.append(illuminance*10**-3)
    #         if daymeantemp > CDDbase:
    #             MonthlyCDD_list[i-1] = MonthlyCDD_list[i-1] + (daymeantemp - CDDbase)
    #             TotalCDD = TotalCDD + (daymeantemp - CDDbase)
    #         if daymeantemp < HDDbase:
    #             MonthlyHDD_list[i-1] = MonthlyHDD_list[i-1] + (HDDbase - daymeantemp)
    #             TotalHDD = TotalHDD + (HDDbase - daymeantemp)
    #         dailymeantemp_list.append(daymeantemp)
    #         Diurnal_matrix[i-1].append(max(daytempprofile)-min(daytempprofile))
    #         daytempprofile.clear()

    # #This part calculates ground temperature profiles. 
    # maxmeandaytemp=max(dailymeantemp_list)
    # minmeandaytemp=min(dailymeantemp_list)
    # t_offset = dailymeantemp_list.index(minmeandaytemp)+1
    # amplitude=0.5*(maxmeandaytemp-minmeandaytemp)

    # cum_monthmeandaynum=0
    # for i in range(1,13):
    #     tground_matrix.append([])
    #     cum_monthmeandaynum=cum_monthmeandaynum+daynum_list[i-1]
    #     for depth in range (0,21):
    #         #need to populate a 2D list here with temps for month and depth
    #         #t_mean,t_swing,t_month,t_ref,depth
    #         tground_matrix[i-1].append(Tground(annualmeantemp,amplitude,cum_monthmeandaynum - daynum_list[i-1]/2,t_offset,depth, Conductivity, Density, Cp))
    #         if i==1:
    #             depth_list.append(depth)





    #PRINT SUMMARY STATISTICS
    st.write('Annual global horizontal solar irradiation: {0:1.2f}' .format(AnnualIgh)  + ', kWh/m\u00b2')
    st.write('Annual solar diffuse fraction: {0:1.3f}' .format(DiffuseFraction))
    st.write('Total annual wind kinetic energy flux: {0:1.2f}' .format(WindKineticEnergy) + ', kWh/m\u00b2')
    st.write('Total annual heating degree-days: {0:1.0f}' .format(TotalHDD))
    st.write('Total annual cooling degree-days: {0:1.0f}' .format(TotalCDD))

    Colour_list = ['firebrick', 'salmon', 'darkorange', 'orange', 'gold', 'yellow', 'yellowgreen', 'green', 'olive', 'cyan', 'skyblue', 'blue']
    Month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    fig = plt.figure(figsize=(12, 6))

    for month in range (1,13):
        #plt.scatter(tground_matrix[month-1], depth_list, c=Colour_list[month-1], s=20)
        plt.plot(tground_matrix[month-1], depth_list, lw=2, c=Colour_list[11-(month-1)])
    fig_title = "Ground temperature profile"
    plt.title(fig_title)
    plt.xlabel('temperature, ' + '$^o$C')
    plt.ylabel('depth below surface, m')

    plt.ylim(0,20)
    plt.ylim(plt.ylim()[::-1])

    plt.legend(Month_list)
    # plt.show()
    st.pyplot(fig)
    # st.write(ui.generate_fig_dl_link(fig, fig_title), unsafe_allow_html=True)
    # st.write(ui.generate_dl_link(fig, fig_title, file_format), unsafe_allow_html=True)


    tground_matrix.clear()
    depth_list.clear()
    

    #this plots histograms:
    fig, ax = plt.subplots(1,1, figsize = (12,6), tight_layout=True)
    #plots a standard frequency distribution   

    # xrange=int(max(temp_list))-int(min(temp_list))
    xrange=int(max(windspeed_list)-int(min(windspeed_list)))
    
    ax.hist(temp_list, xrange, alpha=0.3, histtype='step', color='darkgray', lw=3)

    #creates a y2 axis for the cumulative distribution
    ax2 = ax.twinx()
    ax2.hist(temp_list, bins = xrange, cumulative=True, alpha=1, histtype='step', color='red', lw=3)
    ax2.hist(temp_list, bins = xrange, cumulative=-1, alpha=1, histtype='step', color='blue', lw=3)

    fig_title = "temperature frequency histogram"
    ax.set_title(fig_title)
    ax.set_xlabel('temperature bins,' + '$^o$C')
    ax.set_ylabel('counts [grey]')
    ax2.set_ylabel('cumulative counts [red / blue]')

    # plt.show()
    st.pyplot(fig)
    # st.write(ui.generate_fig_dl_link(fig, fig_title), unsafe_allow_html=True)
    # st.write(ui.generate_dl_link(fig, fig_title, file_format), unsafe_allow_html=True)

    # temp_list.clear()

    fig, ax = plt.subplots(1,1, figsize = (12,6), tight_layout=True)
    
    #plots a standard frequency distribution
    xrange=int(max(windspeed_list)-int(min(windspeed_list)))
    ax.hist(windspeed_list, xrange, alpha=0.3, histtype='step', color='darkgray', lw=3)
    #creates a y2 axis for the cumulative distribution
    ax2 = ax.twinx() 
    ax2.hist(windspeed_list, bins = xrange, cumulative=True, alpha=1, histtype='step', color='red', lw=3)
    #ax2.hist(windspeed_list, bins = xrange, cumulative=-1, alpha=1, histtype='step', color='blue', lw=3)

    fig_title = "wind speed frequency histogram"
    ax.set_title(fig_title)
    ax.set_xlabel('wind speed bins, m/s')
    ax.set_ylabel('counts [grey]')
    ax2.set_ylabel('cumulative counts [red]')

    # plt.show()
    st.pyplot(fig)
    # st.write(ui.generate_fig_dl_link(fig, fig_title), unsafe_allow_html=True)
    # st.write(ui.generate_dl_link(fig, fig_title, file_format), unsafe_allow_html=True)

    # windspeed_list.clear()

    #plots a decrementing illuminance histogram
    fig,ax = plt.subplots(1,1, figsize = (12,6), tight_layout=True)
    xrange=int((max(illuminance_list)-int(min(illuminance_list))))
    ax.hist(illuminance_list, xrange, alpha=1, histtype='stepfilled', color='red', cumulative=-1, range = [1,max(illuminance_list)])
    fig_title = "inverse cumulative illuminance frequency histogram"
    ax.set_title(fig_title)
    ax.set_xlabel('illuminance bins, klux')
    ax.set_ylabel('cumulative counts')

    # plt.show()
    st.pyplot(fig)
    # st.write(ui.generate_fig_dl_link(fig, fig_title), unsafe_allow_html=True)
    # st.write(ui.generate_dl_link(fig, fig_title, file_format), unsafe_allow_html=True)



    #plots a degree-day histograms

    fig,ax = plt.subplots(1, 1, figsize = (12,6), tight_layout=True)
    xlist = np.linspace(1, 12, 12)
    y1 = ax.bar(xlist, MonthlyHDD_list, alpha=1, color='red')
    y2 = ax.bar(xlist, MonthlyCDD_list, alpha=1, color='blue')
    
    fig_title = "Monthly degree-days"
    ax.set_title(fig_title)
    ax.set_xlabel('Time, months')
    ax.set_ylabel('Monthly degree days')
    plt.legend((y1[0],y2[0]), ('Heating', 'Cooling'), loc='best')
    # plt.show()
    st.pyplot(fig)
    # st.write(ui.generate_fig_dl_link(fig, fig_title), unsafe_allow_html=True)
    # st.write(ui.generate_dl_link(fig, fig_title, file_format), unsafe_allow_html=True)


    #this plots violin plots:
    fig,axes = plt.subplots(2,2, figsize = (12,6))

    temp_data_to_plot = [temp_matrix[0], temp_matrix[1], temp_matrix[2], temp_matrix[3], temp_matrix[4], temp_matrix[5], temp_matrix[6], temp_matrix[7], temp_matrix[8], temp_matrix[9], temp_matrix[10], temp_matrix[11]]
    axes[0,0].violinplot(temp_data_to_plot)
    axes[0,0].set_title('Temperature Violin Plot')
    axes[0,0].set_xlabel('Time, months')
    axes[0,0].set_ylabel('Temperature, ' + '$^o$C')

    rh_data_to_plot = [rh_matrix[0], rh_matrix[1], rh_matrix[2], rh_matrix[3], rh_matrix[4], rh_matrix[5], rh_matrix[6], rh_matrix[7], rh_matrix[8], rh_matrix[9], rh_matrix[10], rh_matrix[11]]
    axes[0,1].violinplot(rh_data_to_plot)
    axes[0,1].set_title('Relative Humidity Violin Plot')
    axes[0,1].set_xlabel('Time, months')
    axes[0,1].set_ylabel('Relative Humidity, %')

    diurnal_data_to_plot = [Diurnal_matrix[0], Diurnal_matrix[1], Diurnal_matrix[2], Diurnal_matrix[3], Diurnal_matrix[4], Diurnal_matrix[5], Diurnal_matrix[6], Diurnal_matrix[7], Diurnal_matrix[8], Diurnal_matrix[9], Diurnal_matrix[10], Diurnal_matrix[11]]
    axes[1,0].violinplot(diurnal_data_to_plot)
    axes[1,0].set_title('Diurnal Temperature Violin Plot')
    axes[1,0].set_xlabel('Time, months')
    axes[1,0].set_ylabel('Temperature, ' + '$^o$C')

    winspeed_data_to_plot = [windspeed_matrix[0], windspeed_matrix[1], windspeed_matrix[2], windspeed_matrix[3], windspeed_matrix[4], windspeed_matrix[5], windspeed_matrix[6], windspeed_matrix[7], windspeed_matrix[8], windspeed_matrix[9], windspeed_matrix[10], windspeed_matrix[11]]
    axes[1,1].violinplot(winspeed_data_to_plot)
    axes[1,1].set_title('Wind Speed Violin Plot')
    axes[1,1].set_xlabel('Time, months')
    axes[1,1].set_ylabel('Wind Speed, m/s')

    fig.tight_layout()
    # plt.show()
    st.pyplot(fig)
    fig_title = 'Violin Plots'
    # st.write(ui.generate_fig_dl_link(fig, fig_title), unsafe_allow_html=True)
    # st.write(ui.generate_dl_link(fig, fig_title, file_format), unsafe_allow_html=True)


    temp_matrix.clear()
    windspeed_matrix.clear()
    Diurnal_matrix.clear()
    rh_matrix.clear()


    #This creates a 2D solar availability surface plot
    #NOTE: the chart is asymmetric because of the hour-centred convention.
    xlist = np.linspace(0, 23, 24)
    ylist = np.linspace(1, 365, 365)
    X, Y = np.meshgrid(xlist, ylist)
    fig,ax=plt.subplots(1,1, figsize=(12,6))
    #this part converts the list into an array and reshapes it, to match the x,y dimensions
    Z = np.array(global_list)
    Z = Z.reshape(365,24)
    cp = ax.contourf(Y, X, Z, 16, cmap='jet') #'plasma', 'jet' and 'viridis' are also good cmaps
    fig.colorbar(cp, label = 'Global horizontal solar irradiance, W/m\u00b2') # Adds a colorbar
    
    fig_title = 'Solar Availability Surface Plot'
    ax.set_title(fig_title)
    ax.set_xlabel('Time, days')
    ax.set_ylabel('Time, hours')

    plt.plot(day_list, SRtime_list,c='red')
    plt.plot(day_list, SStime_list,c='red')    
    # plt.show()
    st.pyplot(fig)
    # st.write(ui.generate_fig_dl_link(fig, fig_title), unsafe_allow_html=True)
    # st.write(ui.generate_dl_link(fig, fig_title, file_format), unsafe_allow_html=True)

    
    # global_list.clear()


    #This creates a 2D daylight availability surface plot
    #NOTE: the chart is asymmetric because of the hour-centred convention.
    xlist = np.linspace(0, 23, 24)
    ylist = np.linspace(1, 365, 365)
    X, Y = np.meshgrid(xlist, ylist)
    fig,ax=plt.subplots(1,1, figsize=(12,6))
    #this part converts the list into an array and reshapes it, to match the x,y dimensions
    Z = np.array(illuminance_list)
    Z = Z.reshape(365,24)
    cp = ax.contourf(Y, X, Z, 16, cmap='jet') #'plasma', 'jet' and 'viridis' are also good cmaps
    if globaleff==False:
        fig.colorbar(cp, label = 'diffuse horizontal illuminance, kLux') # Adds a colorbar
    else:
        fig.colorbar(cp, label = 'global horizontal illuminance, kLux') # Adds a colorbar
    fig_title = 'Daylight Availability Surface Plot'
    ax.set_title(fig_title)
    ax.set_xlabel('Time, days')
    ax.set_ylabel('Time, hours')

    plt.plot(day_list, SRtime_list,c='red')
    plt.plot(day_list, SStime_list,c='red')    
    # plt.show()
    st.pyplot(fig)
    # st.write(ui.generate_fig_dl_link(fig, fig_title), unsafe_allow_html=True)
    # st.write(ui.generate_dl_link(fig, fig_title, file_format), unsafe_allow_html=True)
    # illuminance_list.clear()