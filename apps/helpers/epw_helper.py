import streamlit as st
import tempfile
from urllib.request import Request, urlopen
import pandas as pd
import csv
import operator
from apps.helpers.helper import Helper

# -*- coding: utf-8 -*-
# General naming convention:
# func(): methods to be called by user
# _func(): assisting methods called by system
class EPWHelper(Helper):  
    def __init__(self):
        Helper.__init__(self)
        self.headers={}
        self.dataframe=pd.DataFrame() 
        self.lat = None
        self.longitude = None
        self.timezone = None  
        self.file_list = []  

    # This is the method (along with its subequent assisting methods) to read the epw file
    def read_epw_f(self, url):
        name = url[url.rfind('/') + 1:]                                         # Extract filename out of url
        response = Request(url, headers={'User-Agent' : "Magic Browser"})     
        with tempfile.TemporaryDirectory() as tmpdirname:                       # temp folder for storing the file during extraction
            with open(tmpdirname + name, 'wb') as f:
                f.write(urlopen(response).read())
                self._read(tmpdirname+name)                                     # read file
                f.close()
        return self.dataframe, self.headers
    
    def _read(self,fp):
        self.headers=self._read_headers(fp)
        self.dataframe=self._read_data(fp)
        self.lat = float(self.headers['LOCATION'][5])
        self.longitude = float(self.headers['LOCATION'][6])
        self.timezone = float(self.headers['LOCATION'][7])
        
    def _read_headers(self,fp):
        d={}
        with open(fp, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                if row[0].isdigit():
                    break
                else:
                    d[row[0]]=row[1:]
            csvfile.close()
        return d
    
    def _read_data(self,fp):
        names=[
            'Year',
            'Month',
            'Day',
            'Hour',
            'Minute',
            'Data Source and Uncertainty Flags',
            'Dry Bulb Temperature',
            'Dew Point Temperature',
            'Relative Humidity',
            'Atmospheric Station Pressure',
            'Extraterrestrial Horizontal Radiation',
            'Extraterrestrial Direct Normal Radiation',
            'Horizontal Infrared Radiation Intensity',
            'Global Horizontal Radiation',
            'Direct Normal Radiation',
            'Diffuse Horizontal Radiation',
            'Global Horizontal Illuminance',
            'Direct Normal Illuminance',
            'Diffuse Horizontal Illuminance',
            'Zenith Luminance',
            'Wind Direction',
            'Wind Speed',
            'Total Sky Cover',
            'Opaque Sky Cover (used if Horizontal IR Intensity missing)',
            'Visibility',
            'Ceiling Height',
            'Present Weather Observation',
            'Present Weather Codes',
            'Precipitable Water',
            'Aerosol Optical Depth',
            'Snow Depth',
            'Days Since Last Snowfall',
            'Albedo',
            'Liquid Precipitation Depth',
            'Liquid Precipitation Quantity'
        ]
        
        first_row = self._first_row_with_climate_data(fp)
        df = pd.read_csv(fp,
                       skiprows=first_row,
                       header=None,
                       names=names,
        )

        # extract only the useful columns
        df = df[
            [
            # 'Year',
            'Month',
            'Day',
            'Hour',
            # 'Minute',
            # 'Data Source and Uncertainty Flags',
            'Dry Bulb Temperature',
            # 'Dew Point Temperature',
            'Relative Humidity',
            # 'Atmospheric Station Pressure',
            # 'Extraterrestrial Horizontal Radiation',
            # 'Extraterrestrial Direct Normal Radiation',
            # 'Horizontal Infrared Radiation Intensity',
            'Global Horizontal Radiation',
            # 'Direct Normal Radiation',
            'Diffuse Horizontal Radiation',
            # 'Global Horizontal Illuminance',
            # 'Direct Normal Illuminance',
            # 'Diffuse Horizontal Illuminance',
            # 'Zenith Luminance',
            'Wind Direction',
            'Wind Speed',
            # 'Total Sky Cover',
            # 'Opaque Sky Cover (used if Horizontal IR Intensity missing)',
            # 'Visibility',
            # 'Ceiling Height',
            # 'Present Weather Observation',
            # 'Present Weather Codes',
            # 'Precipitable Water',
            # 'Aerosol Optical Depth',
            # 'Snow Depth',
            # 'Days Since Last Snowfall',
            # 'Albedo',
            # 'Liquid Precipitation Depth',
            # 'Liquid Precipitation Quantity'
            ]
        ]
        return df
        
    def _first_row_with_climate_data(self,fp):
        with open(fp, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for i,row in enumerate(csvreader):
                if row[0].isdigit():
                    break
            csvfile.close()
        return i 
    



    # This method is called in loading sequence 4, app.run(), app.py, to convert the weather data file dataframe to list.
    # It is currently of no use so it's commented
    # def epw_to_file_list(self):
    #     # Add the first 3 rows of headings (optional(?) implemented to bridge the workflow of backend script)
    #     self.file_list.extend(
    #         [
    #             [self.headers['LOCATION'][0], ' -', self.headers['LOCATION'][2], self.headers['LOCATION'][5], self.headers['LOCATION'][6], self.headers['LOCATION'][7]], 
    #             ['month', 'day', 'hour', 'Dry Bulb Temp', 'Rel Humidity', 'Global Horiz Rad', 'Diffuse Rad', 'Wind Speed', 'Wind Direction', ''], 
    #             [' ', ' ', ' ', 'degrees C', 'percent', '(Wh/sq.m)', '(Wh/sq.m)', 'ms', 'degrees', '']
    #         ]
    #     )
    #     # This is where the unwanted columns in the dataframe gets filtered out. 
    #     self.file_list.extend(
    #         self.dataframe[
    #             ['Month', 'Day', 'Hour', 'Dry Bulb Temperature', 'Relative Humidity', 'Global Horizontal Radiation', 'Diffuse Horizontal Radiation', 'Wind Speed', 'Wind Direction']
    #         ].values.tolist()
    #     )
        
    #     return self.file_list


    # This method passes the time filter parameters to _time_filter_pipeline for filtering
    def epw_filter(self, file_title):
        # Read the corresponding filter parameters from st.session_state according to feature (file_title)
        time_var = self.time_var.copy()
        for feature in self.features:
            if feature['file_title'] == file_title:
                for var in time_var.keys():
                    if feature['file_title']+"_"+var in st.session_state:
                        if (var == 'start_month') | (var == 'end_month'):
                            time_var[var] = st.session_state[feature['file_title']+"_"+var]['value']
                        else:
                            time_var[var] = st.session_state[feature['file_title']+"_"+var]
        
        # filter by day and month
        direction = (time_var['end_month'] > time_var['start_month']) | ((time_var['end_month'] == time_var['start_month']) & (time_var['end_day'] >= time_var['start_day']))
        range = (
            (
            (self.dataframe['Month'] > time_var['start_month']) | 
            ((self.dataframe['Month'] == time_var['start_month']) & (self.dataframe['Day'] >= time_var['start_day']))
            ),
            (
            ((self.dataframe['Month'] < time_var['end_month']) | 
            (self.dataframe['Month'] == time_var['end_month']) & (self.dataframe['Day'] <= time_var['end_day']))
            )
        )
        self.dataframe = self._epw_filter_pipeline(direction, range)
        
        # filter by hour
        direction = (time_var['end_hour'] >= time_var['start_hour'])
        range = (
            (self.dataframe['Hour'] >= time_var['start_hour']),
            (self.dataframe['Hour'] <= time_var['end_hour'])       
        )
        self.dataframe = self._epw_filter_pipeline(direction, range)
        
        return self.dataframe

    # This method filters the data
    def _epw_filter_pipeline(self, op_cond, range):
        #
        # Operator AND is used (op_cond = True) if in dropdowns start month is before end month e.g. start: Feb, end: Nov
        # e.g. May is valid out because it is after Feb **AND** before Nov
        # 
        # Operator OR is used (op_cond = False) if start month is after end month e.g. start: Nov, end: Feb, as it
        # indicates the desired range is Jan to Feb and Nov to Dec
        # e.g. Jan is valid because it is after Nov **OR** before Feb
        #
        filter_operator = operator.__and__ if op_cond else operator.__or__
        self.dataframe = self.dataframe.loc[filter_operator(range[0], range[1])]
        return self.dataframe


