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
from itertools import compress
from sklearn.model_selection import train_test_split


GVA_map_xlim_lower = -13746072.435927173
GVA_map_xlim_higher = -13630000
GVA_map_ylim_lower = 6270302.809935683
GVA_map_ylim_higher = 6345000

# Import data

## Usage data
GVA_DA_cmt_usage = geopandas.read_file(
    os.path.join("Data_Tables", data_version, "GVA_DA_cmt_usage.json")
)

## Access data
GVA_DA_Access = geopandas.read_file(
    os.path.join("Data_Tables", data_version, "GVA_DA_Access.json")
)

## Header
with open(
    os.path.join("Data_Tables", data_version, "GVA_DA_header.json"), "r"
) as DA_header_outfile:
    header = json.load(DA_header_outfile)

GVA_DA_cmt_usage_df = GVA_DA_cmt_usage.loc[
    :,
    [
        "prop_private_driver",
        "prop_private_passenger",
        "prop_public",
        "prop_walk",
        "prop_bicycle",
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
GVA_DA_Preprocess_header = list(header)[:-1] + list(GVA_DA_Preprocess.columns[-20:])

# Cleaning rows

## By basic demographic features

### Population
print(
    f"There are {sum(GVA_DA_Preprocess['vn13'] == 0)} DA(s) with zero population in 2016."
)
GVA_DA_Preprocess = GVA_DA_Preprocess.loc[
    (GVA_DA_Preprocess["vn13"] != 0) & (GVA_DA_Preprocess["vn13"].isnull() == False), :
]

### Land size
print(
    f"There are {sum(GVA_DA_Preprocess['vn19'] == 0)} DA(s) with zero land size in 2016."
)
GVA_DA_Preprocess = GVA_DA_Preprocess.loc[
    (GVA_DA_Preprocess["vn19"] != 0) & (GVA_DA_Preprocess["vn19"].isnull() == False), :
]

#### Remove very large DAs (above 2 standard deviations above mean)
land_area_threshold = (
    GVA_DA_Preprocess["vn19"].mean() + GVA_DA_Preprocess["vn19"].std() * 2
)
print(
    f"There are {sum(GVA_DA_Preprocess['vn19'] >= land_area_threshold)} DA(s) with land size 2 standard deviations above the mean in 2016"
)

GVA_DA_Preprocess = GVA_DA_Preprocess.loc[
    GVA_DA_Preprocess["vn19"] < land_area_threshold, :
]

### Population density
pop_dens_threshold_higher = np.exp(
    np.log(GVA_DA_Preprocess["vn18"]).mean()
    + 2 * np.log(GVA_DA_Preprocess["vn18"]).std()
)
print(
    f"There are {sum(GVA_DA_Preprocess['vn18'] >= pop_dens_threshold_higher)} DA(s) with population density 2 standard deviations above the mean in 2016"
)

pop_dens_threshold_lower = np.exp(
    np.log(GVA_DA_Preprocess["vn18"]).mean()
    - 2 * np.log(GVA_DA_Preprocess["vn18"]).std()
)
print(
    f"There are {sum(GVA_DA_Preprocess['vn18'] <= pop_dens_threshold_lower)} DA(s) with population density 2 standard deviations below the mean in 2016"
)

GVA_DA_Preprocess = GVA_DA_Preprocess.loc[
    (GVA_DA_Preprocess["vn18"] < pop_dens_threshold_higher)
    & (GVA_DA_Preprocess["vn18"] > pop_dens_threshold_lower),
    :,
]

### Service count
print(
    f"There are {sum(GVA_DA_Preprocess['DA_NBA_services_count'] == 0)} DA(s) without public transit service in its neighborhood area."
)

GVA_DA_Preprocess = GVA_DA_Preprocess.loc[
    (GVA_DA_Preprocess["DA_NBA_services_count"] != 0)
    & (GVA_DA_Preprocess["DA_NBA_services_count"].isnull() == False),
    :,
]

### Stop count
print(
    f"There are {sum(GVA_DA_Preprocess['DA_NBA_stops_count'] == 0)} DA(s) without public transit stops in its neighborhood area."
)

GVA_DA_Preprocess = GVA_DA_Preprocess.loc[
    (GVA_DA_Preprocess["DA_NBA_stops_count"] != 0)
    & (GVA_DA_Preprocess["DA_NBA_stops_count"].isnull() == False),
    :,
]

## By outcome variable

### Proportion of transit use
print(
    f"There are {sum(GVA_DA_Preprocess['prop_public'].isnull() == True)} DA(s) where the propotion of people using public transit is invalid."
)

GVA_DA_Preprocess = GVA_DA_Preprocess.loc[
    GVA_DA_Preprocess["prop_public"].isnull() == False,
    :,
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
        "Maps",
        data_version,
        "DA_removed.png",
    )
)

# Create proportion variables
# There are two types of numeric columns in the dataframe:
# 1) Proportions or averages
# 2) Counts
# We will put (1)-type variables directly into our models. For (2)-type variables, there are two sub-types:
# 2.1) Counts of subjects belonging to the widest category in a DA, for example, total number of people who are immigrants.
# We will put (2.1)-type variables directly into our models.
# 2.2) Counts of subjects belonging to a sub-category of a (2.1)-type variable in a DA. There are two sub-types:
# 2.2.1) Counts of subjects belonging to a immediate sub-category of a (2.1)-type variable, for example, total number of immigrants who are born in Asia.
# We will use (2.2.1)-type variables in two ways.
# Firstly, we will put type (2.2.1) variables directly into our models.
# Secondly, we will calculate the proportion that each (2.2.1)-type variable accounts for in the (2.1)-type variable that it belongs to.
# 2.2.2) Counts of subjects beloinging to a further-off sub-category of a variable in (2.1), for example, total number of immigrants who are born in India, Asia.
# We will use (2.2.2)-type bariables in three ways.
# Firstly, we will put type (2.2.2) variables directly into our models.
# Secondly, we will calculate the proportion that each (2.2.2)-type variable accounts for in the (2.1)-type variable that it ultimately (but not immediately) belongs to.
# Thirdly, we will calculate the proportion that each (2.2.2)-type variable accounts for in the (2.2.1)- or (2.2.2)-type variable that it immediately belongs to.

GVA_DA_Preprocess_variable_types = pd.DataFrame(
    {"variable_name": list(GVA_DA_Preprocess_header)}
)

GVA_DA_Preprocess_variable_types["variable_type"] = None

GVA_DA_Preprocess_variable_types.loc[
    GVA_DA_Preprocess_variable_types["variable_name"] == "DAUID", "variable_type"
] = "IND"

GVA_DA_Preprocess_variable_types.loc[1:21, "variable_type"] = "CAT"

GVA_DA_Preprocess_variable_types.loc[
    1:21, "variable_type"
] = GVA_DA_Preprocess_variable_types.loc[1:21, "variable_type"].where(
    GVA_DA_Preprocess_variable_types.loc[1:21, "variable_name"].str.endswith("ID"),
    "DEL",
)

GVA_DA_Preprocess_variable_types.loc[22:27, "variable_type"] = "DEL"

GVA_DA_Preprocess_variable_types.loc[550:569, "variable_type"] = "1_2_1"

## Find type(1) and type (2.1) variables
GVA_DA_Preprocess_variable_types.loc[
    28:549, "variable_type"
] = GVA_DA_Preprocess_variable_types.loc[28:549, "variable_type"].where(
    GVA_DA_Preprocess_variable_types.loc[
        GVA_DA_Preprocess_variable_types["variable_name"] == "DAUID", "variable_name"
    ].str.count("/")
    > 1,
    "1_2_1",
)

## Find type(2.2.1) variables
GVA_DA_Preprocess_variable_types.loc[
    28:549, "variable_type"
] = GVA_DA_Preprocess_variable_types.loc[28:549, "variable_type"].where(
    (
        (
            GVA_DA_Preprocess_variable_types.loc[28:549, "variable_name"].str.count("/")
            > 2
        )
        | (
            GVA_DA_Preprocess_variable_types.loc[28:549, "variable_name"].str.count("/")
            <= 1
        )
    ),
    "2_2_1",
)

## Find variables that should not be included as predictors in modeling
GVA_DA_Preprocess_variable_types.loc[462:481, "variable_type"] = "N_INC"
GVA_DA_Preprocess_variable_types.loc[505:524, "variable_type"] = "N_INC"
GVA_DA_Preprocess_variable_types.loc[530:549, "variable_type"] = "N_INC"
GVA_DA_Preprocess_variable_types.loc[550, "variable_type"] = "N_INC"
GVA_DA_Preprocess_variable_types.loc[552, "variable_type"] = "N_INC"
GVA_DA_Preprocess_variable_types.loc[555:556, "variable_type"] = "N_INC"
GVA_DA_Preprocess_variable_types.loc[558:569, "variable_type"] = "N_INC"


### Find parent variables of type(2.2.1) variables
GVA_DA_Preprocess_variable_types["ultimate_parent"] = None
GVA_DA_Preprocess_variable_types["immediate_parent"] = None

ultimate_parents = list(
    map(
        lambda s: s[: s.find("/", s.find("/") + 1) - 1],
        list(
            GVA_DA_Preprocess_variable_types.loc[
                GVA_DA_Preprocess_variable_types["variable_type"] == "2_2_1",
                "variable_name",
            ]
        ),
    )
)

GVA_DA_Preprocess_variable_types.loc[
    GVA_DA_Preprocess_variable_types["variable_type"] == "2_2_1",
    "ultimate_parent",
] = [
    ultimate_parent
    if (ultimate_parent in list(GVA_DA_Preprocess_variable_types["variable_name"]))
    else None
    for ultimate_parent in ultimate_parents
]

## Find type(2.2.2) variables
GVA_DA_Preprocess_variable_types.loc[
    28:549, "variable_type"
] = GVA_DA_Preprocess_variable_types.loc[28:549, "variable_type"].where(
    GVA_DA_Preprocess_variable_types.loc[28:549, "variable_name"].str.count("/") <= 2,
    "2_2_2",
)

### Find parent variables of type(2.2.2) variables

#### Find ultimate parents
ultimate_parents = list(
    map(
        lambda s: s[: s.find("/", s.find("/") + 1) - 1],
        list(
            GVA_DA_Preprocess_variable_types.loc[
                GVA_DA_Preprocess_variable_types["variable_type"] == "2_2_2",
                "variable_name",
            ]
        ),
    )
)

GVA_DA_Preprocess_variable_types.loc[
    GVA_DA_Preprocess_variable_types["variable_type"] == "2_2_2",
    "ultimate_parent",
] = [
    ultimate_parent
    if (ultimate_parent in list(GVA_DA_Preprocess_variable_types["variable_name"]))
    else None
    for ultimate_parent in ultimate_parents
]

#### Find immediate parents
immediate_parents = list(
    map(
        lambda s: s[: s.rfind("/") - 1],
        list(
            GVA_DA_Preprocess_variable_types.loc[
                GVA_DA_Preprocess_variable_types["variable_type"] == "2_2_2",
                "variable_name",
            ]
        ),
    )
)

GVA_DA_Preprocess_variable_types.loc[
    GVA_DA_Preprocess_variable_types["variable_type"] == "2_2_2",
    "immediate_parent",
] = [
    immediate_parent
    if (immediate_parent in list(GVA_DA_Preprocess_variable_types["variable_name"]))
    else None
    for immediate_parent in immediate_parents
]

# Create new dataframe containing ultimate-parents proportion variables
ultimate_proportions = pd.DataFrame()

for i, variable_name in enumerate(GVA_DA_Preprocess_variable_types.variable_name):
    if not GVA_DA_Preprocess_variable_types.ultimate_parent[i]:
        continue
    parent_variable_name = GVA_DA_Preprocess.columns[
        list(GVA_DA_Preprocess_variable_types.variable_name).index(
            GVA_DA_Preprocess_variable_types.ultimate_parent[i]
        )
    ]
    new_variable_name = (
        GVA_DA_Preprocess.columns[i] + "_ultimate_" + parent_variable_name
    )

    ultimate_proportions[new_variable_name] = (
        GVA_DA_Preprocess[GVA_DA_Preprocess.columns[i]]
        / GVA_DA_Preprocess[parent_variable_name]
    )

# Create new dataframe containing immediate-parents proportion variables
immediate_proportions = pd.DataFrame()

for i, variable_name in enumerate(GVA_DA_Preprocess_variable_types.variable_name):
    if not GVA_DA_Preprocess_variable_types.immediate_parent[i]:
        continue
    parent_variable_name = GVA_DA_Preprocess.columns[
        list(GVA_DA_Preprocess_variable_types.variable_name).index(
            GVA_DA_Preprocess_variable_types.immediate_parent[i]
        )
    ]
    new_variable_name = (
        GVA_DA_Preprocess.columns[i] + "_immediate_" + parent_variable_name
    )

    immediate_proportions[new_variable_name] = (
        GVA_DA_Preprocess[GVA_DA_Preprocess.columns[i]]
        / GVA_DA_Preprocess[parent_variable_name]
    )

# Create and save dataframes ready for modeling
GVA_DA_Modeling_header = (
    list(
        compress(
            GVA_DA_Preprocess_header,
            list(
                (GVA_DA_Preprocess_variable_types.variable_type != "DEL")
                & (GVA_DA_Preprocess_variable_types.variable_type != "N_INC")
            ),
        )
    )
    + list(ultimate_proportions.columns)
    + list(immediate_proportions.columns)
)

GVA_DA_Modeling = pd.concat(
    [
        GVA_DA_Preprocess.loc[
            :,
            list(
                (GVA_DA_Preprocess_variable_types.variable_type != "DEL")
                & (GVA_DA_Preprocess_variable_types.variable_type != "N_INC")
            ),
        ],
        ultimate_proportions,
        immediate_proportions,
    ],
    axis=1,
)

GVA_DA_Modeling.dtypes

## Create training and testing sets

GVA_DA_Modeling_train, GVA_DA_Modeling_test = train_test_split(
    GVA_DA_Modeling, test_size=0.2, random_state=2020
)

## Save dataframes

GVA_DA_Modeling.to_file(
    os.path.join("Data_Tables", data_version, "GVA_DA_Modeling.json"),
    driver="GeoJSON",
)

GVA_DA_Modeling_train.to_file(
    os.path.join("Data_Tables", data_version, "GVA_DA_Modeling_train.json"),
    driver="GeoJSON",
)

GVA_DA_Modeling_test.to_file(
    os.path.join("Data_Tables", data_version, "GVA_DA_Modeling_test.json"),
    driver="GeoJSON",
)

with open(
    os.path.join("Data_Tables", data_version, "GVA_DA_Modeling_header.json"),
    "w+",
) as GVA_DA_Modeling_header_outfile:
    json.dump(GVA_DA_Modeling_header, GVA_DA_Modeling_header_outfile)