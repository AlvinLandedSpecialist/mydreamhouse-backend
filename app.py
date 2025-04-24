from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

projects = [
    {"name": "Cyberjaya Project", "lat": 2.9226, "lng": 101.6500, "area": "Cyberjaya", "link": "/project/Cyberjaya-Project"},
    {"name": "Banting Project", "lat": 2.8137, "lng": 101.5022, "area": "Banting", "link": "/project/Banting-Project"},
    {"name": "Kajang Project", "lat": 2.9927, "lng": 101.7871, "area": "Kajang", "link": "/project/Kajang-Project"},
    {"name": "Bangi Project", "lat": 2.9448, "lng": 101.7821, "area": "Bangi", "link": "/project/Bangi-Project"},
    {"name": "Semenyih Project", "lat": 2.9481, "lng": 101.8449, "area": "Semenyih", "link": "/project/Semenyih-Project"},
    {"name": "Puchong Project", "lat": 3.0322, "lng": 101.6167, "area": "Puchong", "link": "/project/Puchong-Project"},
    {"name": "Klang Project", "lat": 3.0339, "lng": 101.4455, "area": "Klang", "link": "/project/Klang-Project"},
    {"name": "Shah Alam Project", "lat": 3.0738, "lng": 101.5183, "area": "Shah Alam", "link": "/project/Shah-Alam-Project"},
    {"name": "Rawang Project", "lat": 3.3181, "lng": 101.5767, "area": "Rawang", "link": "/project/Rawang-Project"},
    {"name": "Sungai Buloh Project", "lat": 3.2131, "lng": 101.5778, "area": "Sungai Buloh", "link": "/project/Sungai-Buloh-Project"}
]

@app.route('/api/projects')
def get_projects():
    return jsonify(projects)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
