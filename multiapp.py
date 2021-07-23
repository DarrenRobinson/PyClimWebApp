'''
This class is the framework of the web-app. 
It is called and run (instantiated) in app.py.
'''

import streamlit as st
from apps.helpers.helper import Helper
from apps.helpers.ui_helper import UIHelper
from apps.helpers.epw_helper import EPWHelper
import streamlit_analytics

class MultiApp:
    def __init__(self):
        self.apps = []
        self.helper = Helper()
        self.ui = UIHelper() 
        self.epw = EPWHelper()

    # This method allows you to add features (script files) to the 'Select Feature' dropdown menu on the sidebar
    def add_app(self, title, file_title, func):
        self.apps.append({
            "title": title,
            "file_title": file_title, 
            "function": func
        })

    # This method starts the web-app
    def run(self):

        with streamlit_analytics.track():
            st.sidebar.write('# PyClim')
            self.helper.features = self.apps                        # Inform helper of available features
            self.ui.advanced_search()                               # Display sorting/filtering functionalities
            self.epw.read_epw_f(self.ui.file_name['file_url'])      # Fetch the epw dataframe and header info 
            st.sidebar.markdown(                                    
                "Latitude: "+str(self.epw.lat)+                     
                " Longitude: "+str(self.epw.longitude)+             
                "<br>Time Zone: "+str(self.epw.timezone), 
                unsafe_allow_html=True                              
            )
            st.sidebar.write("---")

            # Display feature selection dropdown
            app = st.sidebar.selectbox(
                'Analysis Tools:',
                self.apps,
                format_func=lambda app: app['title']
            )

            self.epw.epw_filter(app['file_title'])               # Filter dataset for selected feature if applicable
            # self.epw.epw_to_file_list()                          # Convert the epw dataframe to list format with first two rows as header info
            st.sidebar.write("---")
            app['function'](app, self.epw, self.ui)              # Run the selected feature script
