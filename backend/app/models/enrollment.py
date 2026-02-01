from datetime import datetime
from app import db

class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Prevent duplicate enrollments for same user-course pair
    __table_args__ = (
        db.UniqueConstraint("user_id", "course_id", name="uq_user_course_enrollment"),
    )

    # Relationships (optional but helpful)
    user = db.relationship("User", backref="enrollments", lazy=True)
    course = db.relationship("Course", backref="enrollments", lazy=True)

    def __repr__(self):
        return f"<Enrollment user={self.user_id} course={self.course_id}>"
