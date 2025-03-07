import streamlit as st


def app(app, epw, ui):
    st.write("# " + app["title"])
    st.write("""
    The PyClim Web App (built using Streamlit) is an interface to PyClim: a suite of graphical analysis modules (based around Python’s matplotlib library) for the analysis of hourly weather data. This is intended as a resources for architectural / engineering / technology students and practitioners, to help develop early-stage bioclimatic design concepts.

    There are two stages to the use of the PyClim Web App. 
    
    First, a weather file needs to be selected. The is done either by directly entering a filename or by performing a keyword search in the Weather Data List box, or by performing a Weather data search. This latter has two options: 1) search by distance - this ranks weather files based on their Euclidean distance (distance, as the crow flies) from the coordinates of your target site location (just enter the latitude and longitude), or 2) search hierarchically by region - this allows you to navigate down a geographical hierarchy from Region (the scale of continents) through country to state (where applicable) and then to select the weather file from the list of those available.

    The second stage is to analyse the selected data using the dropdown list of Analysis Tools:

    -  Sunpath and Shading: this creates sunpath diagrams in stereographic projection, plotting time lines either according to solar or clock time; this latter representing the Analemma, calculated using the equation of time. You can also project shading protractors onto the diagram for a wall of specified azimuth.

    -  Solar Geometry Subplots: this is more of a pedagogical resource, to help develop students’ understanding of how solar geometry and sun position influences the cosine of the angle of incidence (CAI) on a receiving surface (e.g. a wall or a solar collector). A 3x2 grid of subplots is created: the first three plotting daily variations in declination, Equation of time and solar daylength; the latter three plotting hourly solar altitude, azimuth and cosine of the angle of incidence on the receiving surface.

    -  Annual Solar Irradiation Surface Plot: this is a computationally-heavy feature. For 10 degree increments of azimuth (or orientation) and tilt, this calculates the annual incident global (direct and diffuse from sky and ground) solar irradiation; creating a surface contour plot. This helps to understand where solar collectors would be best positioned to harness solar radiation. Users can specific whether they wish to create this chart for an isotropic (the same sky brightness in all directions) or an anistropic (direction-dependent brightness) sky; also whether to create this for diffuse radiation only (so no direct solar radiation) and can modify the ground reflectance.

    -  Weather Analysis: this creates a range of plots and statistics of climate variables. Following the statistics header, users are presented with: 1) ground temperature profile, 2) temperature / wind speed frequency histograms, 3) inverse illuminance cumulative distribution function: this helps to determine artificial light switch-off hours, 4) Monthly degree-day bar charts, 5) violin plots of key synoptic (or non-solar) variables (a little like boxplots, but more informative), 6) temporal solar irradiance / maps with sunrise / sunset times indicated in red.
    
    -  Psychrometric Analysis: this creates psychrometric charts for the plotting of hourly climate data {and of transformed data to mimic direct evaporative cooling}.
    
    -  Wind rose: this plots a user-controllable wind rose, with theta (e.g. from the centre outwards) segments of azimuthal sectors (e.g. clockwise from North) falsecoloured either according to the hours that the wind approaches that direction and in the indicated (theta) speed, or at the indicated (theta) temperature. 
    
    This linked video tutorial demonstrates the use of the App: navigating the analysis features, interpreting the charts and selecting weather data files:-
    https://digitalmedia.sheffield.ac.uk/media/PyClim-WebApp-Tutorial1/1_z98gtuf8 
    
    This second linked video demonstrates some of the more advanced features of the App for manipulating the charts:-
    https://digitalmedia.sheffield.ac.uk/media/PyClim-WebApp-Tutorial2/1_2ffevizg 
    
    For further advice on the interpretation of charts from the PyClim Web App please refer to: http://www.ibpsa.org/proceedings/BSO2020/BSOV2020_Robinson.pdf.
    
    If you would like to access the source code for this app, please visit the GitHub repository: https://github.com/DarrenRobinson/PyClimWebApp.
    
    Tip: if you would like to enlarge the charts, try using wide mode: simply click on the icon with the three horizontal bars to the top right of the white content area, click on settings and tick the 'Wide mode' box. 
    
    
    THE TEAM:
    
    PyClim and this PyClim Web App interface to it were developed at and are maintained by the University of Sheffield, UK.

    The original PyClim backend was developed in Python by Prof. Darren Robinson.

    The Web App front end was developed using Streamlit by Alvin Mok through an internship funded by the University of Sheffield, under the supervision of Reena Sayani and Darren Robinson.

    We are grateful to the following staff and students of the Sheffield School of Architecture for their constructive feedback on earlier prototypes of this App: Elizaveta Arestova, Danni Kerr, Anupama Rao, Jonathan Sykes, Parag Wate.



    FEEDBACK:
    
    If you encounter any bugs with this App, please send a description by e-mail to Darren Robinson: d.robinson1@sheffield.ac.uk  
    """)
