import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

def detect_anomalies():
    # Cargar y preparar los datos
    df = pd.read_csv('reportes.csv', na_values=['', ' ', 'NA', 'null'])
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha'])
    df['fecha'] = df['fecha'].dt.tz_convert('America/Mexico_City')
    df['month'] = df['fecha'].dt.month
    df['day_of_week'] = df['fecha'].dt.dayofweek
    le_edificio = LabelEncoder()
    df['letra_edificio'] = le_edificio.fit_transform(df['letra_edificio'].astype(str))

    features = df[['month', 'day_of_week', 'letra_edificio']]
    model = IsolationForest(contamination=0.01, random_state=42)
    model.fit(features)

    df['anomaly_score'] = model.decision_function(features)
    df['anomaly'] = model.predict(features)

    anomalies = df[df['anomaly'] == -1]
    anomalies.to_csv('anomalies_report.csv', index=False)
    
    return anomalies

if __name__ == "__main__":
    detect_anomalies()
