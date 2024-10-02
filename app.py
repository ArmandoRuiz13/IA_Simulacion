from flask import Flask, request, jsonify, redirect
from flasgger import Swagger, swag_from
from predict import predict_problems
from anomalies import detect_anomalies
from flask_cors import CORS
from top10 import top10Reported
import pandas as pd
from reports import getReports
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from recomend import generateRecomendation





app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:1aF3E-4*36B4Cg24Da2AGA324Gf2cgaf@roundhouse.proxy.rlwy.net:15260/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SWAGGER'] = {
    'title': 'Problems Prediction API',
    'description': 'API for predicting problems and analyzing data to find unusual patterns',
    'uiversion': 3
}

# Initialize SQLAlchemy
db = SQLAlchemy(app)


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

    # Execute the query to fetch all rows from user_problema table
    # result = db.session.execute(text('SELECT * FROM user_problema;'))
    
    # # Fetch all rows
    # rows = result.fetchall()

    # # If rows exist, print them and return a response
    # reports = []
    # for row in rows:
    #     report = dict(row._mapping)  #  # Convert the row to a dictionary for easier processing
    #     reports.append(report)
    #     print(report)

    return redirect('/apidocs/')



# @app.route('/api/problems/top-ten-reported-places', methods=['GET'])
# @swag_from({
#     'tags': ['Problems'],
#     'summary': 'Top ten places with the most reported problems',
#     'responses': {
#         200: {
#             'description': 'Returns the top ten places with the most reported problems',
#             'schema': {
#                 'type': 'object',
#                 'properties': {
#                     'message': {
#                         'type': 'string',
#                         'example': 'Results will be displayed here'
#                     }
#                 }
#             }
#         }
#     }
# })


@app.route('/api/problems', methods=['GET'])
@swag_from({
    'tags': ['Problems'],
    'summary': 'Retrieve problems grouped by the parameters given',
    'parameters': [
        {
            'name': 'group_month',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Send true to group the problems by month'
        },
        {
            'name': 'last_13_months',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Send true of the last 13 months'
        },
        {
            'name': 'group_problem_type',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Send true to group the problems by type'
        },
        {
            'name': 'group_building_type',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Send true to group the problems by building type'
        },
        {
            'name': 'problem_type',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter the problems by the type given'
        },
        {
            'name': 'building_type',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter the problems by the building type given'
        },
        {
            'name': 'month',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter the problems by the month given'

        }
    ],
    'responses': {
        200: {
            'description': 'Gets the problems grouped by the parameters given',
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

def getProblems():
    group_month = request.args.get('group_month')  # Get the value of 'param1'
    last_13_months = request.args.get('last_13_months')  # Get the value of 'param1'
    group_problem_type = request.args.get('group_problem_type')  # Get the value of 'param2'
    group_building_type = request.args.get('group_building_type')
    problem_type = request.args.get('problem_type')
    building_type = request.args.get('building_type')
    month = request.args.get('month')
    return getReports(group_month, group_problem_type, group_building_type, problem_type, building_type, last_13_months, month)

@app.route('/api/problems/top-ten-reported-places', methods=['GET'])
@swag_from({
    'tags': ['Problems'],
    'summary': 'Top ten places with the most reported problems',
    'responses': {
        200: {
            'description': 'Returns the top ten places with the most reported problems',
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

def topTenReportedPlaces():

    return top10Reported("./reportes.csv")


@app.route('/api/problems/simulation', methods=['GET'])
@swag_from({
    'tags': ['Problems'],
    'summary': 'Top ten places with the most reported problems',
    'parameters': [
        { 'name': 'tipo_edificio',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Type of building to simulate',
        },
        {
            'name': 'cantidad_reportes',
            'in': 'query',
            'type': 'integer',
            'required': True,
            'description': 'Number of reports to simulate',
        },
        {
            'name': 'tipo_problema',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Type of problem to simulate',
        }
    ],
    'responses': {
        200: {
            'description': 'Returns the top ten places with the most reported problems',
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

def simulation():
    tipo_edificio = request.args.get('tipo_edificio')  # Get the value of 'param1'
    cantidad_reportes = request.args.get('cantidad_reportes')  # Get the value of 'param1'
    tipo_problema = request.args.get('tipo_problema')  # Get the value of 'param1'

    return generateRecomendation(tipo_edificio, tipo_problema, cantidad_reportes)


@app.route('/api/problems/predict', methods=['GET'])
@swag_from({
    'tags': ['Problems'],
    'summary': 'Prediction for the number of problems in the next 6 months',
    'parameters': [
        {
            'name': 'month',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Send true to group the problems by month'
        },
        {
            'name': 'problem_type',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter the problems by the type given'
        },
        {
            'name': 'building_type',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter the problems by the building type given'
        },
        {
            'name': 'forecast_steps',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Number of months to predict'
        }
    ],
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
    month = request.args.get('month')  # Get the value of 'param1'
    problem_type = request.args.get('problem_type')  # Get the value of 'param1'
    building_type = request.args.get('building_type')  # Get the value of 'param1'
    forecast_steps = request.args.get('forecast_steps') # Get the value of 'param1'
    return predict_problems(month, problem_type, building_type, forecast_steps)

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
      }
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
    tipo_problema = request.json['tipo_problema']
    detect_anomalies(tipo_problema, '11', '2023')

    # Cargar el archivo CSV
    df = pd.read_csv('anomalies_report.csv')

    # Convertir el DataFrame a formato JSON
    json_data = df.to_dict(orient='records')

    # Devolver el JSON en la respuesta de la API
    return jsonify(json_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
