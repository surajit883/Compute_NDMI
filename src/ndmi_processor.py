#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 11:47:16 2024

@author: Surajit Hazra
"""

from pystac_client import Client
import geopandas as gpd
import os
import requests
import datetime
import rasterio
import rasterio.mask
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from shapely.geometry import mapping
from rasterio.mask import mask



def plot_ndmi(ndmi_array, mean_ndmi, date, output_png, shapefile_geom=None):
    plt.figure(figsize=(10, 8))
    plt.imshow(ndmi_array, cmap='RdYlGn', vmin=-1, vmax=1)
    plt.colorbar(label='NDMI')
    
    if shapefile_geom is not None:
        for geom in shapefile_geom:
            if geom.geom_type == 'Polygon':
                coords = np.array(geom.exterior.xy).T
                plt.plot(coords[:, 0], coords[:, 1], 'b-', linewidth=2)
            elif geom.geom_type == 'MultiPolygon':
                for part in geom:
                    coords = np.array(part.exterior.xy).T
                    plt.plot(coords[:, 0], coords[:, 1], 'b-', linewidth=2)
    
    plt.title(f"NDMI - {date}\nMean NDMI: {mean_ndmi:.4f}", fontsize=16)
    plt.xlabel('Pixel X')
    plt.ylabel('Pixel Y')
    plt.savefig(output_png, format='png')
    plt.close()
    print(f"NDMI plot saved to {output_png}")

def plot_ndmi_with_shapefile(ndmi_array, extent, mean_ndmi, shp, png_date, output_path):
    fig, ax = plt.subplots(figsize=(10, 10), facecolor='white')
    im = ax.imshow(ndmi_array, cmap='RdYlGn',  # Use the RdYlGn colormap
                   extent=extent,
                   vmin=-1, vmax=1)  # Adjust vmin and vmax according to your NDMI range
    shp.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1)
    plt.colorbar(mappable=im, orientation="vertical", fraction=0.03, pad=0.04)
    ax.set_title(f"Normalized Difference Moisture Index (NDMI) - {png_date}", ha='center', fontsize=16, fontweight='bold')
    ax.axis('off')
    
    ax.annotate(f"Mean NDMI: {mean_ndmi:.4f}",
                xy=(0.5, 0.95), xycoords='axes fraction',
                ha='center', va='center',
                fontsize=14, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='white'))

    plt.subplots_adjust(bottom=0.1, right=0.8, top=0.9)
    fig.tight_layout()
    plt.savefig(output_path, format='png', dpi=300)
    plt.close()

    print(f"NDMI plot saved to {output_path}")

def compute_ndmi(b8_path,b11_path,shp,png_date,output_path):
    
    with rasterio.open(b8_path) as src_b8:
        b8 = src_b8.read(1)
        b8_meta = src_b8.meta

    with rasterio.open(b11_path) as src_b11:
        b11 = src_b11.read(1)

    if b8.shape != b11.shape:
        raise ValueError("B8 and B11 bands do not have the same shape")

    ndmi = (b8.astype(float) - b11.astype(float)) / (b8 + b11).astype(float)
    shp = shp.to_crs(b8_meta['crs'].to_proj4())

    with rasterio.MemoryFile() as memfile:
        with memfile.open(
            driver='GTiff',
            height=ndmi.shape[0],  # Rows
            width=ndmi.shape[1],   # Columns
            count=1,               # Number of bands
            dtype=rasterio.float32,
            crs=b8_meta['crs'],
            transform=b8_meta['transform'],
        ) as dataset:
            dataset.write(ndmi, 1)  # Write the NDMI data to the first band

            out_image, out_transform = mask(dataset, shapes=[mapping(geom) for geom in shp.geometry], crop=True)
            out_image[0][out_image[0] == 0] = np.nan
            mean_ndmi = np.nanmean(out_image[0])
            out_meta = dataset.meta.copy()
            out_meta.update({"driver": "GTiff", "height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform})
    extent = [
        out_transform[2], 
        out_transform[2] + out_transform[0] * out_image.shape[2], 
        out_transform[5] + out_transform[4] * out_image.shape[1], 
        out_transform[5]
    ]

    plot_ndmi_with_shapefile(out_image[0], extent, mean_ndmi, shp, png_date, output_path)

def check_ndmi(ndmi_files, output_dir, aoi_geom):
    b8a_path, b11_path = ndmi_files
    ndmi_date = os.path.basename(b8a_path).split('_')[2]
    ndmi_png = f'{output_dir}/{ndmi_date}.png'
    if os.path.exists(ndmi_png):
        print(f"NDMI file already exists: {ndmi_png}")
    else:    
        compute_ndmi(b8a_path, b11_path, aoi_geom, ndmi_date, ndmi_png)

def create_dir(main_dir, _dir):
    _dir = os.path.join(main_dir, _dir)
    _dir = os.path.normpath(_dir)
    if not os.path.exists(_dir):
        os.makedirs(_dir)
    return _dir

def download_tiff_files(urls,date,_dir):
    files = []
    for url in urls:
        try:
            name = f'{date}_{os.path.basename(url)}'
            file_name = os.path.join(_dir, name)
            if os.path.exists(file_name):
                print(f"File already exists: {file_name}")
                files.append(file_name)
                continue
            response = requests.get(url)
            response.raise_for_status() 
            with open(file_name, 'wb') as file:
                file.write(response.content)
            
            print(f"Downloaded: {file_name}")
            files.append(file_name)
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")
    return files

def get_band_links(data_dict, bands, band_dict) -> list:
    links = []
    for band in bands:
        common_name = band_dict.get(band)
        if not common_name:
            print(f"Band {band} not found in band dictionary.")
            continue
        for key, value in data_dict.items():
            if 'href' in value and value.get('eo:bands', [{}])[0].get('common_name') == common_name:
                if value['href'].endswith('tif'):
                    links.append(value['href'])
    return links

def fetch_cogs(main_dir , tdate, shp_file, cloud_cover='10', date_range_days=365, tiff_dir = 'data', png_dir = 'output'):
    shapes = gpd.read_file(shp_file)
    geom = shapes.geometry[0]
    
    ndmi_band_dict = { 
        'b8A': 'nir08', 
        'b11': 'swir16'
    }
    
    collection = "sentinel-2-l2a"
    bands = ['b8A', 'b11']
    api_url = "https://earth-search.aws.element84.com/v1"
    S2_STAC = Client.open(api_url)
    
    target_date = datetime.datetime.strptime(tdate, "%Y-%m-%d")
    
    def search_data(start_date, end_date):
        sdate = start_date.strftime("%Y-%m-%dT00:00:00Z")
        edate = end_date.strftime("%Y-%m-%dT23:59:59Z")
        timeRange = f'{sdate}/{edate}'

        s2satSearch = S2_STAC.search(
            intersects=geom,
            datetime=timeRange,
            query={"eo:cloud_cover": {"lt": cloud_cover}},
            collections=[collection]
        )
        return [i.to_dict() for i in s2satSearch.get_items()]
    
    s2sat_items = search_data(target_date, target_date)
    
    if not s2sat_items:
        
        for i in range(1, 365):
            end_date = target_date - datetime.timedelta(days=i)
            s2sat_items = search_data(end_date, end_date)
            
            if s2sat_items:
                print('data is availble for ', end_date)
                break
    
    if not s2sat_items:
        print(f"No data available for this location from last years to your given date ")
        return
    
    down_dir = create_dir(main_dir, 'data')
    ndmi_dir = create_dir(main_dir, 'output')
    
    for s2band in s2sat_items:
        band_id = s2band['id']
        print(band_id)
        links = get_band_links(s2band['assets'], bands, ndmi_band_dict)
        ndmi_files = download_tiff_files(links, band_id, down_dir)
        ndmi_file_path = check_ndmi(ndmi_files,ndmi_dir, shapes)


if __name__ == "__main__":
    farm_polygon = '../shp/AOI.shp'
    gdf = gpd.read_file(farm_polygon)
    geom = gdf.geometry.iloc[0]
    geojson_dict = geom.__geo_interface__

    tdate = "2024-02-24"
    
    fetch_cogs(tdate, farm_polygon)

    