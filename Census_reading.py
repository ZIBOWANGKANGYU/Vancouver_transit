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
file = geopandas.read_file(os.path.join(data_dir, "lfed000b16a_e","lfed000b16a_e.shp"))
BC_FED = file.loc[file["PRNAME"]=='British Columbia / Colombie-Britannique']
print(f"There are {len(BC_FED.index)} federal electoral districts in British Columbia.")

BC_FED.to_file(os.path.join(os.getcwd(), "Census", "BC_FED.shp"))

# Census Subdivisions 
file = geopandas.read_file(os.path.join(data_dir, "lcsd000b16a_e","lcsd000b16a_e.shp"))
BC_CSD = file.loc[file["PRNAME"]=='British Columbia / Colombie-Britannique']
print(f"There are {len(BC_CSD.index)} census subdivisions in British Columbia.")

BC_CSD.to_file(os.path.join(os.getcwd(), "Census", "BC_CSD.shp"))

# Dissemination Areas
file = geopandas.read_file(os.path.join(data_dir, "lda_000b16a_e","lda_000b16a_e.shp"))
BC_DA = file.loc[file["PRNAME"]=='British Columbia / Colombie-Britannique']
print(f"There are {len(BC_DA.index)} dissemination areas in British Columbia.")

BC_DA.to_file(os.path.join(os.getcwd(), "Census", "BC_DA.shp"))

GVA_DA = BC_DA.loc[BC_DA["CDNAME"] == "Greater Vancouver"]##Greater Vancouver Area
print(f"There are {len(GVA_DA.index)} dissemination areas in Greater Vancouver.")


#Read DA level data
from dbfread import DBF
import pandas as pd
import numpy as np

batch_list = ["pdad", "fhm", "hous", "lang", "incm", "immi", "ethn", "labr", "mobl"]# Census data for Greater Vancouver Area is downloaded in batches. 

def read_census_tables(batch_list):
    lengths = [] 
    data_table_list = []
    header_list = []
    for batch in batch_list:
        pd_dir = os.path.join(data_dir, "data_2016", batch + ".dbf")
        table = DBF(pd_dir, load=True)
        table_df = pd.DataFrame(np.array([list(record.values()) for record in table.records]))
        lengths.append(len(table.records))
        header_dir = os.path.join(data_dir, "data_2016", batch + ".txt")
        header = pd.read_table(header_dir)
        result = all(element == lengths[0] for element in lengths)
        if not result:
            raise ValueError('The input tables are not of the same lengths')
        data_table_list.append(table_df)
        header_list.append(header)
    else: 
        data_table = pd.concat(data_table_list, axis = 1)
        data_header = pd.concat(header_list, axis = 0)
        return data_table, data_header

data_table, header = read_census_tables(batch_list)
header = [item[0].partition(' - ')[2] for item in header.values]
data_table.columns = header
data_table = data_table.loc[:,~data_table.columns.duplicated()]#Remove duplicated columns
header = data_table.columns
data_table.columns = ["vn" + str(col) for col in range(len(data_table.columns))]

GVA_DA_header = GVA_DA.columns
GVA_DA = GVA_DA.merge(data_table, left_on = "DAUID", right_on = "vn0")

header = list(GVA_DA_header) + list(header)

##Converting data types in GVA_DA
for column_name in GVA_DA.columns[29:]:
    GVA_DA[[column_name]] = pd.DataFrame((pd.to_numeric([item[0] for item in GVA_DA[[column_name]].to_numpy()], errors = "coerce")))
    GVA_DA[[column_name]] = GVA_DA[[column_name]].astype("float64")

##Mapping DAs
###Create base map
GVA_DA = GVA_DA.to_crs(epsg=3857)
GVA_base = GVA_DA.iloc[:, 0: 28]

###Population 
import contextily as ctx
import matplotlib.pyplot as plt
GVA_DA_pop = pd.concat([GVA_base, GVA_DA[["vn13"]]], axis = 1)
GVA_DA_pop_ax = GVA_DA_pop.plot(figsize=(20, 20), alpha=0.5, column="vn13", cmap = "OrRd", legend = True)
ctx.add_basemap(GVA_DA_pop_ax, zoom=12)
plt.title("2016 Population by Dissemination Area")
plt.savefig(os.path.join(os.getcwd(), "Vancouver_transit", "Maps", data_version,'pop2016.png'))

###Population density
GVA_DA_pop_dense = pd.concat([GVA_base, GVA_DA[["vn18"]]], axis = 1)
GVA_DA_pop_dense = GVA_DA_pop_dense[GVA_DA_pop_dense.vn18 >= GVA_DA_pop_dense.vn18.quantile(0.9)] # Keep DAs with top 10% population densities
GVA_DA_pop_dense_ax = GVA_DA_pop_dense.plot(figsize=(20, 20), alpha=0.5, legend = True, color = "r")
ctx.add_basemap(GVA_DA_pop_dense_ax, zoom=12)
plt.title("2016 Population density by Dissemination Area: Top 10%")
plt.savefig(os.path.join(os.getcwd(), "Vancouver_transit", "Maps", data_version,'pop_dense201610pc.png'))
print(f"The CSDs with highest number of DAs with top 10% population densities are {list(GVA_DA_pop_dense.CSDNAME.value_counts().index)[:5]}")

GVA_DA_pop_dense1 = pd.concat([GVA_base, GVA_DA[["vn13", "vn19"]]], axis = 1)
GVA_DA_pop_dense1[["pop_dense"]] = GVA_DA_pop_dense1.vn13 / GVA_DA_pop_dense1.vn19
GVA_DA_pop_dense1.pop_dense [np.isinf(GVA_DA_pop_dense1.pop_dense) == True] = None
GVA_DA_pop_dense1_ax = GVA_DA_pop_dense1.plot(figsize=(20, 20), alpha=0.5, column="pop_dense", cmap = "OrRd", legend = True)
ctx.add_basemap(GVA_DA_pop_dense1_ax, zoom=12)
plt.title("2016 Population density by Dissemination Area")
plt.savefig(os.path.join(os.getcwd(), "Vancouver_transit", "Maps", data_version,'pop_dense2016.png'))

##Save census tables
import json
with open(os.path.join(os.getcwd(), "Data_Tables", data_version,'GVA_DA_data.json'), "w+") as DA_data_outfile:
    json.dump(GVA_DA.to_json(), DA_data_outfile)

