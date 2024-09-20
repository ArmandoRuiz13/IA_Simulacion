import pandas as pd
from flask import jsonify

def getReports(group_month=True, group_problem_type=False, group_building_type=False, problem_type=False, building_type=False):
    # Cargar y preparar el dataset
    df = pd.read_csv('reportes.csv', na_values=['', ' ', 'NA', 'null'])
    
    group_by_params = []

    if group_month:
        group_by_params.append('mes')
        fecha = pd.to_datetime(df['fecha'], errors='coerce')

        df['fecha'] = fecha
        df.dropna(subset=['fecha'], inplace=True)

        # Ensure that 'fecha' is timezone-aware and convert to America/Mexico_City
        if df['fecha'].dt.tz is None:
            df['fecha'] = df['fecha'].dt.tz_localize('UTC').dt.tz_convert('America/Mexico_City')
        else:
            df['fecha'] = df['fecha'].dt.tz_convert('America/Mexico_City')

        # Extract group_month from 'fecha' and convert Period to string
        df['mes'] = df['fecha'].dt.to_period('M').astype(str)

    if group_problem_type:
        group_by_params.append('tipo_problema')


    if group_building_type:
        group_by_params.append('tipo_edificio')

    # Agrupar los datos y contar la cantidad de reportes
    df_grouped = df.groupby(group_by_params).size().reset_index(name='cantidad_reportes')

    if problem_type:
        df_grouped = df_grouped[df_grouped['tipo_problema'] == problem_type]

    if building_type:
        df_grouped = df_grouped[df_grouped['tipo_edificio'] == building_type]

    # Sort the data by 'cantidad_reportes' in descending order

    df_grouped = df_grouped.sort_values(by='tipo_problema', ascending=False)

    # Convertir a JSON
    result = df_grouped.to_dict(orient='records')

    # Retornar el resultado en formato JSON
    return jsonify(result)
