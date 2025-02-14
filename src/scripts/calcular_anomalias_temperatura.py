import os
import xarray as xr
import pdb
import pandas as pd
import rioxarray as rxr
import geopandas as gpd

def load_grid_data(file_path, year, month, variable, shapefile_path=None):
    """Load grid data for a specific year, month, and variable, optionally clipping it with a shapefile."""
    
    # Convert temperature to Celsius if needed
    if variable == 't2m':
        grid_data = xr.open_dataset(file_path, engine='cfgrib')[variable].sel(time=f"{year}-{month:02}")
        grid_data -= 273.15
        grid_data['time'] = grid_data.indexes['time'] - pd.Timedelta(hours=5)  # Convert to UTC-5
    
    if variable == 'wind_speed':
        grid_data = xr.open_dataset(file_path, engine='cfgrib')[['u10', 'v10']].sel(time=f"{year}-{month:02}")
    
        # For Colombia we have to convert the time from UTC to UTC-5
        grid_data['time'] = grid_data.indexes['time'] - pd.Timedelta(hours=5)

        grid_data = grid_data.resample(time="1D").mean(dim="time")
    
        # Calculate the wind speed from the U and V components
        grid_data["wind_speed"] = (grid_data["u10"]**2 + grid_data["v10"]**2)**0.5

        # Return only the wind speed
        grid_data = grid_data.drop_vars(["u10", "v10"])

    if shapefile_path:
        # Read the shapefile
        shape = gpd.read_file(shapefile_path)

        # Ensure dataset has spatial dimensions
        grid_data = grid_data.rio.write_crs("EPSG:4326", inplace=True)

        # Clip using the shapefile
        grid_data = grid_data.rio.clip(shape.geometry, shape.crs, drop=True)
    
    return grid_data

def resample_to_daily(grid_data):
    """Resample hourly data to daily max and min."""
    daily_max = grid_data.resample(time='1D').max(dim='time')
    daily_min = grid_data.resample(time='1D').min(dim='time')
    return daily_max, daily_min

def load_percentiles(percentile_file, month, shapefile_path=None):
    """Load and optionally clip precomputed percentiles for a specific month."""
    percentiles_data = xr.open_dataset(percentile_file).sel(month=month)
    
    if shapefile_path:
        shape = gpd.read_file(shapefile_path)

        # Ensure the dataset has spatial dimensions
        percentiles_data = percentiles_data.rio.write_crs("EPSG:4326", inplace=True)

        # Clip the percentile dataset
        percentiles_data = percentiles_data.rio.clip(shape.geometry, shape.crs, drop=True)

    return percentiles_data


def compute_occurrences(daily_data, percentile_10, percentile_90):
    """Compute occurrences of values above the 90th percentile and below the 10th percentile."""
    count_above_90 = (daily_data > percentile_90).sum(dim='time')
    count_below_10 = (daily_data < percentile_10).sum(dim='time')
    return count_above_90, count_below_10

def calculate_anomalies(count_data, mean, std_dev):
    """Calculate normalized anomalies."""
    return (count_data - mean) / std_dev

def drop_unnecessary_coords(data_arrays, coord_name):
    """Drop an unnecessary coordinate from a list of DataArrays."""
    return [data_array.drop(coord_name) for data_array in data_arrays]

def create_anomalies_dataset(variables, attrs):
    """Create an xarray.Dataset for anomalies."""
    return xr.Dataset(variables, attrs=attrs)

def calcular_anomalias(archivo_percentiles, archivo_comparar, year, month, salida_anomalias, shapefile_path=None):
    variable = 't2m'

    # Load and preprocess grid data with clipping
    grid_data = load_grid_data(archivo_comparar, year, month, variable, shapefile_path)
    daily_max, daily_min = resample_to_daily(grid_data)

    # Load percentiles and clip them
    month_percentiles = load_percentiles(archivo_percentiles, month, shapefile_path)
    
    percentile_10_max = month_percentiles['percentiles_max'].sel(quantile=0.1)
    percentile_90_max = month_percentiles['percentiles_max'].sel(quantile=0.9)
    percentile_10_min = month_percentiles['percentiles_min'].sel(quantile=0.1)
    percentile_90_min = month_percentiles['percentiles_min'].sel(quantile=0.9)

    # Compute occurrences
    count_above_90_max, count_below_10_max = compute_occurrences(daily_max, percentile_10_max, percentile_90_max)
    count_above_90_min, count_below_10_min = compute_occurrences(daily_min, percentile_10_min, percentile_90_min)

    # Maximum temperature
    ## Temperatures above the 90th percentile (These are from our interest)
    count_above_90_max = (daily_max > percentile_90_max).astype(int)
    ## Temperatures below the 10th percentile
    count_below_10_max = (daily_max < percentile_10_max).astype(int)

    # Minimum temperature
    ## Temperatures above the 90th percentile
    count_above_90_min = (daily_min > percentile_90_min).astype(int)
    ## Temperatures below the 10th percentile (These are from our interest)
    count_below_10_min = (daily_min < percentile_10_min).astype(int)

    # Promedio de ocurrencias de los valores máximos y mínimos
    valores_max = (count_above_90_max + count_above_90_min)/2
    valores_min = (count_below_10_max + count_below_10_min)/2

    # Promedio de los valores máximos y mínimos mensuales
    valores_max_mensuales = valores_max.groupby(["time.month"]).mean(dim="time").sel(month = month)
    valores_min_mensuales = valores_min.groupby(["time.month"]).mean(dim="time").sel(month = month)

    # Calculate anomalies
    anomalies_above_max = calculate_anomalies(valores_max_mensuales, month_percentiles['mean_max'], month_percentiles['std_dev_max'])
    anomalies_below_min = calculate_anomalies(valores_min_mensuales, month_percentiles['mean_min'], month_percentiles['std_dev_min'])

    ### Calcular los porcentajes
    # Drop unnecessary coordinates
    variables_to_drop = [anomalies_above_max, anomalies_below_min]
    variables_dropped = drop_unnecessary_coords(variables_to_drop, 'quantile')

    # Create anomalies dataset
    anomalies = create_anomalies_dataset({
        't_90': variables_dropped[0],
        't_10': variables_dropped[1]
    }, attrs={'description': 'Anomalies and counts of temperature extremes'})

    # Save the dataset
    anomalies.to_netcdf(salida_anomalias)

    return anomalies.mean(dim=['latitude', 'longitude'], keep_attrs=True)

def procesar_anomalias_temperatura(archivo_percentiles, archivo_comparar_location, output_csv_path, shapefile_path):
    # List all files in the directory
    files = os.listdir(archivo_comparar_location)

    # Initialize an empty list to store monthly datasets
    all_anomalies = []

    # Loop through each year and month
    for year in range(1961, 2025):
        print(f"Processing year {year}...")
        
        # Find all files containing the year
        archivo_comparar = [file for file in files if str(year) in file]
        
        # Filter for GRIB files
        archivo_comparar = [file for file in archivo_comparar if file.endswith(".grib")]
        if not archivo_comparar:
            print(f"Error processing year {year}: No GRIB files found")
            continue
        
        # Check if the file is a temperature file
        archivo_comparar = [file for file in archivo_comparar if "tmp" in file]
        if not archivo_comparar:
            print(f"Error processing year {year}: No temperature files found")
            continue
        
        if len(archivo_comparar) != 1:
            print(f"Error processing year {year}: More than one temperature file found")
            continue
        else:
            archivo_comparar = archivo_comparar[0]

        archivo_comparar = os.path.join(archivo_comparar_location, archivo_comparar)

        for month in range(1, 13):
            try:
                print(f"Processing year {year}, month {month}...")
                ds_month = calcular_anomalias(
                    archivo_percentiles=archivo_percentiles,
                    archivo_comparar=archivo_comparar,
                    year=year,
                    month=month,
                    salida_anomalias=f"../../data/processed/anomalies_temperature_{year}_{month}.nc",
                    shapefile_path=shapefile_path
                )
                ds_month = ds_month.assign_coords(year=year)
                all_anomalies.append(ds_month)
            except Exception as e:
                print(f"Error processing year {year}, month {month}: {e}")
                continue

    # Combine all monthly datasets into one
    combined_anomalies = xr.concat(all_anomalies, dim='time')

    # Convert the xarray.Dataset to a pandas.DataFrame
    anomalies_df = combined_anomalies.to_dataframe().reset_index()

    # Save the DataFrame to a CSV file
    anomalies_df.to_csv(output_csv_path, index=False)
    print(f"Anomalies saved to {output_csv_path}")

if __name__ == "__main__":
    archivo_percentiles = "../../data/processed/era5_temperatura_percentil.nc"
    archivo_comparar_location = "../../data/raw/era5/"
    output_csv_path = "../../data/processed/anomalies_temperature_combined.csv"
    shapefile_path = "../../data/shapefiles/colombia_4326.shp"

    procesar_anomalias_temperatura(archivo_percentiles, archivo_comparar_location, output_csv_path, shapefile_path)
