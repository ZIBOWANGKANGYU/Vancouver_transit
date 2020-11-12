# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 16:53:54 2020

@author: kangyuwang
"""

data_version = "20200606"

import os
import re

cwd = os.path.dirname(os.getcwd())
os.chdir(cwd)
data_dir = os.path.join(os.getcwd(), "TL_data", data_version)

# Read intermediate data
import pandas as pd
import json
import geopandas

with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "calendar.json"), "r"
) as calendar_outfile:
    calendar = pd.read_json(json.load(calendar_outfile))

with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "calendar_dates.json"), "r"
) as calendar_dates_outfile:
    calendar_dates = pd.read_json(json.load(calendar_dates_outfile))

lines_gdf = geopandas.read_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "lines.json")
)

with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "routes.json"), "r"
) as routes_outfile:
    routes = pd.read_json(json.load(routes_outfile))

shapes_gdf = geopandas.read_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "shapes.json")
)

filelist_fd = os.listdir(os.path.join(os.getcwd(), "Data_Tables", data_version))
filelist = [
    filename for filename in filelist_fd if bool(re.match("stop_times.", filename))
]

## The stop_times table is very large in size and should be loaded in batches.
with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "stop_times0.json"), "r"
) as stop_times_outfile:
    stop_times = pd.read_json(json.load(stop_times_outfile))

for i in range(1, len(filelist)):
    print(i)
    filename = "stop_times" + str(i) + ".json"
    with open(
        os.path.join(os.getcwd(), "Data_Tables", data_version, filename), "r"
    ) as stop_times_outfile:
        stop_times_b = pd.read_json(json.load(stop_times_outfile))
    stop_times = stop_times.append(stop_times_b, ignore_index=True)

stops_gdf = geopandas.read_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "stops.json")
)

with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "trips.json"), "r"
) as trips_outfile:
    trips = pd.read_json(json.load(trips_outfile))

# Temporal distribution of all services
import matplotlib.pyplot as plt

# By arrival time
def hr_converter(hr_in):
    if int(hr_in[0:2]) >= 24:
        hr_out = int(hr_in[0:2]) - 24
        return str(hr_out).zfill(2) + hr_in[2:]
    else:
        return hr_in


stop_times.arrival_time

stop_times["arrival_time_24hr"] = [
    hr_converter(arrival_time) for arrival_time in stop_times["arrival_time"]
]

plt.hist(
    pd.to_datetime(stop_times["arrival_time_24hr"], format="%H:%M:%S").dt.hour, bins=24
)
plt.ylabel("Count")
plt.xlabel("Arrival Time")
plt.title("Number of Services by Arrival Time", fontsize=20)
plt.savefig(
    os.path.join(
        os.getcwd(),
        "Vancouver_transit",
        "Figures",
        data_version,
        "arrivaltime_hist.png",
    )
)

# Stops by avearge arrival time 3 am and 4 am
def hr_converter_cut(hr_in):
    if int(hr_in[0:2]) <= 3:
        hr_out = int(hr_in[0:2]) + 24
        return str(hr_out).zfill(2) + hr_in[2:]
    else:
        return hr_in


stop_times["arrival_time_day"] = [
    hr_converter_cut(arrival_time_24hr)
    for arrival_time_24hr in stop_times["arrival_time_24hr"]
]
stop_times["arrival_time_hour"] = [
    int(arrival_time_day[0:2]) for arrival_time_day in stop_times["arrival_time_day"]
]

import numpy as np
import contextily as ctx

stop_times_avrg_arr_t = (
    stop_times.groupby(["stop_id"])
    .agg(avrg_arrival_time=pd.NamedAgg(column="arrival_time_hour", aggfunc=np.mean))
    .sort_values(by=["avrg_arrival_time"])
)

plt.hist(
    stop_times_avrg_arr_t["avrg_arrival_time"], bins=24
)  # Except for few stops with very early or late average arrival times, most stops have average arrival times between 10 to 18

stops_gdf = stops_gdf.merge(
    stop_times_avrg_arr_t, left_on="stop_id", right_on="stop_id"
)

## Identify stops by whether busy or not
stops_cnt_trips = (
    stop_times.groupby("stop_id")
    .agg(num_trips=pd.NamedAgg(column="trip_id", aggfunc=lambda x: len(x.unique())))
    .sort_values(by=["num_trips"])
)

##Make histograms for the stops with most number of trips
fig, axs = plt.subplots(2, 5, figsize=(20, 6), sharex=True, sharey=True)
fig.subplots_adjust(hspace=0.5, wspace=0.001)
axs = axs.ravel()
for i in range(10):
    axs[i].hist(
        pd.to_datetime(
            stop_times.loc[
                stop_times["stop_id"] == stops_cnt_trips[-10:].index.tolist()[i]
            ]["arrival_time_24hr"],
            format="%H:%M:%S",
        ).dt.hour,
        bins=24,
    )
    axs[i].set_title(
        stops_gdf.loc[stops_gdf["stop_id"] == stops_cnt_trips[-10:].index.tolist()[i]][
            "stop_name"
        ].tolist()[0],
        fontsize=11,
        wrap=True,
    )
fig.suptitle("Number of Services by Arrival Time: the busiest stops", fontsize=16)
plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "stops_bz_arr_t.png"
    )
)  # Stops in Vancouver, Burnabay and west Richmond have later average arrival times than stops elsewhere
