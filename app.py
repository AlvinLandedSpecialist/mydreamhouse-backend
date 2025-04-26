from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.utils import secure_filename
import os

from models import db, User, Project, ProjectImage
from config import Config

app = Flask(__name__)
CORS(app)

# --- 配置 ---
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = 'uploads/photos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- 初始化 ---
db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

# --- 根目录测试 ---
@app.route('/')
def index():
    return "API is working!"

# --- 静态访问上传图片 ---
@app.route('/uploads/photos/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- 注册 ---
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

# --- 登录 ---
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Invalid credentials"}), 401

# --- 创建项目（封面+附加图片上传）---
@app.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    current_user = get_jwt_identity()

    title = request.form.get('title')
    content = request.form.get('content')
    price = request.form.get('price')
    youtube_link = request.form.get('youtube_link')

    if not all([title, content, price]):
        return jsonify({"msg": "Missing fields"}), 400

    # 保存封面图
    cover_photo = request.files.get('cover_photo')
    cover_photo_url = None
    if cover_photo:
        filename = secure_filename(cover_photo.filename)
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cover_photo.save(cover_path)
        cover_photo_url = f"/uploads/photos/{filename}"

    # 保存项目
    project = Project(
        title=title,
        content=content,
        price=price,
        youtube_link=youtube_link,
        user_id=current_user,
        cover_photo_url=cover_photo_url
    )
    db.session.add(project)
    db.session.commit()

    # 保存附加照片
    additional_photos = request.files.getlist('additional_photos')
    for photo in additional_photos:
        if photo:
            filename = secure_filename(photo.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(path)
            photo_url = f"/uploads/photos/{filename}"

            project_image = ProjectImage(project_id=project.id, image_url=photo_url)
            db.session.add(project_image)

    db.session.commit()

    return jsonify({"msg": "Project created successfully!"}), 201

# --- 获取所有项目 ---
@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.order_by(Project.id.desc()).all()
    return jsonify([p.to_dict() for p in projects]), 200

# --- 单独上传项目图片 (如果有需要) ---
@app.route('/projects/<int:project_id>/images', methods=['POST'])
@jwt_required()
def upload_project_images(project_id):
    current_user = get_jwt_identity()
    project = Project.query.get_or_404(project_id)

    if project.user_id != current_user:
        return jsonify({"msg": "Not authorized"}), 403

    if 'photos' not in request.files:
        return jsonify({"msg": "No photos uploaded"}), 400

    photos_list = request.files.getlist('photos')
    uploaded_urls = []

    for photo in photos_list:
        if photo:
            filename = secure_filename(photo.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(path)
            photo_url = f"/uploads/photos/{filename}"

            img = ProjectImage(project_id=project.id, image_url=photo_url)
            db.session.add(img)
            uploaded_urls.append(photo_url)

    db.session.commit()

    return jsonify({"msg": "Images uploaded successfully", "images": uploaded_urls}), 201

# --- 启动 ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
