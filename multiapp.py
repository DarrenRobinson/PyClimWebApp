'''
This class is the framework of the web-app. 
It is called and run (instantiated) in app.py.
'''

import streamlit as st
from apps.ClimAnalFunctions import *
from apps.helpers.ui_helpers import ui_helpers
from apps.helpers.epw_helpers import epw_helpers


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



        #
        # Loading sequence 1: advanced search functionalities
        #
        ui_helper = ui_helpers()                                                        # Instantiate the UI helpers
        file_name = ui_helper.advanced_search()                                         # Display sorting/filtering functionalities


        
        #
        # Loading sequence 2: display selected weather file info: latitude, longitude, timezone
        #
        epw_helper = epw_helpers()                                                      # Instantiate the epw helpers       
        epw_file_df, epw_file_headers = epw_helper.read_epw_f(file_name['file_url'])    # Fetch the epw dataframe and header info 
        lat, longitude, timezone = float(epw_file_headers['LOCATION'][5]), float(epw_file_headers['LOCATION'][6]), float(epw_file_headers['LOCATION'][7])
        st.sidebar.markdown("Latitude: "+str(lat)+" Longitude: "+str(longitude)+"<br>Time Zone: "+str(timezone), unsafe_allow_html=True)
        



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

        # The second parameter, app['file_title'], is the name of the selected feature
        # It informs the method for which feature it is filtering
        epw_file_df = ui_helper.time_filter_conditions(epw_file_df, app['file_title']) 

        # Convert the epw dataframe to list format with first two rows as header info
        file_list = epw_helper.epw_to_file_list(epw_file_df, epw_file_headers)
        
        st.sidebar.write("---")



        #
        # Loading sequence 5: run the selected feature script
        #

        # This line is run if the selected feature is psychros 
        # to generate additional parameters to pass into app['function']
        if app['file_title'] == 'psychros':
            filter_applied = ui_helper.is_filter_applied('psychros')
            daynum_list = [31,28,31,30,31,30,31,31,30,31,30,31]     # Default values if dataset is not filtered
            hour_range = 25                                         # Default values if dataset is not filtered
            if filter_applied:
                # Calculate number of days each month if dataset is filtered
                for i in range (1,13):
                    daynum_list[i-1] = len(epw_file_df[epw_file_df['Month'] == i]['Day'].unique()) 
                # Calculate number of hours daily if dataset is filtered
                hour_range = (st.session_state.psychros_end_hour-st.session_state.psychros_start_hour+2) if (st.session_state.psychros_end_hour >= st.session_state.psychros_start_hour) else ((24-st.session_state.psychros_start_hour)+(st.session_state.psychros_end_hour-1)+2)
            app['function'](file_name, app['title'], ui_helper, file_list, lat, longitude, timezone, daynum_list, hour_range, filter_applied)
        
        # This line is run if selected feature is not psychros
        # Please note that ui_helper is passed in as one of the parameters instead of instantiating again in the feature script
        else: 
            app['function'](file_name, app['title'], ui_helper, file_list, lat, longitude, timezone)
