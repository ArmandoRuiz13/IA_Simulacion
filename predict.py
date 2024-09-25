import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from flask import Flask, jsonify
import locale

def predict_problems(month=True, problem_type=None, building_type=None, forecast_steps = 6,  seasonal_periods=12):
    try:
        # Cambiar el locale a español
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Para Linux/Mac
    except locale.Error:
        print("Locale no disponible. Continuando con la configuración predeterminada.")
    
    try:
        # Leer los reportes de problemas desde el archivo CSV
        df = pd.read_csv('reportes.csv')
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    forecast_steps = int(forecast_steps)  # Convertir a entero
    # Asegurarse de que la columna 'fecha' esté en formato de fecha
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')  # Inferir formato de fecha automáticamente
    # Eliminar filas con fechas inválidas
    df = df.dropna(subset=['fecha'])

    # Filtrar por tipo de problema
    if problem_type:
        df = df[df['tipo_problema'] == problem_type]

    # Filtrar por tipo de edificio
    if building_type:
        df = df[df['tipo_edificio'] == building_type]

    # Agrupar por mes y contar el número de reportes por mes
    if month:
        df['mes'] = df['fecha'].dt.to_period('M')  # Agrupar por mes
        reportes_por_mes = df.groupby('mes').size()
    else:
        return jsonify({"error": "Monthly grouping is required"}), 400

    # Verificar si hay datos agrupados
    if reportes_por_mes.empty:
        return jsonify({"error": "No report data found after grouping"}), 404

    # Convertir el resultado en un DataFrame con un índice de fechas mensuales
    reportes_df = pd.DataFrame(reportes_por_mes, columns=['Problemas'])
    reportes_df.index = reportes_df.index.to_timestamp()  # Convertir a formato de tiempo

    try:
        # Definir y entrenar el modelo SARIMA
        model = SARIMAX(reportes_df['Problemas'], 
                        order=(1, 1, 1),  # Orden no estacional (p, d, q)
                        seasonal_order=(1, 1, 1, seasonal_periods),  # Orden estacional (P, D, Q, m)
                        enforce_stationarity=False, 
                        enforce_invertibility=False)
        model_fit = model.fit(disp=False)
    except Exception as e:
        return jsonify({"error": f"SARIMA model training failed: {str(e)}"}), 500

    # Hacer la predicción para los próximos 6 meses
    # forecast_steps = 6  # Número de meses a predecir
    forecast = model_fit.forecast(steps=forecast_steps)

    # Crear una serie temporal para las fechas futuras
    future_dates = pd.date_range(reportes_df.index[-1] + pd.DateOffset(months=1), periods=forecast_steps, freq='M')

    # Serializar los datos en formato JSON
    forecast_data = {
        "forecast": [{"date": str(date.date()), "problemas": float(value)} for date, value in zip(future_dates, forecast)]
    }

    # Retornar la respuesta en formato JSON
    return jsonify(forecast_data)
