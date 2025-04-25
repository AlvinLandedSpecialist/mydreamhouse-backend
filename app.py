from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.Float, nullable=False)
    youtube_link = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates="projects")

User.projects = db.relationship('Project', back_populates="user")

@app.route('/admin/register', methods=['POST'])
def register_admin():
    username = request.json.get('username')
    password = request.json.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "User already exists"}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Admin user created successfully!"}), 201

@app.route('/admin/login', methods=['POST'])
def login_admin():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Invalid credentials"}), 401

@app.route('/admin/projects', methods=['POST'])
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

@app.route('/admin/projects', methods=['GET'])
@jwt_required()
def get_projects():
    current_user = get_jwt_identity()
    projects = Project.query.filter_by(user_id=current_user).all()
    return jsonify([project.to_dict() for project in projects]), 200

@app.route('/admin/projects/<int:id>', methods=['PUT'])
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

@app.route('/admin/projects/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_project(id):
    current_user = get_jwt_identity()
    project = Project.query.get_or_404(id)

    if project.user_id != current_user:
        return jsonify({"msg": "Not authorized to delete this project"}), 403

    db.session.delete(project)
    db.session.commit()
    return jsonify({"msg": "Project deleted successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
