from multiapp import MultiApp
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

app.run()

