import altair as alt
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import nbformat
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd
import geopandas
import os

# Metadata
data_version = "20200606"

# Read data
gdf_toDash = geopandas.read_file(
    os.path.join("Data_Tables", "Dash_data", "gdf_toDash.json")
)
geo_df = geopandas.GeoDataFrame.from_features(
    gdf_toDash.__geo_interface__["features"]
).set_index("DAUID")

# Define app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = dbc.Container(
    [
        dbc.Tabs(
            [
                dbc.Tab(
                    [
                        html.H1(
                            "Public Transportation Development Priorities in Greater Vancouver: A Machine Learning Approach",
                            style={
                                "padding": 20,
                                "text-align": "center",
                                "border-radius": 3,
                            },
                        ),
                        html.P("App Developed by Mark Wang"),
                        dcc.RadioItems(
                            id="model_widget",
                            options=[
                                {"label": "Random Forest", "value": "rf"},
                                {
                                    "label": "LASSO",
                                    "value": "LASSO",
                                },
                            ],
                            value="RF",
                            labelStyle={"display": "block"},
                        ),
                        dcc.Graph(
                            id="map_snapshot",
                            style={
                                "border-width": "0",
                                "width": "100%",
                                "height": "50vh",
                            },
                        ),
                    ],
                    label="Main page",
                ),
                dbc.Tab(
                    [
                        html.H1(
                            "Public Transportation Development Priorities in Greater Vancouver: A Machine Learning Approach",
                            style={
                                "padding": 20,
                                "text-align": "center",
                                "border-radius": 3,
                            },
                        ),
                        html.P("App Developed by Mark Wang"),
                    ],
                    label="About",
                ),
            ]
        )
    ],
    fluid=True,
    style={"max-width": "95%"},
)

# Define elements
### Map
@app.callback(
    Output("map_snapshot", "figure"),
    Input("model_widget", "value"),
)
def display_choropleth(model):
    px.set_mapbox_access_token(open(".mapbox_token").read())
    fig = px.choropleth_mapbox(
        geo_df,
        locations=geo_df.index,
        geojson=geo_df.geometry,
        color="NBA_services_PC",
        mapbox_style="open-street-map",
        center={"lat": 49.25, "lon": -122.955},
        zoom=9,
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


# Run server
if __name__ == "__main__":
    app.run_server(debug=True)