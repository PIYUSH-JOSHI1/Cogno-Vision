from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models.progress import Progress, GameSession, db
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard/dashboard.html', user=current_user)

@dashboard_bp.route('/data')
@login_required
def get_dashboard_data():
    # Get reading progress over time
    reading_progress = db.session.query(
        func.date(Progress.created_at).label('date'),
        func.avg(Progress.reading_speed).label('avg_speed'),
        func.avg(Progress.accuracy).label('avg_accuracy')
    ).filter(
        Progress.user_id == current_user.id,
        Progress.activity_type == 'reading',
        Progress.created_at >= datetime.utcnow() - timedelta(days=30)
    ).group_by(func.date(Progress.created_at)).all()
    
    # Get game scores
    game_scores = db.session.query(
        Progress.activity_name,
        func.avg(Progress.score).label('avg_score'),
        func.count(Progress.id).label('play_count')
    ).filter(
        Progress.user_id == current_user.id,
        Progress.activity_type == 'game'
    ).group_by(Progress.activity_name).all()
    
    # Get recent activities
    recent_activities = Progress.query.filter_by(
        user_id=current_user.id
    ).order_by(Progress.created_at.desc()).limit(10).all()
    
    # Calculate statistics
    total_sessions = Progress.query.filter_by(user_id=current_user.id).count()
    total_time = db.session.query(func.sum(Progress.time_spent)).filter_by(
        user_id=current_user.id
    ).scalar() or 0
    
    avg_reading_speed = db.session.query(func.avg(Progress.reading_speed)).filter(
        Progress.user_id == current_user.id,
        Progress.reading_speed.isnot(None)
    ).scalar() or 0
    
    return jsonify({
        'success': True,
        'reading_progress': [
            {
                'date': str(item.date),
                'avg_speed': float(item.avg_speed or 0),
                'avg_accuracy': float(item.avg_accuracy or 0)
            } for item in reading_progress
        ],
        'game_scores': [
            {
                'game': item.activity_name,
                'avg_score': float(item.avg_score or 0),
                'play_count': item.play_count
            } for item in game_scores
        ],
        'recent_activities': [activity.to_dict() for activity in recent_activities],
        'statistics': {
            'total_sessions': total_sessions,
            'total_time_minutes': int(total_time / 60),
            'avg_reading_speed': round(float(avg_reading_speed or 0), 1)
        },
        'recommendations': generate_recommendations(current_user.id)
    })

def generate_recommendations(user_id):
    """Generate personalized recommendations based on user progress"""
    recommendations = []
    
    # Check recent reading activity
    recent_reading = Progress.query.filter(
        Progress.user_id == user_id,
        Progress.activity_type == 'reading',
        Progress.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    if recent_reading < 3:
        recommendations.append({
            'type': 'reading',
            'title': 'Practice Reading',
            'description': 'Try reading and simplifying 2-3 passages this week',
            'action': 'Go to Reader'
        })
    
    # Check game activity
    recent_games = Progress.query.filter(
        Progress.user_id == user_id,
        Progress.activity_type == 'game',
        Progress.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    if recent_games < 5:
        recommendations.append({
            'type': 'games',
            'title': 'Play Phonics Games',
            'description': 'Play Sound Match or Syllable Counter to improve phonics skills',
            'action': 'Play Games'
        })
    
    # Check reading speed
    avg_speed = db.session.query(func.avg(Progress.reading_speed)).filter(
        Progress.user_id == user_id,
        Progress.reading_speed.isnot(None)
    ).scalar()
    
    if avg_speed and avg_speed < 100:
        recommendations.append({
            'type': 'speed',
            'title': 'Improve Reading Speed',
            'description': 'Practice with shorter texts to build reading fluency',
            'action': 'Practice Reading'
        })
    
    return recommendations
