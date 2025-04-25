from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import psycopg2

app = Flask(__name__)
CORS(app)

# 数据库连接函数
def get_db_connection():
    return psycopg2.connect(
        host="dpg-d05g3eruibrs73flp99g-a.singapore-postgres.render.com",
        database="mydreamhouse_db",
        user="mydreamhouse_db_user",
        password="avFhthVgzSBekdpmHhsIvGNpGaoLgHFO",
        port=5432
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
