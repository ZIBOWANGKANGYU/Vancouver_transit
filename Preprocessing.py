# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 16:53:54 2020

@author: kangyuwang
"""

data_version = "20200606"

import os
import geopandas
import numpy as np
import contextily as ctx
import pandas as pd
import json
import geopandas
import matplotlib.pyplot as plt
import altair as alt
import math

cwd = os.path.dirname(os.getcwd())
os.chdir(cwd)
data_dir = os.path.join(os.getcwd(), "TL_data", data_version)

GVA_map_xlim_lower = -13746072.435927173
GVA_map_xlim_higher = -13630000
GVA_map_ylim_lower = 6270302.809935683
GVA_map_ylim_higher = 6345000

# Import data

## Usage data
GVA_DA_cmt_usage = geopandas.read_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_cmt_usage.json")
)

## Access data
GVA_DA_Access = geopandas.read_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_Access.json")
)

## Header
with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_header.json"), "r"
) as DA_header_outfile:
    header = json.load(DA_header_outfile)

GVA_DA_cmt_usage_df = GVA_DA_cmt_usage.loc[
    :,
    [
        "prop_private_driver",
        "prop_private_passenger",
        "prop_public",
        "prop_walk",
        "bicycle",
        "prop_within_CSD",
        "prop_within_CD",
        "prop_within_province",
        "prop_out_province",
        "prop_less_15",
        "prop_15_29",
        "prop_30_44",
        "prop_45_59",
        "prop_more_60",
        "med_commute_duration",
    ],
]

GVA_DA_Preprocess = pd.concat([GVA_DA_Access, GVA_DA_cmt_usage_df], axis=1)

# Cleaning roles

## By basic demographic features

### Population
print(
    f"There are {sum(GVA_DA_Preprocess['vn13'] == 0)} DA(s) with zero population in 2016."
)
GVA_DA_Preprocess = GVA_DA_Preprocess.loc[GVA_DA_Preprocess["vn13"] != 0, :]

### Land size
print(
    f"There are {sum(GVA_DA_Preprocess['vn19'] == 0)} DA(s) with zero land size in 2016."
)
GVA_DA_Preprocess = GVA_DA_Preprocess.loc[GVA_DA_Preprocess["vn19"] != 0, :]

#### Remove very large DAs (above 2 standard deviations above mean)
land_area_threshold = (
    GVA_DA_Preprocess["vn19"].mean() + GVA_DA_Preprocess["vn19"].std() * 2
)
GVA_DA_Preprocess = GVA_DA_Preprocess.loc[
    GVA_DA_Preprocess["vn19"] < land_area_threshold, :
]

### Population density
pop_dens_threshold_higher = np.exp(
    np.log(GVA_DA_Preprocess["vn18"]).mean()
    + 2 * np.log(GVA_DA_Preprocess["vn18"]).std()
)

pop_dens_threshold_lower = np.exp(
    np.log(GVA_DA_Preprocess["vn18"]).mean()
    - 2 * np.log(GVA_DA_Preprocess["vn18"]).std()
)

GVA_DA_Preprocess = GVA_DA_Preprocess.loc[
    (GVA_DA_Preprocess["vn18"] < pop_dens_threshold_higher)
    & (GVA_DA_Preprocess["vn18"] > pop_dens_threshold_lower),
    :,
]
## By outcome variable

### Service count
GVA_DA_Preprocess = GVA_DA_Preprocess.loc[
    GVA_DA_Preprocess["DA_NBA_services_count"] != 0, :
]

### Stop count
GVA_DA_Preprocess = GVA_DA_Preprocess.loc[
    GVA_DA_Preprocess["DA_NBA_stops_count"] != 0, :
]

## Map removed DAs
GVA_DA_Access["included"] = True
GVA_DA_Access.loc[
    GVA_DA_Access["vn5"].isin(GVA_DA_Preprocess["vn5"]), "included"
] = False

GVA_DA_removed_ax = GVA_DA_Access.plot(
    figsize=(20, 20),
    alpha=0.5,
    column="included",
    legend=True,
    categorical=True,
    cmap="Paired",
)
GVA_DA_removed_ax.set_xlim(GVA_map_xlim_lower, GVA_map_xlim_higher)
GVA_DA_removed_ax.set_ylim(GVA_map_ylim_lower, GVA_map_ylim_higher)

ctx.add_basemap(GVA_DA_removed_ax, zoom=12)
plt.title("Removed DAs", fontsize=30)

plt.savefig(
    os.path.join(
        os.getcwd(),
        "Vancouver_transit",
        "Maps",
        data_version,
        "DA_removed.png",
    )
)

# Preliminary analyses
## Weak nonetheless positive relationship between accesibility and usage
GVA_DA_Preprocess.loc[:, ["NBA_stops_PC", "prop_public"]].corr()

GVA_DA_Preprocess.loc[:, ["NBA_services_PC", "prop_public"]].corr()

## Visualizations
stop_PC_prop_public = (
    alt.Chart(
        GVA_DA_Preprocess, title="Access to Stops in Neighborhood Area and Transit Use"
    )
    .mark_rect()
    .encode(
        x=alt.X(
            "NBA_stops_PC",
            title="Number of stops per capita in neighborhood area",
            bin=alt.Bin(maxbins=100),
            scale=alt.Scale(domain=[0, 0.3]),
        ),
        y=alt.Y(
            "prop_public", title="Proportion of transit user", bin=alt.Bin(maxbins=50)
        ),
        color=alt.Color("count()"),
    )
)

stop_PC_prop_public.save(
    os.path.join(
        os.getcwd(),
        "Vancouver_transit",
        "Maps",
        data_version,
        "stop_PC_prop_public.html",
    )
)

service_PC_prop_public = (
    alt.Chart(
        GVA_DA_Preprocess,
        title="Access to Services in Neighborhood Area and Transit Use",
    )
    .mark_rect()
    .encode(
        x=alt.X(
            "NBA_services_PC",
            title="Number of services per capita in neighborhood area",
            bin=alt.Bin(maxbins=1000),
            scale=alt.Scale(domain=[0, 100]),
        ),
        y=alt.Y(
            "prop_public", title="Proportion of transit user", bin=alt.Bin(maxbins=50)
        ),
        color=alt.Color("count()"),
    )
)

service_PC_prop_public.save(
    os.path.join(
        os.getcwd(),
        "Vancouver_transit",
        "Maps",
        data_version,
        "service_PC_prop_public.html",
    )
)

GVA_DA_Preprocess.to_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_Preprocess.json"),
    driver="GeoJSON",
)
