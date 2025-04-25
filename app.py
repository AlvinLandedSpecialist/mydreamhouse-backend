from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # 用于Session加密
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'  # 数据库配置
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库和Flask-Login
db = SQLAlchemy(app)
login_manager = LoginManager(app)
CORS(app)

# 用户模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# 房地产项目模型
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    imageUrl = db.Column(db.String(200), nullable=True)

# 设置用户加载
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 注册路由
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if user and user.password == password:  # 简单的验证方式
        login_user(user)
        return jsonify({'success': True, 'message': 'Login successful'})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/projects', methods=['GET'])
def get_projects():
    page = request.args.get('page', 1, type=int)
    projects = Project.query.paginate(page, 6, False)
    projects_list = []
    for project in projects.items:
        projects_list.append({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'price': project.price,
            'latitude': project.latitude,
            'longitude': project.longitude,
            'imageUrl': project.imageUrl
        })
    return jsonify({'data': projects_list, 'next': projects.has_next, 'prev': projects.has_prev})

@app.route('/add_project', methods=['POST'])
@login_required
def add_project():
    data = request.get_json()
    new_project = Project(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        imageUrl=data['imageUrl']
    )
    db.session.add(new_project)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Project added successfully'})

if __name__ == '__main__':
    db.create_all()  # 创建数据库表
    app.run(debug=True)
