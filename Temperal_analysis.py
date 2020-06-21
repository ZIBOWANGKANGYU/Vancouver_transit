# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 16:53:54 2020

@author: kangyuwang
"""

data_version = "20200606"

import os

cwd = os.path.dirname(os.getcwd())
os.chdir(cwd)
data_dir = os.path.join(os.getcwd(), "TL_data", data_version)

#Read intermediate data
import pandas as pd
import json
import geopandas

with open(os.path.join(os.getcwd(), "Data_Tables", data_version,'calendar.json'), "r") as calendar_outfile:
    calendar = pd.read_json(json.load(calendar_outfile))
    
with open(os.path.join(os.getcwd(), "Data_Tables", data_version,'calendar_dates.json'), "r") as calendar_dates_outfile:
    calendar_dates = pd.read_json(json.load(calendar_dates_outfile))
   
lines_gdf = geopandas.read_file(os.path.join(os.getcwd(), "Data_Tables", data_version,'lines.json'))

with open(os.path.join(os.getcwd(), "Data_Tables", data_version,'routes.json'), "r") as routes_outfile:
    routes = pd.read_json(json.load(routes_outfile))
   
shapes_gdf = geopandas.read_file(os.path.join(os.getcwd(), "Data_Tables", data_version,'shapes.json'))

with open(os.path.join(os.getcwd(), "Data_Tables", data_version,'stop_times.json'), "r") as stop_times_outfile:
    stop_times = pd.read_json(json.load(stop_times_outfile))
    
stops_gdf = geopandas.read_file(os.path.join(os.getcwd(), "Data_Tables", data_version,'stops.json'))

with open(os.path.join(os.getcwd(), "Data_Tables", data_version,'trips.json'), "r") as trips_outfile:
    trips = pd.read_json(json.load(trips_outfile))

#Temporal distribution of all services
