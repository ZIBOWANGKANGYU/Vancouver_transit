# Read in modules
import altair as alt
import geopandas
import json
import joblib
import os
import numpy as np
import pandas as pd

## sklearn modules
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Lasso
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler,
    MinMaxScaler,
)

## Mapping modules
import contextily as ctx
import matplotlib.pyplot as plt

GVA_map_xlim_lower = -13746072.435927173
GVA_map_xlim_higher = -13630000
GVA_map_ylim_lower = 6270302.809935683
GVA_map_ylim_higher = 6345000

data_version = "20200606"

# Read data
X_train = geopandas.read_file(os.path.join("Data_Tables", data_version, "X_train.json"))

# Whole dataset
df_full = geopandas.read_file(
    os.path.join("Data_Tables", data_version, "GVA_DA_Modeling.json")
)
X = df_full.drop(["prop_public"], axis=1)

# Read in preprocessor and model
(
    preprocessor,
    categorical_transformer,
    numeric_transformer,
    proportion_transformer,
    ColumnTransformer,
) = joblib.load(os.path.join("Models", data_version, "preprocessor.joblib"))
preprocessor.fit(X_train)

random_search_rf = joblib.load(
    os.path.join(
        "Models",
        data_version,
        "random_search_rf.joblib",
    )
)
## Get predictions on whole dataset
X_preprocessed = preprocessor.transform(X)
X_pred_rf = random_search_rf.best_estimator_["rf_reg"].predict(X_preprocessed)

# Simulate policies
preds = dict()
colnames = []
for policy_mag in [0.05, 0.1, 0.15, 0.2, 0.3]:

    X_1 = X.copy()
    delta = policy_mag * X_1.loc[:, "NBA_services_PC"].mean()
    X_1.loc[:, "NBA_services_PC"] = X_1.loc[:, "NBA_services_PC"] + delta

    X_1_preprocessed = preprocessor.transform(X_1)
    X_1_pred_rf = random_search_rf.best_estimator_["rf_reg"].predict(X_1_preprocessed)
    colname = "Sce1" + str(policy_mag)[2:] + "rf"
    preds[colname] = X_1_pred_rf
    colnames.append(colname)

    X_2 = X.copy()
    X_2.loc[:, "NBA_services_PC"] = X_2.loc[:, "NBA_services_PC"] * (1 + policy_mag)

    X_2_preprocessed = preprocessor.transform(X_2)
    X_2_pred_rf = random_search_rf.best_estimator_["rf_reg"].predict(X_2_preprocessed)
    colname = "Sce2" + str(policy_mag)[2:] + "rf"
    preds[colname] = X_2_pred_rf
    colnames.append(colname)

# Save data
preds = pd.DataFrame(preds)

X = pd.concat([X, preds], axis=1)
gdf_toDash = X[["DAUID", "vn13", "vn19", "NBA_services_PC", "geometry"] + colnames]
gdf_toDash = gdf_toDash.copy()
gdf_toDash["prop_public"] = df_full["prop_public"]
gdf_toDash = gdf_toDash.to_crs(epsg=4326)

gdf_toDash.to_file(
    os.path.join("Data_Tables", "Dash_data", "gdf_toDash.json"),
    driver="GeoJSON",
)
