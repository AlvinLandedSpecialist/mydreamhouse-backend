import jwt
import datetime
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

# 设置管理员账号和密码（哈希版）
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = 'pbkdf2:sha256:260000$'

SECRET_KEY = 'your_jwt_secret_key'  # 可以换成更复杂的 key，放在 .env 更安全

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401
