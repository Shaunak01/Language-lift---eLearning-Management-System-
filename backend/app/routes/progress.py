from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.user import User
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
from app.models.progress import Progress

progress_bp = Blueprint("progress", __name__)


def _current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)


# ✅ Mark a lesson as complete (student)
@progress_bp.route("/lessons/<int:lesson_id>/complete", methods=["POST"])
@jwt_required()
def complete_lesson(lesson_id: int):
    user = _current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role not in ("student", "admin"):
        return jsonify({"error": "Only students/admin can mark progress"}), 403

    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404

    # Ensure user is enrolled in the course that owns this lesson
    enrolled = Enrollment.query.filter_by(user_id=user.id, course_id=lesson.course_id).first()
    if not enrolled and user.role != "admin":
        return jsonify({"error": "You must be enrolled in the course to mark progress"}), 403

    entry = Progress.query.filter_by(user_id=user.id, lesson_id=lesson_id).first()
    if not entry:
        entry = Progress(user_id=user.id, lesson_id=lesson_id)

    entry.mark_completed()
    db.session.add(entry)
    db.session.commit()

    return jsonify({
        "message": "Lesson marked complete",
        "user_id": user.id,
        "lesson_id": lesson_id,
        "course_id": lesson.course_id,
        "completed": entry.completed,
        "completed_at": entry.completed_at.isoformat() if entry.completed_at else None
    }), 200


# ✅ Get my progress for a course (student)
@progress_bp.route("/courses/<int:course_id>/progress", methods=["GET"])
@jwt_required()
def course_progress(course_id: int):
    user = _current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    # Ensure enrolled (admins can view anyway)
    enrolled = Enrollment.query.filter_by(user_id=user.id, course_id=course_id).first()
    if not enrolled and user.role != "admin":
        return jsonify({"error": "You must be enrolled in this course to view progress"}), 403

    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order_index.asc()).all()
    total = len(lessons)

    completed_ids = {
        p.lesson_id
        for p in Progress.query.filter_by(user_id=user.id, completed=True).all()
    }

    lesson_rows = []
    completed_count = 0
    for l in lessons:
        is_done = l.id in completed_ids
        if is_done:
            completed_count += 1
        lesson_rows.append({
            "lesson_id": l.id,
            "title": l.title,
            "order_index": l.order_index,
            "completed": is_done,
        })

    percent = 0 if total == 0 else round((completed_count / total) * 100, 2)

    return jsonify({
        "course_id": course_id,
        "user_id": user.id,
        "total_lessons": total,
        "completed_lessons": completed_count,
        "completion_percent": percent,
        "lessons": lesson_rows,
    }), 200
