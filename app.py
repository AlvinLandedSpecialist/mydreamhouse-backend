from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)   # 允许跨域，前端能 fetch

projects = [
  {"name":"Cyberjaya Project","lat":2.9226,"lng":101.6500,"area":"Cyberjaya","link":"/project/Cyberjaya-Project"},
  {"name":"Banting Project","lat":2.8137,"lng":101.5022,"area":"Banting","link":"/project/Banting-Project"},
  # … 其余项目 …
]

@app.route('/api/projects', methods=['GET'])
def get_projects():
    return jsonify(projects)

if __name__ == '__main__':
    # 生产环境不带 debug=True
    app.run(host='0.0.0.0', port=5000)
