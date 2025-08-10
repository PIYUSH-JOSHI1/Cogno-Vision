from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import csv
import os
from werkzeug.security import generate_password_hash, check_password_hash

DOCTOR_CSV = os.path.join('data', 'doctors', 'doctors.csv')
ASSIGNMENTS_CSV = os.path.join('data', 'doctors', 'assignments.csv')
USERS_CSV = os.path.join('data', 'users', 'users.csv')

bp_doctor = Blueprint('doctor', __name__, url_prefix='/doctor')

# Helper to read doctors

def read_doctors():
    with open(DOCTOR_CSV, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def read_assignments():
    with open(ASSIGNMENTS_CSV, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def read_patients():
    with open(USERS_CSV, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

# Doctor signup
@bp_doctor.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        specialization = request.form['specialization']
        doctors = read_doctors()
        if any(d['email'] == email for d in doctors):
            flash('Email already registered.')
            return redirect(url_for('doctor.signup'))
        doctor_id = str(len(doctors) + 1)
        password_hash = generate_password_hash(password)
        with open(DOCTOR_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([doctor_id, name, email, password_hash, specialization])
        flash('Signup successful. Please login.')
        return redirect(url_for('doctor.login'))
    return render_template('doctor/signup.html')

# Doctor login
@bp_doctor.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        doctors = read_doctors()
        doctor = next((d for d in doctors if d['email'] == email), None)
        if doctor and check_password_hash(doctor['password_hash'], password):
            session['doctor_id'] = doctor['doctor_id']
            session['role'] = 'doctor'
            return redirect(url_for('doctor.dashboard'))
        flash('Invalid credentials.')
    return render_template('doctor/login.html')




# Doctor dashboard: show all patients and all reports to any doctor
@bp_doctor.route('/dashboard')
def dashboard():
    if 'doctor_id' not in session:
        return redirect(url_for('doctor.login'))
    patients = read_patients()
    all_progress = []
    try:
        with open('data/dyspraxia/progress.csv', newline='', encoding='utf-8') as f:
            import csv
            reader = csv.DictReader(f)
            all_progress = list(reader)
    except Exception:
        pass
    return render_template('doctor/dashboard.html', patients=patients, all_progress=all_progress)

# Doctor profile page
@bp_doctor.route('/profile')
def profile():
    if 'doctor_id' not in session:
        return redirect(url_for('doctor.login'))
    doctor_id = session['doctor_id']
    doctors = read_doctors()
    doctor = next((d for d in doctors if d['doctor_id'] == doctor_id), None)
    return render_template('doctor/profile.html', doctor=doctor)


# Patient reports page
@bp_doctor.route('/patient_reports')
def patient_reports():
    if 'doctor_id' not in session:
        return redirect(url_for('doctor.login'))
    all_progress = []
    patients = read_patients()
    patient_map = {p['id']: p['username'] for p in patients}
    try:
        with open('data/dyspraxia/progress.csv', newline='', encoding='utf-8') as f:
            import csv
            reader = csv.DictReader(f)
            all_progress = list(reader)
            # Add patient name to each row
            for row in all_progress:
                row['patient_name'] = patient_map.get(row.get('user_id'), 'Unknown')
    except Exception:
        pass
    return render_template('doctor/patient_reports.html', all_progress=all_progress)

# Download all patient reports as CSV
@bp_doctor.route('/download_all_reports')
def download_all_reports():
    if 'doctor_id' not in session:
        return redirect(url_for('doctor.login'))
    import io
    import csv
    all_progress = []
    patients = read_patients()
    patient_map = {p['id']: p['username'] for p in patients}
    try:
        with open('data/dyspraxia/progress.csv', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            all_progress = list(reader)
            for row in all_progress:
                row['patient_name'] = patient_map.get(row.get('user_id'), 'Unknown')
    except Exception:
        pass
    if not all_progress:
        return 'No data', 404
    output = io.StringIO()
    fieldnames = list(all_progress[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_progress)
    output.seek(0)
    return (output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename="all_patient_reports.csv"'
    })



# View patient details, analysis, and reports (all activities)
@bp_doctor.route('/patient/<patient_id>')
def view_patient(patient_id):
    if 'doctor_id' not in session:
        return redirect(url_for('doctor.login'))
    patients = read_patients()
    patient = next((p for p in patients if p['id'] == patient_id), None)
    all_activities = []
    # List of (label, csv_path, filter_field)
    sources = [
        ("Dyslexia", 'data/dyslexia/progress.csv', 'user_id'),
        ("Dyscalculia", 'data/dyscalculia/progress.csv', 'user_id'),
        ("Dysgraphia", 'data/dysgraphia/progress.csv', 'user_id'),
        ("Dyspraxia", 'data/dyspraxia/progress.csv', 'user_id'),
    ]
    import csv
    for label, path, field in sources:
        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get(field) == patient_id:
                        row['activity_source'] = label
                        all_activities.append(row)
        except Exception:
            pass
    return render_template('doctor/patient_detail.html', patient=patient, all_activities=all_activities)

# Download individual patient report as CSV
@bp_doctor.route('/download_patient_report/<patient_id>')
def download_patient_report(patient_id):
    if 'doctor_id' not in session:
        return redirect(url_for('doctor.login'))
    import io
    import csv
    progress = []
    try:
        with open('data/dyspraxia/progress.csv', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            progress = [row for row in reader if row.get('user_id') == patient_id]
    except Exception:
        pass
    if not progress:
        return 'No data', 404
    output = io.StringIO()
    fieldnames = list(progress[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(progress)
    output.seek(0)
    return (output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename="patient_{patient_id}_report.csv"'
    })


# Assignment/unassignment removed: all doctors see all patients and reports
