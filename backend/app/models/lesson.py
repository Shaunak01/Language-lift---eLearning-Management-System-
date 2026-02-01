from datetime import datetime
from app import db

class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)  # Can later hold markdown / HTML / video URL

    order_index = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Key → Course
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    def __repr__(self):
        return f"<Lesson {self.title}>"
