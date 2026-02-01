from datetime import datetime
from app import db

class Progress(db.Model):
    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"), nullable=False)

    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    # One progress row per (user, lesson)
    __table_args__ = (
        db.UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson_progress"),
    )

    # Relationships (helpful)
    user = db.relationship("User", backref="lesson_progress", lazy=True)
    lesson = db.relationship("Lesson", backref="progress_entries", lazy=True)

    def mark_completed(self):
        self.completed = True
        self.completed_at = datetime.utcnow()

    def __repr__(self):
        return f"<Progress user={self.user_id} lesson={self.lesson_id} completed={self.completed}>"
