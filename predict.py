import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from flask import jsonify
import locale

def predictProblems():
    try:
        # Cambiar el locale a español
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Para Linux/Mac
    except locale.Error:
        print("Locale no disponible. Continuando con la configuración predeterminada.")

    # Crear un DataFrame con los datos históricos (usamos años fijos)
    data = {
        'Fecha': ['2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06'],
        'Problemas': [10, 12, 13, 15, 14, 30]
    }
    df = pd.DataFrame(data)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%Y-%m')
    df.set_index('Fecha', inplace=True)

    # Definir y entrenar el modelo ARIMA (orden p, d, q)
    model = ARIMA(df['Problemas'], order=(1, 1, 1))
    model_fit = model.fit()

    # Hacer la predicción para los próximos 6 meses
    forecast_steps = 6  # Número de meses a predecir
    forecast = model_fit.forecast(steps=forecast_steps)

    # Crear una serie temporal para las fechas futuras
    future_dates = pd.date_range(df.index[-1] + pd.DateOffset(months=1), periods=forecast_steps, freq='ME')

    # Serializar los datos en formato JSON
    forecast_data = {
        "forecast": [{"date": str(date.date()), "problemas": float(value)} for date, value in zip(future_dates, forecast)]
    }

    # Retornar la respuesta en formato JSON
    return jsonify(forecast_data)

