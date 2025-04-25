from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# 假设你已设定好数据库连接
def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD')
    )

@app.route('/api/projects')
def get_projects():
    lang = request.args.get('lang', 'zh')  # 默认中文
    name_column = 'name_zh' if lang == 'zh' else 'name_en'

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(f'''
        SELECT id, {name_column} AS name, area, lat, lng, link FROM projects
    ''')
    rows = cur.fetchall()
    cur.close()
    conn.close()

    projects = [
        {
            'id': row[0],
            'name': row[1],
            'area': row[2],
            'lat': row[3],
            'lng': row[4],
            'link': row[5]
        }
        for row in rows
    ]
    return jsonify(projects)
