import os
import sys

from flask import Flask, request, jsonify, Response, current_app

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app.cleaning_robot import BaseCleaningRobot
from app.database import Database
from app.map import Map
from app.robot_path import RobotPath
from app import config

my_app = Flask(__name__)


@my_app.route('/set-map', methods=['POST'])
def set_map():
    if 'file' not in request.files:
        return jsonify({'error': 'No map file uploaded'}), 400

    file = request.files['file']
    try:
        config.map = Map.load(file)
        return jsonify({'message': 'Map uploaded successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@my_app.route('/clean', methods=['POST'])
def clean():
    if 'file' not in request.files:
        return jsonify({'error': 'No actions file uploaded'}), 400

    if config.map is None:
        return jsonify({'error': 'No map loaded: a map must be loaded before cleaning'}), 400

    file = request.files['file']
    try:
        if current_app.config['TESTING']:
            database_conn = current_app.config['DATABASE']
        else:
            database_conn = Database.connect()
        cleaning_robot = BaseCleaningRobot(map=config.map, path=RobotPath.load(file), database_conn=database_conn)
        cleaning_session_report = cleaning_robot.clean()
        if current_app.config['TESTING']:
            Database.connect().clean()
        return jsonify({
            'report': cleaning_session_report
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@my_app.route('/history', methods=['GET'])
def history():
    if current_app.config['TESTING']:
        database_conn = current_app.config['DATABASE']
    else:
        database_conn = Database.connect()

    history = database_conn.get_history()
    # Return the CSV as a downloadable response
    return Response(
        history,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=history.csv'}
    )


if __name__ == '__main__':
    my_app.run(debug=True)
