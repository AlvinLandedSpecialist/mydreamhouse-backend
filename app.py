from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import db, User, Project
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

# 用户注册接口
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    
    # 验证用户是否存在
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "User already exists"}), 400
    
    user = User(username=username)
    user.set_password(password)  # 假设你在 User 模型里有 set_password 方法
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"msg": "User created successfully!"}), 201

# 用户登录接口
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    # 验证用户（你可以根据自己的用户表验证）
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):  # 假设你有密码校验方法
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Invalid credentials"}), 401

# 项目创建接口
@app.route('/projects', methods=['POST'])
@jwt_required()  # 需要 JWT 认证
def create_project():
    current_user = get_jwt_identity()  # 获取当前登录的用户
    title = request.json.get('title')
    content = request.json.get('content')
    price = request.json.get('price')
    youtube_link = request.json.get('youtube_link')
    
    new_project = Project(
        title=title,
        content=content,
        price=price,
        youtube_link=youtube_link,
        user_id=current_user  # 将用户ID关联到项目
    )
    
    db.session.add(new_project)
    db.session.commit()
    
    return jsonify({"msg": "Project created successfully!"}), 201

# 项目更新接口
@app.route('/projects/<int:id>', methods=['PUT'])
@jwt_required()
def update_project(id):
    current_user = get_jwt_identity()
    project = Project.query.get_or_404(id)
    
    if project.user_id != current_user:
        return jsonify({"msg": "You are not authorized to edit this project."}), 403

    project.title = request.json.get('title', project.title)
    project.content = request.json.get('content', project.content)
    project.price = request.json.get('price', project.price)
    project.youtube_link = request.json.get('youtube_link', project.youtube_link)
    
    db.session.commit()
    
    return jsonify({"msg": "Project updated successfully!"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
