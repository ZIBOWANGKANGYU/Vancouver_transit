import zipfile

with zipfile.ZipFile("Census.zip", "r") as zip_ref:
    zip_ref.extractall()

with zipfile.ZipFile("TL_data.zip", "r") as zip_ref:
    zip_ref.extractall("TL_data/20200606")