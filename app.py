import re
import csv
import io
from flask import Flask, render_template, request, session, redirect, url_for, Response
from functools import wraps
from utils.db_handler import (
    get_db_connection, check_email_exists, create_user, get_user_by_email,
    is_admin_user, create_admin, save_login_attempt, get_recent_failed_attempt_count,
    lock_account_by_user_id, is_account_locked, save_risk_assessment, save_explanation,
    get_all_login_attempts, get_all_explanations, create_security_alert, get_all_alerts,
    get_alert_by_id, lock_user_account, mark_alert_false_positive, get_user_login_history,
    get_all_users, unlock_user_account, get_enrolled_courses, get_course_by_id,
    enroll_user_in_all_courses, get_user_by_id, get_latest_risk_score,
    get_all_students_latest_risk, get_security_alerts_for_user, get_admin_dashboard_stats,
    get_all_admin_actions, update_user_password, get_login_attempts_for_export, get_report_data,
    submit_feedback, get_user_feedback
)
from utils.ml_engine import get_login_context, generate_risk_score, generate_explanation
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'codecraft_secret_key_2026'

ALERT_THRESHOLD = 95
MAX_FAILED_ATTEMPTS = 5
ALLOWED_EMAIL_DOMAINS = ['rjt.ac.lk', 'std.rjt.ac.lk', 'gmail.com']

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


def is_valid_email(email):
    return re.match(EMAIL_REGEX, email) is not None


def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-\[\]/\\+=~`]', password):
        return False
    return True


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            return "Access denied. Admins only. <a href='/login'>Login</a>"
        return f(*args, **kwargs)
    return decorated


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('is_admin'):
            return "Please login as a student. <a href='/login'>Login</a>"
        return f(*args, **kwargs)
    return decorated


# ---------- Home route ----------
@app.route('/')
def home():
    return render_template('home.html')


# ---------- Test route ----------
@app.route('/test-db')
def test_db():
    try:
        conn = get_db_connection()
        conn.close()
        return "✅ Database connection successful!"
    except Exception as e:
        return f"❌ Database connection failed: {str(e)}"


# ---------- Register route ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = None
    if request.method == 'POST':
        first_name = request.form['first_name']
        email = request.form['email'].strip()
        password = request.form['password']
        role = request.form.get('role', 'Student')

        email_domain = email.split('@')[-1].lower() if '@' in email else ''

        if not is_valid_email(email):
            message = "Please enter a valid email address (e.g., name@example.com)."
        elif email_domain not in ALLOWED_EMAIL_DOMAINS:
            message = f"Registration failed. Please use an allowed institutional email (e.g., @{ALLOWED_EMAIL_DOMAINS[0]})."
        elif not is_strong_password(password):
            message = "Password must be at least 8 characters long and include a letter, a number, and a special character (e.g., @, #, $)."
        elif check_email_exists(email):
            message = "Account already exists with this email."
        else:
            hashed_password = generate_password_hash(password)

            if role == 'Admin':
                create_admin(first_name, "N/A", email, hashed_password)
            else:
                user_id = create_user(first_name, "N/A", email, hashed_password)
                enroll_user_in_all_courses(user_id)

            return redirect(url_for('login', registered='1'))

    return render_template('register.html', message=message)


# ---------- Unified Login route (Student + Admin) ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.args.get('registered') == '1':
        message = "Registration successful! Please login with your new account."

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user_by_email(email)

        if not user:
            message = "Invalid email or password."
            return render_template('login.html', message=message)

        admin_flag = is_admin_user(user['User_ID'])

        if admin_flag:
            if check_password_hash(user['Password'], password):
                session['user_id'] = user['User_ID']
                session['email'] = user['Email']
                session['first_name'] = user['First_name']
                session['is_admin'] = True
                return redirect(url_for('admin_dashboard'))
            else:
                message = "Invalid email or password."
                return render_template('login.html', message=message)

        if is_account_locked(user['User_ID']):
            message = "Your account has been locked due to multiple failed login attempts. Contact an administrator."
            return render_template('login.html', message=message)

        current_failed_count = get_recent_failed_attempt_count(user['User_ID'])
        context = get_login_context(request, user_id=user['User_ID'], failed_attempts=current_failed_count)

        if check_password_hash(user['Password'], password):
            login_id = save_login_attempt(
                user['User_ID'], context['IP_address'], context['User_agent'], 'Success'
            )

            risk_score, risk_level = generate_risk_score(context)
            risk_id = save_risk_assessment(login_id, risk_score, risk_level)

            summary, key_factors, confidence = generate_explanation(context)
            save_explanation(risk_id, summary, key_factors, confidence)

            if risk_score >= ALERT_THRESHOLD:
                alert_message = f"High Risk Login Detected - {user['Email']} (Risk {risk_score}%)"
                create_security_alert(risk_id, alert_message)

            session['user_id'] = user['User_ID']
            session['email'] = user['Email']
            session['first_name'] = user['First_name']
            session['is_admin'] = False

            return redirect(url_for('student_dashboard'))
        else:
            save_login_attempt(user['User_ID'], context['IP_address'], context['User_agent'], 'Failed')

            failed_count = get_recent_failed_attempt_count(user['User_ID'])
            if failed_count >= MAX_FAILED_ATTEMPTS:
                lock_account_by_user_id(user['User_ID'])
                message = "Too many failed attempts. Your account has been locked."
            else:
                remaining = MAX_FAILED_ATTEMPTS - failed_count
                message = f"Invalid email or password. {remaining} attempt(s) remaining before lockout."

    return render_template('login.html', message=message)


# ---------- Logout route ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# =====================================================
# ---------------- STUDENT ROUTES --------------------
# =====================================================

@app.route('/dashboard')
@student_required
def student_dashboard():
    history = get_user_login_history(session['user_id'])
    courses = get_enrolled_courses(session['user_id'])
    alerts = get_security_alerts_for_user(session['user_id'])
    return render_template(
        'student_dashboard.html',
        history=history, courses=courses, alerts=alerts,
        email=session['email'], first_name=session['first_name']
    )


@app.route('/profile')
@student_required
def profile():
    user = get_user_by_id(session['user_id'])
    risk = get_latest_risk_score(session['user_id'])
    return render_template('profile.html', user=user, risk=risk)


@app.route('/login-history')
@student_required
def login_history():
    history = get_user_login_history(session['user_id'])
    return render_template('login_history.html', history=history)


@app.route('/security-alerts')
@student_required
def security_alerts_student():
    alerts = get_security_alerts_for_user(session['user_id'])
    return render_template('security_alerts_student.html', alerts=alerts)


@app.route('/courses/<int:course_id>')
@student_required
def view_course(course_id):
    course = get_course_by_id(course_id, session['user_id'])
    if not course:
        return "You are not enrolled in this course, or it does not exist. <a href='/dashboard'>Back</a>"
    return render_template('course_content.html', course=course)


# ---------- Change Password route (Student + Admin) ----------
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return "Please login first. <a href='/login'>Login</a>"

    message = None
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        user = get_user_by_id(session['user_id'])

        if not check_password_hash(user['Password'], current_password):
            message = "Current password is incorrect."
        elif new_password != confirm_password:
            message = "New password and confirmation do not match."
        elif not is_strong_password(new_password):
            message = "New password must be at least 8 characters long and include a letter, a number, and a special character."
        else:
            hashed = generate_password_hash(new_password)
            update_user_password(session['user_id'], hashed)
            message = "Password updated successfully."

    return render_template('change_password.html', message=message)


@app.route('/feedback', methods=['GET', 'POST'])
@student_required
def feedback():
    message = None
    if request.method == 'POST':
        feedback_text = request.form.get('feedback_text', '').strip()
        if feedback_text:
            submit_feedback(session['user_id'], feedback_text)
            message = "Thank you! Your feedback has been submitted."
        else:
            message = "Feedback cannot be empty."

    history = get_user_feedback(session['user_id'])
    return render_template('feedback.html', message=message, history=history)


# =====================================================
# ----------------- ADMIN ROUTES ----------------------
# =====================================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = get_admin_dashboard_stats()
    return render_template('admin_dashboard.html', stats=stats)


@app.route('/admin/login-attempts')
@admin_required
def admin_login_attempts():
    attempts = get_all_login_attempts()
    return render_template('login_attempts.html', attempts=attempts)


@app.route('/admin/risk-scores')
@admin_required
def admin_risk_scores():
    scores = get_all_students_latest_risk()
    return render_template('admin_risk_scores.html', scores=scores)


@app.route('/admin/explanations')
@admin_required
def admin_explanations():
    explanations = get_all_explanations()
    return render_template('explanation_summary.html', explanations=explanations)


@app.route('/admin/alerts')
@admin_required
def admin_alerts():
    alerts = get_all_alerts()
    return render_template('security_alerts.html', alerts=alerts)


@app.route('/admin/review/<int:alert_id>')
@admin_required
def review_alert(alert_id):
    alert = get_alert_by_id(alert_id)
    return render_template('review_alert.html', alert=alert, message=None)


@app.route('/admin/lock/<int:alert_id>', methods=['POST'])
@admin_required
def lock_account(alert_id):
    alert = get_alert_by_id(alert_id)
    if alert:
        lock_user_account(alert['User_ID'], admin_id=session['user_id'])
        message = f"Account for {alert['Email']} has been locked."
    else:
        message = "Alert not found."
    return render_template('review_alert.html', alert=alert, message=message)


@app.route('/admin/false-positive/<int:alert_id>', methods=['POST'])
@admin_required
def false_positive(alert_id):
    alert = get_alert_by_id(alert_id)
    if alert:
        mark_alert_false_positive(alert_id, admin_id=session['user_id'], target_user_id=alert['User_ID'])
        message = "Alert marked as false positive."
    else:
        message = "Alert not found."
    return render_template('review_alert.html', alert=alert, message=message)


@app.route('/admin/users')
@admin_required
def manage_users():
    users = get_all_users()
    return render_template('manage_users.html', users=users, message=None)


@app.route('/admin/unlock/<int:user_id>', methods=['POST'])
@admin_required
def unlock_account(user_id):
    unlock_user_account(user_id, admin_id=session['user_id'])
    users = get_all_users()
    return render_template('manage_users.html', users=users, message="Account unlocked successfully.")


@app.route('/admin/audit-log')
@admin_required
def audit_log():
    actions = get_all_admin_actions()
    return render_template('audit_log.html', actions=actions)


@app.route('/admin/export')
@admin_required
def export_data():
    start_date = request.args.get('start_date') or None
    end_date = request.args.get('end_date') or None
    risk_level = request.args.get('risk_level') or None

    data = get_login_attempts_for_export(start_date, end_date, risk_level)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Login ID', 'Email', 'Login Time', 'IP Address', 'Status', 'Risk Score', 'Risk Level'])
    for row in data:
        writer.writerow([
            row['Login_ID'], row['Email'], row['Login_time'], row['IP_address'],
            row['Login_status'],
            row['Risk_score'] if row['Risk_score'] is not None else '',
            row['Risk_level'] if row['Risk_level'] is not None else ''
        ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=login_attempts_export.csv'}
    )


@app.route('/admin/export-form')
@admin_required
def export_form():
    return render_template('export_data.html')


@app.route('/admin/reports', methods=['GET'])
@admin_required
def generate_reports():
    start_date = request.args.get('start_date') or None
    end_date = request.args.get('end_date') or None
    risk_level = request.args.get('risk_level') or None

    report = None
    if start_date or end_date or risk_level or request.args.get('generated') == '1':
        report = get_report_data(start_date, end_date, risk_level)

    return render_template(
        'generate_reports.html', report=report,
        start_date=start_date, end_date=end_date, risk_level=risk_level
    )


# ---------- Run the app ----------
if __name__ == '__main__':
    app.run(debug=False, port=9000)