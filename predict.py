import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from flask import jsonify
import locale

def predictProblems(csv_file_path):
    try:
        # Cambiar el locale a español
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Para Linux/Mac
    except locale.Error:
        print("Locale no disponible. Continuando con la configuración predeterminada.")

    # Leer los reportes de problemas desde el archivo CSV
    df = pd.read_csv(csv_file_path)

    # Asegurarse de que la columna 'fecha' esté en formato de fecha
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')  # Inferir formato de fecha automáticamente

    # Eliminar filas con fechas inválidas
    df = df.dropna(subset=['fecha'])

    # Agrupar por mes y contar el número de reportes por mes
    df['mes'] = df['fecha'].dt.to_period('M')  # Agrupar por mes
    reportes_por_mes = df.groupby('mes').size()

    # Convertir el resultado en un DataFrame con un índice de fechas mensuales
    reportes_por_mes = reportes_por_mes.to_timestamp()  # Convertir a formato de tiempo
    reportes_df = pd.DataFrame(reportes_por_mes, columns=['Problemas'])

    # Definir y entrenar el modelo ARIMA (orden p, d, q)
    model = ARIMA(reportes_df['Problemas'], order=(1, 1, 1))
    model_fit = model.fit()

    # Hacer la predicción para los próximos 6 meses
    forecast_steps = 6  # Número de meses a predecir
    forecast = model_fit.forecast(steps=forecast_steps)

    # Crear una serie temporal para las fechas futuras
    future_dates = pd.date_range(reportes_df.index[-1] + pd.DateOffset(months=1), periods=forecast_steps, freq='M')

    # Serializar los datos en formato JSON
    forecast_data = {
        "forecast": [{"date": str(date.date()), "problemas": float(value)} for date, value in zip(future_dates, forecast)]
    }

    # Retornar la respuesta en formato JSON
    return jsonify(forecast_data)

