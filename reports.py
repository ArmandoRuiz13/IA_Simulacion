import pandas as pd
from flask import jsonify
from datetime import datetime

def getReports(group_month=True, group_problem_type=False, group_building_type=False, problem_type=False, building_type=False, last_13_months=False, month=False):
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

        # Filtrar por los últimos 13 meses dinámicamente si se especifica
        if last_13_months:
            # Obtener el año actual
            current_year = pd.Timestamp.now(tz='America/Mexico_City').year

            # Definir el rango dinámico: desde enero del año pasado hasta enero del año actual
            start_date = pd.Timestamp(f'{current_year - 1}-01-01', tz='America/Mexico_City')
            end_date = pd.Timestamp(f'{current_year}-01-31', tz='America/Mexico_City')

            # Filtrar los reportes en este rango de fechas
            df = df[(df['fecha'] >= start_date) & (df['fecha'] <= end_date)]

        # Extraer 'mes' de la columna 'fecha' y convertir Period a string
        df['mes'] = df['fecha'].dt.to_period('M').astype(str)
    

    if group_problem_type:
        group_by_params.append('tipo_problema')

    if group_building_type:
        group_by_params.append('tipo_edificio')

    

    df_grouped = df
    # Agrupar los datos y contar la cantidad de reportes



    if building_type:
        df_grouped = df_grouped[df_grouped['tipo_edificio'] == building_type]
        if building_type == 'Departamento':
            group_by_params.append('tipo_departamento')
            group_by_params.append('tipo_edificio_departamento')
        elif building_type == 'Academico':
            group_by_params.append('numero_salon')
            group_by_params.append('letra_edificio')
        elif building_type == 'Baños':
            group_by_params.append('edificio_bano')
            group_by_params.append('tipo_bano')
            # group_by_params.append('piso_bano')
        elif building_type == 'Áreas comunes':
            group_by_params.append('tipo_area')



    if group_by_params.__len__() != 0:
        df_grouped = df.groupby(group_by_params).size().reset_index(name='cantidad_reportes')


    if problem_type:
        df_grouped = df_grouped[df_grouped['tipo_problema'] == problem_type]

    if month:
        df_grouped = df_grouped[df_grouped['mes'] == month]
        print(df_grouped)

  
    # Sort the data by 'cantidad_reportes' in descending order
    if group_problem_type:
        df_grouped = df_grouped.sort_values(by='tipo_problema', ascending=False)

    # Convertir a JSON
    result = df_grouped.to_dict(orient='records')

    # Retornar el resultado en formato JSON
    return jsonify(result)
