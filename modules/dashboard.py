from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from utils.file_manager import file_manager
import pandas as pd
from datetime import datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard', __name__)

class DashboardAI:
    def __init__(self):
        self.performance_thresholds = {
            'excellent': 85,
            'good': 70,
            'needs_improvement': 50
        }
    
    def generate_ai_recommendations(self, user_data):
        """Generate AI-based recommendations based on user performance"""
        recommendations = []
        
        # Analyze dyslexia performance
        dyslexia_data = user_data.get('dyslexia', {})
        if dyslexia_data.get('total_sessions', 0) > 0:
            avg_accuracy = dyslexia_data.get('avg_accuracy', 0)
            
            if avg_accuracy < self.performance_thresholds['needs_improvement']:
                recommendations.append({
                    'type': 'dyslexia',
                    'priority': 'high',
                    'title': 'Focus on Phonics Practice',
                    'description': 'Your reading accuracy could improve. Try the Sound Matching game daily.',
                    'action': 'Play phonics games for 15 minutes daily',
                    'module': 'dyslexia',
                    'icon': 'book-open',
                    'color': 'dyslexia'
                })
            elif avg_accuracy < self.performance_thresholds['good']:
                recommendations.append({
                    'type': 'dyslexia',
                    'priority': 'medium',
                    'title': 'Continue Reading Practice',
                    'description': 'You\'re making good progress! Keep practicing with text simplification.',
                    'action': 'Use the smart reader 3 times this week',
                    'module': 'dyslexia',
                    'icon': 'book-open',
                    'color': 'dyslexia'
                })
        
        # Analyze dyscalculia performance
        dyscalculia_data = user_data.get('dyscalculia', {})
        if dyscalculia_data.get('total_problems', 0) > 0:
            accuracy = dyscalculia_data.get('accuracy', 0)
            
            if accuracy < self.performance_thresholds['needs_improvement']:
                recommendations.append({
                    'type': 'dyscalculia',
                    'priority': 'high',
                    'title': 'Math Fundamentals Practice',
                    'description': 'Focus on basic arithmetic with visual aids to build confidence.',
                    'action': 'Practice visual math problems daily',
                    'module': 'dyscalculia',
                    'icon': 'calculator',
                    'color': 'dyscalculia'
                })
        
        # Analyze dysgraphia performance
        dysgraphia_data = user_data.get('dysgraphia', {})
        if dysgraphia_data.get('total_sessions', 0) > 0:
            avg_words = dysgraphia_data.get('avg_words_per_session', 0)
            
            if avg_words < 20:
                recommendations.append({
                    'type': 'dysgraphia',
                    'priority': 'medium',
                    'title': 'Increase Writing Practice',
                    'description': 'Try to write longer pieces. Use writing prompts for inspiration.',
                    'action': 'Write at least 50 words per session',
                    'module': 'dysgraphia',
                    'icon': 'pen',
                    'color': 'dysgraphia'
                })
        
        # Analyze dyspraxia performance
        dyspraxia_data = user_data.get('dyspraxia', {})
        if dyspraxia_data.get('total_exercises', 0) > 0:
            avg_stability = dyspraxia_data.get('avg_stability', 0)
            
            if avg_stability < self.performance_thresholds['needs_improvement']:
                recommendations.append({
                    'type': 'dyspraxia',
                    'priority': 'high',
                    'title': 'Balance Training Focus',
                    'description': 'Your balance scores suggest more practice is needed. Start with easier exercises.',
                    'action': 'Practice balance exercises for 10 minutes daily',
                    'module': 'dyspraxia',
                    'icon': 'running',
                    'color': 'dyspraxia'
                })
        
        # Overall activity recommendations
        total_activities = user_data.get('overall_stats', {}).get('total_activities', 0)
        if total_activities < 10:
            recommendations.append({
                'type': 'general',
                'priority': 'medium',
                'title': 'Increase Overall Activity',
                'description': 'Try to use the platform more regularly for better results.',
                'action': 'Aim for at least 2 activities per day',
                'module': 'dashboard',
                'icon': 'chart-line',
                'color': 'general'
            })
        
        # Sort by priority
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def analyze_learning_patterns(self, user_data):
        """Analyze learning patterns and provide insights"""
        patterns = {
            'strengths': [],
            'areas_for_improvement': [],
            'learning_style': 'balanced',
            'progress_trend': 'stable'
        }
        
        # Identify strengths
        for module, data in user_data.items():
            if module == 'overall_stats':
                continue
                
            if module == 'dyslexia' and data.get('avg_accuracy', 0) > self.performance_thresholds['good']:
                patterns['strengths'].append('Reading and phonics skills')
            elif module == 'dyscalculia' and data.get('accuracy', 0) > self.performance_thresholds['good']:
                patterns['strengths'].append('Mathematical problem solving')
            elif module == 'dysgraphia' and data.get('avg_words_per_session', 0) > 30:
                patterns['strengths'].append('Written expression')
            elif module == 'dyspraxia' and data.get('avg_stability', 0) > self.performance_thresholds['good']:
                patterns['strengths'].append('Balance and coordination')
        
        # Identify areas for improvement
        for module, data in user_data.items():
            if module == 'overall_stats':
                continue
                
            if module == 'dyslexia' and data.get('avg_accuracy', 0) < self.performance_thresholds['needs_improvement']:
                patterns['areas_for_improvement'].append('Reading fluency and comprehension')
            elif module == 'dyscalculia' and data.get('accuracy', 0) < self.performance_thresholds['needs_improvement']:
                patterns['areas_for_improvement'].append('Number sense and calculation')
            elif module == 'dysgraphia' and data.get('avg_words_per_session', 0) < 15:
                patterns['areas_for_improvement'].append('Writing length and expression')
            elif module == 'dyspraxia' and data.get('avg_stability', 0) < self.performance_thresholds['needs_improvement']:
                patterns['areas_for_improvement'].append('Motor coordination and balance')
        
        return patterns

dashboard_ai = DashboardAI()

@dashboard_bp.route('/')
def main():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard/main.html')

@dashboard_bp.route('/data')
def get_dashboard_data():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    user_id = session['user_id']
    
    # Collect data from all modules
    data = {
        'dyslexia': get_dyslexia_progress(user_id),
        'dyscalculia': get_dyscalculia_progress(user_id),
        'dysgraphia': get_dysgraphia_progress(user_id),
        'dyspraxia': get_dyspraxia_progress(user_id),
        'overall_stats': get_overall_stats(user_id)
    }
    
    # Generate AI recommendations
    recommendations = dashboard_ai.generate_ai_recommendations(data)
    
    # Analyze learning patterns
    learning_patterns = dashboard_ai.analyze_learning_patterns(data)
    
    return jsonify({
        'success': True, 
        'data': data,
        'recommendations': recommendations,
        'learning_patterns': learning_patterns
    })

@dashboard_bp.route('/activity-report/<activity_id>')
def get_activity_report(activity_id):
    """Get detailed report for a specific activity"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    user_id = session['user_id']
    
    # Parse activity_id to determine module and specific activity
    try:
        module, timestamp = activity_id.split('_', 1)
        
        # Get activity details from appropriate module
        if module == 'dyslexia':
            report = get_dyslexia_activity_report(user_id, timestamp)
        elif module == 'dyscalculia':
            report = get_dyscalculia_activity_report(user_id, timestamp)
        elif module == 'dysgraphia':
            report = get_dysgraphia_activity_report(user_id, timestamp)
        elif module == 'dyspraxia':
            report = get_dyspraxia_activity_report(user_id, timestamp)
        else:
            return jsonify({'success': False, 'message': 'Invalid activity module'})
        
        return jsonify({'success': True, 'report': report})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating report: {str(e)}'})

def get_dyslexia_progress(user_id):
    """Get dyslexia progress data"""
    progress_data = file_manager.read_csv('data/dyslexia/progress.csv')
    games_data = file_manager.read_csv('data/dyslexia/games.csv')
    
    user_progress = [p for p in progress_data if p['user_id'] == user_id]
    user_games = [g for g in games_data if g['user_id'] == user_id]
    
    # Calculate average accuracy
    total_accuracy = sum(float(g.get('accuracy', 0)) for g in user_games)
    avg_accuracy = total_accuracy / len(user_games) if user_games else 0
    
    return {
        'total_sessions': len(user_progress),
        'total_games': len(user_games),
        'avg_accuracy': round(avg_accuracy, 1),
        'recent_activity': user_progress[-5:] if user_progress else []
    }

def get_dyscalculia_progress(user_id):
    """Get dyscalculia progress data"""
    progress_data = file_manager.read_csv('data/dyscalculia/progress.csv')
    user_progress = [p for p in progress_data if p['user_id'] == user_id]
    
    correct_answers = len([p for p in user_progress if p.get('correct') == 'True'])
    total_answers = len(user_progress)
    
    return {
        'total_problems': total_answers,
        'correct_answers': correct_answers,
        'accuracy': (correct_answers / total_answers * 100) if total_answers > 0 else 0,
        'recent_activity': user_progress[-5:] if user_progress else []
    }

def get_dysgraphia_progress(user_id):
    """Get dysgraphia progress data"""
    progress_data = file_manager.read_csv('data/dysgraphia/progress.csv')
    user_progress = [p for p in progress_data if p['user_id'] == user_id]
    
    total_words = sum(int(p.get('word_count', 0)) for p in user_progress)
    
    return {
        'total_sessions': len(user_progress),
        'total_words_written': total_words,
        'avg_words_per_session': total_words / len(user_progress) if user_progress else 0,
        'recent_activity': user_progress[-5:] if user_progress else []
    }

def get_dyspraxia_progress(user_id):
    """Get dyspraxia progress data"""
    progress_data = file_manager.read_csv('data/dyspraxia/progress.csv')
    user_progress = [p for p in progress_data if p['user_id'] == user_id]
    
    avg_stability = sum(float(p.get('stability_score', 0)) for p in user_progress) / len(user_progress) if user_progress else 0
    
    return {
        'total_exercises': len(user_progress),
        'avg_stability': round(avg_stability, 1),
        'total_duration': sum(float(p.get('duration', 0)) for p in user_progress),
        'recent_activity': user_progress[-5:] if user_progress else []
    }

def get_overall_stats(user_id):
    """Get overall statistics across all modules"""
    all_activities = 0
    
    for module in ['dyslexia', 'dyscalculia', 'dysgraphia', 'dyspraxia']:
        progress_data = file_manager.read_csv(f'data/{module}/progress.csv')
        user_activities = [p for p in progress_data if p['user_id'] == user_id]
        all_activities += len(user_activities)
    
    return {
        'total_activities': all_activities,
        'active_days': calculate_active_days(user_id),
        'streak': calculate_streak(user_id)
    }

def calculate_active_days(user_id):
    """Calculate number of active days"""
    all_dates = set()
    
    for module in ['dyslexia', 'dyscalculia', 'dysgraphia', 'dyspraxia']:
        progress_data = file_manager.read_csv(f'data/{module}/progress.csv')
        user_activities = [p for p in progress_data if p['user_id'] == user_id]
        
        for activity in user_activities:
            if 'timestamp' in activity:
                date = activity['timestamp'].split('T')[0]
                all_dates.add(date)
    
    return len(all_dates)

def calculate_streak(user_id):
    """Calculate current streak of consecutive days"""
    all_dates = []
    
    for module in ['dyslexia', 'dyscalculia', 'dysgraphia', 'dyspraxia']:
        progress_data = file_manager.read_csv(f'data/{module}/progress.csv')
        user_activities = [p for p in progress_data if p['user_id'] == user_id]
        
        for activity in user_activities:
            if 'timestamp' in activity:
                date = activity['timestamp'].split('T')[0]
                all_dates.append(date)
    
    if not all_dates:
        return 0
    
    # Sort dates and find consecutive days
    unique_dates = sorted(set(all_dates), reverse=True)
    
    if not unique_dates:
        return 0
    
    streak = 1
    current_date = datetime.strptime(unique_dates[0], '%Y-%m-%d').date()
    
    for i in range(1, len(unique_dates)):
        prev_date = datetime.strptime(unique_dates[i], '%Y-%m-%d').date()
        if (current_date - prev_date).days == 1:
            streak += 1
            current_date = prev_date
        else:
            break
    
    return streak

def get_dyslexia_activity_report(user_id, timestamp):
    """Generate detailed report for dyslexia activity"""
    progress_data = file_manager.read_csv('data/dyslexia/progress.csv')
    games_data = file_manager.read_csv('data/dyslexia/games.csv')
    
    # Find specific activity
    activity = None
    for p in progress_data:
        if p['user_id'] == user_id and timestamp in p.get('timestamp', ''):
            activity = p
            break
    
    if not activity:
        # Try games data
        for g in games_data:
            if g['user_id'] == user_id and timestamp in g.get('timestamp', ''):
                activity = g
                break
    
    if not activity:
        return {'error': 'Activity not found'}
    
    # Generate comprehensive report
    report = {
        'title': activity.get('activity', 'Dyslexia Activity'),
        'date': activity.get('timestamp', '').split('T')[0],
        'time': activity.get('timestamp', '').split('T')[1][:8] if 'T' in activity.get('timestamp', '') else '',
        'type': 'dyslexia',
        'details': {},
        'performance': {},
        'recommendations': []
    }
    
    if 'game_type' in activity:
        # Game activity
        report['details'] = {
            'Game Type': activity.get('game_type', ''),
            'Difficulty': activity.get('difficulty', ''),
            'Score': f"{activity.get('score', 0)}/{activity.get('total_questions', 0)}",
            'Accuracy': f"{activity.get('accuracy', 0)}%"
        }
        
        accuracy = float(activity.get('accuracy', 0))
        if accuracy >= 85:
            report['performance']['level'] = 'Excellent'
            report['performance']['message'] = 'Outstanding performance! Your phonics skills are very strong.'
        elif accuracy >= 70:
            report['performance']['level'] = 'Good'
            report['performance']['message'] = 'Good work! Continue practicing to maintain this level.'
        else:
            report['performance']['level'] = 'Needs Improvement'
            report['performance']['message'] = 'Keep practicing! Focus on sound-letter relationships.'
            report['recommendations'].append('Practice phonics games daily for 15 minutes')
            report['recommendations'].append('Use the text reader to improve reading fluency')
    
    else:
        # Text simplification activity
        report['details'] = {
            'Activity': activity.get('activity', ''),
            'Text Length': f"{activity.get('word_count', 0)} words",
            'Difficulty': activity.get('difficulty', ''),
            'Reading Level': activity.get('readability_score', 'N/A')
        }
        
        word_count = int(activity.get('word_count', 0))
        if word_count > 100:
            report['performance']['level'] = 'Good'
            report['performance']['message'] = 'You\'re working with substantial texts. Great progress!'
        else:
            report['performance']['level'] = 'Building'
            report['performance']['message'] = 'Try working with longer texts to challenge yourself.'
            report['recommendations'].append('Gradually increase text length')
            report['recommendations'].append('Practice with different text types')
    
    return report

def get_dyscalculia_activity_report(user_id, timestamp):
    """Generate detailed report for dyscalculia activity"""
    progress_data = file_manager.read_csv('data/dyscalculia/progress.csv')
    
    activity = None
    for p in progress_data:
        if p['user_id'] == user_id and timestamp in p.get('timestamp', ''):
            activity = p
            break
    
    if not activity:
        return {'error': 'Activity not found'}
    
    report = {
        'title': 'Math Practice Session',
        'date': activity.get('timestamp', '').split('T')[0],
        'time': activity.get('timestamp', '').split('T')[1][:8] if 'T' in activity.get('timestamp', '') else '',
        'type': 'dyscalculia',
        'details': {
            'Problem Type': activity.get('problem_type', ''),
            'Difficulty': activity.get('difficulty', ''),
            'Your Answer': activity.get('user_answer', ''),
            'Correct Answer': activity.get('correct_answer', ''),
            'Result': 'Correct' if activity.get('correct') == 'True' else 'Incorrect'
        },
        'performance': {},
        'recommendations': []
    }
    
    if activity.get('correct') == 'True':
        report['performance']['level'] = 'Correct'
        report['performance']['message'] = 'Well done! You solved this problem correctly.'
    else:
        report['performance']['level'] = 'Incorrect'
        report['performance']['message'] = 'Don\'t worry! Learning from mistakes helps you improve.'
        report['recommendations'].append('Review this type of problem')
        report['recommendations'].append('Try visual math exercises')
        report['recommendations'].append('Practice with easier problems first')
    
    return report

def get_dysgraphia_activity_report(user_id, timestamp):
    """Generate detailed report for dysgraphia activity"""
    progress_data = file_manager.read_csv('data/dysgraphia/progress.csv')
    
    activity = None
    for p in progress_data:
        if p['user_id'] == user_id and timestamp in p.get('timestamp', ''):
            activity = p
            break
    
    if not activity:
        return {'error': 'Activity not found'}
    
    report = {
        'title': 'Writing Practice Session',
        'date': activity.get('timestamp', '').split('T')[0],
        'time': activity.get('timestamp', '').split('T')[1][:8] if 'T' in activity.get('timestamp', '') else '',
        'type': 'dysgraphia',
        'details': {
            'Activity': activity.get('activity', ''),
            'Words Written': activity.get('word_count', 0),
            'Issues Found': activity.get('issues_count', 0),
            'Text Sample': activity.get('text_sample', 'N/A')
        },
        'performance': {},
        'recommendations': []
    }
    
    word_count = int(activity.get('word_count', 0))
    issues_count = int(activity.get('issues_count', 0))
    
    if word_count >= 50 and issues_count <= 2:
        report['performance']['level'] = 'Excellent'
        report['performance']['message'] = 'Great writing! Good length with few issues.'
    elif word_count >= 25 and issues_count <= 5:
        report['performance']['level'] = 'Good'
        report['performance']['message'] = 'Nice work! Keep practicing to improve further.'
    else:
        report['performance']['level'] = 'Needs Practice'
        report['performance']['message'] = 'Keep writing! Practice makes perfect.'
        report['recommendations'].append('Try writing longer pieces')
        report['recommendations'].append('Use writing prompts for inspiration')
        report['recommendations'].append('Practice letter formation exercises')
    
    return report

def get_dyspraxia_activity_report(user_id, timestamp):
    """Generate detailed report for dyspraxia activity"""
    progress_data = file_manager.read_csv('data/dyspraxia/progress.csv')
    
    activity = None
    for p in progress_data:
        if p['user_id'] == user_id and timestamp in p.get('timestamp', ''):
            activity = p
            break
    
    if not activity:
        return {'error': 'Activity not found'}
    
    report = {
        'title': activity.get('exercise_name', 'Balance Exercise'),
        'date': activity.get('timestamp', '').split('T')[0],
        'time': activity.get('timestamp', '').split('T')[1][:8] if 'T' in activity.get('timestamp', '') else '',
        'type': 'dyspraxia',
        'details': {
            'Exercise': activity.get('exercise_name', ''),
            'Duration': f"{activity.get('duration', 0)} seconds",
            'Stability Score': f"{activity.get('stability_score', 0)}%",
            'Activity Type': activity.get('activity', '')
        },
        'performance': {},
        'recommendations': []
    }
    
    stability = float(activity.get('stability_score', 0))
    
    if stability >= 85:
        report['performance']['level'] = 'Excellent'
        report['performance']['message'] = 'Outstanding balance! Your coordination is very good.'
    elif stability >= 70:
        report['performance']['level'] = 'Good'
        report['performance']['message'] = 'Good balance! Continue practicing to maintain this level.'
    else:
        report['performance']['level'] = 'Needs Practice'
        report['performance']['message'] = 'Keep working on your balance. Daily practice helps!'
        report['recommendations'].append('Practice balance exercises daily')
        report['recommendations'].append('Start with easier exercises')
        report['recommendations'].append('Focus on core strength')
    
    return report
