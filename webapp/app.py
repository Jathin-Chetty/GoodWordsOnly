import os
import sys
import time

# Ensure the app runs from the parent directory so that 'src' can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
os.chdir(parent_dir)
sys.path.append(parent_dir)

from flask import Flask, request, jsonify, render_template, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from src.predict import predict

app = Flask(__name__, 
            template_folder=os.path.join(current_dir, 'templates'), 
            static_folder=os.path.join(current_dir, 'static'))

# Metrics
REQUEST_COUNT = Counter(
    'app_request_count', 
    'Application Request Count', 
    ['method', 'endpoint', 'http_status']
)

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    return response

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    
    text = data['text'].strip()
    if not text:
         return jsonify({"error": "Text cannot be empty"}), 400
         
    try:
        result = predict(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask application...")
    print(f"Running from directory: {os.getcwd()}")
    app.run(debug=True, host='0.0.0.0', port=7860)

