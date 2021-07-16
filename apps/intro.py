import numpy as np
from numpy.core.numeric import True_
import pandas as pd
import streamlit as st

def app(file_name, title, ui_helper, file_list, lat, longitude, timezone):

    st.write("# "+title)

    st.write(
    """
    The PyClim Web App (built using Streamlit) is an interface to PyClim: a suite of graphical analysis modules (based around Python’s matplotlib library) for the analysis of hourly weather data. This is intended as a resources for architectural / engineering / technology students and practitioners, to help develop early-stage bioclimatic design concepts.

    There are two stages to the use of the PyClim Web App. First, a weather file needs to be selected. The is done by navigating down the hierarchy in the Advanced Search option from Region (continents) through country to state (where applicable) and then selecting the weather file from the list of those available. Alternatively, you can also search by ranking weather files based on their Euclidean distance (distance, as the crow flies) from the coordinates of your targey site location (just enter the latitude and longitude), or you can directly perform a keyword search for the weather data file or city.

    The second stage is to analyse the selected data using the dropdown list of Features:

    -  Sunpath and Shading: this creates sunpath diagrams in stereographic projection, plotting time lines either according to solar or clock time; this latter representing the Analemma, calculated using the equation of time (EqT). You can also project shading protractors onto the diagram for a wall of specified azimuth.

    -  Solar Geometry Subplots: this is more of a pedagogical resource, to help develop students’ understanding of solar geometry and sun position influences the cosine of the angle of incidence (CAI) on a receiving surface (e.g. a wall or a solar collector). A 3x2 grid of subplots is created: the first three plotting daily variations in declination, Equation of time and solar daylength; the latter three plotting hourly solar altitude, azimuth and cosine of the angle of incidence on the receiving surface.

    -  Annual Solar Irradiation Surface Plot: this is a computationally-heavy feature. For 5 degree increments of azimuth (or orientation) and tile, this calculates the annual incident global (direct and diffuse from sky and ground) solar irradiation; creating a surface contour plot. This helps to understand where solar collectors would be best positioned to harness solar radiation. Users can specific whether they wish to create this chart for an isotropic (the same sky brightness in all directions) and an anistropic (direction-dependent brightness) sky; also whether to create this for diffuse radiation only (so no direct solar radiation) and can modify the ground reflectance.

    -  Weather Analysis: this creates a range of plots and statistics of climate variables. Following the statistics header, users are presented with: 1) ground temperature profile, 2) temperature / wind speed frequency histograms, 3) inverse illuminance cumulative distribution function: this helps to determine artificial light switch-off hours, 4) Monthly degree-day bar charts, 5) violin plots of key synoptic variables (a little like boxplots, but more informative), 6) temporal solar irradiance / maps with sunrise / sunset times indicated in red.
    
    -  Psychrometric Analysis: this creates psychrometric charts for the plotting of hourlyclimate data {and of transformed data to mimic evaporative cooling}.
    
    -  Wind rose: this plots a user-controllable wind rose, with theta segments of azimuthal sectors falsecoloured either according to the hours that the wind approaches that direction and in the indicated (theta) speed, or at the indicated (theta) temperature. For further advice on the interpretation of charts from the PyClim Web App please refer to: http://www.ibpsa.org/proceedings/BSO2020/BSOV2020_Robinson.pdf.
    """
    )
