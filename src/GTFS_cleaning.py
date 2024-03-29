# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 18:06:49 2020

@author: kangyuwang
"""
data_version = "20200606"

import altair as alt
import os
import pandas as pd

alt.data_transformers.disable_max_rows()

data_dir = os.path.join(os.getcwd(), "TL_data", data_version)

GVA_map_xlim_lower = -13746072.435927173
GVA_map_xlim_higher = -13630000
GVA_map_ylim_lower = 6270302.809935683
GVA_map_ylim_higher = 6345000

# Read files

calendar = pd.read_csv(os.path.join(data_dir, "calendar.txt"))

calendar_dates = pd.read_csv(os.path.join(data_dir, "calendar_dates.txt"))

routes = pd.read_csv(os.path.join(data_dir, "routes.txt"))

shapes = pd.read_csv(os.path.join(data_dir, "shapes.txt"))

stops = pd.read_csv(os.path.join(data_dir, "stops.txt"))

stop_times = pd.read_csv(os.path.join(data_dir, "stop_times.txt"))

trips = pd.read_csv(os.path.join(data_dir, "trips.txt"))

# Summary statistics
##Stops
print(f"{stops['stop_id'].nunique()} stops are identified.")

##Routes
print(f"{routes['route_id'].nunique()} routes are identified.")
print(
    f"Among them, {routes['route_id'][routes['route_type']==1].nunique()} are subways."
)
print(f"Among them, {routes['route_id'][routes['route_type']==2].nunique()} are rails.")
print(f"Among them, {routes['route_id'][routes['route_type']==3].nunique()} are buses.")
print(
    f"Among them, {routes['route_id'][routes['route_type']==4].nunique()} are ferries."
)

##Trips
print(f"{trips['trip_id'].nunique()} trips are identified.")
route_cnt_trips = (
    trips.groupby("route_id")
    .agg(num_trips=pd.NamedAgg(column="trip_id", aggfunc=lambda x: len(x.unique())))
    .sort_values(by=["num_trips"])
)
route_cnt_trips = route_cnt_trips.merge(
    routes[["route_long_name", "route_short_name", "route_id"]],
    left_on="route_id",
    right_on="route_id",
)
print(
    f"Route {route_cnt_trips['route_long_name'].iloc[-1]} has {route_cnt_trips['num_trips'].iloc[-1]} trips, which is the most among all routes."
)
print(
    f"Route {route_cnt_trips['route_long_name'].iloc[0]} has {route_cnt_trips['num_trips'].iloc[0]} trips, which is the least among all routes."
)

# Maps
## Stops
import geopandas
import matplotlib
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString

stops_gdf = geopandas.GeoDataFrame(
    stops, geometry=[Point(xy) for xy in zip(stops.stop_lon, stops.stop_lat)]
)
stops_gdf.plot()
stops_gdf.crs = {"init": "epsg:4326"}

stops_gdf = stops_gdf.to_crs(epsg=3857)  # Convert to web mercator

import contextily as ctx

stops_ax = stops_gdf.plot(figsize=(20, 20), alpha=0.5, edgecolor="k")
stops_ax.set_xlim(GVA_map_xlim_lower, GVA_map_xlim_higher)
stops_ax.set_ylim(GVA_map_ylim_lower, GVA_map_ylim_higher)
ctx.add_basemap(stops_ax, zoom=12)
plt.title("Transit Stops in Great Vancouver Area", fontsize=30)
plt.axis("off")
plt.savefig(os.path.join("Maps", data_version, "stops.png"))

## Trips
### Number of stops per trip
trips_cnt_stops = (
    stop_times.groupby("trip_id")
    .agg(num_stops=pd.NamedAgg(column="stop_id", aggfunc=lambda x: len(x.unique())))
    .sort_values(by=["num_stops"])
)

route_max_stops = trips.loc[trips["trip_id"] == trips_cnt_stops["num_stops"].idxmax()][
    "route_id"
].unique()
print(
    f"Route {routes.loc[routes['route_id'] == route_max_stops[0]]['route_long_name'].tolist()[0]} has {max(trips_cnt_stops['num_stops'])} stops, which is the most among all routes."
)

route_min_stops = trips.loc[trips["trip_id"] == trips_cnt_stops["num_stops"].idxmin()][
    "route_id"
].unique()
print(
    f"Route {routes.loc[routes['route_id'] == route_min_stops[0]]['route_long_name'].tolist()[0]} has {min(trips_cnt_stops['num_stops'])} stops, which is the least among all routes."
)

trips_cnt_stops_hist = (
    alt.Chart(trips_cnt_stops)
    .mark_bar()
    .encode(
        x=alt.X("num_stops:Q", bin=alt.Bin(maxbins=40), title="Number of stops"),
        y="count()",
    )
    .properties(title="Number of trips by stop counting")
)
rule = (
    alt.Chart(trips_cnt_stops)
    .mark_rule(color="red")
    .encode(x="mean(num_stops):Q", size=alt.value(5))
)

(trips_cnt_stops_hist + rule).save(
    os.path.join(
        "Figures",
        data_version,
        "trips_cnt_stops_hist.png",
    )
)

### Number of trips per stop
stops_cnt_trips = (
    stop_times.groupby("stop_id")
    .agg(num_trips=pd.NamedAgg(column="trip_id", aggfunc=lambda x: len(x.unique())))
    .sort_values(by=["num_trips"])
)

stop_max_trips = stops.loc[stops["stop_id"] == stops_cnt_trips["num_trips"].idxmax()][
    "stop_id"
].unique()
print(
    f"Stop {stops.loc[stops['stop_id'] == stop_max_trips[0]]['stop_name'].tolist()[0]} serves {max(stops_cnt_trips['num_trips'])} trips, which is the most among all stops."
)

stops_cnt_trips_hist = (
    alt.Chart(stops_cnt_trips)
    .mark_bar()
    .encode(
        x=alt.X("num_trips:Q", bin=alt.Bin(maxbins=50), title="Number of trips"),
        y="count()",
    )
    .properties(title="Number of stops by trip counting")
)
rule = (
    alt.Chart(stops_cnt_trips)
    .mark_rule(color="red")
    .encode(x="mean(num_trips):Q", size=alt.value(5))
)

(stops_cnt_trips_hist + rule).save(
    os.path.join(
        "Figures",
        data_version,
        "stops_cnt_trips_hist.png",
    )
)

### Busiest stops
stops_gdf = stops_gdf.to_crs(epsg=3857)  # Convert to web mercator

stops_gdf_bz = stops_gdf.loc[
    stops_gdf.stop_id.isin(stops_cnt_trips[-10:].index.tolist())
]

stops_ax_bz = stops_gdf_bz.plot(
    figsize=(10, 10),
    markersize=30,
    alpha=0.5,
    color="red",
)
ctx.add_basemap(stops_ax_bz, zoom=12)
plt.title("10 Busiest stops", fontsize=30)
plt.axis("off")
plt.savefig(os.path.join("Maps", data_version, "stops_bz.png"))

###Distribution of stops by whether busy or not
stops_gdf_cnt_trips = stops_gdf.merge(
    stops_cnt_trips, left_on="stop_id", right_on="stop_id"
)

stops_ax_cnt_trips = stops_gdf_cnt_trips.plot(
    figsize=(20, 20),
    markersize=20,
    alpha=0.5,
    column="num_trips",
    cmap="OrRd",
    norm=matplotlib.colors.LogNorm(),
)
stops_ax_cnt_trips.set_xlim(GVA_map_xlim_lower, GVA_map_xlim_higher)
stops_ax_cnt_trips.set_ylim(GVA_map_ylim_lower, GVA_map_ylim_higher)
plt.title("Stops by number of trips", fontsize=30)
plt.axis("off")
ctx.add_basemap(stops_ax_cnt_trips, zoom=12)
fig = stops_ax_cnt_trips.get_figure()
cbax = fig.add_axes([0.93, 0.3, 0.03, 0.39])
cbax.set_title("# of trips")

sm = plt.cm.ScalarMappable(
    cmap="OrRd",
    norm=plt.Normalize(
        vmin=min(stops_gdf_cnt_trips.num_trips), vmax=max(stops_gdf_cnt_trips.num_trips)
    ),
)
sm._A = []
fig.colorbar(sm, cax=cbax, format="%1.0f")
fig.show()

fig.savefig(os.path.join("Maps", data_version, "stops_cnt_trips.png"))


## Shapes
shapes_gdf = geopandas.GeoDataFrame(
    shapes, geometry=[Point(xy) for xy in zip(shapes.shape_pt_lon, shapes.shape_pt_lat)]
)
lines = shapes_gdf.groupby("shape_id").agg(
    max_dist=pd.NamedAgg(column="shape_dist_traveled", aggfunc=max)
)
lines_gdf = geopandas.GeoDataFrame(
    lines,
    geometry=[
        LineString(
            shapes_gdf.loc[shapes_gdf["shape_id"] == shape_id]
            .sort_values(by=["shape_pt_sequence"])["geometry"]
            .tolist()
        )
        for shape_id in lines.index
    ],
)

lines_gdf.crs = {"init": "epsg:4326"}
lines_gdf = lines_gdf.to_crs(epsg=3857)  # Convert to web mercator

lines_gdf.plot()
lines_ax = lines_gdf.plot(
    figsize=(20, 20),
    alpha=0.5,
    edgecolor="k",
)

lines_ax.set_xlim(GVA_map_xlim_lower, GVA_map_xlim_higher)
lines_ax.set_ylim(GVA_map_ylim_lower, GVA_map_ylim_higher)

ctx.add_basemap(lines_ax, zoom=12)
plt.title("Transit Lines", fontsize=30)
plt.axis("off")
plt.savefig(os.path.join("Maps", data_version, "lines.png"))

trips_line = trips.merge(lines_gdf, left_on="shape_id", right_on="shape_id")
trips_line = trips_line.merge(
    routes[["route_long_name", "route_short_name", "route_type", "route_id"]],
    left_on="route_id",
    right_on="route_id",
)

trips_line_hist_df = pd.DataFrame(trips_line.drop(["geometry"], axis=1))
trips_line_hist = (
    alt.Chart(trips_line_hist_df)
    .mark_bar()
    .encode(
        x=alt.X("max_dist:Q", bin=alt.Bin(maxbins=50), title="Trip distance (km)"),
        y="count()",
    )
    .properties(title="Number of trips by distance")
)
rule = (
    alt.Chart(trips_line_hist_df)
    .mark_rule(color="red")
    .encode(x="mean(max_dist):Q", size=alt.value(5))
)

(stops_cnt_trips_hist + rule).save(
    os.path.join("Figures", data_version, "dist_hist.png")
)

print(f"Median trip distance is {trips_line['max_dist'].median():.2f} km.")

###Longest routes
route_max_dist = trips.loc[trips["shape_id"] == lines_gdf["max_dist"].idxmax()][
    "route_id"
].unique()
print(
    f"Route {routes.loc[routes['route_id'] == route_max_dist[0]]['route_long_name'].tolist()[0]} is {max(lines_gdf['max_dist'])} kms long, which is the longest route."
)
lines_max_dist = lines_gdf[lines_gdf.index == lines_gdf["max_dist"].idxmax()]
lines_ax_max = lines_max_dist.plot(
    figsize=(25, 10), alpha=0.5, color="red", edgecolor="k", linewidth=5
)
plt.title("Longest Route in Great Vancouver Transit", fontsize=30)
plt.axis("off")
ctx.add_basemap(lines_ax_max, zoom=12)
plt.savefig(os.path.join("Maps", data_version, "lines_max.png"))

# Save intermediate data
import json

with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "calendar.json"), "w+"
) as calendar_outfile:
    json.dump(calendar.to_json(), calendar_outfile)

with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "calendar_dates.json"), "w+"
) as calendar_dates_outfile:
    json.dump(calendar_dates.to_json(), calendar_dates_outfile)

lines_gdf.to_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "lines.json"),
    driver="GeoJSON",
)

with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "routes.json"), "w+"
) as routes_outfile:
    json.dump(routes.to_json(), routes_outfile)

shapes_gdf.to_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "shapes.json"),
    driver="GeoJSON",
)

## The stop_times table is very large in size. Remove some columns and break up the file to save them in batches.

n_batch = len(stop_times) // 200000

for i in range(n_batch + 1):
    stop_times_b = stop_times.iloc[i * 200000 : min((i + 1) * 200000, len(stop_times))]
    filename = "stop_times" + str(i) + ".json"
    with open(
        os.path.join(os.getcwd(), "Data_Tables", data_version, filename), "w+"
    ) as stop_times_outfile:
        json.dump(stop_times_b.to_json(), stop_times_outfile)

stops_gdf.to_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "stops.json"),
    driver="GeoJSON",
)

with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "trips.json"), "w+"
) as trips_outfile:
    json.dump(trips.to_json(), trips_outfile)
