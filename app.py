from multiapp import MultiApp
# 1. Import your features here using file names (without extension)
from apps import sunpath, WindRose, SolarGeo_subplots_solartime, WeatherAnalysis, SolarIrradiation_Aniso, psychros, intro
import streamlit.components.v1 as components

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

components.html("""
    <!-- Default Statcounter code for PyClim
    https://share.streamlit.io/alvin902london/pyclimwebapp/main/app.py?analytics=on
    -->
    <script type="text/javascript">
    var sc_project=12570287; 
    var sc_invisible=1; 
    var sc_security="514acaac"; 
    </script>
    <script type="text/javascript"
    src="https://www.statcounter.com/counter/counter.js" async></script>
    <noscript><div class="statcounter"><a title="Web Analytics Made Easy -
    StatCounter" href="https://statcounter.com/" target="_blank"><img
    class="statcounter" src="https://c.statcounter.com/12570287/0/514acaac/1/"
    alt="Web Analytics Made Easy - StatCounter"></a></div></noscript>
    <!-- End of Statcounter Code -->
""")