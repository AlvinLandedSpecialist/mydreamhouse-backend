from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from auth import auth_bp
from projects import project_bp  # 导入项目蓝图
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # 确保设置一个安全的密钥

# CORS 配置
CORS(app)

# 数据库配置
db.init_app(app)

# JWT 配置
jwt = JWTManager(app)

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(project_bp)  # 注册项目蓝图

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
