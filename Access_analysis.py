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

GVA_map_xlim_lower = -13746072.435927173
GVA_map_xlim_higher = -13630000
GVA_map_ylim_lower = 6270302.809935683
GVA_map_ylim_higher = 6345000

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

import contextily as ctx
import matplotlib.pyplot as plt

### Example: Burnaby DA

GVA_DA_Burnaby = GVA_DA[GVA_DA["CSDNAME"] == "Burnaby"]
DA_Burnaby_ax = GVA_DA_Burnaby.plot(edgecolor="red", figsize=(20, 20), alpha=0.5)
ctx.add_basemap(DA_Burnaby_ax, zoom=12)
plt.title("DAs in Burnaby CSD", fontsize=30)
plt.axis("off")
plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "DA_Burnaby.png"
    )
)

### Population

GVA_DA_pop = pd.concat([GVA_base, GVA_DA[["vn13"]]], axis=1)
GVA_DA_pop_ax = GVA_DA_pop.plot(figsize=(20, 20), alpha=0.5, column="vn13", cmap="OrRd")
GVA_DA_pop_ax.set_xlim(GVA_map_xlim_lower, GVA_map_xlim_higher)
GVA_DA_pop_ax.set_ylim(GVA_map_ylim_lower, GVA_map_ylim_higher)
plt.title("2016 Population by Dissemination Area", fontsize=30)
plt.axis("off")
ctx.add_basemap(GVA_DA_pop_ax, zoom=12)

fig = GVA_DA_pop_ax.get_figure()
cbax = fig.add_axes([0.93, 0.3, 0.03, 0.39])
cbax.set_title("Population")

sm = plt.cm.ScalarMappable(
    cmap="OrRd",
    norm=plt.Normalize(vmin=min(GVA_DA_pop.vn13), vmax=max(GVA_DA_pop.vn13)),
)
sm._A = []
fig.colorbar(sm, cax=cbax, format="%1.0f")
fig.show()

fig.savefig(
    os.path.join(os.getcwd(), "Vancouver_transit", "Maps", data_version, "pop2016.png")
)

####Population density
GVA_DA_pop_dense = pd.concat([GVA_base, GVA_DA[["vn18"]]], axis=1)
GVA_DA_pop_dense = GVA_DA_pop_dense[
    GVA_DA_pop_dense.vn18 >= GVA_DA_pop_dense.vn18.quantile(0.9)
]  # Keep DAs with top 10% population densities
GVA_DA_pop_dense_ax = GVA_DA_pop_dense.plot(figsize=(20, 20), alpha=0.5, color="r")
GVA_DA_pop_dense_ax.set_xlim(GVA_map_xlim_lower, GVA_map_xlim_higher)
GVA_DA_pop_dense_ax.set_ylim(GVA_map_ylim_lower, GVA_map_ylim_higher)
plt.axis("off")
ctx.add_basemap(GVA_DA_pop_dense_ax, zoom=12)
plt.title("2016 Population density by Dissemination Area: Top 10%", fontsize=30)

plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "pop_dense201610pc.png"
    )
)
print(
    f"The CSDs with highest number of DAs with top 10% population densities are {list(GVA_DA_pop_dense.CSDNAME.value_counts().index)[:5]}"
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

GVA_DA_Access["NBA_stops_PC"] = (
    GVA_DA_Access["DA_NBA_stops_count"] / GVA_DA_Access["vn13"]
)

#### DA_NBAs without stop count
GVA_DA_Access_no_stop = GVA_DA_Access.loc[GVA_DA_Access["DA_NBA_stops_count"] == 0, :]
GVA_DA_Access_no_stop_ax = GVA_DA_Access_no_stop.plot(
    figsize=(20, 20), alpha=0.5, legend=True, color="r"
)
ctx.add_basemap(GVA_DA_Access_no_stop_ax, zoom=12)
plt.title(
    "DAs Whose Neighborhood Area Does Not Have Transit Stops",
    fontsize=25,
)
GVA_DA_Access_no_stop_ax.set_xlim(GVA_map_xlim_lower, GVA_map_xlim_higher)
GVA_DA_Access_no_stop_ax.set_ylim(GVA_map_ylim_lower, GVA_map_ylim_higher)
plt.axis("off")

plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "DA_NBA_no_stops.png"
    )
)

### Mapping the top 10%
GVA_DA_stops_PC = pd.concat([GVA_base, GVA_DA_Access[["NBA_stops_PC"]]], axis=1)
GVA_DA_stops_PC = GVA_DA_stops_PC[
    GVA_DA_stops_PC.NBA_stops_PC >= GVA_DA_stops_PC.NBA_stops_PC.quantile(0.9)
]

GVA_DA_stops_PC_ax = GVA_DA_stops_PC.plot(
    figsize=(20, 20), alpha=0.5, legend=True, color="r"
)
ctx.add_basemap(GVA_DA_stops_PC_ax, zoom=12)
plt.title(
    "Top 10% Dissemination Areas by Access to Transit Stops per Capita", fontsize=28
)
GVA_DA_stops_PC_ax.set_xlim(GVA_map_xlim_lower, GVA_map_xlim_higher)
GVA_DA_stops_PC_ax.set_ylim(GVA_map_ylim_lower, GVA_map_ylim_higher)
plt.axis("off")

plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "NBA_stops_PC_10pc.png"
    )
)

### Number of services in region (per resident)
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

GVA_DA_Access["NBA_services_PC"] = (
    GVA_DA_Access["DA_NBA_services_count"] / GVA_DA_Access["vn13"]
)

#### DA_NBAs without service count
GVA_DA_Access_no_service = GVA_DA_Access.loc[
    GVA_DA_Access["DA_NBA_services_count"] == 0, :
]
GVA_DA_Access_no_service_ax = GVA_DA_Access_no_service.plot(
    figsize=(20, 20), alpha=0.5, legend=True, color="r"
)
ctx.add_basemap(GVA_DA_Access_no_service_ax, zoom=12)

GVA_DA_Access_no_service_ax.set_xlim(GVA_map_xlim_lower, GVA_map_xlim_higher)
GVA_DA_Access_no_service_ax.set_ylim(GVA_map_ylim_lower, GVA_map_ylim_higher)
plt.axis("off")
plt.title(
    "DAs Whose Neighborhood Area Does Not Have Transit Service",
    fontsize=24,
)
plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "DA_NBA_no_services.png"
    )
)

### Mapping the top 10%
GVA_DA_services_PC = pd.concat([GVA_base, GVA_DA_Access[["NBA_services_PC"]]], axis=1)
GVA_DA_services_PC = GVA_DA_services_PC[
    GVA_DA_services_PC.NBA_services_PC
    >= GVA_DA_services_PC.NBA_services_PC.quantile(0.9)
]

GVA_DA_services_PC_ax = GVA_DA_services_PC.plot(
    figsize=(28, 20), alpha=0.5, legend=True, color="r"
)
ctx.add_basemap(GVA_DA_services_PC_ax, zoom=12)
GVA_DA_services_PC_ax.set_xlim(GVA_map_xlim_lower, GVA_map_xlim_higher)
GVA_DA_services_PC_ax.set_ylim(GVA_map_ylim_lower, GVA_map_ylim_higher)
plt.axis("off")
plt.title(
    "Top 10% Dissemination Areas by Access to Transit Services per Capita", fontsize=30
)

plt.savefig(
    os.path.join(
        os.getcwd(),
        "Vancouver_transit",
        "Maps",
        data_version,
        "NBA_services_PC_10pc.png",
    )
)

# Save access data

GVA_DA_Access.to_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_Access.json"),
    driver="GeoJSON",
)
