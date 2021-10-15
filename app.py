from multiapp import MultiApp
# import random
# import datetime
# import psutil
# import tracemalloc
# import streamlit as st

# 1. Import your features here using file names (without extension)
from apps import sunpath, WindRose, SolarGeo_subplots_solartime, WeatherAnalysis, SolarIrradiation_Aniso, psychros, intro

app = MultiApp()

# 2. Add all your features here
# add_app method takes 3 parameters: title, file_title and func
# file_title and func are for system settings and should always be named in such way (e.g. file_title all small letters no space)
# e.g. intro.py = "intro"     for file_title
#                 "intro.app" for func


app.add_app("About", "intro", intro.app)
app.add_app("Sun Path and Shading Analysis", "sunpath", sunpath.app)
app.add_app("Solar Geometry Subplots", "SolarGeo_subplots_solartime", SolarGeo_subplots_solartime.app)
app.add_app("Annual Solar Irradiation Surface Plot", "SolarIrradiation_Aniso", SolarIrradiation_Aniso.app)
app.add_app("Weather Analysis", "WeatherAnalysis", WeatherAnalysis.app)
app.add_app("Psychrometric Analysis", "psychros", psychros.app)
app.add_app("Wind Rose", "windrose", WindRose.app)


# num = list(range(0,7))
# random.shuffle(num)
# rand_list = [
#     ['About', 'intro', intro.app],
#     ['Sun Path and Shading Analysis', 'sunpath', sunpath.app],
#     ['Solar Geometry Subplots', 'SolarGeo_subplots_solartime', SolarGeo_subplots_solartime.app],
#     ['Annual Solar Irradiation Surface Plot', 'SolarIrradiation_Aniso', SolarIrradiation_Aniso.app],
#     ['Weather Analysis', 'WeatherAnalysis', WeatherAnalysis.app],
#     ['Psychrometric Analysis', 'psychros', psychros.app],
#     ['Wind Rose', 'windrose', WindRose.app]
# ]


# for i in range(0,7):
#     app.add_app(rand_list[num[i]][0], rand_list[num[i]][1], rand_list[num[i]][2])


# begin_time = datetime.datetime.now()
# tracemalloc.start()
app.run()
# st.write(datetime.datetime.now() - begin_time)
# current, peak = tracemalloc.get_traced_memory()
# st.write(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
# tracemalloc.stop()