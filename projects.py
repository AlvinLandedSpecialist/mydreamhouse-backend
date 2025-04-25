from flask import Blueprint, request, jsonify
from models import db, Project, ProjectImage
from flask_jwt_extended import jwt_required

# 创建蓝图
project_bp = Blueprint('projects', __name__)

# 创建项目
@project_bp.route('/projects', methods=['POST'])
@jwt_required()  # 确保用户已登录才能创建项目
def create_project():
    data = request.get_json()
    
    title = data.get('title')
    content = data.get('content')
    price = data.get('price')
    video_link = data.get('video_link')
    viewing_video_link = data.get('viewing_video_link')
    
    if not title or not price:
        return jsonify({"msg": "Title and Price are required"}), 400
    
    project = Project(
        title=title,
        content=content,
        price=price,
        video_link=video_link,
        viewing_video_link=viewing_video_link
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify({"msg": "Project created successfully", "project_id": project.id}), 201


# 更新项目
@project_bp.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"msg": "Project not found"}), 404
    
    data = request.get_json()
    
    project.title = data.get('title', project.title)
    project.content = data.get('content', project.content)
    project.price = data.get('price', project.price)
    project.video_link = data.get('video_link', project.video_link)
    project.viewing_video_link = data.get('viewing_video_link', project.viewing_video_link)
    
    db.session.commit()
    
    return jsonify({"msg": "Project updated successfully"}), 200


# 获取项目详情
@project_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"msg": "Project not found"}), 404
    
    # 获取该项目的所有图片
    images = [{"image_url": image.image_url} for image in project.images]
    
    return jsonify({
        "id": project.id,
        "title": project.title,
        "content": project.content,
        "price": project.price,
        "video_link": project.video_link,
        "viewing_video_link": project.viewing_video_link,
        "images": images
    }), 200


# 上传项目图片
@project_bp.route('/projects/<int:project_id>/images', methods=['POST'])
@jwt_required()
def upload_project_images(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"msg": "Project not found"}), 404

    images = request.files.getlist('images')
    if len(images) > 6:
        return jsonify({"msg": "You can upload a maximum of 6 images"}), 400
    
    for image in images:
        # 假设你使用了一个存储服务，存储图片 URL
        image_url = save_image(image)  # 这里需要实现上传图片并返回 URL 的逻辑
        project_image = ProjectImage(project_id=project.id, image_url=image_url)
        db.session.add(project_image)
    
    db.session.commit()
    
    return jsonify({"msg": "Images uploaded successfully"}), 200
