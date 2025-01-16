##########################################################################################
# PyClim was developed by Prof. Darren Robinson (University of Sheffield, 2019).         #
# PyClim produces a range of graphs and statistics to support the analysis of climate    #
# data, to support architectural / engineering / technology students to develop their    #
# early-stage bioclimatic design concepts.                                               #
##########################################################################################

# This module creates a stereographic sunpath diagram,given a user-defined latitude, and
# specification of solar or clock time. It can also create shading protractors.

# imports the basic libraries
import math

import matplotlib.pyplot as plt
import streamlit as st
from ClimAnalFunctions import (declin_angle, solar_altitude, solar_azimuth,
                               sunrise_time, time_diff)

pi = math.pi

def app(app, epw, ui):
    st.write("# " + app['title'])

    with st.sidebar.form(key='sunpath_lat'):
        lat = st.number_input('Latitude', -90.0, 90.0, epw.lat)
        st.form_submit_button(label='Apply Change')

    AzimuthIncrement = st.sidebar.slider('Azimuth Increment', 1, 45, 10)
    HorizontalProtractor = st.sidebar.checkbox("Horizontal Protractor", value=False)
    VerticalProtractor = st.sidebar.checkbox("Vertical Protractor", value=False)
    ClockTime = st.sidebar.checkbox("Clock Time", value=False)

    with st.sidebar.form(key='sunpath_wallaz'):
        WallAzimuth = st.number_input('Wall Azimuth', 0, 359, 185)
        st.form_submit_button(label='Apply Change')

    lat = lat * pi / 180
    EqTonly = True
    Hemisphere = "S" if lat < 0 else "N"
    # working backwards from the winter solstice
    SunpathDay_list = [355, 325, 294, 264, 233, 202, 172, 141, 111, 80, 52, 21]
    Colour_list = ['firebrick', 'darkorange', 'orange', 'gold', 'green', 'cyan', 'blue']
    Month_list = ['Dec', 'Nov/Jan', 'Oct/Feb', 'Sep/Mar', 'Aug/Apr', 'Jul/May', 'Jun']

    #######################################
    # THIS PLOTS THE ISO-ALTITUDE CIRCLES AND RADIAL AZIMUTH LINES
    #######################################

    fig_sun, ax_sun = plt.subplots(1, 1, figsize=(9, 9), tight_layout=True)

    for circle in range(90, 0, -10):
        circles_x = []
        circles_y = []
        spokes_x = []
        spokes_y = []
        for orientation in range(0, 360 + AzimuthIncrement, AzimuthIncrement):
            circles_x.append(circle * math.sin(orientation * pi / 180))
            circles_y.append(circle * math.cos(orientation * pi / 180))
            if circle == 80:
                spokes_x.append(90 * math.sin(orientation * pi / 180))
                spokes_y.append(90 * math.cos(orientation * pi / 180))
                spokes_x.append(0 * math.sin(orientation * pi / 180))
                spokes_y.append(0 * math.cos(orientation * pi / 180))
            if circle == 90 and orientation < 360:
                ax_sun.text(95 * math.sin(orientation * pi / 180), 95 * math.cos(orientation * pi / 180),
                            str(orientation) + '$^o$', c='darkgray', horizontalalignment='center', fontsize=8)
        if circle < 90 and circle != 0:
            ax_sun.text((circle + 1) * math.sin(5 * pi / 180), (circle + 1) * math.cos(orientation * pi / 180),
                        str(90 - circle) + '$^o$', c='darkgray', horizontalalignment='center', fontsize=8)

        ax_sun.plot(circles_x, circles_y, lw=1, color='darkgray')
        ax_sun.plot(spokes_x, spokes_y, lw=1, color='darkgray')

    for month in range(1, 8):
        azi_list = []
        alt_list = []
        sunpath_x = []
        sunpath_y = []

        position = 0
        day = SunpathDay_list[month - 1]
        dec = declin_angle(day)
        ss, sr = sunrise_time(dec, lat, day)

        if ss < 24:
            # in this case we need to plot from the non-integer sunrise time, through to sunset
            alt_list.append(solar_altitude(day, sr, lat, dec) * 180 / pi)
            azi_list.append(solar_azimuth(day, sr, lat, alt_list[0] * pi / 180, dec))
            sunpath_x.append((90 - alt_list[0]) * math.sin(azi_list[0]))
            sunpath_y.append((90 - alt_list[0]) * math.cos(azi_list[0]))

            for hour in range(math.ceil(sr), int(sr) + 2 * (12 - int(sr))):
                position += 1
                alt_list.append(solar_altitude(day, hour, lat, dec) * 180 / pi)
                azi_list.append(solar_azimuth(day, hour, lat, alt_list[position] * pi / 180, dec))
                sunpath_x.append((90 - alt_list[position]) * math.sin(azi_list[position]))
                sunpath_y.append((90 - alt_list[position]) * math.cos(azi_list[position]))

            alt_list.append(solar_altitude(day, ss, lat, dec) * 180 / pi)
            azi_list.append(solar_azimuth(day, ss, lat, solar_altitude(day, ss, lat, dec) * pi / 180, dec))
            sunpath_x.append(90 * math.sin(azi_list[position + 1]))
            sunpath_y.append(90 * math.cos(azi_list[position + 1]))
        else:
            # in this case we simply need to plot for the entire 24h period
            for hour in range(0, 25):
                alt_list.append(solar_altitude(day, hour, lat, dec) * 180 / pi)
                azi_list.append(solar_azimuth(day, hour, lat, alt_list[position] * pi / 180, dec))
                sunpath_x.append((90 - alt_list[position]) * math.sin(azi_list[position]))
                sunpath_y.append((90 - alt_list[position]) * math.cos(azi_list[position]))
                position += 1

        ax_sun.plot(sunpath_x, sunpath_y, c=Colour_list[7 - month], label=(Month_list[month - 1]), marker='o')

    for hour in range(0, 25):
        time_curve_x = []
        time_curve_y = []
        for day in range(1, 366):
            # if the sun is below the horizon during the summer solstice for this hour then skip
            summerday = 172 if Hemisphere == "N" else 355
            if solar_altitude(summerday, hour, lat, declin_angle(summerday)) > 0:
                # this controls whether solar time curves of the analemma are plotted
                EqT = time_diff(day, EqTonly, 0, 0, 0) if ClockTime else 0
                Dec = declin_angle(day)
                Solalt = solar_altitude(day, hour + EqT, lat, Dec)
                if Solalt > 0:
                    Solaz = solar_azimuth(day, hour + EqT, lat, Solalt, Dec)
                    time_curve_x.append((90 - (Solalt * 180 / pi)) * math.sin(Solaz))
                    time_curve_y.append((90 - (Solalt * 180 / pi)) * math.cos(Solaz))
        ax_sun.plot(time_curve_x, time_curve_y, c='darkblue')

    # WEIRD PROBLEM: EQT FOR FIRST HOUR IN (ANT)ARCTIC CIRCLE ISN'T CORRECT (IT MIRRORS ABOUT THE HALF YEAR).

    #######################################
    # THIS PLOTS THE SHADING PROTRACTORS
    #######################################

    if HorizontalProtractor:
        for Theta in range(10, 90, 10):
            HorizontalProtractor_x = []
            HorizontalProtractor_y = []
            for h_orientation in range(WallAzimuth - 90, WallAzimuth + 100, 10):
                ThetaAdjusted = math.atan(
                    math.tan(Theta * pi / 180) * math.cos(math.fabs(h_orientation - WallAzimuth) * pi / 180)) * 180 / pi
                HorizontalProtractor_x.append((90 - ThetaAdjusted) * math.sin(h_orientation * pi / 180))
                HorizontalProtractor_y.append((90 - ThetaAdjusted) * math.cos(h_orientation * pi / 180))
            ax_sun.plot(HorizontalProtractor_x, HorizontalProtractor_y, c='darkorange', lw=2, linestyle=':')

    if VerticalProtractor:
        for v_orientation in range(WallAzimuth - 90, WallAzimuth + 100, 10):
            VerticalProtractor_x = []
            VerticalProtractor_y = []
            VerticalProtractor_x.append(90 * math.sin(v_orientation * pi / 180))
            VerticalProtractor_y.append(90 * math.cos(v_orientation * pi / 180))
            VerticalProtractor_x.append(0 * math.sin(v_orientation * pi / 180))
            VerticalProtractor_y.append(0 * math.cos(v_orientation * pi / 180))
            ax_sun.plot(VerticalProtractor_x, VerticalProtractor_y, c='darkorange', lw=2, linestyle=':')

    fig_title = 'Stereographic sunpath diagram, for latitude: ' + str(int(180 * math.fabs(lat) / pi)) + '$^o$' + str(
        Hemisphere)
    ax_sun.set_title(fig_title, loc='center')
    ax_sun.legend(loc='lower left', frameon=False)
    ax_sun.axis('off')

    graph, href = ui.base64_to_link_and_graph(fig_sun, fig_title, 'jpg', 700, 700)
    st.write(graph, href, unsafe_allow_html=True)
