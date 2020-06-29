'''
This script prepares data for use with SWAT+ AW v1.0.4 for Blue Nile.

Author  : Celray James CHAWANDA
Contact : celray.chawanda@vub.be
Date    : 2020/03/31
Licence : MIT 2020 or Later
'''
import urllib
import os
import sys
import zipfile
from glob import glob

import geopandas
import rasterio
from rasterio import features
import requests
import shutil

# functions


def read_from(filename, report_=False):
    '''
    a function to read ascii files
    '''
    try:
        g = open(filename, 'r')
    except:
        print("\t! error reading {0}, make sure the file exists".format(filename))
        return
    file_text = g.readlines()
    if report_:
        print("\t> read {0}".format(file_name(filename)))
    g.close
    return file_text


def clip_features(mask, input_feature, output_feature):
    os.system("ogr2ogr -clipsrc " + mask + " " +
              output_feature + " " + input_feature)
    print("\t > clipped feature to " + output_feature)


def write_to(filename, text_to_write, report_=False):
    '''
    a function to write to file
    '''
    try:
        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
            print("! the directory {0} has been created".format(
                os.path.dirname(filename)))
    except:
        pass
    g = open(filename, 'w')
    try:
        g.write(text_to_write)
        if report_:
            print('\n\t> file saved to ' + filename)
    except:
        print("\t> error writing to {0}, make sure the file is not open in another program".format(
            filename))
        response = input("\t> continue with the error? (Y/N): ")
        if response == "N" or response == "n":
            sys.exit()
    g.close


def list_files(folder, extension="*"):
    if folder.endswith("/"):
        if extension == "*":
            list_of_files = glob(folder + "*")
        else:
            list_of_files = glob(folder + "*." + extension)
    else:
        if extension == "*":
            list_of_files = glob(folder + "/*")
        else:
            list_of_files = glob(folder + "/*." + extension)
    return list_of_files


def download_file(url, save_path, local_filename=None):
    if local_filename is None:
        local_filename = url.split('/')[-1]

    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(f"{save_path}/{local_filename}", 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def file_name(path_, extension=True):
    if extension:
        fn = os.path.basename(path_)
    else:
        fn = os.path.basename(path_).split(".")[0]
    return(fn)


# global variables
base_link = "http://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/"
tile_names = ["srtm_44_11.zip", "srtm_43_10.zip", "srtm_44_10.zip",
              "srtm_43_11.zip", "srtm_44_09.zip", "srtm_43_09.zip"]
mask_shapefile = "bn_mask.gpkg"

landuse_tif = "ftp://geo10.elie.ucl.ac.be/v207/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2009-v2.0.7.tif"
soils_shapefile = "http://www.fao.org/geonetwork/srv/en/resources.get?id=14116&fname=DSMW.zip&access=private"

# process DEM
print("# Downloading DEM raw data")
for f_name in tile_names:
    if not os.path.isfile(f"temp/dem/raw/{f_name}"):
        print(f"\t- downloading {f_name}")
        download_file(f"{base_link}{f_name}", "temp/dem/raw")

print("# Extracting downloaded DEM tiles")
zipped_tiles = list_files("temp/dem/raw")
for zipped_file in zipped_tiles:
    print(f"\t- extracting {f_name}")
    zip_ref = zipfile.ZipFile(zipped_file, 'r')
    if not os.path.isdir("temp/dem/extracted"):
        os.makedirs("temp/dem/extracted")
    if not os.path.isfile(f"temp/dem/extracted/{zipped_file.split('.')[0]}.tif"):
        zip_ref.extractall("temp/dem/extracted")

print("# Merging DEM tiles")
if not os.path.isdir("temp/dem/merged"):
    os.makedirs("temp/dem/merged")
if not os.path.isfile("temp/dem/merged/srtm_data.tif"):
    os.system("gdal_merge -o temp/dem/merged/srtm_data.tif -a_nodata -32768 {file_list}".format(
        file_list=" ".join(str(x) for x in list_files("temp/dem/extracted", "tif"))))

print("# Clipping DEM")
if not os.path.isdir("data/rasters/"):
    os.makedirs("data/rasters/")
if not os.path.isfile("data/rasters/dem_blue_nile.tif"):
    os.system("gdalwarp -r {resample_type} -dstnodata {ds_nodata} -tr 300 300 -ot {dt_type} -t_srs EPSG:3395 -of GTiff -cutline {shp_file} -crop_to_cutline {in_tif} {out_tif} -overwrite".format(
        resample_type="bilinear", ds_nodata=-32768, dt_type="Int32", shp_file=mask_shapefile,
        in_tif="temp/dem/merged/srtm_data.tif", out_tif="data/rasters/dem_blue_nile.tif"
    ))

# process soils
print("# Downloading soil data, DSMW.zip")
download_file(soils_shapefile, "temp/soil", "DSMW.zip")
if not os.path.isdir("temp/soil"):
    os.makedirs("temp/soil")

print("Please ignore ERROR 1")

zipfile.ZipFile("temp/soil/DSMW.zip", 'r').extractall("temp/soil")
os.system('ogr2ogr -f "ESRI Shapefile" -t_srs EPSG:3395 -s_srs EPSG:4326 temp/soil/DSMW_3390.shp temp/soil/DSMW.shp')  # reproject
print("Please ignore ERROR 1")

clip_features(mask_shapefile, "temp/soil/DSMW_3390.shp",
              "temp/soil/clipped.shp")

soils = geopandas.read_file("temp/soil/clipped.shp")
rst = rasterio.open("data/rasters/dem_blue_nile.tif")

meta = rst.meta.copy()
meta.update(compress='lzw')

with rasterio.open("data/rasters/soils_blue_nile.tif", 'w+', **meta) as out:
    out_arr = out.read(1)

    # this is where we create a generator of geom, value pairs to use in rasterizing
    shapes = ((geom, value) for geom, value in zip(soils.geometry, soils.SNUM))

    burned = features.rasterize(
        shapes=shapes, fill=0, out=out_arr, transform=out.transform)
    out.write_band(1, burned)

# create usersoil and lookup
lookup_dictionary = {}
for index, row in soils.iterrows():
    if not str(row.SNUM) in lookup_dictionary:
        lookup_dictionary[str(row.SNUM)] = row.FAOSOIL

all_usersoil = read_from("mw_usersoil.csv")

usersoil_string = all_usersoil[0].replace('"', "")
lookup_string = "VALUE,SNAM\n"

for line in all_usersoil:
    line = line.replace('"', "")
    if line.split(",")[2] in lookup_dictionary:
        usersoil_string += line
        lookup_string += "{0},{1}-{0}\n".format(
            line.split(",")[2],
            lookup_dictionary[line.split(",")[2]]
        )


write_to("data/tables/bn_usersoil.csv", usersoil_string)
write_to("data/tables/bn_soil_lookup.csv", lookup_string)


print("# Processing landuse")

if not os.path.isfile("temp/landuse/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2009-v2.0.7.tif"):
    print("\t  downloading ESACCI-LC-L4-LCCS-Map-300m-P1Y-2007-v2.0.7.tif (304 MB)")
    if not os.path.isdir("temp/landuse/"):
        os.makedirs("temp/landuse/")
    urllib.request.urlretrieve(landuse_tif,
                               "temp/landuse/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2009-v2.0.7.tif")

os.system("gdalwarp -r {resample_type} -dstnodata {ds_nodata} -ot {dt_type} -tr 300 300 -t_srs EPSG:3395 -of GTiff -cutline {shp_file} -crop_to_cutline {in_tif} {out_tif} -overwrite".format(
    resample_type="mode", ds_nodata=-32768, dt_type="Int32", shp_file=mask_shapefile,
    in_tif="temp/landuse/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2009-v2.0.7.tif",
    out_tif="data/rasters/landuse_blue_nile.tif"
))

if not os.path.isdir("data/tables/"):
    os.makedirs("data/tables/")
if not os.path.isfile("data/tables/bn_landuse_lookup.csv"):
    shutil.copyfile("land_lookup.csv", "data/tables/bn_landuse_lookup.csv")

if not os.path.isdir("data/observations/"):
    os.makedirs("data/observations/")
if not os.path.isdir("data/calibration/"):
    os.makedirs("data/calibration/")
if not os.path.isdir("data/weather/"):
    os.makedirs("data/weather/")
if not os.path.isdir("data/shapefiles/"):
    os.makedirs("data/shapefiles/")
