import json
import os
import sys

from flask import Flask, request, jsonify, Response, current_app

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app.cleaning_robot import BaseCleaningRobot
from app.database import Database
from app.map import Map
from app.robot_path import RobotPath

my_app = Flask(__name__)

base_cleaning_robot = BaseCleaningRobot()


@my_app.route('/set-map', methods=['POST'])
def set_map():
    if 'file' not in request.files:
        return jsonify({'error': 'No map file uploaded'}), 400

    file = request.files['file']
    try:
        base_cleaning_robot.map = Map.load(file)
        return jsonify({'message': 'Map uploaded successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@my_app.route('/clean', methods=['POST'])
def clean():
    if 'file' not in request.files:
        return jsonify({'error': 'No actions file uploaded'}), 400
    if base_cleaning_robot.map is None:
        return jsonify({'error': 'No map loaded: a map must be loaded before cleaning'}), 400
    file = request.files['file']
    try:
        # Determine database connection
        database_conn = current_app.config['DATABASE'] if current_app.config['TESTING'] else Database.connect()
        base_cleaning_robot.path = RobotPath.load(file)
        base_cleaning_robot.database_conn = database_conn
        cleaning_session_report = json.loads(base_cleaning_robot.clean())
        return jsonify({'report': cleaning_session_report}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@my_app.route('/history', methods=['GET'])
def history():
    try:
        database_conn = current_app.config['DATABASE'] if current_app.config['TESTING'] else Database.connect()
        history = database_conn.get_history()
        # Return the CSV as a downloadable response
        return Response(
            history,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment;filename=history.csv'}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    my_app.run(debug=False)
