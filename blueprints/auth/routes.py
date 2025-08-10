import csv
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User, db

auth_bp = Blueprint('auth', __name__)
# Utility to update users.csv after profile/password change
def update_user_csv(user_id, update_dict):
    csv_path = os.path.join('data', 'users', 'users.csv')
    rows = []
    updated = False
    user_id = str(user_id)
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['id'] == user_id:
                # Ensure all updated fields are strings
                for k, v in update_dict.items():
                    row[k] = str(v) if v is not None else ''
                updated = True
            rows.append(row)
    if updated:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    return updated
# Edit profile route
@auth_bp.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    data = request.get_json()
    username = data.get('username', current_user.username)
    email = data.get('email', current_user.email)
    age = data.get('age', current_user.age)
    conditions = data.get('conditions', current_user.conditions)

    # Update in DB
    current_user.username = username
    current_user.email = email
    current_user.age = age
    current_user.conditions = conditions
    db.session.commit()

    # Update in CSV
    update_user_csv(current_user.id, {
        'username': username,
        'email': email,
        'age': age,
        'conditions': conditions
    })

    return jsonify({'success': True, 'message': 'Profile updated successfully'})
# Change password route
@auth_bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not current_user.check_password(old_password):
        return jsonify({'success': False, 'message': 'Old password is incorrect'}), 400

    current_user.set_password(new_password)
    db.session.commit()

    # Update in CSV
    update_user_csv(current_user.id, {
        'password_hash': generate_password_hash(new_password)
    })

    return jsonify({'success': True, 'message': 'Password changed successfully'})


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
