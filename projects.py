from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Project

project_bp = Blueprint('projects', __name__)

# 创建项目
@project_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    current_user = get_jwt_identity()
    title = request.json.get('title')
    content = request.json.get('content')
    price = request.json.get('price')
    youtube_link = request.json.get('youtube_link')
    
    new_project = Project(
        title=title,
        content=content,
        price=price,
        youtube_link=youtube_link,
        user_id=current_user
    )
    
    db.session.add(new_project)
    db.session.commit()
    
    return jsonify({"msg": "Project created successfully!"}), 201

# 更新项目
@project_bp.route('/projects/<int:id>', methods=['PUT'])
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
