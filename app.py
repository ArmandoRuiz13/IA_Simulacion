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
    'summary': 'A simple Hello World endpoint',
    'responses': {
        200: {
            'description': 'Returns a Hello World message',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Hello, World!'
                    }
                }
            }
        }
    }
})

def predictProblemsNextMonth():
    return predictProblems()

@app.route('/api/anomalies/detect', methods=['POST'])
@swag_from({
    'tags': ['Anomalies'],
    'summary': 'detect anomalies in the data',
    'parameters': [
      {
        'name': 'tipo_problema',
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
                        'example': 'Redirecting to the Swagger UI'
                    }
                }
                
            }
        }
    }
})

def detectAnomalies():
    # Cargar el archivo CSV
    df = pd.read_csv('anomalies_report.csv')

    # Convertir el DataFrame a formato JSON
    json_data = df.to_dict(orient='records')

    detect_anomalies()

    # Devolver el JSON en la respuesta de la API
    return jsonify(json_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
