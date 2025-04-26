from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_wtf import FlaskForm
from flask_uploads import UploadSet, configure_uploads, IMAGES
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from models import db, User, Project
import os
from config import Config  # 引入配置文件

app = Flask(__name__)
CORS(app)

# --- ✅ 加载配置文件 ---
app.config.from_object(Config)

# --- ✅ 配置上传文件路径 ---
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.getcwd(), 'uploads/photos')  # 保存图片的绝对路径
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 设置最大上传大小为 16MB

# --- ✅ 初始化上传集（只允许图片类型） ---
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# --- ✅ 初始化数据库和 JWT ---
db.init_app(app)
jwt = JWTManager(app)

# --- ✅ 创建表结构 ---
with app.app_context():
    db.create_all()

# --- ✅ 注册蓝图 ---
from auth import auth_bp
from projects import project_bp
app.register_blueprint(auth_bp)
app.register_blueprint(project_bp)

# --- 测试根路径 ---
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

# --- 项目上传表单类 ---
class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    youtube_link = StringField('YouTube Link', validators=[DataRequired()])

# --- 创建项目（带封面图上传） ---
@app.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    current_user = get_jwt_identity()
    form = ProjectForm(request.form)

    if form.validate():
        title = form.title.data
        content = form.content.data
        price = form.price.data
        youtube_link = form.youtube_link.data

        # 处理封面图上传
        photo = request.files.get('photo')
        if photo:
            filename = photos.save(photo)
            file_url = photos.url(filename)
        else:
            file_url = None

        new_project = Project(
            title=title,
            content=content,
            price=price,
            youtube_link=youtube_link,
            user_id=current_user,
            image_url=file_url
        )

        db.session.add(new_project)
        db.session.commit()

        return jsonify({"msg": "Project created successfully!"}), 201
    else:
        return jsonify({"msg": "Form validation failed"}), 400

# --- 获取项目列表 ---
@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.order_by(Project.id.desc()).all()
    return jsonify([p.to_dict() for p in projects]), 200

# --- 启动程序 ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
