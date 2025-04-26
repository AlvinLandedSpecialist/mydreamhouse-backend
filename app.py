from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import db, User, Project
from auth import auth_bp
from projects import project_bp
import os
from config import Config  # 引入配置文件

app = Flask(__name__)
CORS(app)

# --- ✅ 配置 JWT 和数据库 --- 
app.config.from_object(Config)  # 从配置文件加载配置

# 初始化数据库 & JWT
db.init_app(app)

with app.app_context():
    db.create_all()

jwt = JWTManager(app)

# --- 注册蓝图 ---
app.register_blueprint(auth_bp)
app.register_blueprint(project_bp)

# --- 根路径测试 ---
@app.route('/')
def index():
    return "API is working!"

# --- 用户注册接口 ---
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "User already exists"}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User created successfully!"}), 201

# --- 用户登录接口 ---
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Invalid credentials"}), 401

# --- 创建项目接口（需要登录）---
@app.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    current_user = get_jwt_identity()
    data = request.json

    new_project = Project(
        title=data.get('title'),
        content=data.get('content'),
        price=data.get('price'),
        youtube_link=data.get('youtube_link'),
        user_id=current_user
    )

    db.session.add(new_project)
    db.session.commit()
    return jsonify({"msg": "Project created successfully!"}), 201

# --- 获取所有项目（公开） ---
@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.order_by(Project.id.desc()).all()
    return jsonify([p.to_dict() for p in projects]), 200

# --- 启动程序 ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
