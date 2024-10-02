import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.statespace.sarimax import SARIMAX
import os

def generate_and_save_plots(problem_type=None, building_type=None, seasonal_periods=10, forecast_steps=6):
    try:
        # Leer los reportes desde el archivo CSV
        df = pd.read_csv('reportes.csv')
    except Exception as e:
        print(f"Error al leer el archivo CSV: {str(e)}")
        return
    
    # Asegurarse de que la columna 'fecha' esté en formato de fecha
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    
    # Verificar si hay fechas inválidas (NaT)
    if df['fecha'].isna().sum() > 0:
        print(f"Advertencia: {df['fecha'].isna().sum()} fechas no válidas encontradas y eliminadas.")
    
    # Eliminar filas con fechas no válidas
    df = df.dropna(subset=['fecha'])
    
    print(df.head())  # Mostrar algunas filas para verificar los datos
    print(df['fecha'].dtype)  # Verificar el tipo de dato de 'fecha'

    # Filtrar por tipo de problema
    if problem_type:
        df = df[df['tipo_problema'] == problem_type]

    # Filtrar por tipo de edificio
    if building_type:
        df = df[df['tipo_edificio'] == building_type]

    # Mostrar las opciones disponibles en el DataFrame
    print("Tipos de problemas únicos:", df['tipo_problema'].unique())
    print("Tipos de edificios únicos:", df['tipo_edificio'].unique())

    # Agrupar por mes
    df['mes'] = df['fecha'].dt.to_period('M')
    reportes_por_mes = df.groupby('mes').size()

    if reportes_por_mes.empty:
        print("No se encontraron datos de reportes después del filtrado.")
        return

    # Convertir a DataFrame
    reportes_df = pd.DataFrame(reportes_por_mes, columns=['Problemas'])
    reportes_df.index = reportes_df.index.to_timestamp()

    # Crear carpeta para guardar los gráficos
    output_dir = 'output_plots'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # Generar gráficos ACF y PACF
        fig, ax = plt.subplots(2, 1, figsize=(10, 8))

        # Graficar ACF y PACF
        plot_acf(reportes_df['Problemas'], ax=ax[0])
        ax[0].set_title("Autocorrelation Function (ACF)")
        
        plot_pacf(reportes_df['Problemas'], ax=ax[1])
        ax[1].set_title("Partial Autocorrelation Function (PACF)")

        # Guardar gráficos ACF y PACF
        plt.tight_layout()
        acf_pacf_path = os.path.join(output_dir, 'acf_pacf.png')
        plt.savefig(acf_pacf_path)
        plt.close(fig)  # Cerrar la figura para liberar memoria
        print(f"Gráfico ACF y PACF guardado en {acf_pacf_path}")

        # Modelo SARIMA para obtener el BIC
        print(reportes_df['Problemas'])
        model = SARIMAX(reportes_df['Problemas'],
                        order=(1, 0, 0),  # Orden no estacional (p, d, q)
                        seasonal_order=(1, 1, 1, 9),  # Orden estacional (P, D, Q, m)
                        enforce_stationarity=False,
                        enforce_invertibility=False)
        model_fit = model.fit(disp=True)

        # Obtener y guardar el valor BIC
        bic_value = model_fit.bic
        aic_value = model_fit.aic

        aic_file_path = os.path.join(output_dir, 'aic_value.txt');
      
        bic_file_path = os.path.join(output_dir, 'bic_value.txt')
    
        with open(bic_file_path, 'w') as f:
            f.write(f"BIC: {bic_value}\n")
        print(f"Valor BIC guardado en {bic_file_path}")

        with open(aic_file_path, 'w') as f:
            f.write(f"AIC: {aic_value}\n")
        print(f"Valor BIC guardado en {aic_file_path}")

    except Exception as e:
        print(f"Error al generar gráficos o modelo SARIMA: {str(e)}")

# Ejecutar la función
generate_and_save_plots(problem_type="Humedad", building_type="Academico")
