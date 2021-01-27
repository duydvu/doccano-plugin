import os
import logging
from flask import Flask, jsonify, render_template, request as flask_request, send_file

from services.client import refresh_client, Client
from services.sample import handle_request as handle_sample_request
from services.evaluate import handle_request as handle_evaluate_request
from services.download import handle_request as handle_download_request


HOST = '0.0.0.0'
PORT = 5500
debug = False
app = Flask(__name__,
    template_folder='template',
    static_url_path='/static',
    static_folder='static')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/evaluate')
def evaluate():
    return render_template('evaluate.html')


@app.route('/download')
def download():
    return render_template('download.html')


@app.route('/api/sample', methods=['POST'])
def create_sample_test_project():
    try:
        print('Create sample test project')
        refresh_client()
        new_project_id = handle_sample_request(flask_request, Client.doccano_client)
        print(f'Project ID: {new_project_id}')
        return jsonify({
            'status': 'OK',
            'link': f'http://103.113.81.36:8000/projects/{new_project_id}',
        }), 200
    except Exception as e:
        logging.exception(e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/evaluate', methods=['GET'])
def evaluate_test_project():
    try:
        print('Evaluate test project')
        refresh_client()
        return jsonify(handle_evaluate_request(flask_request, Client.doccano_client)), 200
    except Exception as e:
        logging.exception(e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/download', methods=['GET'])
def download_test_project():
    try:
        print('Download test project')
        refresh_client()
        file_name = handle_download_request(flask_request, Client.doccano_client)
        file_path = os.path.join('download', file_name)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logging.exception(e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=debug)
