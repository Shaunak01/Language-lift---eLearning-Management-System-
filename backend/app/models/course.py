from datetime import datetime
from app import db

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    level = db.Column(db.String(50), nullable=True)  # Beginner, Intermediate, etc.

    instructor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: one course → many lessons
    lessons = db.relationship("Lesson", backref="course", cascade="all, delete", lazy=True)

    # Relationship: one instructor → many courses
    instructor = db.relationship("User", backref="courses", lazy=True)

    def __repr__(self):
        return f"<Course {self.title}>"
