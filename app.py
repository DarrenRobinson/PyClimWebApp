import streamlit as st
from multiapp import MultiApp
from apps import sunpath, WindRose, SolarGeo_subplots_solartime, WeatherAnalysis, SolarIrradiation_Aniso, psychros, intro

app = MultiApp()

# Add all your application here
app.add_app("About", "intro", intro.app)
app.add_app("Sun Path and Shading Analysis", "sunpath", sunpath.app)
app.add_app("Solar Geometry Subplots", "SolarGeo_subplots_solartime", SolarGeo_subplots_solartime.app)
app.add_app("Annual Solar Irradiation Surface Plot", "SolarIrradiation_Aniso", SolarIrradiation_Aniso.app)
app.add_app("Weather Analysis", "WeatherAnalysis", WeatherAnalysis.app)
app.add_app("Psychrometric Analysis", "psychros", psychros.app)
app.add_app("Wind Rose", "windrose", WindRose.app)

app.run()