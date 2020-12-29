# Introduction

In this project, I try to understand the relationship between demographic characters and use of public transit in the Greater Vancouver Area, and model how access to transit services and infrastructure impacts transit use.

Firstly, I gathered [General Transit Feed Specification (GTFS)](https://gtfs.org/) data for Greater Vancouver, and Canada's 2016 census. I cleaned both datasets and selected relevant variables. 

Secondly, I extracted information about people's access to, and usage of public transportation across Greater Vancouver's neighborhoods. I also conducted an overview of Vancouver's transit service, and local residents' demographic characters in general. 

Thirdly, I built the data table for machine learning modeling, and applied LASSO and random forest models. I concluded that access to transit services is a key determinant of residents' use of public transportation. I identified areas where increased transit services will lead to the most increase in transit usage. 

# Usage

## Download census data

Ideally, we would want to use an API to directly download Canada's 2016 census data. However, the volumne of data required by this analysis, which goes down to the Dissemination Area (DA) level, exceeds what available free APIs can download. Therefore, I have stored the zipped dataset in my personal OneDrive folder for you to download. 

    wget --no-check-certificate -O Census.zip "https://onedrive.live.com/download?cid=FD70C8A06BE32527&resid=FD70C8A06BE32527%21701526&authkey=ADw5q9yT-Y-RX0A"

## Download GTFS data

    wget --no-check-certificate -O TL_data.zip https://transitfeeds.com/p/translink-vancouver/29/20200606/download    

## Unzip downloaded data

    python Unzip_downloads.py

## Data cleaning

    python GTFS_cleaning.py
    python Census_reading.py

## Exploratory Analyses

    python Temporal_analysis.py
    python Access_analysis.py
    python Usage_analysis.py

## Modeling

    python Preprocessing.py
    python Modelling.py
    jupyter nbconvert --to notebook --execute Model_analysis.ipynb --ExecutePreprocessor.timeout=600
    jupyter nbconvert --to HTML Model_analysis.ipynb

# License

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
# Dependencies

  - Python 3.8.3 and Python packages:
      - altair=4.1.0
      - contextily=1.0.0
      - dbfread=2.0.7
      - geopandas=0.8.1
      - json=2.0.9
      - matplotlib=3.3.1
      - numpy=1.19.1
      - pandas=1.1.1
      - re=2.2.1
      - sklearn=0.23.2
      - shap=0.37.0
      - shapely=1.7.1
      - tabulate=0.8.7