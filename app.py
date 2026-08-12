import re
import csv
import io
import os

from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    Response
)

from werkzeug.utils import secure_filename
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from utils.db_handler import (
    get_db_connection,
    check_email_exists,
    create_user,
    get_user_by_email,
    is_admin_user,
    create_admin,
    save_login_attempt,
    get_recent_failed_attempt_count,
    lock_account_by_user_id,
    is_account_locked,
    save_risk_assessment,
    save_explanation,
    get_all_login_attempts,
    get_all_explanations,
    create_security_alert,
    get_all_alerts,
    get_alert_by_id,
    lock_user_account,
    mark_alert_false_positive,
    get_user_login_history,
    get_all_users,
    unlock_user_account,
    get_enrolled_courses,
    get_course_by_id,
    enroll_user_in_all_courses,
    get_user_by_id,
    get_latest_risk_score,
    get_all_students_latest_risk,
    get_security_alerts_for_user,
    get_admin_dashboard_stats,
    get_all_admin_actions,
    update_user_password,
    get_login_attempts_for_export,
    get_report_data,
    submit_feedback,
    get_user_feedback,
    update_user_profile,

    is_super_admin,
    get_admin_approval_status,
    get_pending_admins,
    approve_admin,
    save_admin_otp,
    verify_admin_otp,
    get_admin_name_email,
    reject_admin_with_reason,
    get_rejection_log,

    # Forgot Password
    save_password_reset_otp,
    verify_password_reset_otp,
    reset_user_password
)

from utils.ml_engine import (
    get_login_context,
    generate_risk_score,
    generate_explanation
)

from utils.mailer import (
    generate_otp,
    send_otp_email
)


# =====================================================
# FLASK APP CONFIGURATION
# =====================================================

app = Flask(__name__)

app.secret_key = 'codecraft_secret_key_2026'


# =====================================================
# SECURITY SETTINGS
# =====================================================

ALERT_THRESHOLD = 80

MAX_FAILED_ATTEMPTS = 5

ALLOWED_EMAIL_DOMAINS = [
    'rjt.ac.lk',
    'std.rjt.ac.lk',
    'gmail.com'
]


# =====================================================
# REGEX
# =====================================================

EMAIL_REGEX = (
    r'^[a-zA-Z0-9._%+-]+'
    r'@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

PASSWORD_SPECIAL_REGEX = (
    r'[!@#$%^&*(),.?":{}|<>_\-\\[\]/+=~`]'
)


# =====================================================
# PROFILE IMAGE SETTINGS
# =====================================================

UPLOAD_FOLDER = os.path.join(
    'static',
    'uploads'
)

ALLOWED_IMAGE_EXTENSIONS = {
    'png',
    'jpg',
    'jpeg'
}

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def allowed_image_file(filename):

    return (
        '.' in filename
        and filename.rsplit(
            '.',
            1
        )[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


def is_valid_email(email):

    return (
        re.match(
            EMAIL_REGEX,
            email
        )
        is not None
    )


def is_strong_password(password):

    if len(password) < 8:
        return False

    if not re.search(
        r'[A-Za-z]',
        password
    ):
        return False

    if not re.search(
        r'[0-9]',
        password
    ):
        return False

    if not re.search(
        PASSWORD_SPECIAL_REGEX,
        password
    ):
        return False

    return True


# =====================================================
# LOGIN DECORATORS
# =====================================================

def admin_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        if (
            'user_id' not in session
            or not session.get('is_admin')
        ):
            return (
                "Access denied. Admins only. "
                "<a href='/login'>Login</a>"
            )

        return f(
            *args,
            **kwargs
        )

    return decorated


def student_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        if (
            'user_id' not in session
            or session.get('is_admin')
        ):
            return (
                "Please login as a student. "
                "<a href='/login'>Login</a>"
            )

        return f(
            *args,
            **kwargs
        )

    return decorated


def super_admin_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        if (
            'user_id' not in session
            or not session.get('is_super_admin')
        ):
            return (
                "Access denied. Super Admins only. "
                "<a href='/admin'>Back</a>"
            )

        return f(
            *args,
            **kwargs
        )

    return decorated


# =====================================================
# HOME ROUTE
# =====================================================

@app.route('/')
def home():

    return render_template(
        'home.html'
    )


# =====================================================
# TEST DATABASE ROUTE
# =====================================================

@app.route('/test-db')
def test_db():

    try:

        conn = get_db_connection()

        conn.close()

        return (
            "✅ Database connection successful!"
        )

    except Exception as e:

        return (
            f"❌ Database connection failed: "
            f"{str(e)}"
        )


# =====================================================
# REGISTER ROUTE
# =====================================================

@app.route(
    '/register',
    methods=['GET', 'POST']
)
def register():

    message = None

    if request.method == 'POST':

        first_name = request.form.get(
            'first_name',
            ''
        ).strip()

        email = request.form.get(
            'email',
            ''
        ).strip()

        password = request.form.get(
            'password',
            ''
        )

        role = request.form.get(
            'role',
            'Student'
        )

        email_domain = (
            email.split('@')[-1].lower()
            if '@' in email
            else ''
        )

        if not first_name:

            message = (
                "First name cannot be empty."
            )

        elif not is_valid_email(email):

            message = (
                "Please enter a valid email address "
                "(e.g., name@example.com)."
            )

        elif email_domain not in ALLOWED_EMAIL_DOMAINS:

            message = (
                "Registration failed. Please use "
                "an allowed institutional email "
                f"(e.g., @{ALLOWED_EMAIL_DOMAINS[0]})."
            )

        elif not is_strong_password(password):

            message = (
                "Password must be at least 8 characters "
                "long and include a letter, a number, "
                "and a special character."
            )

        elif check_email_exists(email):

            message = (
                "Account already exists with this email."
            )

        else:

            hashed_password = generate_password_hash(
                password
            )

            if role == 'Admin':

                create_admin(
                    first_name,
                    "N/A",
                    email,
                    hashed_password
                )

                return redirect(
                    url_for(
                        'login',
                        admin_pending='1'
                    )
                )

            else:

                user_id = create_user(
                    first_name,
                    "N/A",
                    email,
                    hashed_password
                )

                enroll_user_in_all_courses(
                    user_id
                )

                return redirect(
                    url_for(
                        'login',
                        registered='1'
                    )
                )

    return render_template(
        'register.html',
        message=message
    )


# =====================================================
# LOGIN ROUTE
# STUDENT + ADMIN
# =====================================================

@app.route(
    '/login',
    methods=['GET', 'POST']
)
def login():

    message = None

    if request.args.get('registered') == '1':

        message = (
            "Registration successful! "
            "Please login with your new account."
        )

    elif request.args.get('admin_pending') == '1':

        message = (
            "Admin registration submitted. "
            "Your account is pending approval "
            "by a Super Admin."
        )

    elif request.args.get('reset') == '1':

        message = (
            "Password reset successful! "
            "Please login with your new password."
        )

    if request.method == 'POST':

        email = request.form.get(
            'email',
            ''
        ).strip()

        password = request.form.get(
            'password',
            ''
        )

        user = get_user_by_email(
            email
        )

        if not user:

            message = (
                "Invalid email or password."
            )

            return render_template(
                'login.html',
                message=message
            )

        admin_flag = is_admin_user(
            user['User_ID']
        )

        # =================================================
        # ADMIN LOGIN
        # =================================================

        if admin_flag:

            if check_password_hash(
                user['Password'],
                password
            ):

                approval_status = (
                    get_admin_approval_status(
                        user['User_ID']
                    )
                )

                if approval_status == 'OTP_Sent':

                    message = (
                        "Your email verification is pending. "
                        "Check your inbox for the code, or ask "
                        "a Super Admin to resend it."
                    )

                    return render_template(
                        'login.html',
                        message=message
                    )

                elif approval_status != 'Approved':

                    message = (
                        "Your admin account is pending "
                        "approval by a Super Admin."
                    )

                    return render_template(
                        'login.html',
                        message=message
                    )

                session['user_id'] = (
                    user['User_ID']
                )

                session['email'] = (
                    user['Email']
                )

                session['first_name'] = (
                    user['First_name']
                )

                session['is_admin'] = True

                session['is_super_admin'] = (
                    is_super_admin(
                        user['User_ID']
                    )
                )

                return redirect(
                    url_for(
                        'admin_dashboard'
                    )
                )

            else:

                message = (
                    "Invalid email or password."
                )

                return render_template(
                    'login.html',
                    message=message
                )

        # =================================================
        # STUDENT LOGIN
        # =================================================

        if is_account_locked(
            user['User_ID']
        ):

            message = (
                "Your account has been locked due "
                "to multiple failed login attempts. "
                "Contact an administrator."
            )

            return render_template(
                'login.html',
                message=message
            )

        context = get_login_context(
            request
        )

        if check_password_hash(
            user['Password'],
            password
        ):

            login_id = save_login_attempt(
                user['User_ID'],
                context['IP_address'],
                context['User_agent'],
                'Success'
            )

            risk_score, risk_level = (
                generate_risk_score(
                    context
                )
            )

            risk_id = save_risk_assessment(
                login_id,
                risk_score,
                risk_level
            )

            summary, key_factors, confidence = (
                generate_explanation(
                    context
                )
            )

            save_explanation(
                risk_id,
                summary,
                key_factors,
                confidence
            )

            if risk_score >= ALERT_THRESHOLD:

                alert_message = (
                    "High Risk Login Detected - "
                    f"{user['Email']} "
                    f"(Risk {risk_score}%)"
                )

                create_security_alert(
                    risk_id,
                    alert_message
                )

            session['user_id'] = (
                user['User_ID']
            )

            session['email'] = (
                user['Email']
            )

            session['first_name'] = (
                user['First_name']
            )

            session['is_admin'] = False

            session['is_super_admin'] = False

            return redirect(
                url_for(
                    'student_dashboard'
                )
            )

        else:

            save_login_attempt(
                user['User_ID'],
                context['IP_address'],
                context['User_agent'],
                'Failed'
            )

            failed_count = (
                get_recent_failed_attempt_count(
                    user['User_ID']
                )
            )

            if failed_count >= MAX_FAILED_ATTEMPTS:

                lock_account_by_user_id(
                    user['User_ID']
                )

                message = (
                    "Too many failed attempts. "
                    "Your account has been locked."
                )

            else:

                remaining = (
                    MAX_FAILED_ATTEMPTS
                    - failed_count
                )

                message = (
                    "Invalid email or password. "
                    f"{remaining} attempt(s) remaining "
                    "before lockout."
                )

    return render_template(
        'login.html',
        message=message
    )


# =====================================================
# FORGOT PASSWORD
# =====================================================

@app.route(
    '/forgot-password',
    methods=['GET', 'POST']
)
def forgot_password():

    message = None

    if request.method == 'POST':

        email = request.form.get(
            'email',
            ''
        ).strip()

        if not email:

            message = (
                "Please enter your email address."
            )

        elif not is_valid_email(email):

            message = (
                "Please enter a valid email address."
            )

        else:

            user = get_user_by_email(
                email
            )

            if not user:

                message = (
                    "No account was found with "
                    "this email address."
                )

            else:

                otp = generate_otp()

                save_password_reset_otp(
                    email,
                    otp,
                    expiry_minutes=10
                )

                success, mode = send_otp_email(
                    user['Email'],
                    user['First_name'],
                    otp
                )

                if mode == "console":

                    message = (
                        f"OTP generated for {email}. "
                        "SMTP is not configured. "
                        f"Demo OTP: {otp}"
                    )

                else:

                    message = (
                        "Verification code sent "
                        "to your email."
                    )

                return render_template(
                    'reset_password.html',
                    email=email,
                    message=message
                )

    return render_template(
        'forgot_password.html',
        message=message
    )


# =====================================================
# RESET PASSWORD
# =====================================================

@app.route(
    '/reset-password',
    methods=['GET', 'POST']
)
def reset_password():

    message = None

    email = request.args.get(
        'email',
        ''
    )

    if request.method == 'POST':

        email = request.form.get(
            'email',
            ''
        ).strip()

        otp_code = request.form.get(
            'otp_code',
            ''
        ).strip()

        new_password = request.form.get(
            'new_password',
            ''
        )

        confirm_password = request.form.get(
            'confirm_password',
            ''
        )

        if not email:

            message = (
                "Please enter your email."
            )

        elif not otp_code:

            message = (
                "Please enter the verification code."
            )

        elif not new_password:

            message = (
                "Please enter a new password."
            )

        elif new_password != confirm_password:

            message = (
                "New password and confirmation "
                "do not match."
            )

        elif not is_strong_password(
            new_password
        ):

            message = (
                "Password must be at least 8 "
                "characters long and include "
                "a letter, a number, and a "
                "special character."
            )

        else:

            valid, otp_message = (
                verify_password_reset_otp(
                    email,
                    otp_code
                )
            )

            if not valid:

                message = otp_message

            else:

                hashed_password = (
                    generate_password_hash(
                        new_password
                    )
                )

                reset_user_password(
                    email,
                    hashed_password
                )

                return redirect(
                    url_for(
                        'login',
                        reset='1'
                    )
                )

    return render_template(
        'reset_password.html',
        email=email,
        message=message
    )


# =====================================================
# PUBLIC ADMIN OTP VERIFICATION
# =====================================================

@app.route(
    '/verify-admin-email',
    methods=['GET', 'POST']
)
def verify_admin_email():

    message = None
    success = False

    if request.method == 'POST':

        email = request.form.get(
            'email',
            ''
        ).strip()

        otp_code = request.form.get(
            'otp_code',
            ''
        ).strip()

        success, message = (
            verify_admin_otp(
                email,
                otp_code
            )
        )

    return render_template(
        'verify_admin_email.html',
        message=message,
        success=success
    )


# =====================================================
# LOGOUT
# =====================================================

@app.route('/logout')
def logout():

    session.clear()

    return redirect(
        url_for('home')
    )


# =====================================================
# STUDENT ROUTES
# =====================================================

@app.route('/dashboard')
@student_required
def student_dashboard():

    history = get_user_login_history(
        session['user_id']
    )

    courses = get_enrolled_courses(
        session['user_id']
    )

    alerts = get_security_alerts_for_user(
        session['user_id']
    )

    return render_template(
        'student_dashboard.html',
        history=history,
        courses=courses,
        alerts=alerts,
        email=session['email'],
        first_name=session['first_name']
    )


@app.route('/profile')
@student_required
def profile():

    user = get_user_by_id(
        session['user_id']
    )

    risk = get_latest_risk_score(
        session['user_id']
    )

    return render_template(
        'profile.html',
        user=user,
        risk=risk
    )


@app.route(
    '/profile/edit',
    methods=['GET', 'POST']
)
@student_required
def edit_profile():

    message = None

    user = get_user_by_id(
        session['user_id']
    )

    if request.method == 'POST':

        first_name = request.form.get(
            'first_name',
            ''
        ).strip()

        email = request.form.get(
            'email',
            ''
        ).strip()

        if not first_name:

            message = (
                "Name cannot be empty."
            )

        elif not is_valid_email(email):

            message = (
                "Please enter a valid email address."
            )

        else:

            profile_image_filename = None

            file = request.files.get(
                'profile_image'
            )

            if file and file.filename:

                if allowed_image_file(
                    file.filename
                ):

                    filename = secure_filename(
                        f"user_"
                        f"{session['user_id']}_"
                        f"{file.filename}"
                    )

                    file.save(
                        os.path.join(
                            UPLOAD_FOLDER,
                            filename
                        )
                    )

                    profile_image_filename = (
                        filename
                    )

                else:

                    message = (
                        "Invalid image format. "
                        "Only PNG, JPG, JPEG allowed."
                    )

                    return render_template(
                        'edit_profile.html',
                        user=user,
                        message=message
                    )

            update_user_profile(
                session['user_id'],
                first_name,
                email,
                profile_image_filename
            )

            session['email'] = email

            session['first_name'] = (
                first_name
            )

            return redirect(
                url_for('profile')
            )

    return render_template(
        'edit_profile.html',
        user=user,
        message=message
    )


@app.route('/login-history')
@student_required
def login_history():

    history = get_user_login_history(
        session['user_id']
    )

    return render_template(
        'login_history.html',
        history=history
    )


@app.route('/security-alerts')
@student_required
def security_alerts_student():

    alerts = get_security_alerts_for_user(
        session['user_id']
    )

    return render_template(
        'security_alerts_student.html',
        alerts=alerts
    )


@app.route(
    '/courses/<int:course_id>'
)
@student_required
def view_course(course_id):

    course = get_course_by_id(
        course_id,
        session['user_id']
    )

    if not course:

        return (
            "You are not enrolled in this course, "
            "or it does not exist. "
            "<a href='/dashboard'>Back</a>"
        )

    return render_template(
        'course_content.html',
        course=course
    )


# =====================================================
# CHANGE PASSWORD
# =====================================================

@app.route(
    '/change-password',
    methods=['GET', 'POST']
)
def change_password():

    if 'user_id' not in session:

        return (
            "Please login first. "
            "<a href='/login'>Login</a>"
        )

    message = None

    if request.method == 'POST':

        current_password = request.form.get(
            'current_password',
            ''
        )

        new_password = request.form.get(
            'new_password',
            ''
        )

        confirm_password = request.form.get(
            'confirm_password',
            ''
        )

        user = get_user_by_id(
            session['user_id']
        )

        if not check_password_hash(
            user['Password'],
            current_password
        ):

            message = (
                "Current password is incorrect."
            )

        elif new_password != confirm_password:

            message = (
                "New password and confirmation "
                "do not match."
            )

        elif not is_strong_password(
            new_password
        ):

            message = (
                "New password must be at least "
                "8 characters long and include "
                "a letter, a number, and a "
                "special character."
            )

        else:

            hashed = generate_password_hash(
                new_password
            )

            update_user_password(
                session['user_id'],
                hashed
            )

            message = (
                "Password updated successfully."
            )

    return render_template(
        'change_password.html',
        message=message
    )


# =====================================================
# FEEDBACK
# =====================================================

@app.route(
    '/feedback',
    methods=['GET', 'POST']
)
@student_required
def feedback():

    message = None

    if request.method == 'POST':

        feedback_text = request.form.get(
            'feedback_text',
            ''
        ).strip()

        if feedback_text:

            submit_feedback(
                session['user_id'],
                feedback_text
            )

            message = (
                "Thank you! Your feedback "
                "has been submitted."
            )

        else:

            message = (
                "Feedback cannot be empty."
            )

    history = get_user_feedback(
        session['user_id']
    )

    return render_template(
        'feedback.html',
        message=message,
        history=history
    )


# =====================================================
# ADMIN ROUTES
# =====================================================

@app.route('/admin')
@admin_required
def admin_dashboard():

    stats = get_admin_dashboard_stats()

    return render_template(
        'admin_dashboard.html',
        stats=stats
    )


@app.route('/admin/login-attempts')
@admin_required
def admin_login_attempts():

    attempts = get_all_login_attempts()

    return render_template(
        'login_attempts.html',
        attempts=attempts
    )


@app.route('/admin/risk-scores')
@admin_required
def admin_risk_scores():

    scores = get_all_students_latest_risk()

    return render_template(
        'admin_risk_scores.html',
        scores=scores
    )


@app.route('/admin/explanations')
@admin_required
def admin_explanations():

    explanations = get_all_explanations()

    return render_template(
        'explanation_summary.html',
        explanations=explanations
    )


@app.route('/admin/alerts')
@admin_required
def admin_alerts():

    alerts = get_all_alerts()

    return render_template(
        'security_alerts.html',
        alerts=alerts
    )


@app.route(
    '/admin/review/<int:alert_id>'
)
@admin_required
def review_alert(alert_id):

    alert = get_alert_by_id(
        alert_id
    )

    return render_template(
        'review_alert.html',
        alert=alert,
        message=None
    )


@app.route(
    '/admin/lock/<int:alert_id>',
    methods=['POST']
)
@admin_required
def lock_account(alert_id):

    alert = get_alert_by_id(
        alert_id
    )

    if alert:

        lock_user_account(
            alert['User_ID'],
            admin_id=session['user_id']
        )

        message = (
            f"Account for {alert['Email']} "
            "has been locked."
        )

    else:

        message = (
            "Alert not found."
        )

    return render_template(
        'review_alert.html',
        alert=alert,
        message=message
    )


@app.route(
    '/admin/false-positive/<int:alert_id>',
    methods=['POST']
)
@admin_required
def false_positive(alert_id):

    alert = get_alert_by_id(
        alert_id
    )

    if alert:

        mark_alert_false_positive(
            alert_id,
            admin_id=session['user_id'],
            target_user_id=alert['User_ID']
        )

        message = (
            "Alert marked as false positive."
        )

    else:

        message = (
            "Alert not found."
        )

    return render_template(
        'review_alert.html',
        alert=alert,
        message=message
    )


@app.route('/admin/users')
@admin_required
def manage_users():

    users = get_all_users()

    return render_template(
        'manage_users.html',
        users=users,
        message=None
    )


@app.route(
    '/admin/unlock/<int:user_id>',
    methods=['POST']
)
@admin_required
def unlock_account(user_id):

    unlock_user_account(
        user_id,
        admin_id=session['user_id']
    )

    users = get_all_users()

    return render_template(
        'manage_users.html',
        users=users,
        message="Account unlocked successfully."
    )


@app.route('/admin/audit-log')
@admin_required
def audit_log():

    actions = get_all_admin_actions()

    return render_template(
        'audit_log.html',
        actions=actions
    )


# =====================================================
# ADMIN EXPORT
# =====================================================

@app.route('/admin/export')
@admin_required
def export_data():

    start_date = (
        request.args.get('start_date')
        or None
    )

    end_date = (
        request.args.get('end_date')
        or None
    )

    risk_level = (
        request.args.get('risk_level')
        or None
    )

    data = get_login_attempts_for_export(
        start_date,
        end_date,
        risk_level
    )

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        'Login ID',
        'Email',
        'Login Time',
        'IP Address',
        'Status',
        'Risk Score',
        'Risk Level'
    ])

    for row in data:

        writer.writerow([
            row['Login_ID'],
            row['Email'],
            row['Login_time'],
            row['IP_address'],
            row['Login_status'],
            (
                row['Risk_score']
                if row['Risk_score'] is not None
                else ''
            ),
            (
                row['Risk_level']
                if row['Risk_level'] is not None
                else ''
            )
        ])

    csv_data = output.getvalue()

    output.close()

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={
            'Content-Disposition':
                'attachment; '
                'filename=login_attempts_export.csv'
        }
    )


@app.route('/admin/export-form')
@admin_required
def export_form():

    return render_template(
        'export_data.html'
    )


# =====================================================
# ADMIN REPORTS
# =====================================================

@app.route(
    '/admin/reports',
    methods=['GET']
)
@admin_required
def generate_reports():

    start_date = (
        request.args.get('start_date')
        or None
    )

    end_date = (
        request.args.get('end_date')
        or None
    )

    risk_level = (
        request.args.get('risk_level')
        or None
    )

    report = None

    if (
        start_date
        or end_date
        or risk_level
        or request.args.get('generated') == '1'
    ):

        report = get_report_data(
            start_date,
            end_date,
            risk_level
        )

    return render_template(
        'generate_reports.html',
        report=report,
        start_date=start_date,
        end_date=end_date,
        risk_level=risk_level
    )


# =====================================================
# SUPER ADMIN ROUTES
# =====================================================

@app.route('/admin/pending-admins')
@super_admin_required
def pending_admins():

    pending = get_pending_admins()

    return render_template(
        'pending_admins.html',
        pending=pending,
        message=None
    )


@app.route(
    '/admin/approve/<int:user_id>',
    methods=['POST']
)
@super_admin_required
def approve_admin_route(user_id):

    approve_admin(
        user_id,
        approver_id=session['user_id']
    )

    pending = get_pending_admins()

    return render_template(
        'pending_admins.html',
        pending=pending,
        message="Admin account approved."
    )


@app.route(
    '/admin/send-otp/<int:user_id>',
    methods=['POST']
)
@super_admin_required
def send_otp_route(user_id):

    person = get_admin_name_email(
        user_id
    )

    if not person:

        message = (
            "Admin request not found."
        )

    else:

        otp = generate_otp()

        save_admin_otp(
            user_id,
            otp
        )

        success, mode = send_otp_email(
            person['Email'],
            person['First_name'],
            otp
        )

        if mode == "console":

            message = (
                f"OTP generated for "
                f"{person['Email']}. "
                "SMTP not configured — "
                f"demo OTP: {otp} "
                "(also printed to server console)."
            )

        else:

            message = (
                f"Verification code sent to "
                f"{person['Email']}."
            )

    pending = get_pending_admins()

    return render_template(
        'pending_admins.html',
        pending=pending,
        message=message
    )


@app.route(
    '/admin/reject/<int:user_id>',
    methods=['POST']
)
@super_admin_required
def reject_admin_route(user_id):

    reason = request.form.get(
        'reason',
        ''
    ).strip()

    if not reason:

        pending = get_pending_admins()

        return render_template(
            'pending_admins.html',
            pending=pending,
            message=(
                "Rejection requires a reason. "
                "Please provide evidence/justification."
            )
        )

    reject_admin_with_reason(
        user_id,
        approver_id=session['user_id'],
        reason=reason
    )

    pending = get_pending_admins()

    return render_template(
        'pending_admins.html',
        pending=pending,
        message=(
            "Admin request rejected and logged."
        )
    )


@app.route('/admin/rejection-log')
@super_admin_required
def rejection_log():

    log = get_rejection_log()

    return render_template(
        'rejection_log.html',
        log=log
    )


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == '__main__':

    app.run(
        debug=False,
        port=9000
    )