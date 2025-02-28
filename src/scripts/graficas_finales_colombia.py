import os
import pandas as pd 
import matplotlib.pyplot as plt


def plot_temp_anomalies(anomalies_combined,output_dir):
    """
    Genera un gráfico de la media móvil de 5 años de los componentes T90 y T10 de la temperatura.

    Parámetros:
    df (DataFrame): DataFrame con las columnas 'year', 'month','t_90' Y 't_10'.
    """
    df = pd.read_csv(anomalies_combined)
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))

    df = df.sort_values(by='date')

    df['T90_5yr_moving_avg'] = df['t_90'].rolling(window=60, center=True).mean()
    df['T10_5yr_moving_avg'] = df['t_10'].rolling(window=60, center=True).mean()

    #Compound component of temperature
    df['composite'] = df['t_90'] - df['t_10']
    df['composite_5yr_moving_avg'] = df['composite'].rolling(window=60, center=True).mean()

    plt.figure(figsize=(15, 6)) #tamaño de la grafica

    plt.plot(df['date'], df['T90_5yr_moving_avg'], color='#6B8E8E', alpha=1, label="T90 Standardized Anomalies")
    plt.plot(df['date'], df['T10_5yr_moving_avg'], color='#A9C8C8', alpha=1, label="T10 Standardized Anomalies")
    plt.plot(df['date'], df['composite_5yr_moving_avg'], color='black', alpha=1, label="Composite")

    # linea punteada del fin del periodo de referencia
    plt.axvline(pd.Timestamp('1990-01-01'), color='gray', linestyle='dotted', linewidth=1)

    plt.xlabel("Year")
    plt.ylabel("Standardized Anomalies")
    plt.legend()
    plt.grid(True, linestyle='dotted', linewidth=0.5, alpha=0.5)
    plt.title("Temperature Standardized Anomalies 5-Year Moving Average")

    # Guardar la imagen
    output_path = os.path.join(output_dir, "anomalies_temperature.png")
    plt.savefig(output_path, format="png", dpi=300)
    print(f"Gráfica guardada en: {output_path}")

def plot_rainfall_anomalies(anomalies_combined,output_dir):
    """
    Genera un gráfico de la media móvil de 5 años de la anomalia de precipitacion.

    Parámetros:
    df (DataFrame): DataFrame con las columnas 'Año', 'Mes','Anomalia_Lluvia'.
    """
    df = pd.read_csv(anomalies_combined)

    df = df.rename(columns={'Año': 'year', 'Mes': 'month'})

    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))

    df = df.sort_values(by='date')

    df['rainfall_5yr_moving_avg'] = df['Anomalia_Lluvia'].rolling(window=60, center=True).mean()

    plt.figure(figsize=(15, 6)) #tamaño de la grafica

    plt.bar(df['date'], df['Anomalia_Lluvia'], color='#A9C8C8', alpha=1, label="Standardized Anomalies", width=40)
    plt.plot(df['date'], df['rainfall_5yr_moving_avg'], color='black', linewidth=2, label="5-Year Moving Average")

    # linea punteada del fin del periodo de referencia
    plt.axvline(pd.Timestamp('1990-01-01'), color='gray', linestyle='dotted', linewidth=1)

    plt.xlabel("Year")
    plt.ylabel("Standardized Anomalies")
    plt.legend()
    plt.grid(True, linestyle='dotted', linewidth=0.5, alpha=0.5)
    plt.title("Maximum 5-day rainfall Standardized Anomalies 5-Year Moving Average")
    
    # Guardar la imagen
    output_path = os.path.join(output_dir, "anomalies_precipitation.png")
    plt.savefig(output_path, format="png", dpi=300)
    print(f"Gráfica guardada en: {output_path}")

def plot_drought_anomalies(anomalies_combined,output_dir):
    """
    Genera un gráfico de la media móvil de 5 años de la anomalia de sequia.

    Parámetros:
    df (DataFrame): DataFrame con las columnas 'Año', 'Mes','Anomalia_Sequia'.
    """
    df = pd.read_csv(anomalies_combined)

    df = df.rename(columns={'Año': 'year', 'Mes': 'month'})

    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))

    df = df.sort_values(by='date')

    df['rainfall_5yr_moving_avg'] = df['Anomalia_Sequia'].rolling(window=60, center=True).mean()

    plt.figure(figsize=(15, 6)) #tamaño de la grafica

    plt.bar(df['date'], df['Anomalia_Sequia'], color='#A9C8C8', alpha=1, label="Standardized Anomalies", width=40)
    plt.plot(df['date'], df['rainfall_5yr_moving_avg'], color='black', linewidth=2, label="5-Year Moving Average")

    # linea punteada del fin del periodo de referencia
    plt.axvline(pd.Timestamp('1990-01-01'), color='gray', linestyle='dotted', linewidth=1)

    plt.xlabel("Year")
    plt.ylabel("Standardized Anomalies")
    plt.legend()
    plt.grid(True, linestyle='dotted', linewidth=0.5, alpha=0.5)
    plt.title("Consecutive dry days Standardized Anomalies 5-Year Moving Average")

    # Guardar la imagen
    output_path = os.path.join(output_dir, "anomalies_drought.png")
    plt.savefig(output_path, format="png", dpi=300)
    print(f"Gráfica guardada en: {output_path}")

def plot_wind_anomalies(anomalies_combined,output_dir):
    """
    Genera un gráfico de la media móvil de 5 años de la anomalia del viento.

    Parámetros:
    df (DataFrame): DataFrame con las columnas 'year', 'month' y 'anomalies_above'.
    """
    df = pd.read_csv(anomalies_combined)

    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))

    df = df.sort_values(by='date')

    df['5yr_moving_avg'] = df['anomalies_above'].rolling(window=60, center=True).mean()

    plt.figure(figsize=(15, 6)) #tamaño de la grafica

    plt.bar(df['date'], df['anomalies_above'], color='#A9C8C8', alpha=1, label="Standardized Anomalies", width=40)
    plt.plot(df['date'], df['5yr_moving_avg'], color='black', linewidth=2, label="5-Year Moving Average")

    # linea punteada del fin del periodo de referencia
    plt.axvline(pd.Timestamp('1990-01-01'), color='black', linestyle='dotted', linewidth=1)

    plt.xlabel("Year")
    plt.ylabel("Standardized Anomalies")
    plt.legend()
    plt.grid(True, linestyle='dotted', linewidth=0.5, alpha=0.5)
    plt.title("Wind Power Standardized Anomalies 5-Year Moving Average")

    # Guardar la imagen
    output_path = os.path.join(output_dir, "anomalies_wind.png")
    plt.savefig(output_path, format="png", dpi=300)
    print(f"Gráfica guardada en: {output_path}")

def plot_ICA(anomalies_combined_temp, anomalies_combined_rainfall, anomalies_combined_drought, anomalies_combined_wind,output_dir):
    """
    Genera un gráfico de la media móvil de 5 años del índice climático actuarial.

    Parámetros:
    df_temp (DataFrame): DataFrame con las columnas 'year', 'month', 't_90', 't_10'.
    df_rainfall (DataFrame): DataFrame con las columnas 'Año', 'Mes', 'Anomalia_Lluvia'.
    df_drought (DataFrame): DataFrame con las columnas 'Año', 'Mes', 'Anomalia_Sequia'.
    df_wind (DataFrame): DataFrame con las columnas 'year', 'month', 'anomalies_above'.

    """
    # Lectura Archivos
    df_temp = pd.read_csv(anomalies_combined_temp)
    df_rainfall = pd.read_csv(anomalies_combined_rainfall)
    df_drought = pd.read_csv(anomalies_combined_drought)
    df_wind = pd.read_csv(anomalies_combined_wind)

    # Arreglo de nombres de columnas
    df_rainfall.rename(columns={'Año': 'year', 'Mes': 'month'}, inplace=True)
    df_drought.rename(columns={'Año': 'year', 'Mes': 'month'}, inplace=True)

    # Convertir fechas a formato datetime
    for df in [df_temp, df_rainfall, df_drought, df_wind]:
        df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
        df.sort_values(by='date', inplace=True)

    # Crear DataFrame de ICA
    ICA = df_wind[['date', 'anomalies_above']].copy()
    ICA = ICA.merge(df_temp[['date', 't_90', 't_10']], on='date', how='left')
    ICA = ICA.merge(df_rainfall[['date', 'Anomalia_Lluvia']], on='date', how='left')
    ICA = ICA.merge(df_drought[['date', 'Anomalia_Sequia']], on='date', how='left')

    # Renombrar variables
    ICA.rename(columns={'anomalies_above': 'W_std', 'Anomalia_Lluvia': 'P_std', 'Anomalia_Sequia': 'D_std'}, inplace=True)

    # Calcular el Índice Climático Actuarial
    ICA['ICA'] = (ICA['t_90'] - ICA['t_10'] + ICA['W_std'] + ICA['P_std'] + ICA['D_std']) / 5

    # Calcular la media móvil de 5 años
    ICA['ICA_5yr_avg'] = ICA['ICA'].rolling(window=60, center=True).mean()
    ICA['t90_5yr_avg'] = ICA['t_90'].rolling(window=60, center=True).mean()
    ICA['t10_5yr_avg'] = ICA['t_10'].rolling(window=60, center=True).mean()
    ICA['W_std_5yr_avg'] = ICA['W_std'].rolling(window=60, center=True).mean()
    ICA['P_std_5yr_avg'] = ICA['P_std'].rolling(window=60, center=True).mean()
    ICA['D_std_5yr_avg'] = ICA['D_std'].rolling(window=60, center=True).mean()

    # Gráfico
    plt.figure(figsize=(15, 6))

    plt.plot(ICA['date'], ICA['t90_5yr_avg'], color='#6B8E8E',alpha=0.6, linewidth=2, label="T90 5-Year Moving Avg")
    plt.plot(ICA['date'], ICA['t10_5yr_avg'], color='#A9C8C8',alpha=0.4, linewidth=2, label="T10 5-Year Moving Avg")
    plt.plot(ICA['date'], ICA['W_std_5yr_avg'], color='#C08056',alpha=0.5, linewidth=2, label="Wind 5-Year Moving Avg")
    plt.plot(ICA['date'], ICA['P_std_5yr_avg'], color='#D9A441',alpha=0.5, linewidth=2, label="Rainfall 5-Year Moving Avg")
    plt.plot(ICA['date'], ICA['D_std_5yr_avg'], color='#EAD8C0',alpha=0.5, linewidth=2, label="Drought 5-Year Moving Avg")
    plt.plot(ICA['date'], ICA['ICA_5yr_avg'], color='black', linewidth=2, label="ICA 5-Year Moving Avg")

    # Línea punteada en 1990
    plt.axvline(pd.Timestamp('1990-01-01'), color='gray', linestyle='dotted', linewidth=1)

    # Mejoras visuales EAD8C0
    plt.xlabel("Year")
    plt.ylabel("Standardized Anomalies")
    plt.legend()
    plt.grid(True, linestyle='dotted', linewidth=0.5, alpha=0.5)
    plt.title("Actuarial Climate Index - 5-Year Moving Average")

    # Guardar la imagen
    output_path = os.path.join(output_dir, "ICA.png")
    plt.savefig(output_path, format="png", dpi=300)
    print(f"Gráfica guardada en: {output_path}")

def plot_creation_storage(anomalies_combined_temp, anomalies_combined_rainfall, anomalies_combined_drought, anomalies_combined_wind,output_dir):
    """
    Funcion de generación y almacenamiento de graficas 

    Parámetros:
    df_temp (DataFrame): DataFrame con las columnas 'year', 'month', 't_90', 't_10'.
    df_rainfall (DataFrame): DataFrame con las columnas 'Año', 'Mes', 'Anomalia_Lluvia'.
    df_drought (DataFrame): DataFrame con las columnas 'Año', 'Mes', 'Anomalia_Sequia'.
    df_wind (DataFrame): DataFrame con las columnas 'year', 'month', 'anomalies_above'.
    """
    plot_temp_anomalies(anomalies_combined_temp,output_dir)
    plot_rainfall_anomalies(anomalies_combined_rainfall,output_dir)
    plot_drought_anomalies(anomalies_combined_drought,output_dir)
    plot_wind_anomalies(anomalies_combined_wind,output_dir)
    plot_ICA(anomalies_combined_temp, anomalies_combined_rainfall, anomalies_combined_drought, anomalies_combined_wind,output_dir)


if __name__ == "__main__":

    # Graficas Colombia
    anomalies_combined_temp_col = "../../data/processed/anomalias_colombia/anomalies_temperature_combined.csv"
    anomalies_combined_rainfall_col = "../../data/processed/anomalias_colombia/anomalies_precipitation_combined.csv"
    anomalies_combined_drought_col = "../../data/processed/anomalias_colombia/anomalies_drought_combined.csv"
    anomalies_combined_wind_col = "../../data/processed/anomalias_colombia/anomalies_wind_combined.csv"
    output_dir_col = "../../articles/graficas/anomalias_colombia"

    plot_creation_storage(anomalies_combined_temp_col, anomalies_combined_rainfall_col, anomalies_combined_drought_col, anomalies_combined_wind_col,output_dir_col)  

    # Graficas Antioquia
    anomalies_combined_temp_ant = "../../data/processed/anomalias_antioquia/anomalies_temperature_combined.csv"
    anomalies_combined_rainfall_ant = "../../data/processed/anomalias_antioquia/anomalies_precipitation_combined.csv"
    anomalies_combined_drought_ant = "../../data/processed/anomalias_antioquia/anomalies_drought_combined.csv"
    anomalies_combined_wind_ant = "../../data/processed/anomalias_antioquia/anomalies_wind_combined.csv"
    output_dir_ant = "../../articles/graficas/anomalias_antioquia"

    plot_creation_storage(anomalies_combined_temp_ant, anomalies_combined_rainfall_ant, anomalies_combined_drought_ant, anomalies_combined_wind_ant,output_dir_ant)  

     # Graficas cundinamarca y Bogotá
    anomalies_combined_temp_cun = "../../data/processed/anomalias_cundinamarca_bogota/anomalies_temperature_combined.csv"
    anomalies_combined_rainfall_cun = "../../data/processed/anomalias_cundinamarca_bogota/anomalies_precipitation_combined.csv"
    anomalies_combined_drought_cun = "../../data/processed/anomalias_cundinamarca_bogota/anomalies_drought_combined.csv"
    anomalies_combined_wind_cun = "../../data/processed/anomalias_cundinamarca_bogota/anomalies_wind_combined.csv"
    output_dir_cun = "../../articles/graficas/anomalias_cundinamarca_bogota"

    plot_creation_storage(anomalies_combined_temp_cun, anomalies_combined_rainfall_cun, anomalies_combined_drought_cun, anomalies_combined_wind_cun,output_dir_cun)  

     # Graficas Valle del Cauca 
    anomalies_combined_temp_val = "../../data/processed/anomalias_valle_cauca/anomalies_temperature_combined.csv"
    anomalies_combined_rainfall_val = "../../data/processed/anomalias_valle_cauca/anomalies_precipitation_combined.csv"
    anomalies_combined_drought_val = "../../data/processed/anomalias_valle_cauca/anomalies_drought_combined.csv"
    anomalies_combined_wind_val = "../../data/processed/anomalias_valle_cauca/anomalies_wind_combined.csv"
    output_dir_val = "../../articles/graficas/anomalias_valle_cauca"

    plot_creation_storage(anomalies_combined_temp_val, anomalies_combined_rainfall_val, anomalies_combined_drought_val, anomalies_combined_wind_val,output_dir_val)  
