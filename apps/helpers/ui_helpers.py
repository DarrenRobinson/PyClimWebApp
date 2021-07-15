import math
import tempfile
import pandas as pd
import streamlit as st
import operator
import io
from PIL import Image
from io import BytesIO
import base64
import json
import re
from urllib.request import Request, urlopen
import geocoder

class ui_helpers():  
    def __init__(self):
        self.feats = ['psychros', 'windrose']
        self.time_var = {'start_month': 1, 'start_day': 1, 'end_month': 12, 'end_day': 31, 'start_hour': 1, 'end_hour': 24}
        
    def epw_file_time_filter(self, feature):
        for feat in self.feats:
            if feat == feature:
                session_keys = {
                    "start_month": feat+"_start_month",
                    "end_month": feat+"_end_month",
                    "start_day": feat+"_start_day",
                    "end_day": feat+"_end_day",
                    "start_hour": feat+"_start_hour",
                    "end_hour": feat+"_end_hour"
                }    

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

        days = [0] * 12
        for i in range(1,13):
            if i in [1, 3, 5, 7, 8, 11, 12]:
                days[i-1] = list(range(1,32))
            elif i == 2:
                days[i-1] = list(range(1,29))
            else:
                days[i-1] = list(range(1,31))  
        
        start_month_index = st.session_state[ session_keys['start_month'] ]['value']-1 if session_keys['start_month'] in st.session_state else 0
        end_month_index = st.session_state[ session_keys['end_month'] ]['value']-1 if session_keys['end_month'] in st.session_state else 11

        start_days = days[start_month_index]
        end_days = days[end_month_index]

        start_day_index = st.session_state[ session_keys['start_day'] ]-1 if session_keys['start_day'] in st.session_state else 0
        if session_keys['start_day'] in st.session_state:
            if st.session_state[ session_keys['start_day'] ] > (len(start_days)): 
                start_day_index = 0

        end_day_index = st.session_state[ session_keys['end_day'] ]-1 if session_keys['end_day'] in st.session_state else end_days.index(max(end_days))
        if session_keys['end_day'] in st.session_state:
            if st.session_state[ session_keys['end_day'] ] > (len(end_days)): 
                end_day_index = 0
        
        start_hour_index = st.session_state[ session_keys['start_hour'] ]-1 if session_keys['start_hour'] in st.session_state else 0
        end_hour_index = st.session_state[ session_keys['end_hour'] ]-1 if session_keys['end_hour'] in st.session_state else 23

        col1, col2 = st.sidebar.beta_columns(2)

        col2.selectbox(
            "Start Month", 
            months, 
            format_func=lambda months: months['title'], 
            key=session_keys['start_month'], 
            index = start_month_index, 
            help="This filter controls the range of data points that are plotted"
        )

        col2.selectbox(
            "End Month", 
            months, 
            format_func=lambda months: months['title'], 
            key=session_keys['end_month'], 
            index = end_month_index, 
            help="This filter controls the range of data points that are plotted"
        )

        col1.selectbox(
            "Start Day", 
            start_days, 
            key=session_keys['start_day'], 
            index = start_day_index,
            help="This filter controls the range of data points that are plotted"
        )

        col1.selectbox(
            "End Day", 
            end_days, 
            key=session_keys['end_day'], 
            index = end_day_index, 
            help="This filter controls the range of data points that are plotted"
        )
        
        col1.selectbox(
            "Start Hour", 
            list(range(1,25)), 
            key=session_keys['start_hour'], 
            index = start_hour_index, 
            help="This filter controls the range of data points that are plotted"
        )
        
        col2.selectbox(
            "End Hour",
            list(range(1,25)), 
            key=session_keys['end_hour'], 
            index = end_hour_index, 
            help="This filter controls the range of data points that are plotted"
        )    
        
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
                "to", str(end_day_index+1), 
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

    def _epw_file_time_filter_pipeline(self, epw_file_dataframe, op_cond, limits):
        filter_operator = operator.__and__ if op_cond else operator.__or__
        epw_file_dataframe = epw_file_dataframe.loc[filter_operator(limits[0], limits[1])]
        return epw_file_dataframe

    def epw_file_time_filter_conditions(self, epw_file_dataframe, file_title):
        time_var = self.time_var.copy()
        for feat in self.feats:
            if feat == file_title:
                for var in time_var.keys():
                    if feat+"_"+var in st.session_state:
                        if (var == 'start_month') | (var == 'end_month'):
                            time_var[var] = st.session_state[feat+"_"+var]['value']
                        else:
                            time_var[var] = st.session_state[feat+"_"+var]
        
        # filter by day and month
        conditions = (time_var['end_month'] > time_var['start_month']) | ((time_var['end_month'] == time_var['start_month']) & (time_var['end_day'] >= time_var['start_day']))
        limits = (
            (
            (epw_file_dataframe['Month'] > time_var['start_month']) | 
            ((epw_file_dataframe['Month'] == time_var['start_month']) & (epw_file_dataframe['Day'] >= time_var['start_day']))
            ),
            (
            ((epw_file_dataframe['Month'] < time_var['end_month']) | 
            (epw_file_dataframe['Month'] == time_var['end_month']) & (epw_file_dataframe['Day'] <= time_var['end_day']))
            )
        )
        epw_file_dataframe = self._epw_file_time_filter_pipeline(epw_file_dataframe, conditions, limits)
        
        # filter by hour
        conditions = (time_var['end_hour'] >= time_var['start_hour'])
        limits = (
            (epw_file_dataframe['Hour'] >= time_var['start_hour']),
            (epw_file_dataframe['Hour'] <= time_var['end_hour'])       
        )
        epw_file_dataframe = self._epw_file_time_filter_pipeline(epw_file_dataframe, conditions, limits)

        return epw_file_dataframe

    def is_filter_applied(self, feat):
        for var in self.time_var.keys():
            if feat+"_"+var in st.session_state:
                if (var == 'start_month') | (var == 'end_month'):
                    if st.session_state[feat+"_"+var]['value'] != self.time_var[var]:
                        return True
                elif st.session_state[feat+"_"+var] != self.time_var[var]:
                    return True
        return False

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

    @st.cache
    def get_db(self):
        # Connect to EnergyPlus
        response = urlopen('https://github.com/NREL/EnergyPlus/raw/develop/weather/master.geojson')
        data = json.loads(response.read().decode('utf8'))
        df = []
        for location in data['features']:
            url_str = []
            for file_type in ['epw']:
                match = re.search(r'href=[\'"]?([^\'" >]+)', location['properties'][file_type])
                if match:
                    url = match.group(1)
                    urls = []
                    urls.append(url)
                    url_str = url.split('/')
                    url_str += urls
            url_str += location['geometry']['coordinates']        
            df.append(url_str)
        df = pd.DataFrame(df)

        # Get current location and sort epw files by distance from it
        geo = geocoder.ip('me')
        latlng = geo.latlng

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

        # Generate dropdowns for filter by epw file categories
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
        
    def advanced_search(self):
        regions_dropdown, countries_dropdown, states_dropdown, weather_data_dropdown = self.get_db()
        expander = st.sidebar.beta_expander(label='Advanced Search')
        with expander:
            region = st.selectbox(
                "Region", 
                regions_dropdown,
                format_func=lambda x: x['title']
            )
            epw_col1, epw_col2 = st.beta_columns(2)

            if region['title'] == 'All':
                countries_dropdown_options = []
                # countries_dropdown_options = countries_dropdown["All"]
            else:
                countries_dropdown_options = countries_dropdown[region['pf']]

            country = epw_col1.selectbox("Country", countries_dropdown_options)
            
            # if 'All in ' in country:
            states_dropdown_options = []
            if country is not None:
                if 'All in ' not in country:
                    if len(states_dropdown[country]) > 1:
                        states_dropdown_options = states_dropdown[country] 

            state = epw_col2.selectbox("State", states_dropdown_options)

        weather_data_dropdown_options = weather_data_dropdown
        if (region['pf'] != 'all'):
            if ('All in ' not in country):
                if state is not None:
                    if ('All in ' not in state):
                        weather_data_dropdown_options = [ d for d in weather_data_dropdown if ((d['state'] in state) & (d['state'] != ''))]
                    else:
                        weather_data_dropdown_options = [ d for d in weather_data_dropdown if d['country'] in country]
                else:
                    weather_data_dropdown_options = [ d for d in weather_data_dropdown if d['country'] in country]
            else:
                weather_data_dropdown_options = [ d for d in weather_data_dropdown if d['region'] in region['pf']]

        file_name = st.sidebar.selectbox(
            'Select Weather Data (Keyword Search Enabled)', 
            weather_data_dropdown_options,
            format_func=lambda x: x['title'],
            # index = weather_data_dropdown_default_index,
            help="A list of available weather data files sorted by the distance from your current location."
        )      
        
        return file_name