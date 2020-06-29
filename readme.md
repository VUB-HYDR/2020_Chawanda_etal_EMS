
# Data Preparation for 2020_Chawanda_etal_EMS
Scripts used to process data and namelist used in Chawanda et al. (2020).
Find the SWAT+ AW [here](https://github.com/VUB-HYDR/SWATPlus-AW)

## To Install
[gdal](https://pypi.org/project/GDAL/)   
[geopandas](https://geopandas.org/)   
[rasterio](https://rasterio.readthedocs.io/en/latest/)   
 
## For users
This repository includes the scripts that automatically downloads SRTM data for Blue Nile area and processes it for use with [SWAT+ AW](https://github.com/VUB-HYDR/SWATPlus-AW)
It also has script to process ESA land use data downloaded from [http://maps.elie.ucl.ac.be/CCI/viewer/download.php](http://maps.elie.ucl.ac.be/CCI/viewer/download.php) for the Blue Nile area. In This case, the 2009 land use map (ESACCI-LC-L4-LCCS-Map-300m-P1Y-2009-v2.0.7.tif) was used.
There is also a script that processes the FAO soil data downloaded from [FAO's website](http://www.fao.org/geonetwork/srv/en/resources.get?id=14116&fname=DSMW.zip&access=private).

The Prepared dataset is also available at [Hydroshare](https://doi.org/10.4211/hs.0890b3a954bf423db7d5b08f122b5436).

### Running The Script
Execute the [prepare_input.py](./prepare_input.py) in Command Prompt or PowerShell.

## Author
[Celray James CHAWANDA](https://github.com/celray/) 

## License
This project is licensed under the MIT License. See also the [license](./LICENSE) file.




