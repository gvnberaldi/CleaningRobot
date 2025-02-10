import json
import os
import sys

from flask import Flask, request, jsonify, Response, current_app

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app.cleaning_robot import BaseCleaningRobot, PremiumCleaningRobot
from app.database import Database
from app.map import Map
from app.robot_path import RobotPath

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB limit

my_app = Flask(__name__)

base_cleaning_robot = BaseCleaningRobot()
premium_cleaning_robot = PremiumCleaningRobot()


def check_file_size(file):
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise ValueError('File is too large (max 5MB)')


def set_robot_map(robot, file):
    try:
        check_file_size(file)
        robot.map = Map.load(file)
        if isinstance(robot, PremiumCleaningRobot):
            robot.reset_cleaned_tiles()  # Only reset for premium robot
        return jsonify({'message': 'Map uploaded successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@my_app.route('/set-map', methods=['POST'])
def set_map():
    if 'file' not in request.files:
        return jsonify({'error': 'No map file uploaded'}), 400

    file = request.files['file']
    return set_robot_map(base_cleaning_robot, file)


@my_app.route('/set-map-premium', methods=['POST'])
def set_map_premium():
    if 'file' not in request.files:
        return jsonify({'error': 'No map file uploaded'}), 400

    file = request.files['file']
    return set_robot_map(premium_cleaning_robot, file)


def process_cleaning_request(robot, file):
    if robot.map is None:
        raise ValueError('No map loaded: a map must be loaded before cleaning.')
    # Determine database connection
    database_conn = current_app.config['DATABASE'] if current_app.config['TESTING'] else Database.connect()
    # Load the robot path
    robot.path = RobotPath.load(file)
    robot.database_conn = database_conn
    # Return the cleaning session report
    return json.loads(robot.clean())


@my_app.route('/clean', methods=['POST'])
def clean():
    if 'file' not in request.files:
        return jsonify({'error': 'No actions file uploaded'}), 400

    file = request.files['file']
    try:
        check_file_size(file)
        # Use the helper function to process the cleaning request
        cleaning_session_report = process_cleaning_request(base_cleaning_robot, file)
        return jsonify({'report': cleaning_session_report}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@my_app.route('/clean-premium', methods=['POST'])
def clean_premium():
    if 'file' not in request.files:
        return jsonify({'error': 'No actions file uploaded'}), 400

    file = request.files['file']
    try:
        check_file_size(file)
        # Use the helper function to process the cleaning request
        cleaning_session_report = process_cleaning_request(premium_cleaning_robot, file)
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
