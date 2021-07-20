import streamlit as st
from apps.ClimAnalFunctions import *
from apps.helpers.ui_helpers import ui_helpers
from apps.helpers.epw import epw

class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, file_title, func):
        self.apps.append({
            "title": title,
            "file_title": file_title,
            "function": func
        })

    def run(self):
        st.sidebar.write('# PyClim')

        ui_helper = ui_helpers()
        file_name = ui_helper.advanced_search() 
        
        epw_helper = epw() 
        epw_file_df, epw_file_headers = epw_helper.read_epw_f(file_name['file_url'])
        # ui_helper.map_viewer()
        lat, longitude, timezone = float(epw_file_headers['LOCATION'][5]), float(epw_file_headers['LOCATION'][6]), float(epw_file_headers['LOCATION'][7])
        st.sidebar.markdown("Latitude: "+str(lat)+" Longitude: "+str(longitude)+"<br>Time Zone: "+str(timezone), unsafe_allow_html=True)

        app = st.sidebar.selectbox(
            'Select Feature',
            self.apps,
            format_func=lambda app: app['title']
        )

        epw_file_df = ui_helper.epw_file_time_filter_conditions(epw_file_df, app['file_title'])
        file_list = epw_helper.epw_to_file_list(epw_file_df, epw_file_headers)
        
        st.sidebar.write("---")

        if app['file_title'] == 'psychros':
            filter_applied = ui_helper.is_filter_applied('psychros')
            daynum_list = [31,28,31,30,31,30,31,31,30,31,30,31]
            hour_range = 25
            if filter_applied:
                for i in range (1,13):
                    daynum_list[i-1] = len(epw_file_df[epw_file_df['Month'] == i]['Day'].unique()) 
                hour_range = (st.session_state.psychros_end_hour-st.session_state.psychros_start_hour+2) if (st.session_state.psychros_end_hour >= st.session_state.psychros_start_hour) else ((24-st.session_state.psychros_start_hour)+(st.session_state.psychros_end_hour-1)+2)
            app['function'](file_name, app['title'], ui_helper, file_list, lat, longitude, timezone, daynum_list, hour_range, filter_applied)
        
        else: 
            app['function'](file_name, app['title'], ui_helper, file_list, lat, longitude, timezone)