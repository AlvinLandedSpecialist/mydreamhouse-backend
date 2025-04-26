from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Project

project_bp = Blueprint('projects', __name__)

@project_bp.route('/projects', methods=['GET'])
def get_projects():
    """获取分页项目列表"""
    page = request.args.get('page', 1, type=int)  # 获取页码，默认值为1
    per_page = 10  # 每页显示10个项目

    # 获取查询条件（如果有）
    filter_price = request.args.get('price', type=int)

    # 查询项目
    query = Project.query
    if filter_price:
        query = query.filter(Project.price <= filter_price)
    
    projects = query.order_by(Project.id.desc()).paginate(page, per_page, False)

    return jsonify({
        'projects': [p.to_dict() for p in projects.items],  # 返回项目数据
        'total_pages': projects.pages,  # 总页数
        'current_page': projects.page,  # 当前页码
    }), 200


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
