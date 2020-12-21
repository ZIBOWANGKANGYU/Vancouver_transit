# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 16:53:54 2020

@author: kangyuwang
"""

data_version = "20200606"

import altair as alt
import os
import re
import numpy as np
import contextily as ctx
import pandas as pd
import json
import geopandas
import matplotlib.pyplot as plt

cwd = os.path.dirname(os.getcwd())
os.chdir(cwd)
data_dir = os.path.join(os.getcwd(), "TL_data", data_version)

GVA_map_xlim_lower = -13746072.435927173
GVA_map_xlim_higher = -13630000
GVA_map_ylim_lower = 6270302.809935683
GVA_map_ylim_higher = 6345000

alt.data_transformers.disable_max_rows()

# Read intermediate data

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
## Mode of commuting: data from 2016 census
GVA_DA_cmt = pd.concat([GVA_base, GVA_DA[GVA_DA.columns[457:482]]], axis=1)

### Destination

GVA_DA_cmt_dest = GVA_DA_cmt.copy()

GVA_DA_cmt_dest["prop_within_CSD"] = GVA_DA_cmt_dest["vn436"] / GVA_DA_cmt_dest["vn435"]
GVA_DA_cmt_dest["prop_within_CD"] = GVA_DA_cmt_dest["vn437"] / GVA_DA_cmt_dest["vn435"]
GVA_DA_cmt_dest["prop_within_province"] = (
    GVA_DA_cmt_dest["vn438"] / GVA_DA_cmt_dest["vn435"]
)
GVA_DA_cmt_dest["prop_out_province"] = (
    GVA_DA_cmt_dest["vn439"] / GVA_DA_cmt_dest["vn435"]
)

#### CSD level

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
CSD_within_CSD_ax.set_xlim(GVA_map_xlim_lower, GVA_map_xlim_higher)
CSD_within_CSD_ax.set_ylim(GVA_map_ylim_lower, GVA_map_ylim_higher)

ctx.add_basemap(CSD_within_CSD_ax, zoom=12)
plt.title("Proportion of population transitting within CSD", fontsize=30)

plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "commut_within_csd.png"
    )
)

### Mode of commuting
GVA_DA_cmt_mode = GVA_DA_cmt.copy()

GVA_DA_cmt_mode["prop_private_driver"] = (
    GVA_DA_cmt_mode["vn441"] / GVA_DA_cmt_mode["vn440"]
)
GVA_DA_cmt_mode["prop_private_passenger"] = (
    GVA_DA_cmt_mode["vn442"] / GVA_DA_cmt_mode["vn440"]
)
GVA_DA_cmt_mode["prop_public"] = GVA_DA_cmt_mode["vn443"] / GVA_DA_cmt_mode["vn440"]
GVA_DA_cmt_mode["prop_walk"] = GVA_DA_cmt_mode["vn444"] / GVA_DA_cmt_mode["vn440"]
GVA_DA_cmt_mode["prop_bicycle"] = GVA_DA_cmt_mode["vn445"] / GVA_DA_cmt_mode["vn440"]

#### Histogram of distribution of proportion of commute mode use across DAs

GVA_DA_cmt_mode_hist = GVA_DA_cmt_mode.melt(
    id_vars=["DAUID"],
    value_vars=[
        "prop_private_driver",
        "prop_private_passenger",
        "prop_public",
        "prop_walk",
        "prop_bicycle",
    ],
)

GVA_DA_cmt_mode_hist = GVA_DA_cmt_mode_hist.rename(
    columns={"variable": "mode", "value": "prop"}
)
GVA_DA_cmt_mode_hist = GVA_DA_cmt_mode_hist.query("mode !='prop_bicycle' & prop > 0")

GVA_DA_cmt_mode_hist_plot = (
    alt.Chart(GVA_DA_cmt_mode_hist)
    .mark_area(opacity=0.3, interpolate="step")
    .encode(
        x=alt.X("prop:Q", bin=alt.Bin(maxbins=100), title="Proportion"),
        y=alt.Y("count()", stack=None),
        color=alt.Color("mode:N", title="Mode of commute"),
    )
    .properties(title="Mode of Commute Across DAs (Without Biking)")
)


GVA_DA_cmt_mode_hist_plot.save(
    os.path.join(
        os.getcwd(),
        "Vancouver_transit",
        "Figures",
        data_version,
        "DA_mode.png",
    )
)

#### Maps of DAs by quantiles of public transportation proportions
DA_public_cmt_ax = GVA_DA_cmt_mode.plot(
    figsize=(20, 20),
    alpha=0.5,
    column="prop_public",
    cmap="Greens",
    legend=True,
    scheme="quantiles",
)
DA_public_cmt_ax.set_xlim(GVA_map_xlim_lower, GVA_map_xlim_higher)
DA_public_cmt_ax.set_ylim(GVA_map_ylim_lower, GVA_map_ylim_higher)
ctx.add_basemap(DA_public_cmt_ax, zoom=12)
plt.title("Proportion of population using public transportation", fontsize=30)

plt.savefig(
    os.path.join(
        os.getcwd(), "Vancouver_transit", "Maps", data_version, "DA_public_prop.png"
    )
)

#### CSD level
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
GVA_DA_cmt_duration = GVA_DA_cmt.copy()

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
DA_cmt_duration_ax.set_xlim(GVA_map_xlim_lower, GVA_map_xlim_higher)
DA_cmt_duration_ax.set_ylim(GVA_map_ylim_lower, GVA_map_ylim_higher)

ctx.add_basemap(DA_cmt_duration_ax, zoom=12)
plt.title("Average Commuting Time", fontsize=30)

plt.savefig(
    os.path.join(
        os.getcwd(),
        "Vancouver_transit",
        "Maps",
        data_version,
        "DA_commute_duration.png",
    )
)

#### CSD level

GVA_CSD_cmt_duration = GVA_DA_cmt_duration.dissolve(by="CSDNAME", aggfunc="sum")
GVA_CSD_cmt_duration = GVA_CSD_cmt_duration[
    GVA_CSD_cmt_duration.vn447 != 0
]  # Remove SCDs without commute duration data

GVA_CSD_cmt_duration["prop_less_15"] = (
    GVA_CSD_cmt_duration["vn448"] / GVA_CSD_cmt_duration["vn447"]
)
GVA_CSD_cmt_duration["prop_15_29"] = (
    GVA_CSD_cmt_duration["vn449"] / GVA_CSD_cmt_duration["vn447"]
)
GVA_CSD_cmt_duration["prop_30_44"] = (
    GVA_CSD_cmt_duration["vn450"] / GVA_CSD_cmt_duration["vn447"]
)
GVA_CSD_cmt_duration["prop_45_59"] = (
    GVA_CSD_cmt_duration["vn451"] / GVA_CSD_cmt_duration["vn447"]
)
GVA_CSD_cmt_duration["prop_more_60"] = (
    GVA_CSD_cmt_duration["vn452"] / GVA_CSD_cmt_duration["vn447"]
)

GVA_CSD_cmt_duration.loc[
    GVA_CSD_cmt_duration["prop_less_15"] > 0.5, "med_commute_duration"
] = 7.5
GVA_CSD_cmt_duration.loc[
    (GVA_CSD_cmt_duration["prop_less_15"] <= 0.5)
    & (GVA_CSD_cmt_duration["prop_less_15"] + GVA_CSD_cmt_duration["prop_15_29"] > 0.5),
    "med_commute_duration",
] = 22.5
GVA_CSD_cmt_duration.loc[
    (GVA_CSD_cmt_duration["prop_less_15"] + GVA_CSD_cmt_duration["prop_15_29"] <= 0.5)
    & (
        GVA_CSD_cmt_duration["prop_less_15"]
        + GVA_CSD_cmt_duration["prop_15_29"]
        + GVA_CSD_cmt_duration["prop_30_44"]
        > 0.5
    ),
    "med_commute_duration",
] = 37.5
GVA_CSD_cmt_duration.loc[
    (
        GVA_CSD_cmt_duration["prop_less_15"]
        + GVA_CSD_cmt_duration["prop_15_29"]
        + GVA_CSD_cmt_duration["prop_30_44"]
        <= 0.5
    )
    & (
        GVA_CSD_cmt_duration["prop_less_15"]
        + GVA_CSD_cmt_duration["prop_15_29"]
        + GVA_CSD_cmt_duration["prop_30_44"]
        + GVA_CSD_cmt_duration["prop_45_59"]
        > 0.5
    ),
    "med_commute_duration",
] = 52.5
GVA_CSD_cmt_duration.loc[
    (
        GVA_CSD_cmt_duration["prop_less_15"]
        + GVA_CSD_cmt_duration["prop_15_29"]
        + GVA_CSD_cmt_duration["prop_30_44"]
        + GVA_CSD_cmt_duration["prop_45_59"]
        <= 0.5
    ),
    "med_commute_duration",
] = 60

GVA_med_commute_duration = np.average(
    GVA_CSD_cmt_duration.med_commute_duration, weights=GVA_CSD_cmt_duration.vn447
)

CSD_max_commute_duration = GVA_CSD_cmt_duration[
    GVA_CSD_cmt_duration.med_commute_duration
    == max(GVA_CSD_cmt_duration.med_commute_duration)
].index[0]
CSD_min_commute_duration = GVA_CSD_cmt_duration[
    GVA_CSD_cmt_duration.med_commute_duration
    == min(GVA_CSD_cmt_duration.med_commute_duration)
].index[0]

print(
    f"In the Greater Vancouver Area, the average medium commute duration across CSDs is about {GVA_med_commute_duration:.1f} minutes."
)
print(
    f"{CSD_max_commute_duration} has the highest medium commuting time, which is {max(GVA_CSD_cmt_duration.med_commute_duration):.1f} minutes."
)
print(
    f"{CSD_min_commute_duration} has the lowest medium commuting time, which is {min(GVA_CSD_cmt_duration.med_commute_duration):.1f} minutes."
)

# Export files
GVA_DA_cmt_usage = pd.concat(
    [
        GVA_DA_cmt_mode,
        GVA_DA_cmt_dest.loc[
            :,
            [
                "prop_within_CSD",
                "prop_within_CD",
                "prop_within_province",
                "prop_out_province",
            ],
        ],
        GVA_DA_cmt_duration.loc[
            :,
            [
                "prop_less_15",
                "prop_15_29",
                "prop_30_44",
                "prop_45_59",
                "prop_more_60",
                "med_commute_duration",
            ],
        ],
    ],
    axis=1,
)

GVA_DA_cmt_usage.to_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_cmt_usage.json"),
    driver="GeoJSON",
)
