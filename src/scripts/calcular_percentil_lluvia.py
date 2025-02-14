import xarray as xr
import pandas as pd
import os
import numpy as np
import rioxarray as rio
import geopandas as gpd
import pdb

def calcular_estadisticas(data):
    """
    Calcula la media y la desviación estándar de los datos agrupados por mes.

    Parámetros:
    - data (xarray.DataArray): Datos a procesar.

    Retorna:
    - mean_tp (xarray.DataArray): Media mensual de los datos.
    - std_tp (xarray.DataArray): Desviación estándar mensual de los datos.
    """
    mean_tp = data.groupby('time.month').mean(dim='time')  #calcula la media mensual
    std_tp = data.groupby('time.month').std(dim='time')    #calcula la desviación estándar mensual
    
    return mean_tp, std_tp

def guardar_estadisticas(data, archivo_salida, validador = None):
    """
    Guarda los datos en un archivo NetCDF y, si es posible, en un archivo CSV.

    Parámetros:
    - data (xarray.Dataset): Datos a guardar.
    - archivo_salida (str): Nombre del archivo de salida.

    """
    # Check if file exists and delete it
    if os.path.exists(archivo_salida):
        os.remove(archivo_salida)

    #guardar en formato NetCDF
    data.to_netcdf(archivo_salida)

    if validador:
        #convertir los datos de NetCDF a DataFrame y guardar como CSV
        subset = data[['mean_tp','std_tp']].to_dataframe().reset_index()
        output_path = archivo_salida.replace('.nc', '.csv')  # Cambiar la extensión de .nc a .csv
        subset.to_csv(output_path, index=False)

def guardar_estadisticas(data, archivo_salida, validador = None):
    """
    Guarda los datos en un archivo NetCDF y, si es posible, en un archivo CSV.

    Parámetros:
    - data (xarray.Dataset): Datos a guardar.
    - archivo_salida (str): Nombre del archivo de salida.

    """
    #guardar en formato NetCDF
    data.to_netcdf(archivo_salida)

    if validador:
        #convertir los datos de NetCDF a DataFrame y guardar como CSV
        subset = data[['mean_tp','std_tp']].to_dataframe().reset_index()
        output_path = archivo_salida.replace('.nc', '.csv')  # Cambiar la extensión de .nc a .csv
        subset.to_csv(output_path, index=False)

# codigos para procesar el indicador de lluvias

def calcular_5_dias_maximo(data):
    """
    Calcula el máximo acumulado de precipitación en un periodo de 5 días consecutivos dentro de cada mes.

    Parámetros:
    - data (xarray.DataArray): Datos de precipitación diaria.

    Retorna:
    - Rx5day (xarray.DataArray): Máximo acumulado de precipitación en 5 días consecutivos por mes.
    """
    # Sumar la precipitación en ventanas móviles de 5 días
    data_5_day_sum = data.rolling(time=5, min_periods=1).sum()

    # Agregar la columna de mes para verificar que los 5 días pertenezcan al mismo mes
    data_5_day_sum['month'] = data_5_day_sum['time'].dt.month

    # Calcular la diferencia de mes entre el primer y último día de la ventana de 5 días
    month_diff = data_5_day_sum['month'] - data_5_day_sum['month'].shift(time=4)

    # Crear una máscara para filtrar solo los valores donde los 5 días están en el mismo mes
    mask = (month_diff == 0)

    # Aplicar la máscara para eliminar valores que cruzan de un mes a otro
    data_5_day_sum = data_5_day_sum.where(mask, drop=True)

    # Seleccionar el máximo acumulado de 5 días dentro de cada mes
    Rx5day = data_5_day_sum.resample(time='1M').max()

    return Rx5day

def calcular_lluvia(data):
    """
    Calcula la media y desviación estándar del máximo acumulado de 5 días de lluvia por mes.

    Parámetros:
    - data (xarray.DataArray): Datos de precipitación diaria.

    Retorna:
    - p (xarray.Dataset): Contiene la media y desviación estándar del acumulado máximo de 5 días.
    """
    # Aplicar la función para obtener el máximo acumulado en 5 días
    Rx5day = calcular_5_dias_maximo(data)

    # Calcular la media y desviación estándar por mes
    mean_tp, std_tp = calcular_estadisticas(Rx5day)

    # Crear un dataset con la media y la desviación estándar
    p = xr.Dataset({
        'mean_tp': mean_tp['tp_daily_sum'],
        'std_tp': std_tp['tp_daily_sum']
    })

    return p

# codigos para procesar sequia
def count_most_frequent_with_condition(data):
    """
    Encuentra la frecuencia máxima de los valores en el array y ajusta según la condición:
    - Si el valor `0` está presente en los datos, devuelve la frecuencia máxima.
    - Si `0` no está presente, resta 1 a la frecuencia máxima, ya que el primer día es seco pero en la BD se marca como 1.

    Parámetros:
    - data (numpy array): Datos de entrada.

    Retorna:
    - int: Frecuencia máxima ajustada.
    """
    values, counts = np.unique(data, return_counts=True)
    
    return counts.max() - 1
    

def calcular_interpolacion(data):
    """
    Calcula la interpolación lineal de la cantidad de días secos consecutivos (CDD).

    Parámetros:
    - data (xarray.Dataset): Datos de precipitación diaria.

    Retorna:
    - CDD (xarray.Dataset): Serie interpolada de días secos consecutivos.
    """
    # Extraer los años únicos presentes en los datos
    años = data['time.year'].values
    años_unicos = np.unique(años)
    años_validos = []

    # Filtrar años que tengan al menos 365 datos de precipitación
    for año in años_unicos:
        datos_año = data.sel(time=data['time.year'] == año)
        if len(datos_año['time']) >= 365:
            años_validos.append(año)

    # Filtrar solo los datos correspondientes a años válidos
    data = data.sel(time=np.isin(data['time.year'], años_validos))

    # Convertir precipitación a una serie binaria (1 si >= 0.001, 0 si < 0.001)
    data = data.where(data < 0.001, other=1)
    data = data.where(data >= 0.001, other=0)

    # Calcular la suma acumulada de días secos dentro de cada año
    data_cumsum = data.groupby('time.year').cumsum(dim='time')
    data_cumsum['time'] = data['time']

    # Aplicar la función para contar la cantidad más frecuente de días secos consecutivos
    count_most_frequent_da = xr.apply_ufunc(
        count_most_frequent_with_condition,
        data_cumsum.groupby('time.year'),
        input_core_dims=[['time']],  # Dimensión sobre la que se aplica
        output_core_dims=[[]],  # Resultado sin dimensiones adicionales
        vectorize=True,  # Vectorizar para múltiples coordenadas y años
        dask="allowed",  # Soporte para Dask si el dataset es grande
    )

    # Obtener el primer año en la serie de datos
    min_year = count_most_frequent_da['year'].min().values

    # Crear una nueva variable de tiempo con años consecutivos
    count_most_frequent_da['year'] = xr.cftime_range(start=str(min_year), periods=len(count_most_frequent_da['year']), freq='YE')

    # Convertir la variable 'year' en formato datetime estándar
    count_most_frequent_da['year'] = count_most_frequent_da['year'].astype('datetime64[ns]')

    # Realizar interpolación lineal para obtener valores mensuales
    CDD = count_most_frequent_da.resample(year='ME').interpolate('linear')
    CDD = CDD.rename({'year': 'time'})
    
    return CDD

def calcular_sequia(data):
    """
    Calcula la media y desviación estándar de la duración máxima de días secos consecutivos.

    Parámetros:
    - data (xarray.Dataset): Datos de precipitación diaria.

    Retorna:
    - d (xarray.Dataset): Dataset con media y desviación estándar del CDD.
    """
    # Obtener la serie de días secos consecutivos interpolados
    CDD = calcular_interpolacion(data)

    # Calcular media y desviación estándar
    mean_tp, std_tp = calcular_estadisticas(CDD)

    # Crear un dataset con las estadísticas de interés
    d = xr.Dataset({
        'mean_tp': mean_tp['tp_daily_sum'],
        'std_tp': std_tp['tp_daily_sum']
    })

    return d

def calcular_percentiles():
    ruta = "../../data/processed"
    file = 'era5_daily_combined_rain.nc'
    archivo_union = os.path.join(ruta, file)
    archivo_salida_lluvia = os.path.join(ruta, "era5_lluvias_percentil.nc")
    archivo_salida_sequia = os.path.join(ruta, "era5_sequia_percentil.nc")

    #calcular la lluvia
    tp_daily = xr.open_dataset(archivo_union)

    #ordenar_dataset
    tp_daily = tp_daily.sortby('time')

    #filtrar para calcular las estadisticas
    tp_filtered = tp_daily.sel(time=slice(f"1961-01-01", f"1990-12-31"))

    #calcular media y desviacion de referencias
    p = calcular_lluvia(tp_filtered) #lluvia
    d = calcular_sequia(tp_filtered) #sequia

    #guardar estadisticas - ACTUALIZAR
    guardar_estadisticas(p, archivo_salida_lluvia)
    guardar_estadisticas(d, archivo_salida_sequia)

if __name__ == "__main__":
    calcular_percentiles()
