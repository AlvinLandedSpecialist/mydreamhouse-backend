from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Project

project_bp = Blueprint('projects', __name__)

@project_bp.route('/projects', methods=['GET'])
def get_projects():
    """公开获取所有项目"""
    projects = Project.query.order_by(Project.id.desc()).all()
    return jsonify([p.to_dict() for p in projects]), 200

@project_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    """创建新项目，需登录"""
    current_user = get_jwt_identity()
    data = request.get_json() or {}
    
    # 校验必需字段
    for field in ['title', 'content', 'price']:
        if field not in data:
            return jsonify({"msg": f"Missing field {field}"}), 400

    project = Project(
        title=data['title'],
        content=data['content'],
        price=data['price'],
        youtube_link=data.get('youtube_link'),
        user_id=current_user
    )
    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201

@project_bp.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """更新项目，需登录且为项目所有者"""
    current_user = get_jwt_identity()
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user:
        return jsonify({"msg": "Not authorized"}), 403

    data = request.get_json() or {}
    project.title = data.get('title', project.title)
    project.content = data.get('content', project.content)
    project.price = data.get('price', project.price)
    project.youtube_link = data.get('youtube_link', project.youtube_link)

    db.session.commit()
    return jsonify(project.to_dict()), 200

@project_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """删除项目，需登录且为项目所有者"""
    current_user = get_jwt_identity()
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user:
        return jsonify({"msg": "Not authorized"}), 403

    db.session.delete(project)
    db.session.commit()
    return jsonify({"msg": "Project deleted"}), 200
