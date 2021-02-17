import altair as alt
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import json
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

CSD_dict = json.load(
    open(os.path.join("Data_Tables", "Dash_data", "CSD_dict.json"), "r")
)
# Define app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Control panels
scenario_widget = dcc.RadioItems(
    id="scenario_widget",
    options=[
        {"label": "Scenario 1 (increase by same percentage point)", "value": "Sce1"},
        {"label": "Scenario 2 (increase by same percent)", "value": "Sce2"},
    ],
    value="Sce1",
    labelStyle={"display": "block"},
)

scale_widget = dcc.Slider(
    id="scale_widget",
    min=0.05,
    max=0.3,
    step=None,
    marks={0.05: "5%", 0.1: "10%", 0.15: "15%", 0.2: "20%", 0.3: "30%"},
    value=0.1,
)

priority_widget = dcc.Slider(
    id="priority_widget",
    min=0.01,
    max=0.3,
    step=0.01,
    marks={0.05: "5%", 0.1: "10%", 0.15: "15%", 0.2: "20%", 0.25: "25%", 0.3: "30%"},
    value=0.1,
)

CSD_controller = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Checklist(
                            id="select_all_CSD",
                            options=[{"label": "Select All", "value": 1}],
                            value=[],
                        )
                    ]
                ),
            ]
        ),
        dcc.Dropdown(
            id="CSD_widget",
            value=list(CSD_dict.keys()),
            placeholder="Select regions ...",
            options=[
                {"label": CSD_dict[CSDUID], "value": CSDUID}
                for CSDUID in list(CSD_dict.keys())
            ],
            multi=True,
        ),
    ]
)

# Explaner
explaner = dcc.Markdown(
    """
    This application shows areas which Greater Vancouver Area's (GVA) public transit authority should prioritize in developing new public transportation services. 
    Users can customize their queries with three policy options:

    #### Percentage of neighborhoods to priortize
    We assume that the transit authority's resources are limited, and thus can only increase transit services in a limited number of neighborhoods, which are defined as dissemination areas (DAs) in Canada's 2016 census. 
    Priority areas should be DAs where a fixed amount of increase in transit access leads to the most increase in proportion of people using transit.

    #### Type of transit service increase
    The research has specified two scenarios of transit service increase in priority areas.

    In the first scenario, each DA’s number of accessible transit services per capita is increased by a fixed amount. This fixed amount should be equal to a specified proportion of average current number of accessible transit services per capita of all DAs in GVA.
    For example, at present, there are 12 transit services accessible per resident in average for all DAs in GVA. If "Magnitude of transit service increase" (explained in the next section) is set to 0.1, then the number of accessible transit services per capita will be increased by 1.2 for each and every priority DAs.

    In the second scenatio, each DA's number of accessible transit services per capita is increased by a fixed proportion. 
    For example, for a DA that currently has 20 transit services accessible per resident, if we set "Magnitude of transit service increase" to be 20%, this DA's new number of transit services accessible per resident will be 24. 
    By contrast, for a DA that currently has 5 transit services accessible per resident, this DA's new number of transit services accessible per resident will be 6, under the same "Magnitude of transit service increase" being 20%.

    #### Magnitude of transit service increase
    We believe that in the above two hypothetical scenarios, the number of transit services accessible should only be increased in a modest way for our model to be largely valid. Therefore, possible magnitudes is set between 5% and 30%. 
    """
)

server = app.server

app.layout = dbc.Container(
    [
        dbc.Tabs(
            [
                dbc.Tab(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H1(
                                            "Public Transportation Development Priorities in Greater Vancouver: A Machine Learning Approach",
                                            style={
                                                "color": "white",
                                                "text-align": "center",
                                                "font-size": "48px",
                                            },
                                        ),
                                        html.P(
                                            "App Developed by Mark Wang",
                                            style={
                                                "color": "white",
                                            },
                                        ),
                                    ],
                                    style={
                                        "backgroundColor": "steelblue",
                                        "border-radius": 3,
                                        "padding": 15,
                                        "margin-top": 20,
                                        "margin-bottom": 25,
                                        "margin-right": 15,
                                    },
                                )
                            ]
                        ),
                        html.Hr(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H4("Policy options"),
                                        html.Br(),
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    "Percentage of neighborhoods to priortize"
                                                ),
                                                dbc.CardBody(
                                                    priority_widget,
                                                ),
                                            ]
                                        ),
                                        html.Br(),
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    "Type of transit service increase"
                                                ),
                                                dbc.CardBody(
                                                    scenario_widget,
                                                ),
                                            ]
                                        ),
                                        html.Br(),
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    "Magnitude of transit service increase"
                                                ),
                                                dbc.CardBody(
                                                    scale_widget,
                                                ),
                                            ]
                                        ),
                                    ],
                                    md=3,
                                    style={
                                        "background-color": "#e6e6e6",
                                        "padding": 20,
                                        "border-radius": 3,
                                        "margin-right": 15,
                                    },
                                ),
                                dbc.Col(
                                    [
                                        html.H4("Mapping options"),
                                        html.Br(),
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    "Choose neighborhoods to see details"
                                                ),
                                                dbc.CardBody(CSD_controller),
                                            ]
                                        ),
                                    ],
                                    md=3,
                                    style={
                                        "background-color": "#e6e6e6",
                                        "padding": 20,
                                        "border-radius": 3,
                                        "margin-right": 15,
                                    },
                                ),
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            children=dcc.Graph(
                                                id="GVA_map",
                                                style={
                                                    "border-width": "0",
                                                    "width": "100%",
                                                    "height": "50vh",
                                                },
                                            )
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        html.Hr(),
                        dcc.Markdown(
                            """
                        This application is developed by Mark Wang. 
                        It is based on research project: Demographic Characters and Access to Public Transit in Greater Vancouver: Analyses and Recommendations. 
                        
                        A high-level summary of the research can be found [here](https://zibowangkangyu.github.io/Vancouver_transit_summary/).

                        A series of in-depth posts about this project include [data sources](https://zibowangkangyu.github.io/Vancouver_transit1/), [key variables](https://zibowangkangyu.github.io/Vancouver_transit2/), [machine learning modeling](https://zibowangkangyu.github.io/Vancouver_transit3/), and [model analyses and recommendations](https://zibowangkangyu.github.io/Vancouver_transit4/).

                        For the Jupyter Notebook with full analysIs, please see [here](https://nbviewer.jupyter.org/github/ZIBOWANGKANGYU/Vancouver_transit/blob/master/Report.ipynb). The GitHub repo of this analysis is located [here](https://github.com/ZIBOWANGKANGYU/Vancouver_transit).  
                        """
                        ),
                    ],
                    label="Main page",
                ),
                dbc.Tab(
                    [
                        dbc.Col(
                            [
                                html.H1(
                                    "Public Transportation Development Priorities in Greater Vancouver: A Machine Learning Approach",
                                    style={
                                        "color": "white",
                                        "text-align": "center",
                                        "font-size": "48px",
                                    },
                                ),
                                html.P(
                                    "App Developed by Mark Wang",
                                    style={
                                        "color": "white",
                                    },
                                ),
                            ],
                            style={
                                "backgroundColor": "steelblue",
                                "border-radius": 3,
                                "padding": 15,
                                "margin-top": 20,
                                "margin-bottom": 25,
                                "margin-right": 15,
                            },
                        ),
                        explaner,
                        html.Hr(),
                        dcc.Markdown(
                            """
                        This application is developed by Mark Wang. 
                        It is based on research project: Demographic Characters and Access to Public Transit in Greater Vancouver: Analyses and Recommendations. 
                        
                        A high-level summary of the research can be found [here](https://zibowangkangyu.github.io/Vancouver_transit_summary/).

                        A series of in-depth posts about this project include [data sources](https://zibowangkangyu.github.io/Vancouver_transit1/), [key variables](https://zibowangkangyu.github.io/Vancouver_transit2/), [machine learning modeling](https://zibowangkangyu.github.io/Vancouver_transit3/), and [model analyses and recommendations](https://zibowangkangyu.github.io/Vancouver_transit4/).

                        For the Jupyter Notebook with full analysIs, please see [here](https://nbviewer.jupyter.org/github/ZIBOWANGKANGYU/Vancouver_transit/blob/master/Report.ipynb). The GitHub repo of this analysis is located [here](https://github.com/ZIBOWANGKANGYU/Vancouver_transit).  
                        """
                        ),
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
## Map
@app.callback(
    Output("GVA_map", "figure"),
    Input("scenario_widget", "value"),
    Input("scale_widget", "value"),
    Input("priority_widget", "value"),
    Input("select_all_CSD", "value"),
    Input("CSD_widget", "value"),
)
def display_choropleth(scenario, scale, priority, select_all_CSD, CSD):
    scale = str(scale)[2:]
    col_selected = scenario + scale + "rf"
    px.set_mapbox_access_token(open(".mapbox_token").read())
    geo_df["increase"] = geo_df[col_selected] - geo_df["pred_status_quo"]
    geo_df["Priority"] = geo_df["increase"] > geo_df["increase"].quantile(1 - priority)
    if select_all_CSD != 1:
        geo_df_selected = geo_df.loc[geo_df["CSDUID"].isin(CSD)]
    else:
        geo_df_selected = geo_df
    fig = px.choropleth_mapbox(
        geo_df_selected,
        locations=geo_df_selected.index,
        geojson=geo_df_selected.geometry,
        color="Priority",
        mapbox_style="open-street-map",
        center={"lat": 49.25, "lon": -122.955},
        zoom=9,
        hover_data={
            "Priority": True,
            "Population": ":.0f",
            "Area(km2)": ":.2f",
        },
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )
    return fig


# Run server
if __name__ == "__main__":
    app.run_server(debug=True)