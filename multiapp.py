'''
This class is the framework of the web-app. 
It is called and run (instantiated) in app.py.
'''

import streamlit as st
from apps.ClimAnalFunctions import *
from apps.helpers.helper import Helper
from apps.helpers.ui_helper import UIHelper
from apps.helpers.epw_helper import EPWHelper
import os

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
        st.sidebar.write('# PyClim')

        #
        # Loading sequence 1: advanced search functionalities
        #

        self.helper.features = self.apps  
        self.ui.advanced_search()  # Display sorting/filtering functionalities

        #
        # Loading sequence 2: display selected weather file info: latitude, longitude, timezone
        #

        self.epw.read_epw_f(self.ui.file_name['file_url']) # Fetch the epw dataframe and header info 
        st.sidebar.markdown("Latitude: "+str(self.epw.lat)+" Longitude: "+str(self.epw.longitude)+"<br>Time Zone: "+str(self.epw.timezone), unsafe_allow_html=True)
        

        st.sidebar.write("---")



        #
        # Loading sequence 3: display feature selection dropdown
        #
        #
        # Format of variable "app":
        # {
        #   "title": "About"                    # app['title']
        #   "file_title": "intro"               # app['file_title']
        #   "function": "<class 'function'>"    # app['function']
        #}
        app = st.sidebar.selectbox(
            'Analysis Tools:',
            self.apps,
            format_func=lambda app: app['title']
        )

        #
        # Loading sequence 4: prepare dataset for selected feature 
        #

        self.epw.time_filter_conditions(app['file_title'])  # The parameter, app['file_title'], is the name of the selected feature which informs the method for which feature it is filtering
        self.epw.epw_to_file_list() # Convert the epw dataframe to list format with first two rows as header info
        
        st.sidebar.write("---")

        #
        # Loading sequence 5: run the selected feature script
        #


        app['function'](app, self.epw, self.ui)
