# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 11:58:54 2020

@author: kangyuwang
"""
import geopandas
import os
import numpy as np

cwd = os.path.dirname(os.getcwd())
os.chdir(cwd)
data_dir = os.path.join(os.getcwd(), "Census")

data_version = "20200606"
# Federal Electoral Districts
file = geopandas.read_file(os.path.join(data_dir, "lfed000b16a_e", "lfed000b16a_e.shp"))
BC_FED = file.loc[file["PRNAME"] == "British Columbia / Colombie-Britannique"]
print(f"There are {len(BC_FED.index)} federal electoral districts in British Columbia.")

BC_FED.to_file(os.path.join(os.getcwd(), "Census", "BC_FED.shp"))

# Census Subdivisions
file = geopandas.read_file(os.path.join(data_dir, "lcsd000b16a_e", "lcsd000b16a_e.shp"))
BC_CSD = file.loc[file["PRNAME"] == "British Columbia / Colombie-Britannique"]
print(f"There are {len(BC_CSD.index)} census subdivisions in British Columbia.")

BC_CSD.to_file(os.path.join(os.getcwd(), "Census", "BC_CSD.shp"))

# Dissemination Areas
file = geopandas.read_file(os.path.join(data_dir, "lda_000b16a_e", "lda_000b16a_e.shp"))
BC_DA = file.loc[file["PRNAME"] == "British Columbia / Colombie-Britannique"]
print(f"There are {len(BC_DA.index)} dissemination areas in British Columbia.")

BC_DA.to_file(os.path.join(os.getcwd(), "Census", "BC_DA.shp"))

GVA_DA = BC_DA.loc[BC_DA["CDNAME"] == "Greater Vancouver"]  ##Greater Vancouver Area
print(f"There are {len(GVA_DA.index)} dissemination areas in Greater Vancouver.")

# Read DA level data
from dbfread import DBF
import pandas as pd
import numpy as np
import json

batch_list = [
    "pdad",
    "fhm",
    "hous",
    "lang",
    "incm",
    "immi",
    "ethn",
    "labr",
    "mobl",
]  # Census data for Greater Vancouver Area is downloaded in batches.


def read_census_tables(batch_list):
    lengths = []
    data_table_list = []
    header_list = []
    for batch in batch_list:
        pd_dir = os.path.join(data_dir, "data_2016", batch + ".dbf")
        table = DBF(pd_dir, load=True)
        table_df = pd.DataFrame(
            np.array([list(record.values()) for record in table.records])
        )
        lengths.append(len(table.records))
        header_dir = os.path.join(data_dir, "data_2016", batch + ".txt")
        header = pd.read_table(header_dir)
        result = all(element == lengths[0] for element in lengths)
        if not result:
            raise ValueError("The input tables are not of the same lengths")
        data_table_list.append(table_df)
        header_list.append(header)
    else:
        data_table = pd.concat(data_table_list, axis=1)
        data_header = pd.concat(header_list, axis=0)
        return data_table, data_header


data_table, header = read_census_tables(batch_list)
header = [item[0].partition(" - ")[2] for item in header.values]
data_table.columns = header
data_table = data_table.loc[
    :, ~data_table.columns.duplicated()
]  # Remove duplicated columns
header = data_table.columns
data_table.columns = ["vn" + str(col) for col in range(len(data_table.columns))]

GVA_DA_header = GVA_DA.columns
GVA_DA = GVA_DA.merge(data_table, left_on="DAUID", right_on="vn0")

header = list(GVA_DA_header) + list(header)

##Move Geometry to the end of GVA_DA table
GVA_DA.to_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_data.geojson"),
    driver="GeoJSON",
)
GVA_DA = geopandas.read_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_data.geojson")
)
GVA_DA.crs = BC_DA.crs

header.remove("geometry")
header.append("geometry")

##Converting data types in GVA_DA
for column_name in GVA_DA.columns[28:-1]:
    GVA_DA[[column_name]] = pd.DataFrame(
        (
            pd.to_numeric(
                [item[0] for item in GVA_DA[[column_name]].to_numpy()], errors="coerce"
            )
        )
    )
    GVA_DA[[column_name]] = GVA_DA[[column_name]].astype("float64")

##Save census tables
GVA_DA.to_file(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_data.shp")
)

with open(
    os.path.join(os.getcwd(), "Data_Tables", data_version, "GVA_DA_header.json"), "w+"
) as DA_header_outfile:
    json.dump(header, DA_header_outfile)
