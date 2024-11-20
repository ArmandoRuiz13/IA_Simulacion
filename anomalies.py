import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_anomalies(tipo_problema, mes, anio):
    # Cargar y preparar el dataset
    df = pd.read_csv('reportes.csv', na_values=['', ' ', 'NA', 'null'])

    # Convertir la columna de fecha a datetime
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha'])
    # df['fecha'] = df['fecha']

    # Extraer el mes y el año
    df['month'] = df['fecha'].dt.month
    df['year'] = df['fecha'].dt.year

    # Llenar los valores faltantes
    df['tipo_problema'].fillna('No Aplica', inplace=True)

    # Filtrar los reportes por el tipo de problema, mes y año específicos
    df_filtered = df[(df['tipo_problema'] == tipo_problema) & (df['month'] == int(mes)) & (df['year'] == int(anio))]

    if df_filtered.empty:
        print(f"No se encontraron reportes para el tipo de problema '{tipo_problema}' en el mes {mes}/{anio}.")
        return

    # Agrupar por tipo_problema
    df_grouped = df_filtered.groupby('tipo_problema').size().reset_index(name='cantidad_reportes')

    # Seleccionar la característica para la detección de anomalías
    features = df_grouped[['cantidad_reportes']]

    # Entrenar un modelo de Isolation Forest para detectar anomalías
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(features)

    # Predecir anomalías
    df_grouped['anomaly_score'] = model.decision_function(features)
    df_grouped['anomaly'] = model.predict(features)

    # Filtrar las anomalías
    anomalies = df_grouped[df_grouped['anomaly'] == -1]

    # Imprimir resultados
    print("Número de anomalías detectadas:", len(anomalies))
    print(anomalies[['tipo_problema', 'cantidad_reportes', 'anomaly_score']])

    # Guardar anomalías en un archivo CSV
    anomalies.to_csv('anomalies_report.csv', index=False)
