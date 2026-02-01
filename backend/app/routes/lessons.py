from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.user import User
from app.models.course import Course
from app.models.lesson import Lesson

lessons_bp = Blueprint("lessons", __name__)


def _current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)


def _is_owner_or_admin(user: User, course: Course) -> bool:
    if not user:
        return False
    return user.role == "admin" or course.instructor_id == user.id


# ✅ List lessons for a course (public)
@lessons_bp.route("/courses/<int:course_id>/lessons", methods=["GET"])
def list_lessons(course_id: int):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order_index.asc()).all()

    return jsonify([
        {
            "id": l.id,
            "course_id": l.course_id,
            "title": l.title,
            "content": l.content,
            "order_index": l.order_index,
            "created_at": l.created_at.isoformat(),
        }
        for l in lessons
    ]), 200


# ✅ Create lesson (only course owner instructor/admin)
@lessons_bp.route("/courses/<int:course_id>/lessons", methods=["POST"])
@jwt_required()
def create_lesson(course_id: int):
    user = _current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    # must be instructor/admin AND owner (unless admin)
    if user.role not in ("instructor", "admin"):
        return jsonify({"error": "Only instructors/admin can create lessons"}), 403

    if not _is_owner_or_admin(user, course):
        return jsonify({"error": "You can only add lessons to your own course"}), 403

    data = request.get_json() or {}
    title = data.get("title")
    content = data.get("content")
    order_index = data.get("order_index", 1)

    if not title:
        return jsonify({"error": "Missing field: title"}), 400

    lesson = Lesson(
        title=title,
        content=content,
        order_index=order_index,
        course_id=course_id,
    )
    db.session.add(lesson)
    db.session.commit()

    return jsonify({
        "id": lesson.id,
        "course_id": lesson.course_id,
        "title": lesson.title,
        "content": lesson.content,
        "order_index": lesson.order_index,
        "created_at": lesson.created_at.isoformat(),
    }), 201


# ✅ Get one lesson (public)
@lessons_bp.route("/lessons/<int:lesson_id>", methods=["GET"])
def get_lesson(lesson_id: int):
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    return jsonify({
        "id": lesson.id,
        "course_id": lesson.course_id,
        "title": lesson.title,
        "content": lesson.content,
        "order_index": lesson.order_index,
        "created_at": lesson.created_at.isoformat(),
    }), 200
