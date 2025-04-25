from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import db, User, Project
from auth import auth_bp
from projects import project_bp
import os

app = Flask(__name__)
CORS(app)

# --- ✅ 配置 JWT 密钥 ---
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your_fallback_secret_key')

# --- ✅ 配置数据库 URI（Render PostgreSQL）---
uri = os.environ.get('DATABASE_URL')  # Render 会提供 DATABASE_URL
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///local.db'  # 本地开发 fallback
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- 初始化数据库 & JWT ---
db.init_app(app)
jwt = JWTManager(app)

# --- 注册蓝图 ---
app.register_blueprint(auth_bp)
app.register_blueprint(project_bp)

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

# --- 创建项目接口 ---
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

# --- 更新项目接口 ---
@app.route('/projects/<int:id>', methods=['PUT'])
@jwt_required()
def update_project(id):
    current_user = get_jwt_identity()
    project = Project.query.get_or_404(id)

    if project.user_id != current_user:
        return jsonify({"msg": "Not authorized to update this project"}), 403

    data = request.json
    project.title = data.get('title', project.title)
    project.content = data.get('content', project.content)
    project.price = data.get('price', project.price)
    project.youtube_link = data.get('youtube_link', project.youtube_link)

    db.session.commit()
    return jsonify({"msg": "Project updated successfully!"}), 200

# --- 启动程序 ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
