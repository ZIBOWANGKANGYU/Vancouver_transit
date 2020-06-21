# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 11:58:54 2020

@author: kangyuwang
"""
import geopandas 
import os 
cwd = os.path.dirname(os.getcwd())
os.chdir(cwd)
data_dir = os.path.join(os.getcwd(), "Census")
# Federal Electoral Districts
file = geopandas.read_file(os.path.join(data_dir, "lfed000b16a_e","lfed000b16a_e.shp"))
BC_FED = file.loc[file["PRNAME"]=='British Columbia / Colombie-Britannique']
BC_FED.to_file(os.path.join(os.getcwd(), "Census", "BC_FED.shp"))

# Census Subdivisions 
file = geopandas.read_file(os.path.join(data_dir, "lcsd000b16a_e","lcsd000b16a_e.shp"))
BC_CSD = file.loc[file["PRNAME"]=='British Columbia / Colombie-Britannique']
BC_CSD.to_file(os.path.join(os.getcwd(), "Census", "BC_CSD.shp"))

# Dissemination Areas
file = geopandas.read_file(os.path.join(data_dir, "lda_000b16a_e","lda_000b16a_e.shp"))
BC_DA = file.loc[file["PRNAME"]=='British Columbia / Colombie-Britannique']
BC_DA.to_file(os.path.join(os.getcwd(), "Census", "BC_DA.shp"))

BC_DA.loc[BC_DA["CDNAME"] == "Greater Vancouver"].plot()##Greater Vancouver Area