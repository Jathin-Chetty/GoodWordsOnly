import os
import time
import json
import requests
from flask import Flask, request, jsonify, render_template, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Paths for static/templates
app = Flask(__name__, 
            template_folder='/app/webapp/templates', 
            static_folder='/app/webapp/static')

# Hugging Face Space API URL
HF_API_URL = "https://jathin-ch-goodwordsonly.hf.space/api/predict"

# Use a dedicated session for outbound HF calls.
# By default, requests will honor HTTP(S)_PROXY env vars; in some environments
# that breaks access to external HTTPS endpoints. We disable that by default.
HF_HTTP_TRUST_ENV = os.getenv("HF_HTTP_TRUST_ENV", "false").strip().lower() in ("1", "true", "yes", "y", "on")
HF_SESSION = requests.Session()
HF_SESSION.trust_env = HF_HTTP_TRUST_ENV

# History File (Stored in PVC)
HISTORY_FILE = "/app/data/history.json"

# Metrics
REQUEST_COUNT = Counter(
    'app_request_count', 
    'Application Request Count', 
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Application Request Latency',
    ['method', 'endpoint']
)


def normalize_prediction(raw):
    """Normalize HF response shape to the UI contract."""
    if isinstance(raw, list):
        classes = raw[0] if raw and isinstance(raw[0], list) else raw
    else:
        classes = raw.get('classes', []) if isinstance(raw, dict) else []

    if not classes:
        return {
            'model': '',
            'label': 'UNKNOWN',
            'display_label': 'Unknown',
            'probability': 0.0,
            'classes': []
        }

    sorted_classes = sorted(classes, key=lambda x: x.get('score', 0), reverse=True)
    top = sorted_classes[0]

    return {
        'model': '',
        'label': top.get('label', 'UNKNOWN'),
        'display_label': top.get('display_label', top.get('label', 'Unknown')),
        'probability': float(top.get('score', 0)),
        'classes': [
            {
                'label': c.get('label', 'UNKNOWN'),
                'display_label': c.get('display_label', c.get('label', 'Unknown')),
                'score': float(c.get('score', 0))
            }
            for c in sorted_classes
        ]
    }

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(entry):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    history = load_history()
    # Insert at beginning
    history.insert(0, entry)
    # Keep only last 50 to prevent huge files
    history = history[:50]
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)
    except Exception as e:
        print(f"Error saving history: {e}")

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    resp_time = time.time() - request.start_time
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    # Don't track latency for metrics endpoint to avoid noise
    if request.path != '/metrics':
        REQUEST_LATENCY.labels(request.method, request.path).observe(resp_time)
    return response

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        
        # Forward to Hugging Face
        response = HF_SESSION.post(HF_API_URL, json={'text': text}, timeout=30)
        
        if response.status_code == 200:
            raw_result = response.json()
            result = normalize_prediction(raw_result)
            
            # Save to PVC history
            history_entry = {
                'timestamp': time.time(),
                'text': text,
                'result': result
            }
            save_history(history_entry)
            
            return jsonify(result)
        else:
            return jsonify({'error': f'Hugging Face API Error: {response.text}'}), response.status_code
            
    except requests.exceptions.ProxyError as e:
        return jsonify({
            'error': 'Upstream connection failed (proxy).',
            'details': str(e),
            'hint': 'If you are behind a corporate proxy, set HF_HTTP_TRUST_ENV=true to use it, or unset HTTPS_PROXY/HTTP_PROXY in the runtime.'
        }), 502
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(load_history())

if __name__ == '__main__':
    # Local testing will store data in current dir
    if not os.path.exists('/app/data'):
        HISTORY_FILE = "history.json"
        app.template_folder = '../webapp/templates'
        app.static_folder = '../webapp/static'
    app.run(debug=True, host='0.0.0.0', port=8080)
