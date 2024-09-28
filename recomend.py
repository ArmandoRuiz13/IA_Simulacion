import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from flask import jsonify

# Crear un array vacío de tamaño 15 con valores iniciales None
recomendaciones = [None] * 15

# Asignaciones de recomendaciones basadas en las predicciones y el umbral de gravedad
recomendaciones[0] = "Se recomienda revisar posibles filtraciones menores y realizar mantenimiento preventivo, como el sellado de juntas y mejorar la ventilación."
recomendaciones[6] = "Es recomendable inspeccionar las conexiones eléctricas y cambiar fusibles si es necesario. Un mantenimiento básico ayudará a evitar problemas futuros."
recomendaciones[12] = "Limpia los conductos de ventilación y ajusta las entradas de aire para mejorar el flujo en el área afectada."
recomendaciones[3] = "Revisa estructuras como puertas y ventanas para aplicar reparaciones menores o ajustes que puedan mejorar su funcionalidad."
recomendaciones[9] = "Realiza una revisión básica de los electrodomésticos y reemplaza componentes pequeños si presentan desgaste."

recomendaciones[10] = "Investiga las fuentes de humedad, como filtraciones ocultas o problemas en el sistema de drenaje, y planifica una intervención moderada."
recomendaciones[1] = "Se recomienda inspeccionar el sistema eléctrico a fondo para detectar cortocircuitos o sobrecargas y, de ser necesario, contactar a un profesional."
recomendaciones[7] = "Evalúa los sistemas de ventilación y ajusta la infraestructura si es necesario para mejorar la circulación de aire en los espacios afectados."
recomendaciones[13] = "Realiza una inspección detallada de las estructuras afectadas y considera reparaciones más complejas o sustituciones de partes dañadas."
recomendaciones[4] = "Se recomienda realizar una revisión más exhaustiva de los electrodomésticos y contactar a un técnico especializado si es necesario para evitar daños mayores."

recomendaciones[5] = "Atiende de inmediato posibles inundaciones o filtraciones serias. Se recomienda una inspección profesional para evitar daños estructurales."
recomendaciones[11] = "Contacta urgentemente a un electricista calificado debido al riesgo de fallos eléctricos graves o posibles incendios."
recomendaciones[2] = "Realiza una revisión completa del sistema de ventilación y, si es necesario, planifica una intervención mayor o la instalación de nuevos sistemas."
recomendaciones[8] = "Es urgente intervenir en las estructuras afectadas para evitar riesgos mayores. Se podría requerir una reparación extensa o sustitución completa de las áreas dañadas."
recomendaciones[14] = "Desconecta de inmediato los electrodomésticos involucrados y solicita asistencia técnica, ya que existe riesgo de fallos graves o peligro para los usuarios."


def generateRecomendation(tipo_edificio, tipo_problema, cantidad_reportes):
    # Datos de ejemplo con recomendaciones del 0 al 59
    global recomendaciones

    cantidad_reportes = int(cantidad_reportes)

    data = {
        'cantidad_reportes': [15, 25, 45] * 5,
        'tipo_problema': ['Humedad', 'Eléctrico', 'Ventilación', 'Físico', 'Electrodomésticos'] * 3,
        'recomendacion': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    }

    df = pd.DataFrame(data)

    # Aumentar el conjunto de datos para incluir todas las combinaciones posibles
    df = pd.concat([df] * 50, ignore_index=True)  # Duplicar el dataset

    # Convertir tipo_problema a códigos numéricos
    encoder_problema = LabelEncoder()
    df['tipo_problema'] = encoder_problema.fit_transform(df['tipo_problema'])

    # Aplicar umbrales en función de 'cantidad_reportes'
    def calcular_umbral(cantidad):
        if cantidad > 40:
            return 'Grave'
        elif cantidad > 20:
            return 'Medio'
        else:
            return 'Bajo'
    
    df['umbral_problemas'] = df['cantidad_reportes'].apply(calcular_umbral)

    # Codificar los umbrales (Bajo, Medio, Grave)
    encoder_umbral = LabelEncoder()
    df['umbral_problemas'] = encoder_umbral.fit_transform(df['umbral_problemas'])

    # Variables predictivas y variable objetivo
    X = df[['umbral_problemas', 'tipo_problema']]
    y = df['recomendacion']

    # División de datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Ajuste del clasificador con hiperparámetros ajustados
    classifier = DecisionTreeClassifier(
        max_depth=10,           # Aumentar la profundidad máxima del árbol
        min_samples_split=20,   # Número mínimo de muestras para dividir un nodo
        min_samples_leaf=4,    # Número mínimo de muestras en una hoja
        criterion='entropy',   # Usar la entropía en lugar del índice Gini
        random_state=42
    )
    classifier.fit(X_train, y_train)

    # Función para hacer predicciones
    def predecir_recomendacion(nuevo_umbral_problemas, nuevo_tipo_problema):
        nuevo_umbral_codificado = encoder_umbral.transform([nuevo_umbral_problemas])[0]
        nuevo_problema_codificado = encoder_problema.transform([nuevo_tipo_problema])[0]
        
        nuevo_dato = pd.DataFrame({
            'umbral_problemas': [nuevo_umbral_codificado],
            'tipo_problema': [nuevo_problema_codificado]
        })
        
        # Obtener la predicción
        prediccion = classifier.predict(nuevo_dato)[0]
        return prediccion

    # recomendaciones[predecir_recomendacion(calcular_umbral(cantidad_reportes), tipo_problema)]

    return jsonify(
        {"recomendacion" : recomendaciones[predecir_recomendacion(calcular_umbral(cantidad_reportes), tipo_problema)]})
    # # Probar todas las combinaciones y verificar si falta el número 5
    # recomendaciones = set()

    # for umbral in ['Bajo', 'Medio', 'Grave']:
    #     for problema in ['Humedad', 'Eléctrico', 'Ventilación', 'Físico', 'Electrodomésticos']:
    #         prediccion_clasificador = predecir_recomendacion(umbral, problema)
    #         recomendaciones.add(prediccion_clasificador)
    #         print(f'Umbral: {umbral}, Problema: {problema}, Predicción: {prediccion_clasificador}')

    # # Mostrar todas las recomendaciones únicas obtenidas
    # print(f'Todas las recomendaciones únicas obtenidas: {sorted(recomendaciones)}')

    # # Verificar si falta alguna recomendación
    # missing = [i for i in range(15) if i not in recomendaciones]
    # print(f'Recomendaciones faltantes: {missing}')


