import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

def detect_anomalies(tipo_problema, mes, anio):
    # Cargar y preparar el dataset
    df = pd.read_csv('reportes.csv', na_values=['', ' ', 'NA', 'null'])

    # Convertir la columna de fecha a datetime
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha'])
    df['fecha'] = df['fecha'].dt.tz_convert('America/Mexico_City')

    # Extraer el mes y el año
    df['month'] = df['fecha'].dt.month
    df['year'] = df['fecha'].dt.year

    # Llenar los valores faltantes
    df['tipo_edificio'].fillna('No Aplica', inplace=True)
    df['tipo_problema'].fillna('No Aplica', inplace=True)


    # Filtrar los reportes por el tipo de problema, mes y año específicos
    df_filtered = df[(df['tipo_problema'] == tipo_problema) & (df['month'] == int(mes)) & (df['year'] == int(anio))]

    if df_filtered.empty:
        print(f"No se encontraron reportes para el tipo de problema '{tipo_problema}' en el mes {mes}/{anio}.")
        return

    # Agrupar los reportes válidos por tipo_edificio
    df_grouped = df_filtered.groupby(['tipo_edificio']).size().reset_index(name='cantidad_reportes')

    # Preparar los datos para la detección de anomalías
    le_tipo_edificio = LabelEncoder()
    df_grouped['tipo_edificio_encoded'] = le_tipo_edificio.fit_transform(df_grouped['tipo_edificio'].astype(str))

    # Seleccionar las características para la detección de anomalías
    features = df_grouped[['tipo_edificio_encoded', 'cantidad_reportes']]

    # Entrenar un modelo de Isolation Forest para detectar anomalías
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(features)

    # Predecir anomalías
    df_grouped['anomaly_score'] = model.decision_function(features)
    df_grouped['anomaly'] = model.predict(features)

    # Filtrar las anomalías
    anomalies = df_grouped[df_grouped['anomaly'] == -1]

    # Decodificar los valores a su forma original si es necesario
    anomalies['tipo_edificio_original'] = le_tipo_edificio.inverse_transform(anomalies['tipo_edificio_encoded'])

    # Imprimir resultados
    print("Número de anomalías detectadas:", len(anomalies))
    print(anomalies[['tipo_edificio_original', 'cantidad_reportes', 'anomaly_score']])

    # Guardar anomalías en un archivo CSV
    anomalies.to_csv('anomalies_report.csv', index=False)
