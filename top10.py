import pandas as pd
from flask import jsonify
import locale

def top10Reported(csv_file_path):
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

    # Agrupar por tipo de edificio
    def group_by_location(row):
        if row['tipo_edificio'] == 'Academico':
            return f"{row['letra_edificio']}-{row['numero_salon']}"
        elif row['tipo_edificio'] == 'Baños':
            return f"{row['edificio_bano']}-{row['tipo_bano']}-{row['piso_bano']}"
        elif row['tipo_edificio'] == 'Áreas comunes':
            return row['tipo_area']
        elif row['tipo_edificio'] == 'Departamento':
            return f"{row['tipo_departamento']}-{row['tipo_edificio_departamento']}"
        else:
            return 'Otro'

    df['ubicacion_agrupada'] = df.apply(group_by_location, axis=1)

    # Contar reportes por cada ubicación agrupada
    reportes_por_ubicacion = df.groupby('ubicacion_agrupada').size().sort_values(ascending=False)

    # Tomar los 10 lugares más reportados
    top_10_ubicaciones = reportes_por_ubicacion.head(10)

    # Serializar los datos en formato JSON
    forecast_data = {
        "top_10": [{"ubicacion": str(ubicacion), "reportes": int(reportes)} for ubicacion, reportes in top_10_ubicaciones.items()]
    }

    # Retornar la respuesta en formato JSON
    return jsonify(forecast_data)

