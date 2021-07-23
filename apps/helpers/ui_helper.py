import streamlit as st
import math
import pandas as pd
from io import BytesIO
import base64
import json
import re
from urllib.request import Request, urlopen
# import pydeck as pdk
import pandas as pd
from apps.helpers.helper import Helper

# General naming convention:
# func(): methods to be called by user
# _func(): assisting methods called by system
class UIHelper(Helper):  
    def __init__(self):
        Helper.__init__(self)
        self._days_in_a_month()
        self.session_keys = {}
        self.sort_list = 'by distance from target site:'
        self.filter_list = 'hierarchically by region:'
        self.file_name = {}

    #
    # The following methods
    # (
    # _session_keys_init, 
    # _days_in_a_month, 
    # _check_day, 
    # _check_start_day, 
    # _check_end_day,
    # time_filter
    # )
    # are used for displaying the time filter panel in psychros and WindRose
    #

    # This method generates a set of feature-specific names e.g. psychros_start_month, windrose_start_month
    # so that the time filter stores these parameters separately for each feature in st.session_state.
    def _session_keys_init(self, selected_feature):
        for feature in self.features:
            if feature['file_title'] == selected_feature:
                self.session_keys = {
                    "start_month": feature['file_title']+"_start_month",
                    "end_month": feature['file_title']+"_end_month",
                    "start_day": feature['file_title']+"_start_day",
                    "end_day": feature['file_title']+"_end_day",
                    "start_hour": feature['file_title']+"_start_hour",
                    "end_hour": feature['file_title']+"_end_hour"
                } 
                

    # This method generates a set of number arrays for days in different months (e.g. for start and end day dropdowns)
    def _days_in_a_month(self):
        self.days = [0] * 12
        for i in range(1,13):
            if i in [1, 3, 5, 7, 8, 11, 12]:
                self.days[i-1] = list(range(1,32))
            elif i == 2:
                self.days[i-1] = list(range(1,29))
            else:
                self.days[i-1] = list(range(1,31))

    # _check_day, _check_start_day, _check_end_day are callbacks from start_month and end_month dropdowns.
    def _check_day(self, start_or_end):
        if (self.session_keys[start_or_end+'_day'] in st.session_state) & (self.session_keys[start_or_end+'_month'] in st.session_state):
            # If the stored day exceeds the range of days in the new selected month, it will be reset to 1.
            if st.session_state[ self.session_keys[start_or_end+'_day'] ] > (len(self.days[ st.session_state[ self.session_keys[start_or_end+'_month'] ]['value']-1 ])): 
                st.session_state[ self.session_keys[start_or_end+'_day'] ] = 1     

    def _check_start_day(self):
        self._check_day('start')

    def _check_end_day(self):
        self._check_day('end')

    # This is the main method to display the time filter dropdowns.
    def time_filter(self, feature):
        self._session_keys_init(feature)
        months = [
            {"title": "January", "value": 1}, 
            {"title": "February", "value": 2}, 
            {"title": "March", "value": 3}, 
            {"title": "April", "value": 4}, 
            {"title": "May", "value": 5}, 
            {"title": "June", "value": 6}, 
            {"title": "July", "value": 7}, 
            {"title": "August", "value": 8}, 
            {"title": "September", "value": 9}, 
            {"title": "October", "value": 10}, 
            {"title": "November", "value": 11}, 
            {"title": "December", "value": 12}
        ]
        
        # Set the dropdowns to display the previously selected month if applicable
        start_month_index = st.session_state[ self.session_keys['start_month'] ]['value']-1 if self.session_keys['start_month'] in st.session_state else 0
        end_month_index = st.session_state[ self.session_keys['end_month'] ]['value']-1 if self.session_keys['end_month'] in st.session_state else 11

        # Set the day range according to the month selected 
        start_days = self.days[start_month_index]
        end_days = self.days[end_month_index]

        # Set the dropdowns to display the previously selected day if applicable
        start_day_index = st.session_state[ self.session_keys['start_day'] ]-1 if self.session_keys['start_day'] in st.session_state else 0
        end_day_index = st.session_state[ self.session_keys['end_day'] ]-1 if self.session_keys['end_day'] in st.session_state else end_days.index(max(end_days))
        
        # Set the dropdowns to display the previously selected hour if applicable
        start_hour_index = st.session_state[ self.session_keys['start_hour'] ]-1 if self.session_keys['start_hour'] in st.session_state else 0
        end_hour_index = st.session_state[ self.session_keys['end_hour'] ]-1 if self.session_keys['end_hour'] in st.session_state else 23

        # Dropdowns
        col1, col2 = st.sidebar.beta_columns(2)
        col2.selectbox(
            "Start Month", 
            months, 
            format_func=lambda months: months['title'], 
            key=self.session_keys['start_month'], 
            index = start_month_index, 
            help="This filter controls the range of data points that are plotted",
            on_change=self._check_start_day
        )
        col2.selectbox(
            "End Month", 
            months, 
            format_func=lambda months: months['title'], 
            key=self.session_keys['end_month'], 
            index = end_month_index, 
            help="This filter controls the range of data points that are plotted",
            on_change=self._check_end_day
        )
        col1.selectbox(
            "Start Day", 
            start_days, 
            key=self.session_keys['start_day'], 
            index = start_day_index,
            help="This filter controls the range of data points that are plotted"
        )
        col1.selectbox(
            "End Day", 
            end_days, 
            key=self.session_keys['end_day'], 
            index = end_day_index, 
            help="This filter controls the range of data points that are plotted"
        )
        col1.selectbox(
            "Start Hour", 
            list(range(1,25)), 
            key=self.session_keys['start_hour'], 
            index = start_hour_index, 
            help="This filter controls the range of data points that are plotted"
        )
        col2.selectbox(
            "End Hour",
            list(range(1,25)), 
            key=self.session_keys['end_hour'], 
            index = end_hour_index, 
            help="This filter controls the range of data points that are plotted"
        )    
        
        # Display text underneath title to indicate the range of filtered data currently showing
        if (end_hour_index >= start_hour_index):
            show_hour = str(start_hour_index+1)+":00 to "+str(end_hour_index+1)+":00,"
        else:
            show_hour = "1:00 to "+str(end_hour_index+1)+":00 and "+str(start_hour_index+1)+":00 to 24:00,"
        
        if (
            (end_month_index > start_month_index) 
            | 
            ((end_month_index == start_month_index) & (end_day_index >= start_day_index))
        ):
            st.write(
                "Showing:", 
                show_hour, 
                str(start_day_index+1), 
                months[start_month_index]['title'], 
                "to", 
                str(end_day_index+1), 
                months[end_month_index]['title']
            )
        else:
            st.write(
                "Showing:", 
                show_hour, 
                "1", 
                months[0]['title'], 
                "to", 
                str(end_day_index+1), 
                months[end_month_index]['title'], 
                "and", 
                str(start_day_index+1), 
                months[start_month_index]['title'], 
                "to 31", 
                months[-1]['title']
            )



    # This method helps with display decisions. It checks if any time filter parameters i.e. month, day & hour are different from default.
    def is_filter_applied(self, feat):
        for var in self.time_var.keys():
            if feat+"_"+var in st.session_state:
                if (var == 'start_month') | (var == 'end_month'):
                    if st.session_state[feat+"_"+var]['value'] != self.time_var[var]:
                        return True
                elif st.session_state[feat+"_"+var] != self.time_var[var]:
                    return True
        return False


    #
    # The following methods
    # (
    # _save_plt_fig, 
    # generate_fig_dl_link
    # )
    # are used for generating figure download links
    #

    def _save_plt_fig(self, fig, filename, format):
        tmpfile = BytesIO()
        fig.savefig(tmpfile, format=format, dpi=300)
        encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
        href = '<a href=\'data:image/{};base64,{}\' download=\'{}\'>{}</a>'.format(format, encoded, filename+"."+format, format.upper())
        return href

    def generate_fig_dl_link(self, fig, filename):
        formats = ['jpg', 'png', 'svg', 'pdf']
        links = []
        for format in formats:
            links.append(self._save_plt_fig(fig, filename, format))
        links_str = ' '.join(links)
        hrefs = '<center>Download figures '+links_str+'</center><br>'
        return hrefs

    #
    # The following methods
    # (
    # _get_db, 
    # _sort_list_by_distance,
    # _get_db_df, 
    # 
    # )
    # are used for connecting to EnergyPlus
    #

    # @st.cache
    def _get_db(self):
        # Connect to EnergyPlus
        response = urlopen('https://github.com/NREL/EnergyPlus/raw/develop/weather/master.geojson')
        data = json.loads(response.read().decode('utf8'))
        return data

    # This method sort locations by euclidean distance
    def _sort_list_by_distance(self, df):
        latlng = [0] * 2
        latlng[0] = st.session_state.user_lat if 'user_lat' in st.session_state else 53.4
        latlng[1] = st.session_state.user_lng if 'user_lng' in st.session_state else -1.5

        R = 6373.0

        lat1 = math.radians(latlng[0])
        lon1 = math.radians(latlng[1])

        lat2 = df[11].astype(float).apply(math.radians)
        lon2 = df[10].astype(float).apply(math.radians)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = ((dlat/2).apply(math.sin)**2) + math.cos(lat1) * (lat2.apply(math.cos)) * (dlon/2).apply(math.sin)**2

        temp_df = pd.DataFrame()
        temp_df['a_sq'] = a.apply(math.sqrt)
        temp_df['one_minus_a_sq'] = (1-a).apply(math.sqrt)
        temp_df['c'] = 2 * temp_df.apply(lambda x: math.atan2(x['a_sq'], x['one_minus_a_sq']), axis=1)

        distance = R * temp_df['c'] 
        
        df[len(df.columns)] = distance
        df = df.sort_values(len(df.columns)-1) 

        return df

    # This method converts the data object to a dataframe with columns like coordinates and epw file names;
    # it also sorts the dataframe according to the preferred order
    def _get_db_df(self):
        data = self._get_db()
        df = []
        for location in data['features']:
            match = re.search(r'href=[\'"]?([^\'" >]+)', location['properties']['epw'])
            if match:
                url = match.group(1)
                url_str = url.split('/')
                url_str += [url]
            url_str += location['geometry']['coordinates']        
            df.append(url_str)

        df = pd.DataFrame(df)

        if 'filter_option' in st.session_state:
            if st.session_state.filter_option == self.sort_list:
                df = self._sort_list_by_distance(df)
            elif st.session_state.filter_option == self.filter_list:
                df = df.sort_values([5, 6, 7])
        else:
            df = self._sort_list_by_distance(df)
        return df


    #
    # The following methods
    # (
    # _get_advanced_search_dropdowns, 
    # _filter_settings_reset,
    # _check_if_a_valid_option_is_selected, 
    # advanced_search
    # )
    # are used for displaying the weather data search
    #

    def _get_advanced_search_dropdowns(self):
        df = self._get_db_df()

        regions = df[4].unique() 
        regions_dropdown = [{
            "title": "All",
            "pf": 'all',
        }] * (len(regions)+1)
        countries_dropdown = {"All": ['All']}
        states_dropdown = {"All": ['All']}
        for i in range(len(regions)):
            countries_dropdown_individual_region = df[df[4] == regions[i]][5].unique().tolist()        
            countries_dropdown[regions[i]] = ['All in Region '+regions[i][-1]] + countries_dropdown_individual_region
            
            regions_str = regions[i].split('_')
            regions_str = [regions_str[j].upper() if (regions_str[j] == 'wmo') else regions_str[j].capitalize() if (regions_str[j] != 'and') else regions_str[j] for j in range(len(regions_str))]
            regions_dropdown_title = ' '.join(regions_str)
            regions_dropdown[int(regions_str[-1])] = {
                "title": regions_dropdown_title,
                "pf": regions[i]
            }

            for j in range(len(countries_dropdown_individual_region)):        
                states_dropdown_individual_country = df[df[5] == countries_dropdown_individual_region[j]][6].dropna().unique().tolist()
                states_dropdown_individual_country = list(filter(None, states_dropdown_individual_country))
                states_dropdown[countries_dropdown_individual_region[j]] = ['All in '+countries_dropdown_individual_region[j]] + states_dropdown_individual_country

        weather_data_dropdown = []
        weather_data_dropdown_titles = pd.DataFrame(df[7].apply(lambda x: re.split('_|\.', str(x))).tolist())
        weather_data_dropdown_titles = weather_data_dropdown_titles.apply(lambda x: x.str.cat(sep=' '), axis=1)
        
        for i in range(len(df)):
            weather_data_dropdown.append({
                "title": weather_data_dropdown_titles[i],
                "region": df.iloc[i,4],
                "country": df.iloc[i,5],
                "state": df.iloc[i,6],
                "file_name": df.iloc[i,8],
                "file_url": df.iloc[i,9]
            })
                
        return regions_dropdown, countries_dropdown, states_dropdown, weather_data_dropdown
   

    # This method is callback. This method resets the settings when another radio option is selected.
    def _filter_settings_reset(self):
        if 'filter_option' in st.session_state:
            if st.session_state.filter_option != self.sort_list:
                if 'user_lat' in st.session_state:
                    st.session_state.user_lat = 53.40
                if 'user_lng' in st.session_state:
                    st.session_state.user_lng = -1.5
            if st.session_state.filter_option != self.filter_list:
                if 'region' in st.session_state:
                    st.session_state.region = {
                        "title": "All",
                        "pf": "all"
                    }
    
    def _check_if_a_valid_option_is_selected(self, var_to_check, str_to_check):
        if var_to_check in st.session_state:
            if st.session_state[var_to_check] is not None:
                if var_to_check == 'region':
                    if str_to_check not in st.session_state[var_to_check]['pf']:
                        return True        
                else:
                    if str_to_check not in st.session_state[var_to_check]:
                        return True
        return False

    # This method populates the advanced search panel and weather data file list
    def advanced_search(self):
        regions_dropdown, countries_dropdown, states_dropdown, weather_data_dropdown = self._get_advanced_search_dropdowns()

        expander = st.sidebar.beta_expander(label='Weather Data Search')
        with expander:
            st.write("Search")
            st.radio("", [self.sort_list, self.filter_list], key='filter_option', on_change=self._filter_settings_reset)

            if 'filter_option' in st.session_state:
                if st.session_state.filter_option == self.sort_list:
                    st.number_input("Latitude", -90.0, 90.0, 53.4, 0.1, key='user_lat')
                    st.number_input("Longitude", -180.0, 180.0, -1.5, 0.1, key='user_lng')
                    
                if st.session_state.filter_option == self.filter_list:
                    st.selectbox(
                        "Region", 
                        regions_dropdown,
                        format_func=lambda x: x['title'], 
                        key='region'
                    )
                    epw_col1, epw_col2 = st.beta_columns(2)

                    if 'region' in st.session_state:
                        if st.session_state.region['title'] == 'All':
                            countries_dropdown_options = []
                        else:
                            countries_dropdown_options = countries_dropdown[st.session_state.region['pf']]
                    epw_col1.selectbox("Country", countries_dropdown_options, key='country')
                    
                    states_dropdown_options = []
                    if self._check_if_a_valid_option_is_selected('country', 'All in'):
                        if len(states_dropdown[st.session_state.country]) > 1:
                            states_dropdown_options = states_dropdown[st.session_state.country] 
                    epw_col2.selectbox("State", states_dropdown_options, key='state')
                    
                    weather_data_dropdown_options = weather_data_dropdown
                    if self._check_if_a_valid_option_is_selected('region', 'all'):
                        if self._check_if_a_valid_option_is_selected('country', 'All in'):
                            if self._check_if_a_valid_option_is_selected('state', 'All in'):
                                weather_data_dropdown_options = [ d for d in weather_data_dropdown if ((d['state'] in st.session_state.state) & (d['state'] != ''))]
                            else:
                                weather_data_dropdown_options = [ d for d in weather_data_dropdown if d['country'] in st.session_state.country]
                        else:
                            weather_data_dropdown_options = [ d for d in weather_data_dropdown if d['region'] in st.session_state.region['pf']]   

        self.file_name = st.sidebar.selectbox(
            'Weather Data File List (Keyword Search Enabled)', 
            weather_data_dropdown_options,
            format_func=lambda x: x['title'],
            help="A list of available weather data files"
        )      

        return self.file_name



    # This method is under construction. Currently when it's called, it outputs a map pinpointing selections in weather data file list
    # It is commented out as it's currently unused
    # def map_viewer(self):
    #     data = self._get_db()
    #     coordinates = []
    #     for location in data['features']:
    #         # for file_type in ['epw']:
    #         #     match = re.search(r'href=[\'"]?([^\'" >]+)', location['properties'][file_type])
    #         #     if match:
    #         #         url = match.group(1)
    #         #         urls = []
    #         #         urls.append(url)
    #         #         url_str = url.split('/')
    #         #         url_str += urls
    #         # url_str += location['geometry']['coordinates']        
    #         coordinates.append(location['geometry']['coordinates'])   
    #     df = pd.DataFrame(coordinates)
    #     df = df.rename(columns={0: 'Longitude', 1: 'Latitude'})
    #     df = df[:11]
    #     layer = pdk.Layer(
    #         "ScatterplotLayer",
    #         df,
    #         pickable=True,
    #         opacity=0.8,
    #         filled=True,
    #         radius_scale=2,
    #         radius_min_pixels=10,
    #         radius_max_pixels=5,
    #         line_width_min_pixels=0.01,
    #         get_position='[Longitude, Latitude]',
    #         get_fill_color=[255, 0, 0],
    #         get_line_color=[0, 0, 0],
    #     )
    #     view_state = pdk.ViewState(latitude=df['Latitude'].iloc[0], longitude=df['Longitude'].iloc[0], zoom=1, min_zoom= 1, max_zoom=30, height=100)
    #     r = pdk.Deck(layers=[layer], map_style='mapbox://styles/mapbox/streets-v11', initial_view_state=view_state, tooltip={"html": "<b>Longitude: </b> {Longitude} <br /> " "<b>Latitude: </b>{Latitude} <br /> "})
                            
    #     st.sidebar.pydeck_chart(r)
