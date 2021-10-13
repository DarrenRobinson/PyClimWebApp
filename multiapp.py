'''
This class is the framework of the web-app. 
It is called and run (instantiated) in app.py.
'''

# import datetime
import streamlit as st
from apps.helpers.helper import Helper
from apps.helpers.ui_helper import UIHelper
from apps.helpers.epw_helper import EPWHelper
import streamlit.components.v1 as components

class MultiApp:
    def __init__(self):
        self.apps = []

    # This method allows you to add features (script files) to the 'Select Feature' dropdown menu on the sidebar
    def add_app(self, title, file_title, func):
        self.apps.append({
            "title": title,
            "file_title": file_title, 
            "function": func
        })

    # This method starts the web-app
    def run(self):
        st.sidebar.write('# PyClim')

        helper = Helper()
        ui = UIHelper() 
        epw = EPWHelper()

        helper.features = self.apps                        # Inform helper of available features
        ui.advanced_search()                               # Display sorting/filtering functionalities
        epw.read_epw_f(self.ui.file_name['file_url'])      # Fetch the epw dataframe and header info 

        st.sidebar.markdown(                                    
            "Latitude: "+str(st.session_state['lat'])+                     
            " Longitude: "+str(st.session_state['longitude'])+             
            "<br>Time Zone: "+str(st.session_state['timezone']), 
            unsafe_allow_html=True                              
        )
        st.sidebar.write("---")

        # Display feature selection dropdown
        app = st.sidebar.selectbox(
            'Analysis Tools:',
            self.apps,
            format_func=lambda app: app['title']
        )
        
        epw.epw_filter(app['file_title'])               # Filter dataset for selected feature if applicable
        st.sidebar.write("---")
        app['function'](app, epw, ui)              # Run the selected feature script

        # Site analytics
        with st.sidebar:
            if app['file_title'] != 'intro':
                st.write("---")
            st.markdown('<center><a href="https://statcounter.com/p12570505/?guest=1" id="load_test" target="_blank">View Visitor Stats</a></center>', unsafe_allow_html=True)
            components.html("""
                <!-- Default Statcounter code for PyClim Web App
                https://share.streamlit.io/darrenrobinson/pyclimwebapp/main/app.py
                -->
                <center><script type="text/javascript">
                var sc_project=12570505; 
                var sc_invisible=0; 
                var sc_security="a197d8ba"; 
                var scJsHost = "https://";
                document.write("<sc"+"ript type='text/javascript' src='" +
                scJsHost+
                "statcounter.com/counter/counter.js'></"+"script>");
                </script></center>
                <noscript><div class="statcounter"><a title="free web stats"
                href="https://statcounter.com/" target="_blank"><img
                class="statcounter"
                src="https://c.statcounter.com/12570505/0/a197d8ba/0/"
                alt="free web stats"></a></div></noscript>
                <!-- End of Statcounter Code -->
            """)
            
