import streamlit as st
from multiapp import MultiApp
from apps import sunpath, WindRose, SolarGeo_subplots_solartime, WeatherAnalysis, SolarIrradiation_Aniso, psychros, intro

from settings import *

app = MultiApp()

# Add all your application here
app.add_app(intro_title, "intro", intro.app)
app.add_app(sunpath_title, "sunpath", sunpath.app)
app.add_app(SolarGeo_subplots_solartime_title, "SolarGeo_subplots_solartime", SolarGeo_subplots_solartime.app)
app.add_app(SolarIrradiation_Aniso_title, "SolarIrradiation_Aniso", SolarIrradiation_Aniso.app)
app.add_app(WeatherAnalysis_title, "WeatherAnalysis", WeatherAnalysis.app)
app.add_app(psychros_title, "psychros", psychros.app)
app.add_app(windrose_title, "windrose", WindRose.app)

app.run()