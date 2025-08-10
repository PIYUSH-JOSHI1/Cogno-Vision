from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'reading', 'game', 'simplification'
    activity_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float)
    reading_speed = db.Column(db.Float)  # words per minute
    accuracy = db.Column(db.Float)  # percentage
    time_spent = db.Column(db.Integer)  # seconds
    difficulty_level = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'activity_name': self.activity_name,
            'score': self.score,
            'reading_speed': self.reading_speed,
            'accuracy': self.accuracy,
            'time_spent': self.time_spent,
            'difficulty_level': self.difficulty_level,
            'created_at': self.created_at.isoformat()
        }

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.String(50), nullable=False)
    game_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'abandoned'
    score = db.Column(db.Integer, default=0)
    max_score = db.Column(db.Integer, default=100)
    level = db.Column(db.Integer, default=1)
    answers = db.Column(db.Text)  # JSON string of answers
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'game_name': self.game_name,
            'status': self.status,
            'score': self.score,
            'max_score': self.max_score,
            'level': self.level,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
