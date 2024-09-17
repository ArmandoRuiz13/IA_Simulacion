import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

# Cargar y preparar el dataset
df = pd.read_csv('reportes.csv', na_values=['', ' ', 'NA', 'null'])

# Convertir la columna de fecha a datetime
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
df = df.dropna(subset=['fecha'])
df['fecha'] = df['fecha'].dt.tz_convert('America/Mexico_City')

# Extraer el mes y el día de la semana
df['month'] = df['fecha'].dt.month
df['day_of_week'] = df['fecha'].dt.dayofweek

# Llenar los valores faltantes en 'edificio_bano'
df['edificio_bano'].fillna('No Aplica', inplace=True)

# Separar los reportes con "No Aplica" en edificio_bano
df_no_aplica = df[df['edificio_bano'] == 'No Aplica']
df_valid = df[df['edificio_bano'] != 'No Aplica']

# Agrupar los reportes válidos (con edificio_bano) por edificio_bano y mes
df_grouped = df_valid.groupby(['edificio_bano', 'month']).size().reset_index(name='cantidad_reportes')

# Preparar los datos para la detección de anomalías
le_edificio_bano = LabelEncoder()
df_grouped['edificio_bano_encoded'] = le_edificio_bano.fit_transform(df_grouped['edificio_bano'].astype(str))

# Seleccionar las características para la detección de anomalías
features = df_grouped[['edificio_bano_encoded', 'month', 'cantidad_reportes']]

# Entrenar un modelo de Isolation Forest para detectar anomalías en el aumento de reportes
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(features)

# Predecir anomalías
df_grouped['anomaly_score'] = model.decision_function(features)
df_grouped['anomaly'] = model.predict(features)

# Filtrar las anomalías
anomalies = df_grouped[df_grouped['anomaly'] == -1]

# Decodificar los valores a su forma original si es necesario
anomalies['edificio_bano_original'] = le_edificio_bano.inverse_transform(anomalies['edificio_bano_encoded'])

# Imprimir resultados
print("Número de anomalías detectadas:", len(anomalies))
print(anomalies[['edificio_bano_original', 'month', 'cantidad_reportes', 'anomaly_score']])

# También podrías analizar los reportes que tienen "No Aplica" si fuera necesario:
print("\nReportes con 'No Aplica' en edificio_bano:")
print(df_no_aplica[['month', 'tipo_problema', 'gravedad_problema']])

anomalies.to_csv('anomalies_report.csv', index=False)
2