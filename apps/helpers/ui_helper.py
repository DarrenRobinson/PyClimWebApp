import io
import os
import streamlit as st
import math
import pandas as pd
from io import BytesIO
import base64
import json
import re
from urllib.request import urlopen
# import pydeck as pdk
# import datetime
# import tracemalloc
# from altair.vegalite.v4.schema.core import Axis
import pandas as pd
from apps.helpers.helper import Helper

# General naming convention:
# func(): methods to be called by user
# _func(): assisting methods called by system
class UIHelper(Helper):  
    def __init__(self):
        Helper.__init__(self)
        self._days_in_a_month()
        self.sort_list = 'by distance from target site:'
        self.filter_list = 'hierarchically by region:'
        self.file_name = {}
        self.default_lat = 53.4
        self.default_lon = -1.5
        self.df = self._get_db_df()

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
                if 'session_keys' not in st.session_state:
                    st.session_state['session_keys'] = {}
                st.session_state['session_keys']['start_month'] = feature['file_title']+"_start_month"
                st.session_state['session_keys']['end_month'] = feature['file_title']+"_end_month"
                st.session_state['session_keys']['start_day'] = feature['file_title']+"_start_day"
                st.session_state['session_keys']['end_day'] = feature['file_title']+"_end_day"
                st.session_state['session_keys']['start_hour'] = feature['file_title']+"_start_hour"
                st.session_state['session_keys']['end_hour'] = feature['file_title']+"_end_hour"

    # This method generates a set of number arrays for days in different months (e.g. for start and end day dropdowns)
    def _days_in_a_month(self):
        self.days = [0] * 12
        for i in range(1,13):
            if i in [1, 3, 5, 7, 8, 10, 12]:
                self.days[i-1] = list(range(1,32))
            elif i == 2:
                self.days[i-1] = list(range(1,29))
            else:
                self.days[i-1] = list(range(1,31))

    # _check_day, _check_start_day, _check_end_day are callbacks from start_month and end_month dropdowns.
    def _check_day(self, start_or_end):
        # if (self.session_keys[start_or_end+'_day'] in st.session_state) & (self.session_keys[start_or_end+'_month'] in st.session_state):
        #     # If the stored day exceeds the range of days in the new selected month, it will be reset to 1.
        #     if st.session_state[ self.session_keys[start_or_end+'_day'] ] > (len(self.days[ st.session_state[ self.session_keys[start_or_end+'_month'] ]['value']-1 ])): 
        #         st.session_state[ self.session_keys[start_or_end+'_day'] ] = 1     
        day = st.session_state['session_keys'][start_or_end+'_day']
        month = st.session_state['session_keys'][start_or_end+'_month']
        if (day in st.session_state) & (month in st.session_state):
            # If the stored day exceeds the range of days in the new selected month, it will be reset to 1.
            if st.session_state[day] > (len(self.days[ st.session_state[month]['value']-1 ])): 
                st.session_state[day] = 1  

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
        start_day = st.session_state['session_keys']['start_day']
        end_day = st.session_state['session_keys']['end_day']
        start_month = st.session_state['session_keys']['start_month']
        end_month = st.session_state['session_keys']['end_month']
        start_hour = st.session_state['session_keys']['start_hour']
        end_hour = st.session_state['session_keys']['end_hour']

        # Set the dropdowns to display the previously selected month if applicable
        start_month_index = st.session_state[ start_month ]['value']-1 if start_month in st.session_state else 0
        end_month_index = st.session_state[ end_month ]['value']-1 if end_month in st.session_state else 11

        # Set the day range according to the month selected 
        start_days = self.days[ start_month_index ]
        end_days = self.days[ end_month_index ]
        
        # Set the dropdowns to display the previously selected day if applicable
        start_day_index = st.session_state[ start_day ]-1 if start_day in st.session_state else 0
        end_day_index = st.session_state[ end_day ]-1 if end_day in st.session_state else end_days.index(max(end_days))
        
        # Set the dropdowns to display the previously selected hour if applicable
        start_hour_index = st.session_state[ start_hour ]-1 if start_hour in st.session_state else 0
        end_hour_index = st.session_state[ end_hour ]-1 if end_hour in st.session_state else 23

        # Dropdowns
        col1, col2 = st.sidebar.columns(2)
        col2.selectbox(
            "Start Month", 
            months, 
            format_func=lambda months: months['title'], 
            key=start_month, 
            index = start_month_index, 
            help="This filter controls the range of data points that are plotted",
            on_change=self._check_start_day
        )
        col2.selectbox(
            "End Month", 
            months, 
            format_func=lambda months: months['title'], 
            key=end_month, 
            index = end_month_index, 
            help="This filter controls the range of data points that are plotted",
            on_change=self._check_end_day
        )
        col1.selectbox(
            "Start Day", 
            start_days, 
            key=start_day, 
            index = start_day_index,
            help="This filter controls the range of data points that are plotted"
        )
        col1.selectbox(
            "End Day", 
            end_days, 
            key=end_day, 
            index = end_day_index, 
            help="This filter controls the range of data points that are plotted"
        )
        col1.selectbox(
            "Start Hour", 
            list(range(1,25)), 
            key=start_hour, 
            index = start_hour_index, 
            help="This filter controls the range of data points that are plotted"
        )
        col2.selectbox(
            "End Hour",
            list(range(1,25)), 
            key=end_hour, 
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

    # def _save_plt_fig(self, fig, filename, format):
    #     tmpfile = BytesIO()
    #     fig.savefig(tmpfile, format=format, dpi=300)
    #     encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    #     href = '<a href=\'data:image/{};base64,{}\' download=\'{}\'>{}</a>'.format(format, encoded, filename+"."+format, format.upper())
    #     return href

    # def generate_fig_dl_link(self, fig, filename):
    #     formats = ['jpg', 'png', 'svg', 'pdf']
    #     links = []
    #     for format in formats:
    #         links.append(self._save_plt_fig(fig, filename, format))
    #     links_str = ' '.join(links)
    #     hrefs = '<center>Download figures '+links_str+'</center><br>'
    #     return hrefs
    
    def _fig_to_base64(self, figure, format):
        img = io.BytesIO()
        figure.savefig(img, format=format, dpi=300)
        img.seek(0)
        return base64.b64encode(img.getvalue())

    def base64_to_link_and_graph(self, figure, filename, format, width, height):
        decoded = self._fig_to_base64(figure, format).decode('utf-8')
        graph = '<img width={} height={} src="data:image/jpg;base64, {}">'.format(width, height, decoded)
        href = '<center>Download figure <a href=\'data:image/{};base64,{}\' download=\'{}\'>{}</a></center><br>'.format(format, decoded, filename+"."+format, format.upper())
        return graph, href

            
    # def generate_dl_link(self, fig, filename, format):
    #     tmpfile = BytesIO()
    #     fig.savefig(tmpfile, format=format, dpi=300)
    #     encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    #     href = '<center><a href=\'data:image/{};base64,{}\' download=\'{}\'>{}</a></center><br>'.format(format, encoded, filename+"."+format, 'Download figure')
    #     return href

    # def format_selector(self):
    #     options = ['jpg', 'png', 'svg', 'pdf']
    #     file_format = st.sidebar.selectbox(
    #         "Figure format to download",
    #         options,
    #         index=0
    #     )
    #     return file_format
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

    @st.cache
    def _get_db(self):
        # Connect to EnergyPlus
        response = urlopen('https://github.com/NREL/EnergyPlus/raw/develop/weather/master.geojson')
        data = json.loads(response.read().decode('utf8'))
        # script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        # rel_path = "master.geojson"
        # abs_file_path = os.path.join(script_dir, rel_path)
        # with open(abs_file_path) as fp:
        #     data = json.loads(fp)

        return data
    
    # These methods (_calculate_d, _sort_list_by_distance) sort locations by euclidean distance
    def _calculate_distance(self, df_latlng, session_str, default_val):
        latlng = st.session_state[session_str] if session_str in st.session_state else default_val
        d1 = math.radians(latlng)
        d2 = df_latlng.astype(float).apply(math.radians)
        d3 = d2 - d1
        return d3, d2, d1

    def _sort_list_by_distance(self, df):
        dlat, lat2, lat1 = self._calculate_distance(df['lat'], 'user_lat', self.default_lat)
        dlon, lon2, lon1 = self._calculate_distance(df['lon'], 'user_lng', self.default_lon)

        a = ((dlat/2).apply(math.sin)**2) + math.cos(lat1) * (lat2.apply(math.cos)) * (dlon/2).apply(math.sin)**2

        temp_df = pd.DataFrame()
        temp_df['a_sq'] = a.apply(math.sqrt)
        temp_df['one_minus_a_sq'] = (1-a).apply(math.sqrt)
        temp_df['c'] = 2 * temp_df.apply(lambda x: math.atan2(x['a_sq'], x['one_minus_a_sq']), axis=1)
        
        R = 6373.0
        df['distance'] = R * temp_df['c'] 
        df = df.sort_values('distance') 

        return df

    # This method converts the data object to a dataframe with columns like coordinates and epw file names;
    # it also sorts the dataframe according to the preferred order
    def _get_db_df(self):
        data = self._get_db()
        filter_list = [
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/ARG/ARG_Chaco_Saenz.Pena.AP_871490_ArgTMY/ARG_Chaco_Saenz.Pena.AP_871490_ArgTMY.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/ATA_Estacao.Comandante.Ferraz.892520_INMET/ATA_Estacao.Comandante.Ferraz.892520_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AC_Feijo.AP.819240_INMET/BRA_AC_Feijo.AP.819240_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AC_Parque.Chandless.819630_INMET/BRA_AC_Parque.Chandless.819630_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AC_Porto.Walter.819210_INMET/BRA_AC_Porto.Walter.819210_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AC_Rio.Branco.829150_INMET/BRA_AC_Rio.Branco.829150_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AL_Arapiraca.AP.819960_INMET/BRA_AL_Arapiraca.AP.819960_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AL_Coruripe.866190_INMET/BRA_AL_Coruripe.866190_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AL_Maceio-Palmares.Intl.AP.829930_TRY.1962/BRA_AL_Maceio-Palmares.Intl.AP.829930_TRY.1962.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AL_Maceio.829940_INMET/BRA_AL_Maceio.829940_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AL_Palmeira.dos.Indios.829920_INMET/BRA_AL_Palmeira.dos.Indios.829920_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AL_Pao.de.Acucar.819940_INMET/BRA_AL_Pao.de.Acucar.819940_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AL_Sao.Luis.do.Quitunde.819970_INMET/BRA_AL_Sao.Luis.do.Quitunde.819970_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AM_Autazes.817320_INMET/BRA_AM_Autazes.817320_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AM_Barcelos.AP.816480_INMET/BRA_AM_Barcelos.AP.816480_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AM_Coari.817700_INMET/BRA_AM_Coari.817700_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AM_Humaita.AP.818900_INMET/BRA_AM_Humaita.AP.818900_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AM_Itacoatiara.AP.817330_INMET/BRA_AM_Itacoatiara.AP.817330_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AM_Manacapuru.817290_INMET/BRA_AM_Manacapuru.817290_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AM_Manaus-Gomez.Intl.AP.817300_INMET/BRA_AM_Manaus-Gomez.Intl.AP.817300_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AM_Maues.817340_INMET/BRA_AM_Maues.817340_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AM_Parintins.817030_INMET/BRA_AM_Parintins.817030_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AM_Presidente.Figueiredo.816990_INMET/BRA_AM_Presidente.Figueiredo.816990_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AM_Urucara.AP.817020_INMET/BRA_AM_Urucara.AP.817020_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AP_Macapa-Alcolumbre.Intl.AP.820980_INMET/BRA_AP_Macapa-Alcolumbre.Intl.AP.820980_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AP_Oiapoque.816090_INMET/BRA_AP_Oiapoque.816090_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AP_Porto.Grande.816370_INMET/BRA_AP_Porto.Grande.816370_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_AP_Tartarugalzinho.816280_INMET/BRA_AP_Tartarugalzinho.816280_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Amargosa.AP.866750_INMET/BRA_BA_Amargosa.AP.866750_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Barra.AP.866340_INMET/BRA_BA_Barra.AP.866340_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Barreiras.866520_INMET/BRA_BA_Barreiras.866520_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Belmonte.867440_INMET/BRA_BA_Belmonte.867440_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Bom.Jesus.da.Lapa.AP.866720_INMET/BRA_BA_Bom.Jesus.da.Lapa.AP.866720_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Brumado.866960_INMET/BRA_BA_Brumado.866960_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Buritirama.AP.866090_INMET/BRA_BA_Buritirama.AP.866090_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Caravelas.834970_INMET/BRA_BA_Caravelas.834970_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Conde.866390_INMET/BRA_BA_Conde.866390_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Correntina.866710_INMET/BRA_BA_Correntina.866710_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Cruz.das.Almas.866570_INMET/BRA_BA_Cruz.das.Almas.866570_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Delfino.866100_INMET/BRA_BA_Delfino.866100_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Euclides.da.Cunha.866130_INMET/BRA_BA_Euclides.da.Cunha.866130_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Feira.de.Santana.866580_INMET/BRA_BA_Feira.de.Santana.866580_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Guanambi.AP.866940_INMET/BRA_BA_Guanambi.AP.866940_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Ibotirama.866530_INMET/BRA_BA_Ibotirama.866530_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Ilheus.866990_INMET/BRA_BA_Ilheus.866990_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Ipiau.866980_INMET/BRA_BA_Ipiau.866980_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Irece.AP.866350_INMET/BRA_BA_Irece.AP.866350_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Itaberaba.832440_INMET/BRA_BA_Itaberaba.832440_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Itapetinga.867230_INMET/BRA_BA_Itapetinga.867230_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Itirucu.866740_INMET/BRA_BA_Itirucu.866740_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Jacobina.866360_INMET/BRA_BA_Jacobina.866360_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Lencois.866540_INMET/BRA_BA_Lencois.866540_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Macajuba.866550_INMET/BRA_BA_Macajuba.866550_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Marau.866770_INMET/BRA_BA_Marau.866770_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Paulo.Afonso.829860_INMET/BRA_BA_Paulo.Afonso.829860_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Piata.866730_INMET/BRA_BA_Piata.866730_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Porto.Seguro.867450_INMET/BRA_BA_Porto.Seguro.867450_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Queimadas.866120_INMET/BRA_BA_Queimadas.866120_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Remanso.829790_INMET/BRA_BA_Remanso.829790_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Salvador-Magalhaes.Intl.AP.832480_TRY.1961/BRA_BA_Salvador-Magalhaes.Intl.AP.832480_TRY.1961.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Salvador.866780_INMET/BRA_BA_Salvador.866780_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Santa.Rita.de.Cassia.866330_INMET/BRA_BA_Santa.Rita.de.Cassia.866330_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Senhor.do.Bonfim.830880_INMET/BRA_BA_Senhor.do.Bonfim.830880_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Serrinha.866370_INMET/BRA_BA_Serrinha.866370_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Uaua.819920_INMET/BRA_BA_Uaua.819920_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Una.867240_INMET/BRA_BA_Una.867240_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Valenca.866760_INMET/BRA_BA_Valenca.866760_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_BA_Vitoria.da.Conquista-Figueiredo.AP.866970_INMET/BRA_BA_Vitoria.da.Conquista-Figueiredo.AP.866970_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_CE_Acarau.817550_INMET/BRA_CE_Acarau.817550_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_CE_Barbalha.819110_INMET/BRA_CE_Barbalha.819110_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_CE_Campos.Sales.827770_INMET/BRA_CE_Campos.Sales.827770_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_CE_Crateus.818300_INMET/BRA_CE_Crateus.818300_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_CE_Fortaleza-Pinto.Martins.Intl.AP.817580_INMET/BRA_CE_Fortaleza-Pinto.Martins.Intl.AP.817580_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_CE_Guaramiranga.824870_INMET/BRA_CE_Guaramiranga.824870_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_CE_Iguatu.818730_INMET/BRA_CE_Iguatu.818730_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_CE_Itapipoca.817560_INMET/BRA_CE_Itapipoca.817560_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_CE_Jaguaribe.818330_INMET/BRA_CE_Jaguaribe.818330_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_CE_Jaguaruana.824930_INMET/BRA_CE_Jaguaruana.824930_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_CE_Morada.Nova.825940_INMET/BRA_CE_Morada.Nova.825940_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_CE_Quixeramobim.825860_INMET/BRA_CE_Quixeramobim.825860_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_CE_Taua.818720_INMET/BRA_CE_Taua.818720_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_DF_Brasilia-Kubitschek.Intl.AP.833780_TRY.1962/BRA_DF_Brasilia-Kubitschek.Intl.AP.833780_TRY.1962.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_DF_Brasilia.867150_INMET/BRA_DF_Brasilia.867150_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_DF_Planaltina.867160_INMET/BRA_DF_Planaltina.867160_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_ES_Alegre.868280_INMET/BRA_ES_Alegre.868280_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_ES_Alfredo.Chaves.868290_INMET/BRA_ES_Alfredo.Chaves.868290_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_ES_Linhares.868050_INMET/BRA_ES_Linhares.868050_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_ES_Nova.Venecia.867850_INMET/BRA_ES_Nova.Venecia.867850_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_ES_Presidente.Kennedy.868530_INMET/BRA_ES_Presidente.Kennedy.868530_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_ES_Santa.Teresa.868040_INMET/BRA_ES_Santa.Teresa.868040_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_ES_Sao.Mateus.867860_INMET/BRA_ES_Sao.Mateus.867860_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_ES_Vitoria-Salles.AP.836490_TRY.1962/BRA_ES_Vitoria-Salles.AP.836490_TRY.1962.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_ES_Vitoria.868300_INMET/BRA_ES_Vitoria.868300_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Alto.Paraiso.de.Goias.866910_INMET/BRA_GO_Alto.Paraiso.de.Goias.866910_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Aragarcas.833740_INMET/BRA_GO_Aragarcas.833740_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Caiaponia.867300_INMET/BRA_GO_Caiaponia.867300_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Catalao.867770_INMET/BRA_GO_Catalao.867770_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Cristalina.867370_INMET/BRA_GO_Cristalina.867370_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Goianesia.867130_INMET/BRA_GO_Goianesia.867130_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Goiania.834230_INMET/BRA_GO_Goiania.834230_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Goias.867120_INMET/BRA_GO_Goias.867120_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Itapaci.866890_INMET/BRA_GO_Itapaci.866890_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Itumbiara.867740_INMET/BRA_GO_Itumbiara.867740_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Jatai.867520_INMET/BRA_GO_Jatai.867520_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Luziania.867360_INMET/BRA_GO_Luziania.867360_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Mineiros.867510_INMET/BRA_GO_Mineiros.867510_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Monte.Alegre.de.Goias.866700_INMET/BRA_GO_Monte.Alegre.de.Goias.866700_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Morrinhos.867550_INMET/BRA_GO_Morrinhos.867550_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Niquelandia.866900_INMET/BRA_GO_Niquelandia.866900_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Parauna.867320_INMET/BRA_GO_Parauna.867320_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Pires.do.Rio.867560_INMET/BRA_GO_Pires.do.Rio.867560_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Posse.866920_INMET/BRA_GO_Posse.866920_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Rio.Verde.867530_INMET/BRA_GO_Rio.Verde.867530_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_GO_Sao.Simao.867730_INMET/BRA_GO_Sao.Simao.867730_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Alto.Parnaiba.829700_INMET/BRA_MA_Alto.Parnaiba.829700_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Bacabal.817900_INMET/BRA_MA_Bacabal.817900_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Balsas.819030_INMET/BRA_MA_Balsas.819030_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Barra.do.Corda.818250_INMET/BRA_MA_Barra.do.Corda.818250_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Buriticupu.817880_INMET/BRA_MA_Buriticupu.817880_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Carolina.819010_INMET/BRA_MA_Carolina.819010_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Caxias.817920_INMET/BRA_MA_Caxias.817920_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Chapadinha.817490_INMET/BRA_MA_Chapadinha.817490_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Colinas.818660_INMET/BRA_MA_Colinas.818660_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Estreito.818630_INMET/BRA_MA_Estreito.818630_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Farol.Preguicas.817170_INMET/BRA_MA_Farol.Preguicas.817170_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Farol.Santana.822770_INMET/BRA_MA_Farol.Santana.822770_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Grajau.818230_INMET/BRA_MA_Grajau.818230_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Imperatriz.818220_INMET/BRA_MA_Imperatriz.818220_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Sao.Luis-Machado.Intl.AP.822810_TRY.1966/BRA_MA_Sao.Luis-Machado.Intl.AP.822810_TRY.1966.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Sao.Luis.817150_INMET/BRA_MA_Sao.Luis.817150_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MA_Turiacu.821980_INMET/BRA_MA_Turiacu.821980_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Aguas.Vermelhas.867220_INMET/BRA_MG_Aguas.Vermelhas.867220_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Aimores.868030_INMET/BRA_MG_Aimores.868030_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Almenara.867430_INMET/BRA_MG_Almenara.867430_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Araxa.867960_INMET/BRA_MG_Araxa.867960_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Belo.Horizonte-Pampulha.AP.868000_INMET/BRA_MG_Belo.Horizonte-Pampulha.AP.868000_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Buritis.867180_INMET/BRA_MG_Buritis.867180_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Caldas.868460_INMET/BRA_MG_Caldas.868460_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Capelinha.867610_INMET/BRA_MG_Capelinha.867610_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Carangola.868230_INMET/BRA_MG_Carangola.868230_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Caratinga.835920_INMET/BRA_MG_Caratinga.835920_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Chapada.Gaucha.867190_INMET/BRA_MG_Chapada.Gaucha.867190_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Conceicao.das.Alagoas.867940_INMET/BRA_MG_Conceicao.das.Alagoas.867940_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Curvelo.867800_INMET/BRA_MG_Curvelo.867800_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Diamantina.AP.867810_INMET/BRA_MG_Diamantina.AP.867810_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Dores.do.Indaia.867970_INMET/BRA_MG_Dores.do.Indaia.867970_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Espinosa.866950_INMET/BRA_MG_Espinosa.866950_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Florestal.867980_INMET/BRA_MG_Florestal.867980_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Formiga.868200_INMET/BRA_MG_Formiga.868200_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Governador.Valadares.835430_INMET/BRA_MG_Governador.Valadares.835430_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Guarda-Mor.867570_INMET/BRA_MG_Guarda-Mor.867570_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Ibirite.868210_INMET/BRA_MG_Ibirite.868210_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Itaobim.867420_INMET/BRA_MG_Itaobim.867420_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Ituiutaba.867750_INMET/BRA_MG_Ituiutaba.867750_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Joao.Pinheiro.AP.867580_INMET/BRA_MG_Joao.Pinheiro.AP.867580_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Juiz.de.Fora.836920_INMET/BRA_MG_Juiz.de.Fora.836920_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Mantena.867840_INMET/BRA_MG_Mantena.867840_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Maria.da.Fe.830150_INMET/BRA_MG_Maria.da.Fe.830150_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Mocambinho.867200_INMET/BRA_MG_Mocambinho.867200_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Montalvania.866930_INMET/BRA_MG_Montalvania.866930_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Monte.Verde.AP.868700_INMET/BRA_MG_Monte.Verde.AP.868700_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Montes.Claros.867400_INMET/BRA_MG_Montes.Claros.867400_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Muriae.868520_INMET/BRA_MG_Muriae.868520_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Ouro.Branco.868230_INMET/BRA_MG_Ouro.Branco.868230_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Passa.Quatro.837370_INMET/BRA_MG_Passa.Quatro.837370_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Passos.868190_INMET/BRA_MG_Passos.868190_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Patrocinio.867780_INMET/BRA_MG_Patrocinio.867780_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Pirapora.AP.867590_INMET/BRA_MG_Pirapora.AP.867590_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Rio.Pardo.de.Minas.867210_INMET/BRA_MG_Rio.Pardo.de.Minas.867210_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Sacramento.867950_INMET/BRA_MG_Sacramento.867950_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Salinas.867410_INMET/BRA_MG_Salinas.867410_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Sao.Joao.del.Rei.836880_INMET/BRA_MG_Sao.Joao.del.Rei.836880_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Sao.Romao.867390_INMET/BRA_MG_Sao.Romao.867390_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Serra.dos.Aimores.867630_INMET/BRA_MG_Serra.dos.Aimores.867630_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Teofilo.Otoni.867620_INMET/BRA_MG_Teofilo.Otoni.867620_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Timoteo.868010_INMET/BRA_MG_Timoteo.868010_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Tres.Marias.867790_INMET/BRA_MG_Tres.Marias.867790_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Uberlandia.867760_INMET/BRA_MG_Uberlandia.867760_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Unai.AP.834280_INMET/BRA_MG_Unai.AP.834280_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Varginha.868480_INMET/BRA_MG_Varginha.868480_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MG_Vicosa.836420_INMET/BRA_MG_Vicosa.836420_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Amambai.868940_INMET/BRA_MS_Amambai.868940_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Campo.Grande.Intl.AP.868100_INMET/BRA_MS_Campo.Grande.Intl.AP.868100_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Chapadao.do.Sul.867720_INMET/BRA_MS_Chapadao.do.Sul.867720_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Corumba.Intl.AP.835520_INMET/BRA_MS_Corumba.Intl.AP.835520_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Coxim.867700_INMET/BRA_MS_Coxim.867700_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Dourados.836590_INMET/BRA_MS_Dourados.836590_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Ivinhema.868600_INMET/BRA_MS_Ivinhema.868600_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Juti.868590_INMET/BRA_MS_Juti.868590_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Miranda.868070_INMET/BRA_MS_Miranda.868070_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Nhumirim.867680_INMET/BRA_MS_Nhumirim.867680_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Ponta.Pora.868570_INMET/BRA_MS_Ponta.Pora.868570_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Porto.Murtinho.AP.868330_INMET/BRA_MS_Porto.Murtinho.AP.868330_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Rio.Brilhante.868360_INMET/BRA_MS_Rio.Brilhante.868360_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Sete.Quedas.868950_INMET/BRA_MS_Sete.Quedas.868950_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Sidrolandia.868090_INMET/BRA_MS_Sidrolandia.868090_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MS_Tres.Lagoas.AP.868130_INMET/BRA_MS_Tres.Lagoas.AP.868130_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Agua.Boa.866860_INMET/BRA_MT_Agua.Boa.866860_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Alto.Taquari.867500_INMET/BRA_MT_Alto.Taquari.867500_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Apiacas.819760_INMET/BRA_MT_Apiacas.819760_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Campo.Novo.do.Parecis.866620_INMET/BRA_MT_Campo.Novo.do.Parecis.866620_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Campo.Verde.867070_INMET/BRA_MT_Campo.Verde.867070_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Carlinda.819780_INMET/BRA_MT_Carlinda.819780_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Comodoro.866610_INMET/BRA_MT_Comodoro.866610_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Confresa.866060_INMET/BRA_MT_Confresa.866060_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Cotriguacu.829270_INMET/BRA_MT_Cotriguacu.829270_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Cuiaba.867050_INMET/BRA_MT_Cuiaba.867050_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Gaucha.do.Norte.866660_INMET/BRA_MT_Gaucha.do.Norte.866660_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Guaranta.do.Norte.819790_INMET/BRA_MT_Guaranta.do.Norte.819790_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Guiratinga.867290_INMET/BRA_MT_Guiratinga.867290_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Itiquira.867480_INMET/BRA_MT_Itiquira.867480_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Juara.866250_INMET/BRA_MT_Juara.866250_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Juina.866240_INMET/BRA_MT_Juina.866240_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Nova.Maringa.866630_INMET/BRA_MT_Nova.Maringa.866630_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Novo.Mundo.866430_INMET/BRA_MT_Novo.Mundo.866430_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Paranatinga.866840_INMET/BRA_MT_Paranatinga.866840_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Pontes.de.Lacerda.867020_INMET/BRA_MT_Pontes.de.Lacerda.867020_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Porto.Estrela.867040_INMET/BRA_MT_Porto.Estrela.867040_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Querencia.866470_INMET/BRA_MT_Querencia.866470_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Rondonopolis.867280_INMET/BRA_MT_Rondonopolis.867280_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Salto.do.Ceu.867030_INMET/BRA_MT_Salto.do.Ceu.867030_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Santo.Antonio.do.Leste.866850_INMET/BRA_MT_Santo.Antonio.do.Leste.866850_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Sao.Felix.do.Araguaia.866280_INMET/BRA_MT_Sao.Felix.do.Araguaia.866280_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Sao.Jose.do.Rio.Claro.866640_INMET/BRA_MT_Sao.Jose.do.Rio.Claro.866640_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Sinop.866260_INMET/BRA_MT_Sinop.866260_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Sorriso.866450_INMET/BRA_MT_Sorriso.866450_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Tangara.da.Serra.866820_INMET/BRA_MT_Tangara.da.Serra.866820_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_MT_Vila.Bela.da.Santissima.Trindade.867010_INMET/BRA_MT_Vila.Bela.da.Santissima.Trindade.867010_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Belem-Ribeiro.Intl.AP.821930_TRY.1964/BRA_PA_Belem-Ribeiro.Intl.AP.821930_TRY.1964.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Belem.816800_INMET/BRA_PA_Belem.816800_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Braganca.816850_INMET/BRA_PA_Braganca.816850_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Cameta.817100_INMET/BRA_PA_Cameta.817100_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Castanhal.816820_INMET/BRA_PA_Castanhal.816820_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Conceicao.do.Araguaia.819400_INMET/BRA_PA_Conceicao.do.Araguaia.819400_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Itaituba.817780_INMET/BRA_PA_Itaituba.817780_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Maraba.825620_INMET/BRA_PA_Maraba.825620_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Novo.Repartimento.817840_INMET/BRA_PA_Novo.Repartimento.817840_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Pacaja.817420_INMET/BRA_PA_Pacaja.817420_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Paragominas.817450_INMET/BRA_PA_Paragominas.817450_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Placas.817370_INMET/BRA_PA_Placas.817370_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Rondon.do.Para.817860_INMET/BRA_PA_Rondon.do.Para.817860_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Salinopolis.816600_INMET/BRA_PA_Salinopolis.816600_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Santana.do.Araguaia.819820_INMET/BRA_PA_Santana.do.Araguaia.819820_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Serra.dos.Carajas.818600_INMET/BRA_PA_Serra.dos.Carajas.818600_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Soure.821410_INMET/BRA_PA_Soure.821410_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Tome.Acu.817110_INMET/BRA_PA_Tome.Acu.817110_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PA_Tucurui.817430_INMET/BRA_PA_Tucurui.817430_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PB_Areia.818770_INMET/BRA_PB_Areia.818770_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PB_Cabaceiras.819150_INMET/BRA_PB_Cabaceiras.819150_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PB_Camaratuba.818780_INMET/BRA_PB_Camaratuba.818780_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PB_Campina.Grande.819160_INMET/BRA_PB_Campina.Grande.819160_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PB_Joao.Pessoa.819180_INMET/BRA_PB_Joao.Pessoa.819180_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PB_Monteiro.819140_INMET/BRA_PB_Monteiro.819140_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PB_Patos.819130_INMET/BRA_PB_Patos.819130_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PB_Sao.Goncalo.817740_INMET/BRA_PB_Sao.Goncalo.817740_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PE_Arcoverde.819530_INMET/BRA_PE_Arcoverde.819530_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PE_Cabrobo.828860_INMET/BRA_PE_Cabrobo.828860_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PE_Caruaru.828950_INMET/BRA_PE_Caruaru.828950_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PE_Floresta.819770_INMET/BRA_PE_Floresta.819770_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PE_Garanhuns.819550_INMET/BRA_PE_Garanhuns.819550_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PE_Ibimirim.819540_INMET/BRA_PE_Ibimirim.819540_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PE_Palmares.819570_INMET/BRA_PE_Palmares.819570_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PE_Petrolina.819910_INMET/BRA_PE_Petrolina.819910_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PE_Recife-Guararapes-Freyre.Intl.AP.828990_TRY.1962/BRA_PE_Recife-Guararapes-Freyre.Intl.AP.828990_TRY.1962.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PE_Recife.819580_INMET/BRA_PE_Recife.819580_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PE_Serra.Talhada.819120_INMET/BRA_PE_Serra.Talhada.819120_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PE_Surubim.819170_INMET/BRA_PE_Surubim.819170_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Alvorada.do.Gurgueia.818460_INMET/BRA_PI_Alvorada.do.Gurgueia.818460_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Bom.Jesus.do.Piaui.829750_INMET/BRA_PI_Bom.Jesus.do.Piaui.829750_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Caracol.819880_INMET/BRA_PI_Caracol.819880_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Castelo.do.Piaui.818290_INMET/BRA_PI_Castelo.do.Piaui.818290_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Esperantina.817510_INMET/BRA_PI_Esperantina.817510_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Floriano.818680_INMET/BRA_PI_Floriano.818680_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Gilbues.819860_INMET/BRA_PI_Gilbues.819860_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Oeiras.818690_INMET/BRA_PI_Oeiras.818690_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Parnaiba.817520_INMET/BRA_PI_Parnaiba.817520_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Paulistana.828820_INMET/BRA_PI_Paulistana.828820_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Picos.827910_INMET/BRA_PI_Picos.827910_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Piripiri.817940_INMET/BRA_PI_Piripiri.817940_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Sao.Joao.do.Piaui.818480_INMET/BRA_PI_Sao.Joao.do.Piaui.818480_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Sao.Pedro.do.Piaui.818280_INMET/BRA_PI_Sao.Pedro.do.Piaui.818280_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Sao.Raimundo.Nonato.819890_INMET/BRA_PI_Sao.Raimundo.Nonato.819890_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Teresina.818320_INMET/BRA_PI_Teresina.818320_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Urucui.819050_INMET/BRA_PI_Urucui.819050_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PI_Valenca.do.Piaui.818700_INMET/BRA_PI_Valenca.do.Piaui.818700_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Castro.869210_INMET/BRA_PR_Castro.869210_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Cidade.Gaucha.868980_INMET/BRA_PR_Cidade.Gaucha.868980_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Clevelandia.869390_INMET/BRA_PR_Clevelandia.869390_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Curitiba.838420_INMET/BRA_PR_Curitiba.838420_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Diamante.do.Norte.868610_INMET/BRA_PR_Diamante.do.Norte.868610_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Dois.Vizinhos.869270_INMET/BRA_PR_Dois.Vizinhos.869270_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Foz.do.Iguacu-Cataratas.Intl.AP.869250_INMET/BRA_PR_Foz.do.Iguacu-Cataratas.Intl.AP.869250_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_General.Carneiro.869410_INMET/BRA_PR_General.Carneiro.869410_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Ibaiti.869020_INMET/BRA_PR_Ibaiti.869020_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Icaraima.868970_INMET/BRA_PR_Icaraima.868970_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Ilha.do.Mel.869350_INMET/BRA_PR_Ilha.do.Mel.869350_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Inacio.Martins.869290_INMET/BRA_PR_Inacio.Martins.869290_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Ivai.869300_INMET/BRA_PR_Ivai.869300_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Joaquim.Tavora.869030_INMET/BRA_PR_Joaquim.Tavora.869030_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Londrina.837680_INMET/BRA_PR_Londrina.837680_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Marechal.Candido.Rondon.869160_INMET/BRA_PR_Marechal.Candido.Rondon.869160_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Maringa.868990_INMET/BRA_PR_Maringa.868990_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Maringa.AP.868990_TRY.1991/BRA_PR_Maringa.AP.868990_TRY.1991.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Nova.Fatima.869010_INMET/BRA_PR_Nova.Fatima.869010_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Nova.Tebas.869190_INMET/BRA_PR_Nova.Tebas.869190_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Paranapoema.868620_INMET/BRA_PR_Paranapoema.868620_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_PR_Planalto.869260_INMET/BRA_PR_Planalto.869260_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Arraial.do.Cabo.868920_INMET/BRA_RJ_Arraial.do.Cabo.868920_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Cambuci.868540_INMET/BRA_RJ_Cambuci.868540_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Campos.dos.Goytacazes.868550_INMET/BRA_RJ_Campos.dos.Goytacazes.868550_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Duque.de.Caxias-Xerem.868770_INMET/BRA_RJ_Duque.de.Caxias-Xerem.868770_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Farol.de.Sao.Tome.868900_INMET/BRA_RJ_Farol.de.Sao.Tome.868900_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Macae.868910_INMET/BRA_RJ_Macae.868910_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Niteroi.868810_INMET/BRA_RJ_Niteroi.868810_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Paraty.869130_INMET/BRA_RJ_Paraty.869130_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Petropolis-Pico.do.Couto.868760_INMET/BRA_RJ_Petropolis-Pico.do.Couto.868760_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Resende.837380_INMET/BRA_RJ_Resende.837380_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Rio.de.Janeiro-Galeao-Jobim.Intl.AP.837460_TRY.1963/BRA_RJ_Rio.de.Janeiro-Galeao-Jobim.Intl.AP.837460_TRY.1963.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Rio.de.Janeiro-Vila.Militar.868790_INMET/BRA_RJ_Rio.de.Janeiro-Vila.Militar.868790_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Teresopolis.868880_INMET/BRA_RJ_Teresopolis.868880_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RJ_Valenca.868750_INMET/BRA_RJ_Valenca.868750_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RN_Apodi.818350_INMET/BRA_RN_Apodi.818350_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RN_Caico.818750_INMET/BRA_RN_Caico.818750_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RN_Macau.818360_INMET/BRA_RN_Macau.818360_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RN_Mossoro.818340_INMET/BRA_RN_Mossoro.818340_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RN_Natal.818390_INMET/BRA_RN_Natal.818390_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RN_Touros.818380_INMET/BRA_RN_Touros.818380_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RO_Ariquemes.819700_INMET/BRA_RO_Ariquemes.819700_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RO_Cacoal.866220_INMET/BRA_RO_Cacoal.866220_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RO_Porto.Velho.819320_INMET/BRA_RO_Porto.Velho.819320_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RO_Vilhena.866420_INMET/BRA_RO_Vilhena.866420_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RR_Boa.Vista.816150_INMET/BRA_RR_Boa.Vista.816150_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Alegrete.869750_INMET/BRA_RS_Alegrete.869750_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Bage.839800_INMET/BRA_RS_Bage.839800_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Bento.Goncalves.869790_INMET/BRA_RS_Bento.Goncalves.869790_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Cacapava.do.Sul.869860_INMET/BRA_RS_Cacapava.do.Sul.869860_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Camaqua.869890_INMET/BRA_RS_Camaqua.869890_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Canela.AP.869800_INMET/BRA_RS_Canela.AP.869800_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Cangucu.869930_INMET/BRA_RS_Cangucu.869930_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Chui.869980_INMET/BRA_RS_Chui.869980_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Cruz.Alta.839120_INMET/BRA_RS_Cruz.Alta.839120_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Erechim.869540_INMET/BRA_RS_Erechim.869540_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Frederico.Westphalen.869510_INMET/BRA_RS_Frederico.Westphalen.869510_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Jaguarao.869960_INMET/BRA_RS_Jaguarao.869960_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Lagoa.Vermelha.869650_INMET/BRA_RS_Lagoa.Vermelha.869650_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Mostardas.839700_INMET/BRA_RS_Mostardas.839700_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Palmeira.das.Missoes.869530_INMET/BRA_RS_Palmeira.das.Missoes.869530_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Passo.Fundo.869630_INMET/BRA_RS_Passo.Fundo.869630_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Porto.Alegre.869880_INMET/BRA_RS_Porto.Alegre.869880_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Quarai.869820_INMET/BRA_RS_Quarai.869820_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Rio.Pardo.869780_INMET/BRA_RS_Rio.Pardo.869780_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Santa.Maria.839360_INMET/BRA_RS_Santa.Maria.839360_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Santana.do.Livramento.839530_INMET/BRA_RS_Santana.do.Livramento.839530_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Santiago.869760_INMET/BRA_RS_Santiago.869760_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Santo.Augusto.869520_INMET/BRA_RS_Santo.Augusto.869520_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Sao.Borja.869600_INMET/BRA_RS_Sao.Borja.869600_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Sao.Gabriel.869840_INMET/BRA_RS_Sao.Gabriel.869840_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Sao.Jose.dos.Ausentes.869670_INMET/BRA_RS_Sao.Jose.dos.Ausentes.869670_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Sao.Luiz.Gonzaga.869610_INMET/BRA_RS_Sao.Luiz.Gonzaga.869610_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Soledade.869640_INMET/BRA_RS_Soledade.869640_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Torres.869810_INMET/BRA_RS_Torres.869810_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Tramandai.869900_INMET/BRA_RS_Tramandai.869900_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Uruguaiana.869730_INMET/BRA_RS_Uruguaiana.869730_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_RS_Vacaria.869660_INMET/BRA_RS_Vacaria.869660_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Ararangua.869710_INMET/BRA_SC_Ararangua.869710_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Cacador.869430_INMET/BRA_SC_Cacador.869430_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Curitibanos.AP.869560_INMET/BRA_SC_Curitibanos.AP.869560_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Dionisio.Cerqueira.869360_INMET/BRA_SC_Dionisio.Cerqueira.869360_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Florianopolis-Luz.AP.838990_TRY.1963/BRA_SC_Florianopolis-Luz.AP.838990_TRY.1963.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Florianopolis.838970_INMET/BRA_SC_Florianopolis.838970_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Indaial.838720_INMET/BRA_SC_Indaial.838720_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Itapoa.869470_INMET/BRA_SC_Itapoa.869470_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Ituporanga.869570_INMET/BRA_SC_Ituporanga.869570_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Joacaba-Santa.Terezinha.Muni.AP.869550_INMET/BRA_SC_Joacaba-Santa.Terezinha.Muni.AP.869550_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Major.Vieira.869420_INMET/BRA_SC_Major.Vieira.869420_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Novo.Horizonte.869380_INMET/BRA_SC_Novo.Horizonte.869380_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Rio.Negrinho.869450_INMET/BRA_SC_Rio.Negrinho.869450_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Santa.Marta.839250_INMET/BRA_SC_Santa.Marta.839250_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Sao.Joaquim.869690_INMET/BRA_SC_Sao.Joaquim.869690_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Sao.Miguel.do.Oeste.AP.869370_INMET/BRA_SC_Sao.Miguel.do.Oeste.AP.869370_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Urubici.869680_INMET/BRA_SC_Urubici.869680_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Urussanga.869700_INMET/BRA_SC_Urussanga.869700_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SC_Xanxere.869400_INMET/BRA_SC_Xanxere.869400_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SE_Aracaju.866160_INMET/BRA_SE_Aracaju.866160_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SE_Brejo.Grande.866180_INMET/BRA_SE_Brejo.Grande.866180_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SE_Carira.866150_INMET/BRA_SE_Carira.866150_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SE_Itabaianinha.866380_INMET/BRA_SE_Itabaianinha.866380_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SE_Poco.Verde.866140_INMET/BRA_SE_Poco.Verde.866140_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Ariranha.868410_INMET/BRA_SP_Ariranha.868410_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Avare.869040_INMET/BRA_SP_Avare.869040_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Bauru.837220_INMET/BRA_SP_Bauru.837220_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Campinas.837210_INMET/BRA_SP_Campinas.837210_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Campos.do.Jordao.868720_INMET/BRA_SP_Campos.do.Jordao.868720_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Casa.Branca.868440_INMET/BRA_SP_Casa.Branca.868440_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Franca.868180_INMET/BRA_SP_Franca.868180_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Ibitinga.868430_INMET/BRA_SP_Ibitinga.868430_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Iguape.869230_INMET/BRA_SP_Iguape.869230_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Itapeva.837740_INMET/BRA_SP_Itapeva.837740_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Itapira.868690_INMET/BRA_SP_Itapira.868690_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Ituverava.868170_INMET/BRA_SP_Ituverava.868170_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Jales.868140_INMET/BRA_SP_Jales.868140_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Jose.Bonifacio.868390_INMET/BRA_SP_Jose.Bonifacio.868390_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Lins.868400_INMET/BRA_SP_Lins.868400_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Ourinhos.868660_INMET/BRA_SP_Ourinhos.868660_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Piracicaba.868680_INMET/BRA_SP_Piracicaba.868680_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Presidente.Prudente.837160_INMET/BRA_SP_Presidente.Prudente.837160_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Rancharia.868640_INMET/BRA_SP_Rancharia.868640_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Sao.Carlos.868450_INMET/BRA_SP_Sao.Carlos.868450_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Sao.Luis.do.Paraitinga.869120_INMET/BRA_SP_Sao.Luis.do.Paraitinga.869120_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Sao.Paulo-Congonhas.AP.837800_TRY.1954/BRA_SP_Sao.Paulo-Congonhas.AP.837800_TRY.1954.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Sao.Paulo.837810_INMET/BRA_SP_Sao.Paulo.837810_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Sorocaba.838510_INMET/BRA_SP_Sorocaba.838510_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Taubate.869110_INMET/BRA_SP_Taubate.869110_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Valparaiso.868380_INMET/BRA_SP_Valparaiso.868380_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_SP_Votuporanga.868150_INMET/BRA_SP_Votuporanga.868150_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_TO_Araguaina.819000_INMET/BRA_TO_Araguaina.819000_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_TO_Araguatins.818210_INMET/BRA_TO_Araguatins.818210_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_TO_Dianopolis.866320_INMET/BRA_TO_Dianopolis.866320_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_TO_Formoso.do.Araguaia.866290_INMET/BRA_TO_Formoso.do.Araguaia.866290_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_TO_Gurupi.866300_INMET/BRA_TO_Gurupi.866300_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_TO_Palmas.866070_INMET/BRA_TO_Palmas.866070_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_TO_Parana.866500_INMET/BRA_TO_Parana.866500_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_TO_Pedro.Afonso.819410_INMET/BRA_TO_Pedro.Afonso.819410_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_TO_Peixe.866490_INMET/BRA_TO_Peixe.866490_INMET.epw'
        ]
        df = []
        for location in data['features']:
            match = re.search(r'href=[\'"]?([^\'" >]+)', location['properties']['epw'])
            if match:
                url = match.group(1)
                if (url not in filter_list) and ('SWEC' not in url): #Remove SWEC files
                    url_str = url.split('/')
                    if len(url_str) == 7:
                        url_str = url_str[0:5]+[None]+url_str[5:7]
                    url_str += [url]
                    url_str += location['geometry']['coordinates']
                    df.append(url_str)
        
        df = pd.DataFrame(df)
        df = df.drop([0, 1, 2, 7], axis = 1)
        df = df.rename(columns={3: 'region', 4: 'country', 5: 'state', 6: 'title', 8: 'file_url', 9: 'lon', 10: 'lat'})
        df['title'] = df['title'].apply(lambda x: ' '.join(re.split('_|\.', str(x))))

        if 'filter_option' in st.session_state:
            if st.session_state.filter_option == self.filter_list:
                df = df.sort_values(['region', 'country', 'state'])
            elif st.session_state.filter_option == self.sort_list:
                df = self._sort_list_by_distance(df)
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
        regions = self.df['region'].unique()
        regions_dropdown = [{
            "title": "All", 
            "pf": 'all', 
        }] * (len(regions) + 1)
        countries_dropdown = {"All": ['All']}
        states_dropdown = {"All": ['All']}
        for i in range(len(regions)):
            regions_str = regions[i].split('_')
            for j in range(len(regions_str)):
                if (regions_str[j] == 'wmo'):
                    regions_str[j] = regions_str[j].upper()
                elif (regions_str[j] != 'and'):
                    regions_str[j] = regions_str[j].capitalize()
                else:
                    regions_str[j] = regions_str[j]
            # regions_str = [regions_str[j].upper() if (regions_str[j] == 'wmo') else regions_str[j].capitalize() if (regions_str[j] != 'and') else regions_str[j] for j in range(len(regions_str))]
            regions_dropdown_title = ' '.join(regions_str)
            regions_dropdown[int(regions_str[-1])] = {
                "title": regions_dropdown_title,
                "pf": regions[i]
            }

            countries_dropdown_individual_region = self.df[self.df['region'] == regions[i]]['country'].unique().tolist()        
            countries_dropdown[regions[i]] = ['All in Region '+regions[i][-1]] + countries_dropdown_individual_region
            for j in range(len(countries_dropdown_individual_region)):        
                states_dropdown_individual_country = self.df[self.df['country'] == countries_dropdown_individual_region[j]]['state'].unique().tolist()
                states_dropdown_individual_country = list(filter(None, states_dropdown_individual_country))
                states_dropdown[countries_dropdown_individual_region[j]] = ['All in '+countries_dropdown_individual_region[j]] + states_dropdown_individual_country

        weather_data_dropdown = self.df[['region', 'country', 'state', 'title', 'file_url']].to_dict('records')
        return regions_dropdown, countries_dropdown, states_dropdown, weather_data_dropdown
   
    # This method is callback. This method resets the settings when another radio option is selected.
    def _filter_settings_reset(self):
        if 'filter_option' in st.session_state:
            if st.session_state.filter_option != self.sort_list:
                if 'user_lat' in st.session_state:
                    st.session_state.user_lat = self.default_lat
                if 'user_lng' in st.session_state:
                    st.session_state.user_lng = self.default_lon
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
        expander = st.sidebar.expander(label='Weather Data Search')
        with expander:
            st.radio("Search", [self.sort_list, self.filter_list], key='filter_option', on_change=self._filter_settings_reset)

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
                    epw_col1, epw_col2 = st.columns(2)
                    
                    if 'region' in st.session_state:
                        if st.session_state.region['title'] == 'All':
                            countries_dropdown = []
                        else:
                            countries_dropdown = countries_dropdown[st.session_state.region['pf']]
                    epw_col1.selectbox("Country", countries_dropdown, key='country')
                    
                    states_dropdown_options = []
                    if self._check_if_a_valid_option_is_selected('country', 'All in'):
                        if len(states_dropdown[st.session_state.country]) > 1:
                            states_dropdown_options = states_dropdown[st.session_state.country] 
                    
                    epw_col2.selectbox("State", states_dropdown_options, key='state')
                    
                    if self._check_if_a_valid_option_is_selected('region', 'all'):
                        if self._check_if_a_valid_option_is_selected('country', 'All in'):
                            if self._check_if_a_valid_option_is_selected('state', 'All in'):
                                results = []
                                for item in weather_data_dropdown:
                                    if item['state'] is not None:
                                        if item['state'] in st.session_state.state:
                                            results.append(item)
                                weather_data_dropdown = results                              
                            else: 
                                weather_data_dropdown = [ d for d in weather_data_dropdown if d['country'] in st.session_state.country]
                        else:
                            weather_data_dropdown = [ d for d in weather_data_dropdown if d['region'] in st.session_state.region['pf']]   

        self.file_name = st.sidebar.selectbox(
            'Weather Data File List', 
            weather_data_dropdown,
            format_func=lambda x: x['title'],
            help="A list of available weather data files (Keyword Search Enabled)"
        )      
        
        # return file_name



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
