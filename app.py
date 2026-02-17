import os
import time
import uuid
from flask import Flask, request, jsonify, render_template_string
from flask import Response
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY

HTML_FORM = """
<!doctype html>
<title>Upload new File</title>
<h1>Upload new File (POST /upload)</h1>
<form method=post action="/upload" enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
<p>Get request to /</p>
"""

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
POST_LATENCY = Histogram('post_request_duration_seconds', 'POST request latency',
                         buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10])


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    if request.method == 'POST' and request.path == '/upload':
        latency = time.time() - request.start_time
        POST_LATENCY.observe(latency)

    REQUEST_COUNT.labels(method=request.method, endpoint=request.path, status=response.status_code).inc()
    return response


@app.route('/')
def index():
    return render_template_string(HTML_FORM)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        original_filename = file.filename
        safe_filename = os.path.basename(original_filename)
        unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

        file.save(filepath)

        return jsonify({
            'message': 'File uploaded successfully',
            'filename': original_filename,
            'stored_as': unique_filename,
            'size': os.path.getsize(filepath)
        }), 200

    return jsonify({'error': 'Unknown error'}), 500


@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/metrics')
def metrics():
    return Response(generate_latest(REGISTRY), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)