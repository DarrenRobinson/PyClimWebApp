# -*- coding: utf-8 -*-

import tempfile
from urllib.request import Request, urlopen
import pandas as pd
import csv

class epw():  
    def __init__(self):
        self.headers={}
        self.dataframe=pd.DataFrame()   
    
    def _read(self,fp):
        self.headers=self._read_headers(fp)
        self.dataframe=self._read_data(fp)
        
    def _read_headers(self,fp):
        d={}
        with open(fp, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                if row[0].isdigit():
                    break
                else:
                    d[row[0]]=row[1:]
        return d
    
    def _read_data(self,fp):
        names=['Year',
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
               'Liquid Precipitation Quantity']
        
        first_row=self._first_row_with_climate_data(fp)
        df=pd.read_csv(fp,
                       skiprows=first_row,
                       header=None,
                       names=names,
                       )
        return df    
        
    def _first_row_with_climate_data(self,fp):
        with open(fp, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for i,row in enumerate(csvreader):
                if row[0].isdigit():
                    break
        return i 
    
    def read_epw_f(self, url):
        name = url[url.rfind('/') + 1:]
        response = Request(url, headers={'User-Agent' : "Magic Browser"}) 
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(tmpdirname + name, 'wb') as f:
                f.write(urlopen(response).read())
                self._read(tmpdirname+name)
                f.close()
        return self.dataframe, self.headers

    def epw_to_file_list(self, epw_file_df, epw_file_header):
        file_list = []
        file_list.extend([[epw_file_header['LOCATION'][0], ' -', epw_file_header['LOCATION'][2], epw_file_header['LOCATION'][5], epw_file_header['LOCATION'][6], epw_file_header['LOCATION'][7]], ['month', 'day', 'hour', 'Dry Bulb Temp', 'Rel Humidity', 'Global Horiz Rad', 'Diffuse Rad', 'Wind Speed', 'Wind Direction', ''], [' ', ' ', ' ', 'degrees C', 'percent', '(Wh/sq.m)', '(Wh/sq.m)', 'ms', 'degrees', '']])
        file_list.extend(epw_file_df[['Month', 'Day', 'Hour', 'Dry Bulb Temperature', 'Relative Humidity', 'Global Horizontal Radiation', 'Diffuse Horizontal Radiation', 'Wind Speed', 'Wind Direction']].values.tolist())
        return file_list
    
    def write(self,fp):
        with open(fp, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for k,v in self.headers.items():
                csvwriter.writerow([k]+v)
            for row in self.dataframe.itertuples(index= False):
                csvwriter.writerow(i for i in row)