
import xarray as xr
import numpy as np
import pandas as pd
import os
import pdb


def load_percentiles(percentile_file_path):
    percentiles_data = xr.open_dataset(percentile_file_path)
    return percentiles_data#.sel(month=month)


def load_grid_data(file_path, year, month, variable):
    """Load grid data for a specific year, month, and variable."""
    grid_data = xr.open_dataset(file_path)[variable].sel(time=f"{year}-{month:02}")
    grid_data['time'] = grid_data.indexes['time'] - pd.Timedelta(hours=5)
    return grid_data


def calculos_componente_viento(ds_path,year,month):
    try:
        variable="wind_speed"
        ds = load_grid_data(ds_path,year,month,variable)
        print("varialbles:", ds)
    except Exception as e:
        print(f"Error al abri archivo: {e}")


    #Calculamos el wind power (WP)
    #pdb.set_trace() 
    ds = ds.assign_coords(year=ds["time"].dt.year, month=ds["time"].dt.month)
    
    p= 1.23  #constante de la densidad del aire (kg/m3)
    ds["wind_power"]= (p* (ds**3))/2 
        
        
        
    wp_mean_monthly =  ds["wind_power"].groupby(['year', 'month']).mean()
    wp_std_monthly = ds["wind_power"].groupby(['year', 'month']).std()
         
    # Umbral WPu(i, j) = media + 1.28 * sigma
    wpu = wp_mean_monthly + 1.28 * wp_std_monthly # el cuantil 90 calcula el límite superior

    
    #ds.dims
    #ds.coords 
    percentiles=load_percentiles("../../data/processed/era5_wind_percentil.nc")

    percentil_90_by_month = percentiles['percentil_90'].sel(month=ds['month'])#se toma el percentil correspondiente al mes en `ds`

    exceedance = (ds['wind_power'] > percentil_90_by_month)
    WP_90_JK = exceedance.sum('time').astype(int) / ds['wind_power'].groupby(['year', 'month']).count('time')# ecuación 9
    
    # Promedio y desviación estándar para la referencia
    mean_ref = WP_90_JK.groupby(['year', 'month']).mean()
    std_ref = WP_90_JK.groupby(['year', 'month']).std()
    
    # Estandarizar WP90 para calcular la componente del viento (WC)
    wind_component = (WP_90_JK - mean_ref) / std_ref

    #pdb.set_trace() 
    # Crear un nuevo Dataset con los resultados
    nuevo_ds = xr.Dataset({
        'wind_power':ds["wind_power"],
        'rate_of_excedance': WP_90_JK,
        'wp_mean_monthly': WP_90_JK,
        'mean_of_excedanteis': mean_ref,
        'std_of_excedanteis': std_ref,
        'wind_speed_component': wind_component
    })
    nuevo_ds.to_netcdf(f"../../data/processed/wind_analysis_{year}_{month}.nc", encoding={'wind_power': {'zlib': True, 'complevel': 5}})
    return  ds
   
#calcular viento 
    
    

def manage_problemas(ds, variable, valor_nulo): # valor_nulo= Nan, 0 ...
    """
    Reemplaza valores nulos en una variable del dataset.
    """
    ds[variable] = ds[variable].fillna(valor_nulo) 
    return ds





if __name__=="__main__":
    print("Oi")
    file_path="../../data/raw/era5/era5_daily_combined_wind.nc"
    year=1984
    month=1    
    ds=calculos_componente_viento(file_path,year,month)
    #aca_indice_climatico\data\raw\era5\era5_daily_combined_wind.nc



    
    

    