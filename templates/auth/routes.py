from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            session['user_id'] = user.id
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'user': user.to_dict()
                })
            else:
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard.dashboard'))
        else:
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Invalid username or password'
                }), 401
            else:
                flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'child')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Username already exists'
                }), 400
            else:
                flash('Username already exists', 'error')
                return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Email already exists'
                }), 400
            else:
                flash('Email already exists', 'error')
                return render_template('auth/register.html')
        
        # Create new user
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        session['user_id'] = user.id
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Registration successful',
                'user': user.to_dict()
            })
        else:
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/update-settings', methods=['POST'])
@login_required
def update_settings():
    data = request.get_json()
    
    current_user.font_size = data.get('font_size', current_user.font_size)
    current_user.line_spacing = data.get('line_spacing', current_user.line_spacing)
    current_user.contrast_mode = data.get('contrast_mode', current_user.contrast_mode)
    current_user.preferred_font = data.get('preferred_font', current_user.preferred_font)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Settings updated successfully'
    })
