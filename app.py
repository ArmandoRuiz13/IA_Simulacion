from flask import Flask, request, jsonify, redirect
from flasgger import Swagger, swag_from
from predict import predictProblems
from anomalies import detect_anomalies
import pandas as pd



app = Flask(__name__)

app.config['SWAGGER'] = {
    'title': 'Problems Prediction API',
    'description': 'API for predicting problems and analyzing data to find unusual patterns',
    'uiversion': 3
}


# Swagger configuration
swagger = Swagger(app)




@app.route('/')
@swag_from({
    'tags': ['Home'],
    'summary': 'Swagger UI landing page',
    'responses': {
        200: {
            'description': 'Redirect to the Swagger UI',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Redirecting to the Swagger UI'
                    }
                }
                
            }
        }
    }
})
def swagger_ui():
    """Landing page redirects to the Swagger UI.
    ---
    responses:
      200:
        description: Redirect to the Swagger UI
    """
    return redirect('/apidocs/')



@app.route('/api/problems/predict', methods=['GET'])
@swag_from({
    'tags': ['Problems'],
    'summary': 'Prediction for the number of problems in the next 6 months',
    'responses': {
        200: {
            'description': 'Returns the predicted number of problems for the next 6 months',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Results will be displayed here'
                    }
                }
            }
        }
    }
})

def predictProblemsNextMonth():
    return predictProblems("./reportes.csv")

@app.route('/api/anomalies/detect', methods=['POST'])
@swag_from({
    'tags': ['Anomalies'],
    'summary': 'detect anomalies in the data',
    'parameters': [
      {
        'name': 'tipo_edificio',
        'in': 'body',
        'type': 'string',
        'required': True,
      },
    ],
    'responses': {
        200: {
            'description': 'Returns recommendations for the detected anomalies and \
             statistical information',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Anomalies detected'
                    }
                }
                
            }
        }
    }
})

def detectAnomalies():
    tipo_edificio = request.json['tipo_edificio']
    detect_anomalies(tipo_edificio)

    # Cargar el archivo CSV
    df = pd.read_csv('anomalies_report.csv')

    # Convertir el DataFrame a formato JSON
    json_data = df.to_dict(orient='records')

    # Devolver el JSON en la respuesta de la API
    return jsonify(json_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
