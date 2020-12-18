# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 16:53:54 2020

@author: kangyuwang
"""

data_version = "20200606"

import altair as alt
import os
import geopandas
from joblib import dump, load
import json
import numpy as np
import pandas as pd
import shap

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import (
    cross_val_score,
    cross_validate,
    train_test_split,
    RandomizedSearchCV,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler,
    MinMaxScaler,
)

cwd = os.path.dirname(os.getcwd())
os.chdir(cwd)
data_dir = os.path.join(os.getcwd(), "TL_data", data_version)

GVA_map_xlim_lower = -13746072.435927173
GVA_map_xlim_higher = -13630000
GVA_map_ylim_lower = 6270302.809935683
GVA_map_ylim_higher = 6345000

# Import data

GVA_DA_Modeling_train = geopandas.read_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_Modeling_train.json")
)

with open(
    os.path.join(
        os.getcwd(), "Data_Tables", data_version, "GVA_DA_Modeling_header.json"
    ),
    "r",
) as GVA_DA_Modeling_header_outfile:
    GVA_DA_Modeling_header = json.load(GVA_DA_Modeling_header_outfile)

GVA_DA_Modeling_header.remove("geometry")
GVA_DA_Modeling_header.append("geometry")

# Preliminary analyses on train set
## Weak yet positive relationship between accesibility and usage
GVA_DA_Modeling_train.loc[:, ["NBA_services_PC", "NBA_stops_PC", "prop_public"]].corr()

## Visualizations
stop_PC_prop_public = (
    alt.Chart(
        GVA_DA_Modeling_train,
        title="Access to Stops in Neighborhood Area and Transit Use",
    )
    .mark_rect(clip=True)
    .encode(
        x=alt.X(
            "NBA_stops_PC",
            title="Number of stops per capita in neighborhood area",
            bin=alt.Bin(maxbins=300),
            scale=alt.Scale(domain=[0, 0.15]),
        ),
        y=alt.Y(
            "prop_public", title="Proportion of transit user", bin=alt.Bin(maxbins=50)
        ),
        color=alt.Color("count()", title="Count"),
    )
)

stop_PC_prop_public.save(
    os.path.join(
        os.getcwd(),
        "Vancouver_transit",
        "Figures",
        data_version,
        "stop_PC_prop_public.png",
    )
)

service_PC_prop_public = (
    alt.Chart(
        GVA_DA_Modeling_train,
        title="Access to Services in Neighborhood Area and Transit Use",
    )
    .mark_rect(clip=True)
    .encode(
        x=alt.X(
            "NBA_services_PC",
            title="Number of services per capita in neighborhood area",
            bin=alt.Bin(maxbins=1000),
            scale=alt.Scale(domain=[0, 75]),
        ),
        y=alt.Y(
            "prop_public", title="Proportion of transit user", bin=alt.Bin(maxbins=50)
        ),
        color=alt.Color("count()", title="Count"),
    )
)

service_PC_prop_public.save(
    os.path.join(
        os.getcwd(),
        "Vancouver_transit",
        "Figures",
        data_version,
        "service_PC_prop_public.png",
    )
)

# Create input and outcome variables
X_train = GVA_DA_Modeling_train.drop(["prop_public"], axis=1)
X_header = GVA_DA_Modeling_header
X_header.remove("prop_public")
y_train = GVA_DA_Modeling_train["prop_public"]

# Create pipeline

## Identify variable types
categorical_features = [
    "PRUID",
    "CDUID",
    "CCSUID",
    "CSDUID",
    "ERUID",
    "CMAUID",
    "CMAPUID",
    # "CTUID", # This categorical variable is excluded due to large number of unique values
    "ADAUID",
]

numeric_features = X_train.columns[10:474]
### Remove numeric features that are made of NAs
numeric_features = [
    feature
    for feature in numeric_features
    if X_train.isnull().all(axis=0)[feature] == False
]

proportion_features = X_train.columns[475:-1]
### Remove numeric features that are made of NAs
proportion_features = [
    feature
    for feature in proportion_features
    if X_train.isnull().all(axis=0)[feature] == False
]

geometry_feature = ["geometry"]

# Create pipelines
## Pre-processing

categorical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ]
)

numeric_transformer = Pipeline(
    steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
)

proportion_transformer = Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))])

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", categorical_transformer, categorical_features),
        ("num", numeric_transformer, numeric_features),
        ("prop", proportion_transformer, proportion_features),
    ],
    remainder="drop",
)

## Dummy model
pipe_dummy = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("dummy_reg", DummyRegressor()),
    ]
)
## LASSO model
pipe_LASSO = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("LASSO_reg", Lasso()),
    ]
)
## Random Forest model
pipe_rf = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("rf_reg", RandomForestRegressor()),
    ]
)

# Baseline: dummy model

scores_dummy = cross_validate(
    pipe_dummy,
    X_train,
    y_train,
    return_train_score=True,
)
pd.DataFrame(scores_dummy).T

# LASSO model

## default model

scores_LASSO_default = cross_validate(
    pipe_LASSO,
    X_train,
    y_train,
    return_train_score=True,
)
pd.DataFrame(scores_LASSO_default).T

## Hyperparameter optimization

param_grid = {
    "LASSO_reg__alpha": 10.0 ** np.arange(-5, 5),
}

random_search_LASSO = RandomizedSearchCV(
    pipe_LASSO, param_distributions=param_grid, n_jobs=-2, n_iter=10
)

random_search_LASSO.fit(X_train, y_train)


LASSO_CV_results = (
    pd.DataFrame(random_search_LASSO.cv_results_)[
        [
            "mean_test_score",
            "param_LASSO_reg__alpha",
            "mean_fit_time",
            "rank_test_score",
        ]
    ]
    .set_index("rank_test_score")
    .sort_index()
)

LASSO_CV_results.to_csv(
    os.path.join(
        os.getcwd(),
        "Models",
        data_version,
        "LASSO_CV_results.csv",
    )
)

# Random Forest model

## Default model

scores_rf_default = cross_validate(
    pipe_rf,
    X_train,
    y_train,
    return_train_score=True,
)
pd.DataFrame(scores_rf_default).T

## Hyperparameter optimization

param_grid = {
    "rf_reg__max_depth": [10, 40, 70, 100, None],
    "rf_reg__max_features": ["auto", "sqrt"],
    "rf_reg__min_samples_leaf": [1, 2, 4],
    "rf_reg__min_samples_split": [2, 5, 10],
    "rf_reg__n_estimators": [200, 600, 1000, 2000],
}

random_search_rf = RandomizedSearchCV(
    pipe_rf, param_distributions=param_grid, n_jobs=-2, n_iter=10
)

random_search_rf.fit(X_train, y_train)

rf_CV_results = (
    pd.DataFrame(random_search_rf.cv_results_)[
        [
            "mean_test_score",
            "param_rf_reg__max_depth",
            "param_rf_reg__max_features",
            "param_rf_reg__min_samples_leaf",
            "param_rf_reg__min_samples_split",
            "param_rf_reg__n_estimators",
            "mean_fit_time",
            "rank_test_score",
        ]
    ]
    .set_index("rank_test_score")
    .sort_index()
)

rf_CV_results.to_csv(
    os.path.join(
        os.getcwd(),
        "Models",
        data_version,
        "rf_CV_results.csv",
    )
)
# Preliminary analyses on models

# Get input variable names

### Define function get_column_names_from_ColumnTransformer


def get_column_names_from_ColumnTransformer(column_transformer):

    col_name = []

    for transformer_in_columns in column_transformer.transformers_[
        :-1
    ]:  # the last transformer is ColumnTransformer's 'remainder'
        print("\n\ntransformer: ", transformer_in_columns[0])

        raw_col_name = list(transformer_in_columns[2])

        if isinstance(transformer_in_columns[1], Pipeline):
            # if pipeline, get the last transformer
            transformer = transformer_in_columns[1].steps[-1][1]
        else:
            transformer = transformer_in_columns[1]

        try:
            if isinstance(transformer, OneHotEncoder):
                names = list(transformer.get_feature_names(raw_col_name))

            elif isinstance(transformer, SimpleImputer) and transformer.add_indicator:
                missing_indicator_indices = transformer.indicator_.features_
                missing_indicators = [
                    raw_col_name[idx] + "_missing_flag"
                    for idx in missing_indicator_indices
                ]

                names = raw_col_name + missing_indicators

            else:
                names = list(transformer.get_feature_names())

        except AttributeError as error:
            names = raw_col_name

        print(names)

        col_name.extend(names)

    return col_name


preprocessor.fit(X_train)
feature_names = get_column_names_from_ColumnTransformer(preprocessor)

## LASSO model

LASSO_coeffs = random_search_LASSO.best_estimator_["LASSO_reg"].coef_

LASSO_feature_coeffs = pd.DataFrame({"feature": feature_names, "coeffs": LASSO_coeffs})

## Random Forest model

### Impurity
rf_immpurity_feat_imp = random_search_rf.best_estimator_["rf_reg"].feature_importances_

rf_immpurity_feat_imp_coeffs = pd.DataFrame(
    {"feature": feature_names, "impurity_importance": rf_immpurity_feat_imp}
)

rf_immpurity_feat_imp_coeffs.to_json(
    os.path.join(
        os.getcwd(), "Data_Tables", data_version, "rf_immpurity_feat_imp_coeffs.json"
    ),
)

### SHAP
explainer = shap.TreeExplainer(random_search_rf.best_estimator_.named_steps["rf_reg"])

preprocessed_data = pd.DataFrame(
    data=preprocessor.transform(X_train),
    columns=feature_names,
    index=X_train.index,
)

shap_values = explainer.shap_values(preprocessed_data)

with open(
    os.path.join(
        os.getcwd(),
        "Models",
        data_version,
        "shap_values.npy",
    ),
    "wb",
) as f:
    np.save(f, shap_values)

# Model performance

## RMSE on the whole train set

pipe_dummy.fit(X_train, y_train)
dummy_pred_train = pipe_dummy.predict(X_train)
print(
    f"The train split RMSE of dummy model is {mean_squared_error(y_train, dummy_pred_train, squared=False):.3f}"
)

random_search_LASSO.best_estimator_.fit(X_train, y_train)
LASSO_pred_train = random_search_LASSO.best_estimator_.predict(X_train)
print(
    f"The train split RMSE of LASSO regression is {mean_squared_error(y_train, LASSO_pred_train, squared=False):.3f}"
)

random_search_rf.best_estimator_.fit(X_train, y_train)
rf_pred_train = random_search_rf.best_estimator_.predict(X_train)
print(
    f"The train split RMSE of best random forest model is {mean_squared_error(y_train, rf_pred_train, squared=False):.3f}"
)

## Performance of Random Forest model on test split

GVA_DA_Modeling_test = geopandas.read_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_Modeling_test.json")
)

X_test = GVA_DA_Modeling_test.drop(["prop_public"], axis=1)
y_test = GVA_DA_Modeling_test["prop_public"]

rf_pred_test = random_search_rf.best_estimator_.predict(X_test)

print(
    f"The test split RMSE of best random forest model is {mean_squared_error(y_test, rf_pred_test, squared=False):.3f}"
)

# Save models and data

dump(
    random_search_LASSO,
    os.path.join(
        os.getcwd(),
        "Models",
        data_version,
        "random_search_LASSO.joblib",
    ),
)

dump(
    random_search_rf,
    os.path.join(
        os.getcwd(),
        "Models",
        data_version,
        "random_search_rf.joblib",
    ),
)

X_train.to_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "X_train.json"),
    driver="GeoJSON",
)

dump(
    (
        preprocessor,
        categorical_transformer,
        numeric_transformer,
        proportion_transformer,
        ColumnTransformer,
    ),
    os.path.join(os.getcwd(), "Models", data_version, "preprocessor.joblib"),
)

with open(
    os.path.join(os.getcwd(), "Models", data_version, "features.json"),
    "w+",
) as feature_outfile:
    json.dump(
        (categorical_features, numeric_features, proportion_features, geometry_feature),
        feature_outfile,
    )

with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "X_header.json"),
    "w+",
) as X_header_outfile:
    json.dump(X_header, X_header_outfile)

with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "y_train.json"),
    "w+",
) as y_train_outfile:
    json.dump(y_train.to_json(), y_train_outfile)
