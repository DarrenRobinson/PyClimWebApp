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

# import hashlib

# def make_hashes(password):
#     return hashlib.sha256(str.encode(password)).hexdigest()

# def check_hashes(password,hashed_text=st.secrets['password']): 
#     if make_hashes(password) == hashed_text:
#         return True
#     return False

# def check_pw():
#   if check_hashes(st.session_state.pw):
#     st.session_state.logged = True

# if 'logged' in st.session_state:
#   if st.session_state.logged:
#     app.run()
#   else:
#     st.write("PyClim")
#     st.text_input("Enter Password", key="pw", on_change=check_pw)
# else:
#   st.write("PyClim")
#   st.text_input("Enter Password", key="pw", on_change=check_pw)

app.run()