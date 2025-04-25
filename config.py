# config.py
class Config:
    JWT_SECRET_KEY = "your-super-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///mydreamhouse.db"  # 可换为您的数据库地址
    SQLALCHEMY_TRACK_MODIFICATIONS = False
