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

## Mapping DAs
### Create base map
GVA_DA = GVA_DA.to_crs(epsg=3857)
GVA_base = GVA_DA.drop(GVA_DA.columns[28:-1], axis=1)

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

## Mode of commuting: data from 2016 census
GVA_DA_cmt = pd.concat([GVA_base, GVA_DA[GVA_DA.columns[457:482]]], axis=1)

### Destination

GVA_CSD_cmt_dest = GVA_DA_cmt.dissolve(by="CSDNAME", aggfunc="sum")

GVA_CSD_cmt_dest["prop_within_CSD"] = (
    GVA_CSD_cmt_dest["vn436"] / GVA_CSD_cmt_dest["vn435"]
)
GVA_CSD_cmt_dest["prop_within_CD"] = (
    GVA_CSD_cmt_dest["vn437"] / GVA_CSD_cmt_dest["vn435"]
)
GVA_CSD_cmt_dest["prop_within_province"] = (
    GVA_CSD_cmt_dest["vn438"] / GVA_CSD_cmt_dest["vn435"]
)
GVA_CSD_cmt_dest["prop_out_province"] = (
    GVA_CSD_cmt_dest["vn439"] / GVA_CSD_cmt_dest["vn435"]
)

CSD_max_within_CSD = GVA_CSD_cmt_dest[
    GVA_CSD_cmt_dest.prop_within_CSD == max(GVA_CSD_cmt_dest.prop_within_CSD)
].index[0]
CSD_min_within_CSD = GVA_CSD_cmt_dest[
    GVA_CSD_cmt_dest.prop_within_CSD == min(GVA_CSD_cmt_dest.prop_within_CSD)
].index[0]

GVA_CSD_cmt_dest.sort_values(by="prop_within_CSD", ascending=False)

GVA_within_CSD_prop = sum(GVA_CSD_cmt_dest["vn436"]) / sum(GVA_CSD_cmt_dest["vn435"])

print(
    f"In the Greater Vancouver Area, {GVA_within_CSD_prop:.1%} of residents commute within their CSDs"
)
print(
    f"{CSD_max_within_CSD} has the highest proportion of residents ({max(GVA_CSD_cmt_dest.prop_within_CSD):.1%}) commuting within the CSD."
)
print(
    f"{CSD_min_within_CSD} has the lowest proportion of residents ({min(GVA_CSD_cmt_dest.prop_within_CSD):.1%}) commuting within the CSD."
)

CSD_within_CSD_ax = GVA_CSD_cmt_dest.plot(
    figsize=(20, 20), alpha=0.5, column="prop_within_CSD", cmap="OrRd", legend=True
)
ctx.add_basemap(CSD_within_CSD_ax, zoom=12)
plt.title("Proportion of population transitting within CSD")

plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "commut_within_csd.png"
    )
)

### Mode of commuting
GVA_DA_cmt_mode = GVA_DA_cmt

GVA_DA_cmt_mode["prop_private_driver"] = (
    GVA_DA_cmt_mode["vn441"] / GVA_DA_cmt_mode["vn440"]
)
GVA_DA_cmt_mode["prop_private_passenger"] = (
    GVA_DA_cmt_mode["vn442"] / GVA_DA_cmt_mode["vn440"]
)
GVA_DA_cmt_mode["prop_public"] = GVA_DA_cmt_mode["vn443"] / GVA_DA_cmt_mode["vn440"]
GVA_DA_cmt_mode["prop_walk"] = GVA_DA_cmt_mode["vn444"] / GVA_DA_cmt_mode["vn440"]
GVA_DA_cmt_mode["bicycle"] = GVA_DA_cmt_mode["vn445"] / GVA_DA_cmt_mode["vn440"]

#### Histogram of distribution of proportion of commute mode use across DAs
import matplotlib.pyplot as plt
import seaborn as sns

GVA_DA_cmt_mode_hist = GVA_DA_cmt_mode.melt(
    id_vars=["DAUID"],
    value_vars=[
        "prop_private_driver",
        "prop_private_passenger",
        "prop_public",
        "prop_walk",
        "bicycle",
    ],
)
GVA_DA_cmt_mode_hist = GVA_DA_cmt_mode_hist.rename(
    columns={"variable": "mode", "value": "prop"}
)

sns.displot(GVA_DA_cmt_mode_hist, x="prop", hue="mode", kind="kde", fill=True)
plt.title("Proportion of commuters by mode of transportation in Greater Vancouver Area")
plt.savefig(
    os.path.join(os.getcwd(), "Vancouver_transit", "Maps", data_version, "DA_mode.png")
)

sns.displot(
    GVA_DA_cmt_mode_hist.query("mode !='bicycle'"),
    x="prop",
    hue="mode",
    kind="kde",
    fill=True,
)
plt.title(
    "Proportion of commuters by mode of transportation in Greater Vancouver Area (Excluding Bicycle)"
)
plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "DA_mode_exl_bi.png"
    )
)

#### Maps of DAs by quantiles of public transportation proportions
DA_public_cmt_ax = GVA_DA_cmt.plot(
    figsize=(20, 20),
    alpha=0.5,
    column="prop_public",
    cmap="Greens",
    legend=True,
    scheme="quantiles",
)
ctx.add_basemap(DA_public_cmt_ax, zoom=12)
plt.title("Proportion of population using public transportation")

plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "DA_public_prop.png"
    )
)

GVA_CSD_cmt_mode = GVA_DA_cmt.dissolve(by="CSDNAME", aggfunc="sum")

GVA_CSD_cmt_mode["prop_private_driver"] = (
    GVA_CSD_cmt_mode["vn441"] / GVA_CSD_cmt_mode["vn440"]
)
GVA_CSD_cmt_mode["prop_private_passenger"] = (
    GVA_CSD_cmt_mode["vn442"] / GVA_CSD_cmt_mode["vn440"]
)
GVA_CSD_cmt_mode["prop_public"] = GVA_CSD_cmt_mode["vn443"] / GVA_CSD_cmt_mode["vn440"]
GVA_CSD_cmt_mode["prop_walk"] = GVA_CSD_cmt_mode["vn444"] / GVA_CSD_cmt_mode["vn440"]
GVA_CSD_cmt_mode["prop_bicycle"] = GVA_CSD_cmt_mode["vn445"] / GVA_CSD_cmt_mode["vn440"]

GVA_CSD_cmt_mode.sort_values(by="prop_public", ascending=False)

GVA_public_prop = sum(GVA_CSD_cmt_dest["vn443"]) / sum(GVA_CSD_cmt_dest["vn440"])

CSD_max_public = GVA_CSD_cmt_mode[
    GVA_CSD_cmt_mode.prop_public == max(GVA_CSD_cmt_mode.prop_public)
].index[0]
CSD_min_public = GVA_CSD_cmt_mode[
    GVA_CSD_cmt_mode.prop_public == min(GVA_CSD_cmt_mode.prop_public)
].index[0]

print(
    f"In the Greater Vancouver Area, {GVA_public_prop:.1%} of residents commute using public transportation."
)
print(
    f"{CSD_max_public} has the highest proportion of residents ({max(GVA_CSD_cmt_mode.prop_public):.1%}) commuting using public transportation."
)
print(
    f"{CSD_min_public} has the lowest proportion of residents ({min(GVA_CSD_cmt_mode.prop_public):.1%}) commuting using public transportation."
)

### Duration of commuting
GVA_DA_cmt_duration = GVA_DA_cmt

GVA_DA_cmt_duration["prop_less_15"] = (
    GVA_DA_cmt_duration["vn448"] / GVA_DA_cmt_duration["vn447"]
)
GVA_DA_cmt_duration["prop_15_29"] = (
    GVA_DA_cmt_duration["vn449"] / GVA_DA_cmt_duration["vn447"]
)
GVA_DA_cmt_duration["prop_30_44"] = (
    GVA_DA_cmt_duration["vn450"] / GVA_DA_cmt_duration["vn447"]
)
GVA_DA_cmt_duration["prop_45_59"] = (
    GVA_DA_cmt_duration["vn451"] / GVA_DA_cmt_duration["vn447"]
)
GVA_DA_cmt_duration["prop_more_60"] = (
    GVA_DA_cmt_duration["vn452"] / GVA_DA_cmt_duration["vn447"]
)

GVA_DA_cmt_duration.loc[
    GVA_DA_cmt_duration["prop_less_15"] > 0.5, "med_commute_duration"
] = 7.5
GVA_DA_cmt_duration.loc[
    (GVA_DA_cmt_duration["prop_less_15"] <= 0.5)
    & (GVA_DA_cmt_duration["prop_less_15"] + GVA_DA_cmt_duration["prop_15_29"] > 0.5),
    "med_commute_duration",
] = 22.5
GVA_DA_cmt_duration.loc[
    (GVA_DA_cmt_duration["prop_less_15"] + GVA_DA_cmt_duration["prop_15_29"] <= 0.5)
    & (
        GVA_DA_cmt_duration["prop_less_15"]
        + GVA_DA_cmt_duration["prop_15_29"]
        + GVA_DA_cmt_duration["prop_30_44"]
        > 0.5
    ),
    "med_commute_duration",
] = 37.5
GVA_DA_cmt_duration.loc[
    (
        GVA_DA_cmt_duration["prop_less_15"]
        + GVA_DA_cmt_duration["prop_15_29"]
        + GVA_DA_cmt_duration["prop_30_44"]
        <= 0.5
    )
    & (
        GVA_DA_cmt_duration["prop_less_15"]
        + GVA_DA_cmt_duration["prop_15_29"]
        + GVA_DA_cmt_duration["prop_30_44"]
        + GVA_DA_cmt_duration["prop_45_59"]
        > 0.5
    ),
    "med_commute_duration",
] = 52.5
GVA_DA_cmt_duration.loc[
    (
        GVA_DA_cmt_duration["prop_less_15"]
        + GVA_DA_cmt_duration["prop_15_29"]
        + GVA_DA_cmt_duration["prop_30_44"]
        + GVA_DA_cmt_duration["prop_45_59"]
        <= 0.5
    ),
    "med_commute_duration",
] = 60

#### Maps of DAs by duration of commute
DA_cmt_duration_ax = GVA_DA_cmt_duration.plot(
    figsize=(20, 20),
    alpha=0.5,
    column="med_commute_duration",
    cmap="OrRd",
    legend=True,
)
ctx.add_basemap(DA_cmt_duration_ax, zoom=12)
plt.title("Average Commuting Time")

plt.savefig(
    os.path.join(
        os.getcwd(),
        "Vancouver_transit",
        "Maps",
        data_version,
        "DA_commute_duration.png",
    )
)
