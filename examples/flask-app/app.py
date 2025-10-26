"""Example Flask application for testing app-publisher."""

from flask import Flask, render_template_string, jsonify
from datetime import datetime
import random

app = Flask(__name__)

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Example App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .card {
            background-color: white;
            padding: 20px;
            margin: 10px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
        }
        .metric h3 {
            margin: 0;
            font-size: 2em;
        }
        .metric p {
            margin: 5px 0 0 0;
            opacity: 0.9;
        }
        button {
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #2980b9;
        }
        #data {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Example Flask Application</h1>
        <p>Deployed using app-publisher</p>
    </div>

    <div class="metrics">
        <div class="metric">
            <h3>{{ users }}</h3>
            <p>Active Users</p>
        </div>
        <div class="metric">
            <h3>{{ requests }}</h3>
            <p>Total Requests</p>
        </div>
        <div class="metric">
            <h3>{{ uptime }}</h3>
            <p>Uptime (hours)</p>
        </div>
    </div>

    <div class="card">
        <h2>API Endpoint Test</h2>
        <button onclick="fetchData()">Fetch Random Data</button>
        <div id="data"></div>
    </div>

    <div class="card">
        <h2>About This Application</h2>
        <p>This is a sample Flask application that demonstrates the app-publisher deployment tool.</p>
        <p><strong>Current Time:</strong> {{ current_time }}</p>
        <p><strong>Status:</strong> <span style="color: green;">✓ Running</span></p>
    </div>

    <script>
        async function fetchData() {
            const response = await fetch('/api/data');
            const data = await response.json();
            document.getElementById('data').innerHTML =
                '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Render the main page."""
    return render_template_string(
        HTML_TEMPLATE,
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        users=random.randint(100, 999),
        requests=random.randint(1000, 9999),
        uptime=random.randint(1, 720)
    )


@app.route('/api/data')
def get_data():
    """API endpoint that returns random data."""
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'random_number': random.randint(1, 100),
        'status': 'success',
        'data': [
            {'id': i, 'value': random.randint(1, 100)}
            for i in range(5)
        ]
    })


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
