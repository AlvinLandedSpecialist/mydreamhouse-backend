from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from sqlalchemy import desc
import os
from models import db, User, Project, ProjectImage
from config import Config
import uuid

def generate_unique_filename(original_filename):
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4().hex}{ext}"

app = Flask(__name__)
CORS(app)

# --- Configuration ---
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = 'uploads/photos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Initialization ---
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

# --- Routes ---
@app.route('/')
def home():
    return "Welcome to the Home Page"

# --- Static file access ---
@app.route('/uploads/photos/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Authentication ---
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

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Invalid credentials"}), 401

# --- Project Management ---
@app.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    current_user = get_jwt_identity()

    title = request.form.get('title')
    content = request.form.get('content')
    price = request.form.get('price')
    youtube_link = request.form.get('youtube_link')

    if not all([title, content, price]):
        return jsonify({"msg": "Missing fields"}), 400

    # Save cover photo
    cover_photo = request.files.get('cover_photo')
    cover_photo_url = None
    if cover_photo:
        filename = generate_unique_filename(cover_photo.filename)
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cover_photo.save(cover_path)
        cover_photo_url = f"/uploads/photos/{filename}"

    # Create project
    project = Project(
        title=title,
        content=content,
        price=price,
        youtube_link=youtube_link,
        user_id=current_user,
        cover_photo_url=cover_photo_url
    )
    db.session.add(project)
    db.session.commit()

    # Save additional photos
    additional_photos = request.files.getlist('additional_photos')
    for photo in additional_photos:
        if photo:
            filename = generate_unique_filename(photo.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(path)
            photo_url = f"/uploads/photos/{filename}"

            project_image = ProjectImage(project_id=project.id, image_url=photo_url)
            db.session.add(project_image)

    db.session.commit()

    return jsonify({"msg": "Project created successfully!"}), 201

@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.order_by(Project.id.desc()).all()
    return jsonify([p.to_dict() for p in projects]), 200

@app.route('/projects/paginated', methods=['GET'])
def get_projects_paginated():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
    except ValueError:
        return jsonify({"msg": "Invalid page or per_page parameter"}), 400

    projects_query = Project.query.order_by(desc(Project.id))
    pagination = projects_query.paginate(page=page, per_page=per_page, error_out=False)

    projects = [project.to_dict() for project in pagination.items]
    return jsonify({
        "projects": projects,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    }), 200

@app.route('/projects/<int:project_id>/images', methods=['POST'])
@jwt_required()
def upload_project_images(project_id):
    current_user = get_jwt_identity()
    project = Project.query.get_or_404(project_id)

    if project.user_id != current_user:
        return jsonify({"msg": "Not authorized"}), 403

    if 'photos' not in request.files:
        return jsonify({"msg": "No photos uploaded"}), 400

    photos_list = request.files.getlist('photos')
    uploaded_urls = []

    for photo in photos_list:
        if photo:
            filename = generate_unique_filename(photo.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(path)
            photo_url = f"/uploads/photos/{filename}"

            img = ProjectImage(project_id=project.id, image_url=photo_url)
            db.session.add(img)
            uploaded_urls.append(photo_url)

    db.session.commit()

    return jsonify({"msg": "Images uploaded successfully", "images": uploaded_urls}), 201

@app.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
def edit_project(project_id):
    current_user = get_jwt_identity()
    project = Project.query.get_or_404(project_id)

    if project.user_id != current_user:
        return jsonify({"msg": "Not authorized"}), 403

    data = request.form

    project.title = data.get('title', project.title)
    project.content = data.get('content', project.content)
    project.price = data.get('price', project.price)
    project.youtube_link = data.get('youtube_link', project.youtube_link)

    # Update cover photo if new one uploaded
    new_cover = request.files.get('cover_photo')
    if new_cover:
        # Delete old cover
        if project.cover_photo_url:
            old_cover_path = project.cover_photo_url.lstrip('/')
            if os.path.exists(old_cover_path):
                os.remove(old_cover_path)

        # Save new cover
        filename = generate_unique_filename(new_cover.filename)
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        new_cover.save(cover_path)
        project.cover_photo_url = f"/uploads/photos/{filename}"

    db.session.commit()
    return jsonify({"msg": "Project updated successfully!"}), 200

@app.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    current_user = get_jwt_identity()
    project = Project.query.get_or_404(project_id)

    if project.user_id != current_user:
        return jsonify({"msg": "Not authorized"}), 403

    # Delete cover photo
    if project.cover_photo_url:
        cover_path = project.cover_photo_url.lstrip('/')
        if os.path.exists(cover_path):
            os.remove(cover_path)

    # Delete additional images
    for image in project.images:
        image_path = image.image_url.lstrip('/')
        if os.path.exists(image_path):
            os.remove(image_path)
        db.session.delete(image)

    # Delete project
    db.session.delete(project)
    db.session.commit()

    return jsonify({"msg": "Project deleted successfully!"}), 200

# --- Error Handlers ---
@app.errorhandler(404)
def not_found(error):
    return jsonify({"msg": "Resource not found", "error": str(error)}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"msg": "Internal server error", "error": str(error)}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"msg": "Bad request", "error": str(error)}), 400

# --- Main ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
