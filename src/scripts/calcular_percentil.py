import xarray as xr
import pandas as pd
import os
import pdb

# Function to count days where daily_max > 90th percentile
def count_days_above_90th(x):
    quantile_90 = x.quantile(0.9)
    print(f"Quantile (90th): {quantile_90.values}")  # Debug
    return (x > quantile_90).sum(dim="time")


def calcular_percentiles(archivo_entrada, variable='t2m'):
    """
    Calcula los percentiles 10 y 90 de un archivo NetCDF por mes.

    Parámetros:
        archivo_entrada (str): Ruta del archivo NetCDF de entrada.

    Retorna:
        xr.Dataset: Dataset con los percentiles calculados.
    """
    dataset = xr.open_dataset(archivo_entrada)
    
    # Convert time from UTC to UTC-5
    dataset['time'] = dataset.indexes['time'] - pd.Timedelta(hours=5)

    # Filter the data in between 1961 and 1990
    dataset_filtered = dataset.sel(time=slice('1961', '1990'))
    
    # Resample to daily frequency and calculate daily max and min
    daily_max = dataset_filtered.resample(time='1D').max()
    daily_min = dataset_filtered.resample(time='1D').min()

    # If the variable is temperature, convert from Kelvin to Celsius
    if variable == 't2m':
        daily_max -= 273.15
        daily_min -= 273.15
    
    # Combine daily max and min into a single dataset
    daily_data = xr.Dataset({
        'daily_max': daily_max[variable],  # Replace 't2m' with the actual variable name
        'daily_min': daily_min[variable]   # Replace 't2m' with the actual variable name
    })
    
    # Calculate percentiles, mean, and standard deviation for each variable
    percentiles_max = daily_data['daily_max'].groupby("time.month").map(
        lambda x: x.quantile([0.1, 0.9], dim="time")
    )
    percentiles_min = daily_data['daily_min'].groupby("time.month").map(
        lambda x: x.quantile([0.1, 0.9], dim="time")
    )
    # Calculate the number of days per month where daily_max > 90th percentile
    days_above_90_max = daily_data['daily_max'].groupby("time.month").map(
        lambda x: (x > x.quantile(0.9)).sum(dim="time")
    )
    days_above_90_max_1 = daily_data['daily_max'].groupby("time.month").apply(
        lambda x: (x > percentiles_max.sel(month=x['time.month'], quantile=0.9)).sum()
    )


    # Calculate the number of days per month where daily_min < 10th percentile
    days_below_10_min = daily_data['daily_min'].groupby("time.month").map(
        lambda x: (x < x.quantile(0.1)).sum(dim="time")
    )
    # Calculate percentiles for each variable
    percentiles_max = daily_data['daily_max'].groupby("time.month").quantile([0.1, 0.9], dim="time")
    percentiles_min = daily_data['daily_min'].groupby("time.month").quantile([0.1, 0.9], dim="time")
    
    # Identify days exceeding the 90th percentile or below the 10th percentile
    
    # Maximum temperature
    ## Temperatures above the 90th percentile (These are from our interest)
    exceed_90_max = daily_data['daily_max'].groupby("time.month") > percentiles_max.sel(quantile=0.9)
    ## Temperatures below the 10th percentile
    below_10_max = daily_data['daily_max'].groupby("time.month") < percentiles_max.sel(quantile=0.1)
    
    # Minimum temperature
    ## Temperatures above the 90th percentile
    exceed_90_min = daily_data['daily_min'].groupby("time.month") > percentiles_min.sel(quantile=0.9)
    ## Temperatures below the 10th percentile (These are from our interest)
    below_10_min = daily_data['daily_min'].groupby("time.month") < percentiles_min.sel(quantile=0.1)

    ################### hasta ac[a fucniona]
    # Calculate mean and standard deviation for days exceeding/below percentiles

    mean_above_90_max = exceed_90_max.groupby("time.month").mean(dim="time")
    std_above_90_max = exceed_90_max.groupby("time.month").std(dim="time")
    
    mean_below_10_max = below_10_max.groupby("time.month").mean(dim="time")
    std_below_10_max = below_10_max.groupby("time.month").std(dim="time")

    mean_above_90_min = exceed_90_min.groupby("time.month").mean(dim="time")
    std_above_90_min = exceed_90_min.groupby("time.month").std(dim="time")

    mean_below_10_min = below_10_min.groupby("time.month").mean(dim="time")
    std_below_10_min = below_10_min.groupby("time.month").std(dim="time")

    # Calculate mean and standard deviation of the number of days per month
    pdb.set_trace()
    mean_max =   mean_above_90_max
    std_dev_max = std_above_90_max
    mean_min =   mean_below_10_min
    std_dev_min = std_below_10_min
    
    # Combine all statistics into a single dataset
    estadisticas = xr.Dataset({
        'percentiles_max': percentiles_max,
        'percentiles_min': percentiles_min,
        'mean_max': mean_max,
        'mean_min': mean_min,
        'std_dev_max': std_dev_max,
        'std_dev_min': std_dev_min
    })
    
    return estadisticas

def guardar_percentiles(estadisticas, archivo_salida, guardar_csv=False):
    """
    Guarda los percentiles calculados en un archivo NetCDF y CSV.

    Parámetros:
        estadisticas (xr.Dataset): Dataset con los percentiles calculados.
        archivo_salida (str): Ruta del archivo NetCDF de salida.
    """
    estadisticas.to_netcdf(archivo_salida)
    
    if guardar_csv:
        subset = estadisticas.sel(latitude=5.9, longitude=-72.99, method = 'nearest')[['month', 'percentiles_max', 'percentiles_min', 'mean_max', 'mean_min', 'std_dev_max', 'std_dev_min']]
        df = subset.to_dataframe().reset_index()
        output_path = "../../data/processed/percentiles.csv"
        df.to_csv(output_path, index=False)

def main():
    ruta_datos = "../../data/processed"
    file = 'era5_tmp_union.nc'
    archivo_union = os.path.join(ruta_datos, file)
    archivo_salida = os.path.join(ruta_datos, "era5_temperatura_percentil.nc")

    try:
        estadisticas = calcular_percentiles(archivo_union)
        guardar_percentiles(estadisticas, archivo_salida, guardar_csv=True)
        print(f"Archivo de percentiles creado en: {archivo_salida}")
    except Exception as e:
        print(f"Error al calcular percentiles: {e}")

if __name__ == "__main__":
    main()