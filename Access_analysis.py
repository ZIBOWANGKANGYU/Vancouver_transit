# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 16:53:54 2020

@author: kangyuwang
"""

data_version = "20200606"

import os
import re
import numpy as np

cwd = os.path.dirname(os.getcwd())
os.chdir(cwd)
data_dir = os.path.join(os.getcwd(), "TL_data", data_version)

# Read intermediate data
import pandas as pd
import json
import geopandas

GVA_DA = geopandas.read_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_data.shp")
)

with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_header.json"), "r"
) as DA_header_outfile:
    header = json.load(DA_header_outfile)

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

### Summarize variables
from tabulate import tabulate

DA_feature_summary = GVA_DA.iloc[:, 35:42].describe().round(decimals=1)
DA_feature_summary = DA_feature_summary.rename(
    columns={
        "vn13": "pop_2016",
        "vn16": "total_private_dwellings",
        "vn17": "total_private_dwellings_usual",
        "vn18": "pop_per_km2",
        "vn19": "land_area_km2",
    }
)
DA_feature_summary = DA_feature_summary.loc["mean":"max"]
print(
    tabulate(DA_feature_summary, DA_feature_summary.columns.tolist(), tablefmt="github")
)

## Mapping DAs
### Create base map
GVA_DA = GVA_DA.to_crs(epsg=3857)
GVA_base = GVA_DA.drop(GVA_DA.columns[28:-1], axis=1)

### Example: Burnaby DA
import contextily as ctx
import matplotlib.pyplot as plt

GVA_DA_Burnaby = GVA_DA[GVA_DA["CSDNAME"] == "Burnaby"]
DA_Burnaby_ax = GVA_DA_Burnaby.plot(edgecolor="red", figsize=(20, 20), alpha=0.5)
ctx.add_basemap(DA_Burnaby_ax, zoom=12)
plt.title("DAs in Burnaby CSD")
plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "DA_Burnaby.png"
    )
)

### Population

GVA_DA_pop = pd.concat([GVA_base, GVA_DA[["vn13"]]], axis=1)
GVA_DA_pop_ax = GVA_DA_pop.plot(
    figsize=(20, 20), alpha=0.5, column="vn13", cmap="OrRd", legend=True
)
ctx.add_basemap(GVA_DA_pop_ax, zoom=12)
plt.title("2016 Population by Dissemination Area")

plt.savefig(
    os.path.join(os.getcwd(), "Vancouver_transit", "Maps", data_version, "pop2016.png")
)

####Population density
GVA_DA_pop_dense = pd.concat([GVA_base, GVA_DA[["vn18"]]], axis=1)
GVA_DA_pop_dense = GVA_DA_pop_dense[
    GVA_DA_pop_dense.vn18 >= GVA_DA_pop_dense.vn18.quantile(0.9)
]  # Keep DAs with top 10% population densities
GVA_DA_pop_dense_ax = GVA_DA_pop_dense.plot(
    figsize=(20, 20), alpha=0.5, legend=True, color="r"
)
ctx.add_basemap(GVA_DA_pop_dense_ax, zoom=12)
plt.title("2016 Population density by Dissemination Area: Top 10%")

plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "pop_dense201610pc.png"
    )
)
print(
    f"The CSDs with highest number of DAs with top 10% population densities are {list(GVA_DA_pop_dense.CSDNAME.value_counts().index)[:5]}"
)


GVA_DA_pop_dense1 = pd.concat([GVA_base, GVA_DA[["vn13", "vn19"]]], axis=1)
GVA_DA_pop_dense1[["pop_dense"]] = GVA_DA_pop_dense1.vn13 / GVA_DA_pop_dense1.vn19
GVA_DA_pop_dense1.loc[np.isinf(GVA_DA_pop_dense1.pop_dense) == True, "pop_dense"] = None
GVA_DA_pop_dense1_ax = GVA_DA_pop_dense1.plot(
    figsize=(20, 20), alpha=0.5, column="pop_dense", cmap="OrRd", legend=True
)
ctx.add_basemap(GVA_DA_pop_dense1_ax, zoom=12)
plt.title("2016 Population density by Dissemination Area")

plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "pop_dense2016.png"
    )
)

# Calculate access

### Define "Neighborhood Area": original DA with 500m buffer zone
GVA_DA_NBA = GVA_DA.copy()
GVA_DA_NBA["geometry"] = GVA_DA_NBA.geometry.buffer(500)

## Two measurements of access to public transit infrastructure
### Number of physical stops (per resident)
GVA_DA_NBA_stops = geopandas.sjoin(GVA_DA_NBA, stops_gdf, how="left", op="intersects")
GVA_DA_NBA_stops_count = (
    GVA_DA_NBA_stops.groupby("DAUID")["stop_code"].count().rename("DA_NBA_stops_count")
)
GVA_DA_Access = GVA_DA.merge(GVA_DA_NBA_stops_count, on="DAUID")

### Number services in region (per resident)
stops_cnt_services = stop_times.groupby("stop_id").size().rename("stop_cnt_services")
stops_gdf_cnt_services = stops_gdf.join(stops_cnt_services, on="stop_id", how="left")
GVA_DA_NBA_stops_cnt_services = geopandas.sjoin(
    GVA_DA_NBA, stops_gdf_cnt_services, how="left", op="intersects"
)
GVA_DA_NBA_services_count = (
    GVA_DA_NBA_stops_cnt_services.groupby("DAUID")["stop_cnt_services"]
    .sum()
    .rename("DA_NBA_services_count")
)
GVA_DA_Access = GVA_DA_Access.merge(GVA_DA_NBA_services_count, on="DAUID")
