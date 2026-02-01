from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.user import User
from app.models.course import Course

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")


def _current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)


@courses_bp.route("", methods=["GET"])
def list_courses():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return jsonify([
        {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "level": c.level,
            "instructor_id": c.instructor_id,
            "created_at": c.created_at.isoformat(),
        }
        for c in courses
    ]), 200


@courses_bp.route("", methods=["POST"])
@jwt_required()
def create_course():
    user = _current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role not in ("instructor", "admin"):
        return jsonify({"error": "Only instructors/admin can create courses"}), 403

    data = request.get_json() or {}
    title = data.get("title")
    description = data.get("description")
    level = data.get("level")

    if not title:
        return jsonify({"error": "Missing field: title"}), 400

    course = Course(
        title=title,
        description=description,
        level=level,
        instructor_id=user.id,
    )
    db.session.add(course)
    db.session.commit()

    return jsonify({
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "level": course.level,
        "instructor_id": course.instructor_id,
        "created_at": course.created_at.isoformat(),
    }), 201


@courses_bp.route("/<int:course_id>", methods=["GET"])
def get_course(course_id: int):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    return jsonify({
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "level": course.level,
        "instructor_id": course.instructor_id,
        "created_at": course.created_at.isoformat(),
    }), 200
