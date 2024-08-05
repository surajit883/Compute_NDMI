
# Compute NDMI from Sentinel-2 Imagery

## Project Overview
This project aims to compute the Normalized Difference Moisture Index (NDMI) from Sentinel-2 imagery. It involves fetching the required imagery from AWS, processing the data to compute NDMI, and generating visual plots of the computed NDMI values.

## Directory Structure
```
/home/surajit/d/PROJECTS/Compute_NDMI/
│
├── data/
│   └── (Downloaded TIFF files will be stored here)
├── output/
│   └── (Output PNG files will be stored here)
├── requirements.txt
├── setup_and_run.sh
├── shp/
│   └── AOI.shp
├── src/
│   ├── main.py
│   └── ndmi_processor.py
│   └── config.py
└── utils/
```

## Prerequisites
Make sure you have the following software installed:
- Python 3.7 or higher
- pip (Python package installer)
- GDAL

## Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/yourusername/compute_ndmi.git
   cd compute_ndmi
   ```

2. **Install required Python packages:**
   ```
   pip install -r requirements.txt  
   or 
   python src/main.py
   ```

## Configuration
Update the configuration file `config/config.py` with your project directory and other necessary settings:
```python
# config/config.py

## Add your project main directory
main_dir = '/home/surajit/d/PROJECTS/Compute_NDMI/'

### Paths to the shapefile and output directories
SHAPEFILE_PATH = f'{main_dir}shp/AOI.shp'
TIFF_DIR = 'data'  # download directory for tiff file
PNG_DIR = 'output'  # output directory for png data

### Date to fetch Sentinel-2 images
TARGET_DATE = '2024-05-24'  # date for downloading image

### Cloud cover threshold
CLOUD_COVER = '10'

DATE_RANGE_DAYS = 365
INSTALLED_PACKAGES = True
```

## Usage

1. **Run the main script:**
   ```
   python src/main.py
   ```

## Script Details

### `src/main.py`
This is the main script that checks for missing packages, installs them if necessary, and calls the `fetch_cogs` function to fetch and process Sentinel-2 imagery.

### `src/ndmi_processor.py`
This script contains functions to:
- Fetch Sentinel-2 imagery from AWS based on the date and cloud cover.
- Download TIFF files of specific bands.
- Compute NDMI from the downloaded bands.
- Plot the NDMI results and save them as PNG files.

## Example

To compute NDMI for a specific date and save the results:

1. Update `config/config.py` with your desired date and parameters.
2. Run the main script:
   ```
   python src/main.py
   ```

## Contributing
Feel free to open issues or submit pull requests with improvements or fixes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author
Surajit Hazra

