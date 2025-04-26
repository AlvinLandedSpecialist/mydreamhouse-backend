from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# 初始化 SQLAlchemy 实例，后续在 app.py 中通过 db.init_app(app) 绑定
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username
        }

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    youtube_link = db.Column(db.String(500), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)  # 封面图
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('projects', lazy=True))
    images = db.relationship('ProjectImage', backref='project', lazy=True)  # 附加图关系

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "price": self.price,
            "youtube_link": self.youtube_link,
            "image_url": self.image_url,
            "user_id": self.user_id,
            "extra_images": [img.image_url for img in self.images]
        }

class ProjectImage(db.Model):
    __tablename__ = 'project_images'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
