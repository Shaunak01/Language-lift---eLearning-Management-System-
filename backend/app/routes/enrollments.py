from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment

enrollments_bp = Blueprint("enrollments", __name__)


def _current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)


# ✅ Student enrolls in a course
@enrollments_bp.route("/courses/<int:course_id>/enroll", methods=["POST"])
@jwt_required()
def enroll(course_id: int):
    user = _current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # Typically only students enroll (you can allow instructors too if you want)
    if user.role not in ("student", "admin"):
        return jsonify({"error": "Only students/admin can enroll"}), 403

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    existing = Enrollment.query.filter_by(user_id=user.id, course_id=course_id).first()
    if existing:
        return jsonify({"message": "Already enrolled", "enrollment_id": existing.id}), 200

    e = Enrollment(user_id=user.id, course_id=course_id)
    db.session.add(e)
    db.session.commit()

    return jsonify({
        "message": "Enrolled successfully",
        "enrollment_id": e.id,
        "course_id": course_id,
        "user_id": user.id,
    }), 201


# ✅ List my enrolled courses
@enrollments_bp.route("/me/enrollments", methods=["GET"])
@jwt_required()
def my_enrollments():
    user = _current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    enrollments = (
        Enrollment.query
        .filter_by(user_id=user.id)
        .order_by(Enrollment.enrolled_at.desc())
        .all()
    )

    result = []
    for e in enrollments:
        c = e.course
        result.append({
            "enrollment_id": e.id,
            "enrolled_at": e.enrolled_at.isoformat(),
            "course": {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "level": c.level,
                "instructor_id": c.instructor_id,
            }
        })

    return jsonify(result), 200
