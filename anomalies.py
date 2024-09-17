import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

def detect_anomalies(tipo_edificio):
    if tipo_edificio == 'Academico':

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
        df['letra_edificio'].fillna('No Aplica', inplace=True)
        df['gravedad_problema'].fillna('Moderada', inplace=True)  # Ejemplo de cómo llenar gravedad_problema
        df['tipo_problema'].fillna('No Aplica', inplace=True)

        # Separar los reportes con "No Aplica" en letra_edificio
        df_no_aplica = df[df['letra_edificio'] == 'No Aplica']
        df_valid = df[df['letra_edificio'] != 'No Aplica']

        df_no_aplica = df_no_aplica[df_no_aplica['tipo_problema'] != 'No Aplica']
        df_valid = df_valid[df_valid['tipo_problema'] != 'No Aplica']

        # Agrupar los reportes válidos (con letra de edificio) por letra del edificio, mes y gravedad_problema
        df_grouped = df_valid.groupby(['letra_edificio', 'gravedad_problema', 'tipo_problema', 'year', 'month']).size().reset_index(name='cantidad_reportes')

        # Preparar los datos para la detección de anomalías
        le_tipo_problema = LabelEncoder()
        df_grouped['tipo_problema_encoded'] = le_tipo_problema.fit_transform(df_grouped['tipo_problema'].astype(str))

        le_letra_edificio = LabelEncoder()
        df_grouped['letra_edificio_encoded'] = le_letra_edificio.fit_transform(df_grouped['letra_edificio'].astype(str))

        le_gravedad_problema = LabelEncoder()
        df_grouped['gravedad_problema_encoded'] = le_gravedad_problema.fit_transform(df_grouped['gravedad_problema'].astype(str))

        # Seleccionar las características para la detección de anomalías, incluyendo gravedad_problema
        features = df_grouped[['letra_edificio_encoded', 'gravedad_problema_encoded', 'year', 'month', 'cantidad_reportes', 'tipo_problema_encoded']]

        # Entrenar un modelo de Isolation Forest para detectar anomalías en el aumento de reportes
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(features)

        # Predecir anomalías
        df_grouped['anomaly_score'] = model.decision_function(features)
        df_grouped['anomaly'] = model.predict(features)

        # Filtrar las anomalías
        anomalies = df_grouped[df_grouped['anomaly'] == -1]

        # Decodificar los valores a su forma original si es necesario
        anomalies['letra_edificio_original'] = le_letra_edificio.inverse_transform(anomalies['letra_edificio_encoded'])
        anomalies['gravedad_problema_original'] = le_gravedad_problema.inverse_transform(anomalies['gravedad_problema_encoded'])
        anomalies['tipo_problema_original'] = le_tipo_problema.inverse_transform(anomalies['tipo_problema_encoded'])

        # Imprimir resultados
        print("Número de anomalías detectadas:", len(anomalies))
        print(anomalies[['letra_edificio_original', 'gravedad_problema_original', 'tipo_problema_original', 'year', 'month', 'cantidad_reportes', 'anomaly_score']])

        # Análisis e interpretación de las anomalías
        print("\nAnálisis e Interpretación de Anomalías:")

        for _, row in anomalies.iterrows():
            edificio = row['letra_edificio_original']
            gravedad = row['gravedad_problema_original']
            tipo_problema = row['tipo_problema_original']
            mes = row['month']
            anio = row['year']
            cantidad_reportes = row['cantidad_reportes']
            score = row['anomaly_score']
            
            # Obtener datos históricos para el edificio, gravedad y mes
            historial = df_grouped[(df_grouped['tipo_problema'] == tipo_problema) & (df_grouped['letra_edificio'] == edificio) & (df_grouped['gravedad_problema'] == gravedad) & (df_grouped['month'] == mes)]
            
            if not historial.empty:
                historial_mean = historial['cantidad_reportes'].mean()
                historial_std = historial['cantidad_reportes'].std()
                # Obtener datos del mes pasado para comparación
                mes_pasado = mes - 1 if mes > 1 else 12
                anio_pasado = anio if mes > 1 else anio - 1
                historial_mes_pasado = df_grouped[(df_grouped['tipo_problema'] == tipo_problema) & (df_grouped['letra_edificio'] == edificio) & (df_grouped['gravedad_problema'] == gravedad) & (df_grouped['month'] == mes_pasado) & (df_grouped['year'] == anio_pasado)]
                
                if not historial_mes_pasado.empty:
                    promedio_mes_pasado = historial_mes_pasado['cantidad_reportes'].mean()
                    porcentaje_cambio_mes_pasado = ((cantidad_reportes - promedio_mes_pasado) / promedio_mes_pasado) * 100
                else:
                    promedio_mes_pasado = None
                    porcentaje_cambio_mes_pasado = None
                
                # Interpretación del aumento/disminución
                aumento_disminucion_hist = cantidad_reportes - historial_mean
                porcentaje_cambio_hist = ((cantidad_reportes - historial_mean) / historial_mean) * 100
                
                if cantidad_reportes > historial_mean + 2 * historial_std:
                    interpretacion = 'Aumento significativo en el número de reportes.'
                elif cantidad_reportes < historial_mean - 2 * historial_std:
                    interpretacion = 'Disminución significativa en el número de reportes.'
                else:
                    interpretacion = 'El número de reportes es inusual pero no extremo.'
                
                if promedio_mes_pasado is not None:
                    if cantidad_reportes > promedio_mes_pasado:
                        comparacion_mes_pasado = f'Aumento del {porcentaje_cambio_mes_pasado:.2f}% en comparación con el mes pasado.'
                    else:
                        comparacion_mes_pasado = f'Disminución del {abs(porcentaje_cambio_mes_pasado):.2f}% en comparación con el mes pasado.'
                else:
                    comparacion_mes_pasado = 'No hay datos del mes pasado para comparación.'

                print(f"\nEdificio: {edificio}")
                print(f"Gravedad del Problema: {gravedad}")
                print(f"Año: {anio}")
                print(f"Mes: {mes}")
                print(f"Cantidad de Reportes: {cantidad_reportes}")
                print(f"Score de Anomalía: {score}")
                print(f"Promedio Histórico: {historial_mean:.2f}")
                print(f"Interpretación: {interpretacion}")
                print(f"Comparación con el mes pasado: {comparacion_mes_pasado}")
            else:
                print(f"\nNo hay datos históricos suficientes para el edificio {edificio} en el mes {mes}.")

        # También podrías analizar los reportes que tienen "No Aplica" si fuera necesario:
        print("\nReportes con 'No Aplica' en letra del edificio:")
        print(df_no_aplica[['month', 'tipo_problema', 'gravedad_problema']])

        # Guardar anomalías en un archivo CSV
        anomalies.to_csv('anomalies_report.csv', index=False)


    elif(tipo_edificio == 'Baños'):
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

    elif(tipo_edificio == 'Áreas comunes'):
        
         # Cargar y preparar el dataset
        df = pd.read_csv('reportes.csv', na_values=['', ' ', 'NA', 'null'])

        # Convertir la columna de fecha a datetime
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df = df.dropna(subset=['fecha'])
        df['fecha'] = df['fecha'].dt.tz_convert('America/Mexico_City')

        # Extraer el mes y el día de la semana
        df['month'] = df['fecha'].dt.month
        df['day_of_week'] = df['fecha'].dt.dayofweek

        # Llenar los valores faltantes en 'tipo_area'
        df['tipo_area'].fillna('No Aplica', inplace=True)

        # Separar los reportes con "No Aplica" en tipo_area
        df_no_aplica = df[df['tipo_area'] == 'No Aplica']
        df_valid = df[df['tipo_area'] != 'No Aplica']

        # Agrupar los reportes válidos (con tipo_area) por tipo_area y mes
        df_grouped = df_valid.groupby(['tipo_area', 'month']).size().reset_index(name='cantidad_reportes')

        # Preparar los datos para la detección de anomalías
        le_tipo_area = LabelEncoder()
        df_grouped['tipo_area_encoded'] = le_tipo_area.fit_transform(df_grouped['tipo_area'].astype(str))

        # Seleccionar las características para la detección de anomalías
        features = df_grouped[['tipo_area_encoded', 'month', 'cantidad_reportes']]

        # Entrenar un modelo de Isolation Forest para detectar anomalías en el aumento de reportes
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(features)

        # Predecir anomalías
        df_grouped['anomaly_score'] = model.decision_function(features)
        df_grouped['anomaly'] = model.predict(features)

        # Filtrar las anomalías
        anomalies = df_grouped[df_grouped['anomaly'] == -1]

        # Decodificar los valores a su forma original si es necesario
        anomalies['tipo_area_original'] = le_tipo_area.inverse_transform(anomalies['tipo_area_encoded'])

        # Imprimir resultados
        print("Número de anomalías detectadas:", len(anomalies))
        print(anomalies[['tipo_area_original', 'month', 'cantidad_reportes', 'anomaly_score']])

        # También podrías analizar los reportes que tienen "No Aplica" si fuera necesario:
        print("\nReportes con 'No Aplica' en tipo_area:")
        print(df_no_aplica[['month', 'tipo_problema', 'gravedad_problema']])

        anomalies.to_csv('anomalies_report.csv', index=False)

        
    elif tipo_edificio == 'Departamento':
        # Cargar y preparar el dataset
        df = pd.read_csv('reportes.csv', na_values=['', ' ', 'NA', 'null'])

        # Convertir la columna de fecha a datetime
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df = df.dropna(subset=['fecha'])
        df['fecha'] = df['fecha'].dt.tz_convert('America/Mexico_City')

        # Extraer el mes y el día de la semana
        df['month'] = df['fecha'].dt.month
        df['day_of_week'] = df['fecha'].dt.dayofweek

        # Llenar los valores faltantes en 'tipo_edificio_departamento'
        df['tipo_edificio_departamento'].fillna('No Aplica', inplace=True)

        # Separar los reportes con "No Aplica" en tipo_edificio_departamento
        df_no_aplica = df[df['tipo_edificio_departamento'] == 'No Aplica']
        df_valid = df[df['tipo_edificio_departamento'] != 'No Aplica']


        # Agrupar los reportes válidos (con tipo_edificio_departamento) por tipo_edificio_departamento y mes
        df_grouped = df_valid.groupby(['tipo_edificio_departamento', 'month']).size().reset_index(name='cantidad_reportes')

        # Preparar los datos para la detección de anomalías
        le_tipo_edificio_departamento = LabelEncoder()
        df_grouped['tipo_edificio_departamento_encoded'] = le_tipo_edificio_departamento.fit_transform(df_grouped['tipo_edificio_departamento'].astype(str))

        # Seleccionar las características para la detección de anomalías
        features = df_grouped[['tipo_edificio_departamento_encoded', 'month', 'cantidad_reportes']]

        # Entrenar un modelo de Isolation Forest para detectar anomalías en el aumento de reportes
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(features)

        # Predecir anomalías
        df_grouped['anomaly_score'] = model.decision_function(features)
        df_grouped['anomaly'] = model.predict(features)

        # Filtrar las anomalías
        anomalies = df_grouped[df_grouped['anomaly'] == -1]

        # Decodificar los valores a su forma original si es necesario
        anomalies['tipo_edificio_departamento_original'] = le_tipo_edificio_departamento.inverse_transform(anomalies['tipo_edificio_departamento_encoded'])

        # Imprimir resultados
        print("Número de anomalías detectadas:", len(anomalies))
        print(anomalies[['tipo_edificio_departamento_original', 'month', 'cantidad_reportes', 'anomaly_score']])

        # También podrías analizar los reportes que tienen "No Aplica" si fuera necesario:
        print("\nReportes con 'No Aplica' en tipo_edificio_departamento:")
        print(df_no_aplica[['month', 'tipo_problema', 'gravedad_problema']])

        # Guardar las anomalías en un archivo CSV
        anomalies.to_csv('anomalies_report.csv', index=False)
    else:
        print("Tipo de edificio no válido. Por favor, selecciona 'Academico', 'Baños' o 'Áreas comunes'.")
