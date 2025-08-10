from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='child')  # 'child' or 'guardian'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Dyslexia-specific settings
    font_size = db.Column(db.Integer, default=16)
    line_spacing = db.Column(db.Float, default=1.5)
    contrast_mode = db.Column(db.String(20), default='normal')
    preferred_font = db.Column(db.String(50), default='OpenDyslexic')
    
    # Relationships
    progress_records = db.relationship('Progress', backref='user', lazy=True)
    game_sessions = db.relationship('GameSession', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'font_size': self.font_size,
            'line_spacing': self.line_spacing,
            'contrast_mode': self.contrast_mode,
            'preferred_font': self.preferred_font
        }
