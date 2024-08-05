## add your projecte main directory 
main_dir = '/home/surajit/d/PROJECTS/Compute_NDMI/'
### Paths to the shapefile and output directories


SHAPEFILE_PATH = f'{main_dir}shp/AOI.shp'
TIFF_DIR = 'data' # download directory for tiff file
PNG_DIR = 'output' # output directory for png data

### Date to fetch Sentinel-2 images
TARGET_DATE = '2024-05-24' # date for downloading image

### Cloud cover threshold
CLOUD_COVER = '10'

DATE_RANGE_DAYS = 365
INSTALLED_PACKAGES = True
