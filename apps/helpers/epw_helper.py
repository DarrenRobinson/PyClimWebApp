import streamlit as st
import operator
import math
import pandas as pd
import json
import re
import tempfile
from urllib.request import Request, urlopen
import csv
import pydeck as pdk
# import datetime
# import tracemalloc
# from altair.vegalite.v4.schema.core import Axis
# from ladybug.epw import EPW

# -*- coding: utf-8 -*-
# General naming convention:
# func(): methods to be called by user
# _func(): subsequent assisting methods called by system
class EPWHelper():  
    def __init__(self):
        self.headers={}
        self.dataframe=pd.DataFrame()
        self.lat = None
        self.lng = None
        self.timezone = None
        
        self.sort_list = 'by distance from target site:'
        self.filter_list = 'hierarchically by region:'
        self.file_name = {}
        self.default_lat = 53.4
        self.default_lon = -1.5
        self.df_in_question = [
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
            'https://energyplus-weather.s3.amazonaws.com/south_america_wmo_region_3/BRA/BRA_TO_Peixe.866490_INMET/BRA_TO_Peixe.866490_INMET.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Albacete.082800_SWEC/ESP_Albacete.082800_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Alicante.083600_SWEC/ESP_Alicante.083600_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Almeria.084870_SWEC/ESP_Almeria.084870_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Avila.082100_SWEC/ESP_Avila.082100_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Badajoz.083300_SWEC/ESP_Badajoz.083300_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Barcelona.081810_SWEC/ESP_Barcelona.081810_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Bilbao.08250_SWEC/ESP_Bilbao.08250_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Burgos.080750_SWEC/ESP_Burgos.080750_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Caceres.082610_SWEC/ESP_Caceres.082610_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Castellon.082860_SWEC/ESP_Castellon.082860_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Ceuta.603200_SWEC/ESP_Ceuta.603200_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Cordoba.084100_SWEC/ESP_Cordoba.084100_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Cuenca.082310_SWEC/ESP_Cuenca.082310_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Gerona.081840_SWEC/ESP_Gerona.081840_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Granada.084190_SWEC/ESP_Granada.084190_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Guadalajara.082260_SWEC/ESP_Guadalajara.082260_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Huelva.083830_SWEC/ESP_Huelva.083830_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Huesca.080940_SWEC/ESP_Huesca.080940_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Jaen.084170_SWEC/ESP_Jaen.084170_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_La.Coruna.080010_SWEC/ESP_La.Coruna.080010_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Las.Palmas.600300_SWEC/ESP_Las.Palmas.600300_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Leon.080550_SWEC/ESP_Leon.080550_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Lerida.081710_SWEC/ESP_Lerida.081710_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Logrono.080840_SWEC/ESP_Logrono.080840_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Lugo.080080_SWEC/ESP_Lugo.080080_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Madrid.082210_SWEC/ESP_Madrid.082210_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Malaga.084820_SWEC/ESP_Malaga.084820_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Melilla.603380_SWEC/ESP_Melilla.603380_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Murcia.084300_SWEC/ESP_Murcia.084300_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Orense.080480_SWEC/ESP_Orense.080480_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Oviedo.080150_SWEC/ESP_Oviedo.080150_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Palencia.080720_SWEC/ESP_Palencia.080720_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Palma.083060_SWEC/ESP_Palma.083060_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Pamplona.080850_SWEC/ESP_Pamplona.080850_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Pontevedra.080440_SWEC/ESP_Pontevedra.080440_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Salamanca.082020_SWEC/ESP_Salamanca.082020_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_San.Sebastian.080270_SWEC/ESP_San.Sebastian.080270_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Santander.080230_SWEC/ESP_Santander.080230_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Segovia.082130_SWEC/ESP_Segovia.082130_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Sevilla.083910_SWEC/ESP_Sevilla.083910_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Soria.081480_SWEC/ESP_Soria.081480_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Tarragona.081760_SWEC/ESP_Tarragona.081760_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Tenerife.600200_SWEC/ESP_Tenerife.600200_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Teruel.082350_SWEC/ESP_Teruel.082350_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Toledo.082720_SWEC/ESP_Toledo.082720_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Valencia.082840_SWEC/ESP_Valencia.082840_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Valladolid.081410_SWEC/ESP_Valladolid.081410_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Vitoria.080800_SWEC/ESP_Vitoria.080800_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Zamora.081300_SWEC/ESP_Zamora.081300_SWEC.epw',
            'https://energyplus-weather.s3.amazonaws.com/europe_wmo_region_6/ESP/ESP_Zaragoza.081600_SWEC/ESP_Zaragoza.081600_SWEC.epw'
        ]
        self.country_codes = {
            'AFG': 'Afghanistan',
            'ALA': 'Åland Islands',
            'ALB': 'Albania',
            'DZA': 'Algeria',
            'ASM': 'American Samoa',
            'AND': 'Andorra',
            'AGO': 'Angola',
            'AIA': 'Anguilla',
            'ATA': 'Antarctica',
            'ATG': 'Antigua and Barbuda',
            'ARG': 'Argentina',
            'ARM': 'Armenia',
            'ABW': 'Aruba',
            'AUS': 'Australia',
            'AUT': 'Austria',
            'AZE': 'Azerbaijan',
            'BHS': 'Bahamas',
            'BHR': 'Bahrain',
            'BGD': 'Bangladesh',
            'BRB': 'Barbados',
            'BLR': 'Belarus',
            'BEL': 'Belgium',
            'BLZ': 'Belize',
            'BEN': 'Benin',
            'BMU': 'Bermuda',
            'BTN': 'Bhutan',
            'BOL': 'Bolivia, Plurinational State of',
            'BIH': 'Bosnia and Herzegovina',
            'BWA': 'Botswana',
            'BVT': 'Bouvet Island',
            'BRA': 'Brazil',
            'IOT': 'British Indian Ocean Territory',
            'BRN': 'Brunei Darussalam',
            'BGR': 'Bulgaria',
            'BFA': 'Burkina Faso',
            'BDI': 'Burundi',
            'KHM': 'Cambodia',
            'CMR': 'Cameroon',
            'CAN': 'Canada',
            'CPV': 'Cape Verde',
            'CYM': 'Cayman Islands',
            'CAF': 'Central African Republic',
            'TCD': 'Chad',
            'CHL': 'Chile',
            'CHN': 'China',
            'CXR': 'Christmas Island',
            'CCK': 'Cocos (Keeling) Islands',
            'COL': 'Colombia',
            'COM': 'Comoros',
            'COG': 'Congo',
            'COD': 'Congo, the Democratic Republic of the',
            'COK': 'Cook Islands',
            'CRI': 'Costa Rica',
            'CIV': "Côte d'Ivoire",
            'HRV': 'Croatia',
            'CUB': 'Cuba',
            'CYP': 'Cyprus',
            'CZE': 'Czech Republic',
            'DNK': 'Denmark',
            'DJI': 'Djibouti',
            'DMA': 'Dominica',
            'DOM': 'Dominican Republic',
            'ECU': 'Ecuador',
            'EGY': 'Egypt',
            'SLV': 'El Salvador',
            'GNQ': 'Equatorial Guinea',
            'ERI': 'Eritrea',
            'EST': 'Estonia',
            'ETH': 'Ethiopia',
            'FLK': 'Falkland Islands (Malvinas)',
            'FRO': 'Faroe Islands',
            'FJI': 'Fiji',
            'FIN': 'Finland',
            'FRA': 'France',
            'GUF': 'French Guiana',
            'PYF': 'French Polynesia',
            'ATF': 'French Southern Territories',
            'GAB': 'Gabon',
            'GMB': 'Gambia',
            'GEO': 'Georgia',
            'DEU': 'Germany',
            'GHA': 'Ghana',
            'GIB': 'Gibraltar',
            'GRC': 'Greece',
            'GRL': 'Greenland',
            'GRD': 'Grenada',
            'GLP': 'Guadeloupe',
            'GUM': 'Guam',
            'GTM': 'Guatemala',
            'GGY': 'Guernsey',
            'GIN': 'Guinea',
            'GNB': 'Guinea-Bissau',
            'GUY': 'Guyana',
            'HTI': 'Haiti',
            'HMD': 'Heard Island and McDonald Islands',
            'VAT': 'Holy See (Vatican City State)',
            'HND': 'Honduras',
            'HKG': 'Hong Kong',
            'HUN': 'Hungary',
            'ISL': 'Iceland',
            'IND': 'India',
            'IDN': 'Indonesia',
            'IRN': 'Iran, Islamic Republic of',
            'IRQ': 'Iraq',
            'IRL': 'Ireland',
            'IMN': 'Isle of Man',
            'ISR': 'Israel',
            'ITA': 'Italy',
            'JAM': 'Jamaica',
            'JPN': 'Japan',
            'JEY': 'Jersey',
            'JOR': 'Jordan',
            'KAZ': 'Kazakhstan',
            'KEN': 'Kenya',
            'KIR': 'Kiribati',
            'PRK': "Korea, Democratic People's Republic of",
            'KOR': 'Korea, Republic of',
            'KWT': 'Kuwait',
            'KGZ': 'Kyrgyzstan',
            'LAO': "Lao People's Democratic Republic",
            'LVA': 'Latvia',
            'LBN': 'Lebanon',
            'LSO': 'Lesotho',
            'LBR': 'Liberia',
            'LBY': 'Libyan Arab Jamahiriya',
            'LIE': 'Liechtenstein',
            'LTU': 'Lithuania',
            'LUX': 'Luxembourg',
            'MAC': 'Macao',
            'MKD': 'Macedonia, the former Yugoslav Republic of',
            'MDG': 'Madagascar',
            'MWI': 'Malawi',
            'MYS': 'Malaysia',
            'MDV': 'Maldives',
            'MLI': 'Mali',
            'MLT': 'Malta',
            'MHL': 'Marshall Islands',
            'MTQ': 'Martinique',
            'MRT': 'Mauritania',
            'MUS': 'Mauritius',
            'MYT': 'Mayotte',
            'MEX': 'Mexico',
            'FSM': 'Micronesia, Federated States of',
            'MDA': 'Moldova, Republic of',
            'MCO': 'Monaco',
            'MNG': 'Mongolia',
            'MNE': 'Montenegro',
            'MSR': 'Montserrat',
            'MAR': 'Morocco',
            'MOZ': 'Mozambique',
            'MMR': 'Myanmar',
            'NAM': 'Namibia',
            'NRU': 'Nauru',
            'NPL': 'Nepal',
            'NLD': 'Netherlands',
            'ANT': 'Netherlands Antilles',
            'NCL': 'New Caledonia',
            'NZL': 'New Zealand',
            'NIC': 'Nicaragua',
            'NER': 'Niger',
            'NGA': 'Nigeria',
            'NIU': 'Niue',
            'NFK': 'Norfolk Island',
            'MNP': 'Northern Mariana Islands',
            'NOR': 'Norway',
            'OMN': 'Oman',
            'PAK': 'Pakistan',
            'PLW': 'Palau',
            'PSE': 'Palestinian Territory, Occupied',
            'PAN': 'Panama',
            'PNG': 'Papua New Guinea',
            'PRY': 'Paraguay',
            'PER': 'Peru',
            'PHL': 'Philippines',
            'PCN': 'Pitcairn',
            'POL': 'Poland',
            'PRT': 'Portugal',
            'PRI': 'Puerto Rico',
            'QAT': 'Qatar',
            'REU': 'Réunion',
            'ROU': 'Romania',
            'RUS': 'Russian Federation',
            'RWA': 'Rwanda',
            'BLM': 'Saint Barthélemy',
            'SHN': 'Saint Helena, Ascension and Tristan da Cunha',
            'KNA': 'Saint Kitts and Nevis',
            'LCA': 'Saint Lucia',
            'MAF': 'Saint Martin (French part)',
            'SPM': 'Saint Pierre and Miquelon',
            'VCT': 'Saint Vincent and the Grenadines',
            'WSM': 'Samoa',
            'SMR': 'San Marino',
            'STP': 'Sao Tome and Principe',
            'SAU': 'Saudi Arabia',
            'SEN': 'Senegal',
            'SRB': 'Serbia',
            'SYC': 'Seychelles',
            'SLE': 'Sierra Leone',
            'SGP': 'Singapore',
            'SVK': 'Slovakia',
            'SVN': 'Slovenia',
            'SLB': 'Solomon Islands',
            'SOM': 'Somalia',
            'ZAF': 'South Africa',
            'SGS': 'South Georgia and the South Sandwich Islands',
            'ESP': 'Spain',
            'LKA': 'Sri Lanka',
            'SDN': 'Sudan',
            'SUR': 'Suriname',
            'SJM': 'Svalbard and Jan Mayen',
            'SWZ': 'Swaziland',
            'SWE': 'Sweden',
            'CHE': 'Switzerland',
            'SYR': 'Syrian Arab Republic',
            'TWN': 'Taiwan, Province of China',
            'TJK': 'Tajikistan',
            'TZA': 'Tanzania, United Republic of',
            'THA': 'Thailand',
            'TLS': 'Timor-Leste',
            'TGO': 'Togo',
            'TKL': 'Tokelau',
            'TON': 'Tonga',
            'TTO': 'Trinidad and Tobago',
            'TUN': 'Tunisia',
            'TUR': 'Turkey',
            'TKM': 'Turkmenistan',
            'TCA': 'Turks and Caicos Islands',
            'TUV': 'Tuvalu',
            'UGA': 'Uganda',
            'UKR': 'Ukraine',
            'ARE': 'United Arab Emirates',
            'GBR': 'United Kingdom',
            'USA': 'United States',
            'UMI': 'United States Minor Outlying Islands',
            'URY': 'Uruguay',
            'UZB': 'Uzbekistan',
            'VUT': 'Vanuatu',
            'VEN': 'Venezuela, Bolivarian Republic of',
            'VNM': 'Viet Nam',
            'VGB': 'Virgin Islands, British',
            'VIR': 'Virgin Islands, U.S.',
            'WLF': 'Wallis and Futuna',
            'ESH': 'Western Sahara',
            'YEM': 'Yemen',
            'ZMB': 'Zambia',
            'ZWE': 'Zimbabwe'
        }
        self.state_codes = {
            'AB': 'Alberta',
            'BC': 'British Columbia',
            'MB': 'Manitoba',
            'NB': 'New Brunswick',
            'NF': 'Newfoundland',
            'NT': 'Northwest Territories',
            'NS': 'Nova Scotia',
            'NU': 'Nunavut',
            'ON': 'Ontario',
            'PE': 'Prince Edward Island',
            'PQ': 'Quebec',
            'SK': 'Saskatchewan',
            'YT': 'Yukon', 
            'AA': 'Armed Forces America',
            'AE': 'Armed Forces',
            'AK': 'Alaska',
            'AL': 'Alabama',
            'AP': 'Armed Forces Pacific',
            'AR': 'Arkansas',
            'AZ': 'Arizona',
            'CA': 'California',
            'CO': 'Colorado',
            'CT': 'Connecticut',
            'DC': 'Washington DC',
            'DE': 'Delaware',
            'FL': 'Florida',
            'GA': 'Georgia',
            'GU': 'Guam',
            'HI': 'Hawaii',
            'IA': 'Iowa',
            'ID': 'Idaho',
            'IL': 'Illinois',
            'IN': 'Indiana',
            'KS': 'Kansas',
            'KY': 'Kentucky',
            'LA': 'Louisiana',
            'MA': 'Massachusetts',
            'MD': 'Maryland',
            'ME': 'Maine',
            'MI': 'Michigan',
            'MN': 'Minnesota',
            'MO': 'Missouri',
            'MS': 'Mississippi',
            'MT': 'Montana',
            'NC': 'North Carolina',
            'ND': 'North Dakota',
            'NE': 'Nebraska',
            'NH': 'New Hampshire',
            'NJ': 'New Jersey',
            'NM': 'New Mexico',
            'NV': 'Nevada',
            'NY': 'New York',
            'OH': 'Ohio',
            'OK': 'Oklahoma',
            'OR': 'Oregon',
            'PA': 'Pennsylvania',
            'PR': 'Puerto Rico',
            'RI': 'Rhode Island',
            'SC': 'South Carolina',
            'SD': 'South Dakota',
            'TN': 'Tennessee',
            'TX': 'Texas',
            'UT': 'Utah',
            'VA': 'Virginia',
            'VI': 'Virgin Islands',
            'VT': 'Vermont',
            'WA': 'Washington',
            'WI': 'Wisconsin',
            'WV': 'West Virginia',
            'WY': 'Wyoming'
        }
        self.weather_data_file_list = self._get_weather_data_file_list()
        self.weather_data_dropdown = None

    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    #EPW Reader
    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


    # This is the method (along with its subequent assisting methods) to read the epw file
    def read_epw_f(self, url):
        name = url[url.rfind('/') + 1:]                                         
        response = Request(url, headers={'User-Agent' : "Magic Browser"})     
        with tempfile.TemporaryDirectory() as tmpdirname:                       
            with open(tmpdirname + name, 'wb') as f:
                f.write(urlopen(response).read())
                # data = EPW(tmpdirname+name)
                self._read(tmpdirname+name)                              
                f.close()
    
    def _read(self,fp):
        self.headers, self.lat, self.lng, self.timezone  = self._read_headers(fp)
        self.dataframe = self._read_data(fp)
        
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

        return d, float(d['LOCATION'][5]), float(d['LOCATION'][6]), float(d['LOCATION'][7])

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
            for i, row in enumerate(csvreader):
                if row[0].isdigit():
                    break
            csvfile.close()
        return i 





    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    #Weather Data File List Reader
    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

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
    def _calculate_distance(self, df_latlng, lat_or_lng, default_val):
        user_latlng = st.session_state[lat_or_lng] if lat_or_lng in st.session_state else default_val
        d1 = math.radians(user_latlng)
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

    def _is_sort_by_distance(self):
        if 'filter_option' in st.session_state:
            if st.session_state.filter_option == self.filter_list:
                return False
            # elif st.session_state.filter_option == self.sort_list:
            #     return True
        return True

    # This method converts the data object to a dataframe with columns like coordinates and epw file names;
    # it also sorts the dataframe according to the preferred order
    def _get_weather_data_file_list(self):
        data = self._get_db()
        weather_data_file_list = []
        for location in data['features']:
            match = re.search(r'href=[\'"]?([^\'" >]+)', location['properties']['epw'])
            if match:
                url = match.group(1)
                # if (url not in self.epw_files_in_question) and ('SWEC' not in url): #Remove SWEC files
                if url not in self.df_in_question:
                    url_str = url.split('/')
                    if len(url_str) == 7:
                        url_str = url_str[0:5]+[None]+url_str[5:7]
                    url_str += [url]
                    url_str += location['geometry']['coordinates']
                    weather_data_file_list.append(url_str)

        weather_data_file_list = pd.DataFrame(weather_data_file_list)
        weather_data_file_list = weather_data_file_list.drop([0, 1, 2, 7], axis = 1)
        weather_data_file_list = weather_data_file_list.rename(columns={3: 'region', 4: 'country', 5: 'state', 6: 'title', 8: 'file_url', 9: 'lon', 10: 'lat'})
        weather_data_file_list['title'] = weather_data_file_list['title'].apply(lambda x: ' '.join(re.split('_|\.', str(x))))

        weather_data_file_list = self._sort_list_by_distance(weather_data_file_list) if self._is_sort_by_distance() else weather_data_file_list.sort_values(['region', 'country', 'state'])
        
        return weather_data_file_list



    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    #Advanced Search
    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    def advanced_search(self):
        expander = st.sidebar.expander(label='Weather Data Search')

        def _format_region(x):
            regions_str = x.split('_')
            for i in range(len(regions_str)):
                if (regions_str[i] == 'wmo'):
                    regions_str[i] = regions_str[i].upper()
                elif (regions_str[i] != 'and'):
                    regions_str[i] = regions_str[i].capitalize()
                else:
                    regions_str[i] = regions_str[i]
            x = ' '.join(regions_str)
            return x

        def _format_country_or_state(x, match):
            try:
                x = f"{x} ({match[x]})"
            except:
                x = f"{x}"
            return x

        def _format_weather_data(x):
            try:
                if x['state'] is not None:
                    x = f"{x['title']} ({self.state_codes[x['state']]}, {self.country_codes[x['country']]})"
                else:
                    x = f"{x['title']} ({self.country_codes[x['country']]})"
            except:
                x = f"{x['title']}"
            return x

        def _format(x, filter=None):
            if x == 'all':
                x = x.capitalize()
            elif filter == 'region':
                x = _format_region(x)
            elif filter == 'country':
                x = _format_country_or_state(x, self.country_codes)
            elif filter == 'state':
                x = _format_country_or_state(x, self.state_codes)
            elif filter == 'weather_data':
                x = _format_weather_data(x)
            return x

        with expander:
            st.radio("Search", [self.sort_list, self.filter_list], key='filter_option', on_change=self._filter_settings_reset) 

            if 'filter_option' in st.session_state:
                if st.session_state.filter_option == self.sort_list:
                    with st.form(key='advanced_search'):
                        st.number_input("Latitude", -90.0, 90.0, 53.4, 0.1, key='user_lat')
                        st.number_input("Longitude", -180.0, 180.0, -1.5, 0.1, key='user_lng')
                        submit_button = st.form_submit_button(label='Submit')
                    
                if st.session_state.filter_option == self.filter_list:        

                    regions = self.weather_data_file_list['region'].unique()
                    regions = sorted(regions, key=lambda x: int(x[-1]))
                    regions_dropdown = ['all']
                    regions_dropdown += regions

                    st.selectbox("Region", regions_dropdown, key='region', format_func=lambda x: _format(x, 'region'))

                    countries_filtered = self.weather_data_file_list.drop_duplicates(['region', 'country'])
                    country_dropdown = countries_filtered['country']
                    if 'region' in st.session_state:
                        if st.session_state['region'] == 'all':
                            country_dropdown = []
                        else:
                            country_dropdown = ['all']
                            country_dropdown += countries_filtered[countries_filtered['region'] == st.session_state['region']]['country'].to_list()

                    st.selectbox("Country", country_dropdown, key='country', format_func=lambda x: _format(x, 'country'))

                    states_filtered = self.weather_data_file_list.drop_duplicates(['country', 'state']).dropna()

                    state_dropdown = []
                    if 'country' in st.session_state:
                        if st.session_state['country'] == 'all':
                            state_dropdown = []
                        elif st.session_state['country'] == None:
                            state_dropdown = []
                        elif not states_filtered[states_filtered['country'] == st.session_state['country']]['state'].empty:
                            state_dropdown = ['all']
                            state_dropdown += states_filtered[states_filtered['country'] == st.session_state['country']]['state'].to_list()

                    st.selectbox("State", state_dropdown, key='state', format_func=lambda x: _format(x, 'state'))

        self.weather_data_dropdown = self.weather_data_file_list[['region', 'country', 'state', 'title', 'file_url', 'lon', 'lat']].to_dict('records')

        def _filter_check(filter_word):
            if filter_word in st.session_state:
                if st.session_state[filter_word] is not None:
                    if 'all' not in st.session_state[filter_word]:
                        return True
            return False
                
        for filter_word in ['state', 'country', 'region']:
            if _filter_check(filter_word):
                self.weather_data_dropdown = [ v for v in self.weather_data_dropdown if v[filter_word] == st.session_state[filter_word] ]
                break

        self.file_name = st.sidebar.selectbox(
            'Weather Data File List', 
            self.weather_data_dropdown,
            format_func=lambda x: _format(x, 'weather_data'),
            help="A list of available weather data files (Keyword Search Enabled)"
        )   


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
                    st.session_state.region = "all"

        
    # def _get_advanced_search_dropdowns(self):
    #     regions = self.weather_data_file_list['region'].unique()
    #     regions_dropdown = [{
    #         "title": "All", 
    #         "pf": 'all', 
    #     }] * (len(regions) + 1)
    #     countries_dropdown = {"All": ['All']}
    #     states_dropdown = {"All": ['All']}
    #     for i in range(len(regions)):
    #         regions_str = regions[i].split('_')
    #         for j in range(len(regions_str)):
    #             if (regions_str[j] == 'wmo'):
    #                 regions_str[j] = regions_str[j].upper()
    #             elif (regions_str[j] != 'and'):
    #                 regions_str[j] = regions_str[j].capitalize()
    #             else:
    #                 regions_str[j] = regions_str[j]
    #         regions_dropdown_title = ' '.join(regions_str)
    #         regions_dropdown[int(regions_str[-1])] = {
    #             "title": regions_dropdown_title,
    #             "pf": regions[i]
    #         }

    #         countries_dropdown_individual_region = self.weather_data_file_list[self.weather_data_file_list['region'] == regions[i]]['country'].unique().tolist()        
    #         countries_dropdown[regions[i]] = ['All in Region '+regions[i][-1]] + countries_dropdown_individual_region
    #         for j in range(len(countries_dropdown_individual_region)):        
    #             states_dropdown_individual_country = self.weather_data_file_list[self.weather_data_file_list['country'] == countries_dropdown_individual_region[j]]['state'].unique().tolist()
    #             states_dropdown_individual_country = list(filter(None, states_dropdown_individual_country))
    #             states_dropdown[countries_dropdown_individual_region[j]] = ['All in '+countries_dropdown_individual_region[j]] + states_dropdown_individual_country

    #     weather_data_dropdown = self.weather_data_file_list[['region', 'country', 'state', 'title', 'file_url']].to_dict('records')
    #     return regions_dropdown, countries_dropdown, states_dropdown, weather_data_dropdown
   
    # # This method is callback. This method resets the settings when another radio option is selected.
    # def _filter_settings_reset(self):
    #     if 'filter_option' in st.session_state:
    #         if st.session_state.filter_option != self.sort_list:
    #             if 'user_lat' in st.session_state:
    #                 st.session_state.user_lat = self.default_lat
    #             if 'user_lng' in st.session_state:
    #                 st.session_state.user_lng = self.default_lon
    #         if st.session_state.filter_option != self.filter_list:
    #             if 'region' in st.session_state:
    #                 st.session_state.region = "all"
    #                 # st.session_state.region = {
    #                 #     "title": "All",
    #                 #     "pf": "all"
    #                 # }
    
    # def _check_if_a_valid_option_is_selected(self, var_to_check, str_to_check):
    #     if var_to_check in st.session_state:
    #         if st.session_state[var_to_check] is not None:
    #             if var_to_check == 'region':
    #                 if str_to_check not in st.session_state[var_to_check]['pf']:
    #                     return True        
    #             else:
    #                 if str_to_check not in st.session_state[var_to_check]:
    #                     return True
    #     return False

    # # This method populates the advanced search panel and weather data file list
    # def advanced_search_bak(self):
    #     regions_dropdown, countries_dropdown, states_dropdown, weather_data_dropdown = self._get_advanced_search_dropdowns()
    #     expander = st.sidebar.expander(label='Weather Data Search')
    #     with expander:
    #         st.radio("Search", [self.sort_list, self.filter_list], key='filter_option', on_change=self._filter_settings_reset)

    #         if 'filter_option' in st.session_state:
    #             if st.session_state.filter_option == self.sort_list:
    #                 st.number_input("Latitude", -90.0, 90.0, 53.4, 0.1, key='user_lat')
    #                 st.number_input("Longitude", -180.0, 180.0, -1.5, 0.1, key='user_lng')
                    
    #             if st.session_state.filter_option == self.filter_list:
    #                 st.selectbox(
    #                     "Region", 
    #                     regions_dropdown,
    #                     format_func=lambda x: x['title'], 
    #                     key='region'
    #                 )
    #                 epw_col1, epw_col2 = st.columns(2)
                    
    #                 if 'region' in st.session_state:
    #                     if st.session_state.region['title'] == 'All':
    #                         countries_dropdown = []
    #                     else:
    #                         countries_dropdown = countries_dropdown[st.session_state.region['pf']]
    #                 epw_col1.selectbox("Country", countries_dropdown, key='country')
                    
    #                 states_dropdown_options = []
    #                 if self._check_if_a_valid_option_is_selected('country', 'All in'):
    #                     if len(states_dropdown[st.session_state.country]) > 1:
    #                         states_dropdown_options = states_dropdown[st.session_state.country] 
                    
    #                 epw_col2.selectbox("State", states_dropdown_options, key='state')
                    
    #                 if self._check_if_a_valid_option_is_selected('region', 'all'):
    #                     if self._check_if_a_valid_option_is_selected('country', 'All in'):
    #                         if self._check_if_a_valid_option_is_selected('state', 'All in'):
    #                             results = []
    #                             for item in weather_data_dropdown:
    #                                 if item['state'] is not None:
    #                                     if item['state'] in st.session_state.state:
    #                                         results.append(item)
    #                             weather_data_dropdown = results                              
    #                         else: 
    #                             weather_data_dropdown = [ d for d in weather_data_dropdown if d['country'] in st.session_state.country]
    #                     else:
    #                         weather_data_dropdown = [ d for d in weather_data_dropdown if d['region'] in st.session_state.region['pf']]   

    #     self.file_name = st.sidebar.selectbox(
    #         'Weather Data File List', 
    #         weather_data_dropdown,
    #         format_func=lambda x: x['title'],
    #         help="A list of available weather data files (Keyword Search Enabled)"
    #     )      

    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    # EPW Filter
    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    # This method passes the time filter parameters to _df_filter_pipeline for filtering
    def df_filter(self, file_title):
        # Read the corresponding filter parameters from st.session_state according to feature (file_title)
        time_var = {'start_month': 1, 'start_day': 1, 'end_month': 12, 'end_day': 31, 'start_hour': 1, 'end_hour': 24}
        for var in time_var.keys():
            if file_title+"_"+var in st.session_state:
                if (var == 'start_month') | (var == 'end_month'):
                    time_var[var] = st.session_state[file_title+"_"+var]['value']
                else:
                    time_var[var] = st.session_state[file_title+"_"+var]

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
        self._df_filter_pipeline(direction, range)
        
        # filter by hour
        direction = (time_var['end_hour'] >= time_var['start_hour'])
        range = (
            (self.dataframe['Hour'] >= time_var['start_hour']),
            (self.dataframe['Hour'] <= time_var['end_hour'])       
        )
        self._df_filter_pipeline(direction, range)

    # This method filters the data
    def _df_filter_pipeline(self, start_month_before_end_month, range):
        #
        # Operator AND is used (start_month_before_end_month = True) if in dropdowns start month is before end month e.g. start: Feb, end: Nov
        # e.g. May is valid out because it is after Feb **AND** before Nov
        # 
        # Operator OR is used (start_month_before_end_month = False) if start month is after end month e.g. start: Nov, end: Feb, as it
        # indicates the desired range is Jan to Feb and Nov to Dec
        # e.g. Jan is valid because it is after Nov **OR** before Feb
        #
        filter_operator = operator.__and__ if start_month_before_end_month else operator.__or__
        self.dataframe = self.dataframe.loc[filter_operator(range[0], range[1])]


    # This method is under construction. Currently when it's called, it outputs a map pinpointing selections in weather data file list
    # It is commented out as it's currently unused
    def map_viewer(self):
        
        self.weather_data_dropdown = pd.DataFrame(self.weather_data_dropdown)  
        df = self.weather_data_dropdown[['lon', 'lat', 'title']]
        layer = pdk.Layer(
            "ScatterplotLayer",
            df,
            pickable=True,
            opacity=0.8,
            filled=True,
            radius_scale=2,
            radius_min_pixels=10,
            radius_max_pixels=4,
            line_width_min_pixels=0.01,
            get_position='[lon, lat]',
            get_fill_color=[200, 27, 27],
            get_line_color=[0, 0, 0],
        )
        selected = pd.DataFrame(self.file_name, index=[0])
        layer2 = pdk.Layer(
            "ScatterplotLayer",
            selected,
            pickable=True,
            opacity=1,
            filled=True,
            radius_scale=2,
            radius_min_pixels=10,
            radius_max_pixels=7,
            line_width_min_pixels=0.01,
            get_position='[lon, lat]',
            get_fill_color=[16, 12, 200],
            get_line_color=[0, 0, 0],
        )
        view_state = pdk.ViewState(latitude=selected['lat'].iloc[0], longitude=selected['lon'].iloc[0], zoom=4, min_zoom= 1, max_zoom=30, height=180)
        
        r = pdk.Deck(
            layers=[layer, layer2],
            map_style='mapbox://styles/mapbox/streets-v11', 
            initial_view_state=view_state, 
            tooltip={"html": "<b>Title: </b> {title} <br />" "<b>Latitude: </b> {lat} <br /> " "<b>Longitude: </b> {lon} <br /> " }
        )
                            
        st.sidebar.pydeck_chart(r)