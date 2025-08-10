from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from utils.file_manager import file_manager
import hashlib

auth_bp = Blueprint('auth', __name__)

# Sample users for quick login
SAMPLE_USERS = [
    {
        'id': 'user_001',
        'username': 'demo_child',
        'email': 'child@demo.com',
        'password': 'demo123',
        'role': 'child',
        'age': 10,
        'conditions': ['dyslexia', 'dyscalculia']
    },
    {
        'id': 'user_002', 
        'username': 'demo_parent',
        'email': 'parent@demo.com',
        'password': 'demo123',
        'role': 'parent',
        'age': 35,
        'conditions': []
    }
]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_sample_users():
    """Initialize sample users in CSV file"""
    users_file = 'data/users/users.csv'
    existing_users = file_manager.read_csv(users_file)
    
    if not existing_users:
        fieldnames = ['id', 'username', 'email', 'password_hash', 'role', 'age', 'conditions', 'created_at']
        users_data = []
        
        for user in SAMPLE_USERS:
            users_data.append({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'password_hash': hash_password(user['password']),
                'role': user['role'],
                'age': user['age'],
                'conditions': ','.join(user['conditions']),
                'created_at': file_manager.get_timestamp()
            })
        
        file_manager.write_csv(users_file, users_data, fieldnames)

# Initialize sample users on module load
init_sample_users()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'patient')
        password_hash = hash_password(password)
        if role == 'doctor':
            # Doctor login
            import csv
            with open('data/doctors/doctors.csv', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for doctor in reader:
                    if (doctor['email'] == username or doctor['name'] == username) and doctor['password_hash'] == password_hash:
                        session['doctor_id'] = doctor['doctor_id']
                        session['username'] = doctor['name']
                        session['role'] = 'doctor'
                        if request.is_json:
                            return jsonify({'success': True, 'redirect': '/doctor/dashboard'})
                        return redirect(url_for('doctor.dashboard'))
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid doctor credentials'})
            return render_template('auth/login.html', error='Invalid doctor credentials')
        else:
            # Patient login (default)
            users = file_manager.read_csv('data/users/users.csv')
            for user in users:
                if (user['username'] == username or user['email'] == username) and user['password_hash'] == password_hash:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    session['conditions'] = user['conditions'].split(',') if user['conditions'] else []
                    if request.is_json:
                        return jsonify({'success': True, 'redirect': '/dashboard'})
                    return redirect(url_for('dashboard.main'))
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid credentials'})
            return render_template('auth/login.html', error='Invalid credentials')
    return render_template('auth/login.html', sample_users=SAMPLE_USERS)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        role = data.get('role', 'patient')
        if role == 'doctor':
            # Doctor registration
            import csv
            name = data.get('username')
            email = data.get('email')
            password = data.get('password')
            specialization = data.get('specialization', '')
            with open('data/doctors/doctors.csv', newline='', encoding='utf-8') as f:
                doctors = list(csv.DictReader(f))
            if any(d['email'] == email for d in doctors):
                return render_template('auth/register.html', error='Doctor email already registered')
            doctor_id = str(len(doctors) + 1)
            password_hash = hash_password(password)
            with open('data/doctors/doctors.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([doctor_id, name, email, password_hash, specialization])
            session['doctor_id'] = doctor_id
            session['username'] = name
            session['role'] = 'doctor'
            if request.is_json:
                return jsonify({'success': True, 'redirect': '/doctor/dashboard'})
            return redirect(url_for('doctor.dashboard'))
        else:
            # Patient registration (default)
            user_data = {
                'id': file_manager.generate_id(),
                'username': data.get('username'),
                'email': data.get('email'),
                'password_hash': hash_password(data.get('password')),
                'role': role,
                'age': data.get('age', ''),
                'conditions': ','.join(data.getlist('conditions') if hasattr(data, 'getlist') else data.get('conditions', [])),
                'created_at': file_manager.get_timestamp()
            }
            fieldnames = ['id', 'username', 'email', 'password_hash', 'role', 'age', 'conditions', 'created_at']
            file_manager.append_csv('data/users/users.csv', user_data, fieldnames)
            session['user_id'] = user_data['id']
            session['username'] = user_data['username']
            session['role'] = user_data['role']
            session['conditions'] = user_data['conditions'].split(',') if user_data['conditions'] else []
            if request.is_json:
                return jsonify({'success': True, 'redirect': '/dashboard'})
            return redirect(url_for('dashboard.main'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@auth_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    users = file_manager.read_csv('data/users/users.csv')
    user = next((u for u in users if u['id'] == session['user_id']), None)
    
    return render_template('auth/profile.html', user=user)
