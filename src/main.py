#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script to run NDMI computation and plotting based on configuration in config.py
"""

import subprocess
import sys
import pkg_resources
import config
from ndmi_processor import fetch_cogs
import os 


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def update_config(config_path):
    with open(config_path, 'r') as file:
        lines = file.readlines()
    
    with open(config_path, 'w') as file:
        for line in lines:
            if line.strip().startswith('INSTALLED_PACKAGES'):
                file.write('INSTALLED_PACKAGES = True\n')
            else:
                file.write(line)

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(os.path.abspath(__file__))
requirements_path = os.path.join(script_dir, '..', 'requirements.txt')
config_path = os.path.join(script_dir,'config.py')
requirements_path = os.path.normpath(requirements_path)

with open(requirements_path) as f:
    required = f.read().splitlines()

installed = {pkg.key for pkg in pkg_resources.working_set}
missing = [pkg for pkg in required if pkg not in installed]

if config.INSTALLED_PACKAGES == False:
    if missing:
        print(f"Installing missing packages: {missing}")
        for package in missing:        
            install(package)
        update_config(config_path)

def main():
    
    # Extract configurations from config.py
    shapefile_path = config.SHAPEFILE_PATH
    target_date = config.TARGET_DATE
    cloud_cover = config.CLOUD_COVER
    date_range_days = config.DATE_RANGE_DAYS
    main_dir = config.main_dir
    tiff_dir = config.TIFF_DIR
    Png_dir = config.PNG_DIR

    # Fetch and process Sentinel-2 COGs
    fetch_cogs(main_dir, target_date, shapefile_path, cloud_cover, date_range_days)

if __name__ == "__main__":
    main()
