from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from models import db
from auth import auth_bp
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def home():
    return "Welcome to the Home Page"

# CORS 配置
CORS(app)

# 数据库配置
db.init_app(app)
migrate = Migrate(app, db)

# JWT 配置
jwt = JWTManager(app)

# 注册蓝图
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
