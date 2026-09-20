import re
import csv
import io
import os
import smtplib
import random
import subprocess
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from functools import wraps

from cryptography.fernet import Fernet, InvalidToken

from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    Response,
    send_from_directory
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
    get_system_monitoring_stats,
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

    # Admin login 2FA (separate from registration-approval OTP)
    save_admin_login_otp,
    verify_admin_login_otp,

    # Forgot Password
    save_password_reset_otp,
    verify_password_reset_otp,
    reset_user_password,
    check_and_update_reset_rate_limit,

    # System Settings & Notifications & Import
    get_setting,
    get_all_settings,
    update_setting,
    create_notification,
    get_user_notifications,
    mark_notifications_read,
    get_unread_count,
    bulk_import_courses
)

from utils.ml_engine import (
    get_login_context,
    generate_risk_score,
    generate_explanation
)

# =====================================================
# EMAIL CONFIGURATION (OTP)
# =====================================================

# ⚠️ DEMO CONFIG — replace with real SMTP credentials for production use.
# Leave blank to run in "console mode": OTP is printed to the server
# terminal only (never shown in the browser), so the flow can still be
# demoed end-to-end without a live inbox, without leaking the code to
# whoever is looking at the page.
SENDER_EMAIL = "codecraft678@gmail.com"       # e.g. "codecraft.security@gmail.com"
SENDER_PASSWORD = "ivkg ycxp txzd jiwv"    # e.g. Gmail App Password (not your normal password)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))


def send_otp_email(to_email, name, otp_code):
    """
    Sends the OTP to the user's email.
    Returns (success: bool, mode: str) — mode is 'sent' or 'console'.
    The OTP value is NEVER returned to the caller for display in the UI —
    it is only ever printed to the server console in demo mode.
    """
    subject = "CodeCraft Verification Code"
    body = (
        f"Hello {name},\n\n"
        f"Your CodeCraft verification code is: {otp_code}\n\n"
        f"This code expires in 10 minutes. If you did not request this, "
        f"please ignore this email.\n\n"
        f"— CodeCraft Security Team"
    )

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        # Console/demo mode — no real SMTP configured.
        # OTP is printed to the SERVER TERMINAL ONLY — never sent back
        # to the browser/user-facing response.
        print(f"\n[DEMO MODE] OTP for {to_email}: {otp_code}\n")
        return True, "console"

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [to_email], msg.as_string())
        return True, "sent"
    except Exception as e:
        print(f"[MAIL ERROR] {e} — falling back to console mode")
        print(f"[DEMO MODE] OTP for {to_email}: {otp_code}\n")
        return True, "console"


# =====================================================
# FLASK APP CONFIGURATION
# =====================================================

app = Flask(__name__)

app.secret_key = 'codecraft_secret_key_2026'

# Used to display server uptime on the System Monitoring page.
APP_START_TIME = datetime.now()

# Auto-logout after this much continuous inactivity.
app.permanent_session_lifetime = timedelta(minutes=15)


# =====================================================
# SECURITY SETTINGS
# =====================================================

# NOTE: ALERT_THRESHOLD is now fetched dynamically from the DB
# via get_setting('alert_threshold_admin', 80)

MAX_FAILED_ATTEMPTS = 5

# Only official campus email addresses may register/login.
# (Generic providers like gmail.com/yahoo.com etc. are intentionally
# NOT allowed anymore.)
ALLOWED_EMAIL_DOMAINS = [
    'as.rjt.ac.lk',
    'std.rjt.ac.lk'
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
# DATA BACKUP SETTINGS
# =====================================================

BACKUP_FOLDER = 'backups'

# The encryption key is generated once and stored locally — it is
# NEVER committed to git (add backup.key and backups/ to .gitignore).
# Anyone with this key can decrypt your backups, so treat it like a
# password.
BACKUP_KEY_PATH = 'backup.key'

# ⚠️ If mysqldump is not on your system PATH, replace this with the
# full path, e.g.:
# r"C:\xampp\mysql\bin\mysqldump.exe"
# r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"
MYSQLDUMP_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"

# The mysql client (used for restoring) lives in the same bin folder
# as mysqldump.
MYSQL_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

# Must match the credentials used in utils/db_handler.py get_db_connection()
DB_BACKUP_HOST = 'localhost'
DB_BACKUP_USER = 'root'
DB_BACKUP_PASSWORD = 'root'
DB_BACKUP_NAME = 'codecraft_db'

os.makedirs(
    BACKUP_FOLDER,
    exist_ok=True
)


def get_or_create_backup_key():
    """
    Loads the Fernet encryption key from disk, generating and
    saving a new one on first use.
    """
    if os.path.exists(BACKUP_KEY_PATH):
        with open(BACKUP_KEY_PATH, 'rb') as f:
            return f.read()

    key = Fernet.generate_key()

    with open(BACKUP_KEY_PATH, 'wb') as f:
        f.write(key)

    return key


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
                "Registration failed. Only official campus email "
                "addresses are allowed "
                f"(e.g., @{ALLOWED_EMAIL_DOMAINS[0]} or "
                f"@{ALLOWED_EMAIL_DOMAINS[1]})."
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
                    # Send them straight to the email-verification
                    # page instead of leaving them stuck on /login.
                    return redirect(
                        url_for(
                            'verify_admin_email',
                            email=email
                        )
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

                # ---- Super Admins skip the login-time OTP step  ----
                # ---- entirely — they log in directly, since they ----
                # ---- are the ones who approve/send OTPs to other ----
                # ---- admins in the first place.                  ----
                if is_super_admin(
                    user['User_ID']
                ):
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

                    session['is_super_admin'] = True

                    session.permanent = True

                    return redirect(
                        url_for(
                            'admin_dashboard'
                        )
                    )

                # ---- Regular (non-super) admin is approved:      ----
                # ---- password correct, but we still require a    ----
                # ---- fresh login-time OTP (2FA) before creating   ----
                # ---- the actual session.                         ----
                otp = generate_otp()

                save_admin_login_otp(
                    user['User_ID'],
                    otp
                )

                send_otp_email(
                    user['Email'],
                    user['First_name'],
                    otp
                )

                # Temporary marker — NOT a real logged-in session yet.
                session['pending_admin_id'] = user['User_ID']

                return redirect(
                    url_for(
                        'admin_login_verify'
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

            # ---- Dynamic alert threshold from DB ----
            admin_threshold = float(
                get_setting(
                    'alert_threshold_admin',
                    80
                ) or 80
            )

            if risk_score >= admin_threshold:
                alert_message = (
                    "High Risk Login Detected - "
                    f"{user['Email']} "
                    f"(Risk {risk_score}%)"
                )

                create_security_alert(
                    risk_id,
                    alert_message
                )

                create_notification(
                    user['User_ID'],
                    f"A high-risk login was detected on your account (Risk {risk_score}%). Please review your activity."
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

            # Enable inactivity-based auto-logout for this session
            session.permanent = True

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

                create_notification(
                    user['User_ID'],
                    "Your account was locked due to multiple failed login attempts. Contact an administrator to unlock it."
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
# ADMIN LOGIN — OTP VERIFICATION (2FA, every login)
# =====================================================

@app.route(
    '/admin/login-verify',
    methods=['GET', 'POST']
)
def admin_login_verify():
    message = None

    # No admin currently mid-login -> nothing to verify, back to login.
    if 'pending_admin_id' not in session:
        return redirect(
            url_for('login')
        )

    if request.method == 'POST':
        otp_code = request.form.get(
            'otp_code',
            ''
        ).strip()

        pending_user_id = session[
            'pending_admin_id'
        ]

        valid, otp_message = (
            verify_admin_login_otp(
                pending_user_id,
                otp_code
            )
        )

        if not valid:
            message = otp_message

            return render_template(
                'admin_login_verify.html',
                message=message
            )

        # OTP correct — now create the real session.
        user = get_user_by_id(
            pending_user_id
        )

        session.pop(
            'pending_admin_id',
            None
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

        session.permanent = True

        return redirect(
            url_for(
                'admin_dashboard'
            )
        )

    return render_template(
        'admin_login_verify.html',
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
                # ---- Rate limit: max N requests per window ----
                allowed, wait_message = check_and_update_reset_rate_limit(
                    email
                )

                if not allowed:
                    message = wait_message

                    return render_template(
                        'forgot_password.html',
                        message=message
                    )

                otp = generate_otp()

                save_password_reset_otp(
                    email,
                    otp,
                    expiry_minutes=10
                )

                # OTP is sent by email (or logged to the server console
                # in demo mode) — it is NEVER included in the response
                # shown to the user in the browser.
                send_otp_email(
                    user['Email'],
                    user['First_name'],
                    otp
                )

                return redirect(
                    url_for(
                        'reset_password',
                        email=email,
                        sent='1'
                    )
                )

    # ---- Fallback: GET requests, and any POST branch above that ----
    # ---- only set `message` without returning a response yet     ----
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

    if request.method == 'GET' and request.args.get('sent') == '1':
        message = (
            "A verification code has been sent to your "
            "email address. Please check your inbox."
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
# (registration-approval verification — one time only)
# =====================================================

@app.route(
    '/verify-admin-email',
    methods=['GET', 'POST']
)
def verify_admin_email():
    message = None
    success = False

    # Pre-fill the email field when redirected here from /login.
    prefill_email = request.args.get(
        'email',
        ''
    ).strip()

    if request.method == 'POST':
        email = request.form.get(
            'email',
            ''
        ).strip()

        prefill_email = email

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
        success=success,
        prefill_email=prefill_email
    )


# =====================================================
# LOGOUT
# =====================================================

@app.route('/help')
def help_support():
    if 'user_id' not in session:
        return (
            "Please login first. "
            "<a href='/login'>Login</a>"
        )

    return render_template(
        'help_support.html'
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


@app.route('/admin/monitoring')
@admin_required
def system_monitoring():
    # ---- Database connectivity check ----
    try:
        conn = get_db_connection()
        conn.close()
        db_status = "Connected"
        db_ok = True

    except Exception as e:
        db_status = f"Disconnected — {str(e)}"
        db_ok = False

    stats = get_system_monitoring_stats()

    # ---- Server uptime ----
    uptime_delta = (
        datetime.now()
        - APP_START_TIME
    )

    total_seconds = int(
        uptime_delta.total_seconds()
    )

    days, remainder = divmod(
        total_seconds,
        86400
    )

    hours, remainder = divmod(
        remainder,
        3600
    )

    minutes, _ = divmod(
        remainder,
        60
    )

    uptime_str = (
        f"{days}d {hours}h {minutes}m"
    )

    # ---- Backup status ----
    backup_count = 0
    latest_backup = None

    if os.path.exists(BACKUP_FOLDER):
        backup_files = sorted(
            [
                f for f in os.listdir(BACKUP_FOLDER)
                if f.endswith('.enc')
            ],
            reverse=True
        )

        backup_count = len(backup_files)

        if backup_files:
            latest_backup = backup_files[0]

    return render_template(
        'system_monitoring.html',
        db_status=db_status,
        db_ok=db_ok,
        stats=stats,
        uptime=uptime_str,
        server_start=APP_START_TIME.strftime(
            '%Y-%m-%d %H:%M:%S'
        ),
        backup_count=backup_count,
        latest_backup=latest_backup
    )


@app.route('/admin/login-attempts')
@admin_required
def admin_login_attempts():
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

    search = (
        request.args.get('search')
        or None
    )

    attempts = get_all_login_attempts(
        start_date,
        end_date,
        risk_level,
        search
    )

    return render_template(
        'login_attempts.html',
        attempts=attempts,
        start_date=start_date or '',
        end_date=end_date or '',
        risk_level=risk_level or '',
        search=search or ''
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
# SUPER ADMIN — DATA BACKUP
# =====================================================

@app.route(
    '/admin/backup',
    methods=['GET', 'POST']
)
@super_admin_required
def data_backup():
    message = None

    if request.method == 'POST':
        try:
            timestamp = datetime.now().strftime(
                '%Y%m%d_%H%M%S'
            )

            dump_filename = f"backup_{timestamp}.sql"

            dump_path = os.path.join(
                BACKUP_FOLDER,
                dump_filename
            )

            with open(dump_path, 'wb') as dump_file:
                result = subprocess.run(
                    [
                        MYSQLDUMP_PATH,
                        '-h', DB_BACKUP_HOST,
                        '-u', DB_BACKUP_USER,
                        f'-p{DB_BACKUP_PASSWORD}',
                        DB_BACKUP_NAME
                    ],
                    stdout=dump_file,
                    stderr=subprocess.PIPE
                )

            if result.returncode != 0:
                if os.path.exists(dump_path):
                    os.remove(dump_path)

                message = (
                    "Backup failed: "
                    + result.stderr.decode(errors='replace')
                )

            else:
                # ---- Encrypt the dump, then delete the ----
                # ---- plaintext copy — it must never sit  ----
                # ---- on disk unencrypted.                ----
                key = get_or_create_backup_key()

                fernet = Fernet(key)

                with open(dump_path, 'rb') as f:
                    raw_data = f.read()

                encrypted_data = fernet.encrypt(
                    raw_data
                )

                encrypted_filename = (
                    dump_filename + '.enc'
                )

                encrypted_path = os.path.join(
                    BACKUP_FOLDER,
                    encrypted_filename
                )

                with open(encrypted_path, 'wb') as f:
                    f.write(encrypted_data)

                os.remove(dump_path)

                message = (
                    "Backup created and encrypted "
                    f"successfully: {encrypted_filename}"
                )

        except FileNotFoundError:
            message = (
                "mysqldump was not found. Make sure MySQL's "
                "command-line tools are installed and either "
                "on your system PATH, or update MYSQLDUMP_PATH "
                "in app.py to the full path of mysqldump.exe."
            )

        except Exception as e:
            message = f"Backup failed: {str(e)}"

    backups = []

    if os.path.exists(BACKUP_FOLDER):
        for filename in sorted(
            os.listdir(BACKUP_FOLDER),
            reverse=True
        ):
            if filename.endswith('.enc'):
                full_path = os.path.join(
                    BACKUP_FOLDER,
                    filename
                )

                size_kb = round(
                    os.path.getsize(full_path) / 1024,
                    1
                )

                backups.append({
                    'name': filename,
                    'size_kb': size_kb
                })

    return render_template(
        'data_backup.html',
        message=message,
        backups=backups
    )


@app.route(
    '/admin/backup/download/<path:filename>'
)
@super_admin_required
def download_backup(filename):
    safe_filename = secure_filename(
        filename
    )

    full_path = os.path.join(
        BACKUP_FOLDER,
        safe_filename
    )

    if not os.path.exists(full_path):
        return (
            "Backup file not found. "
            "<a href='/admin/backup'>Back</a>"
        )

    return send_from_directory(
        BACKUP_FOLDER,
        safe_filename,
        as_attachment=True
    )


# =====================================================
# SUPER ADMIN — DATA RESTORE
# =====================================================

@app.route(
    '/admin/restore',
    methods=['GET', 'POST']
)
@super_admin_required
def data_restore():
    message = None

    if request.method == 'POST':
        confirm = request.form.get(
            'confirm'
        )

        if confirm != 'yes':
            message = (
                "You must confirm before restoring — "
                "this will overwrite all current data."
            )

        else:
            source = request.form.get(
                'source'
            )

            encrypted_bytes = None

            try:
                # ---- Get the encrypted backup bytes,   ----
                # ---- either from an existing backup or ----
                # ---- a freshly uploaded .enc file.      ----
                if source == 'existing':
                    filename = secure_filename(
                        request.form.get(
                            'backup_filename',
                            ''
                        )
                    )

                    full_path = os.path.join(
                        BACKUP_FOLDER,
                        filename
                    )

                    if not os.path.exists(full_path):
                        message = (
                            "Selected backup file not found."
                        )

                    else:
                        with open(full_path, 'rb') as f:
                            encrypted_bytes = f.read()

                else:
                    file = request.files.get(
                        'backup_file'
                    )

                    if not file or not file.filename.endswith('.enc'):
                        message = (
                            "Please upload a valid encrypted "
                            "(.enc) backup file."
                        )

                    else:
                        encrypted_bytes = file.read()

                # ---- Decrypt + validate + restore ----
                if encrypted_bytes and not message:

                    key = get_or_create_backup_key()

                    fernet = Fernet(key)

                    try:
                        decrypted_data = fernet.decrypt(
                            encrypted_bytes
                        )

                    except InvalidToken:
                        message = (
                            "Backup file could not be "
                            "decrypted — wrong key, or the "
                            "file is corrupted/tampered."
                        )

                    else:
                        # ---- Basic integrity check: does this ----
                        # ---- actually look like a SQL dump?    ----
                        preview = decrypted_data[:300].decode(
                            errors='ignore'
                        ).lower()

                        looks_like_sql = (
                            'create table' in preview
                            or 'insert into' in preview
                            or 'mysql dump' in preview
                        )

                        if not looks_like_sql:
                            message = (
                                "This file does not look like a "
                                "valid SQL dump. Restore aborted "
                                "for safety."
                            )

                        else:
                            temp_sql_path = os.path.join(
                                BACKUP_FOLDER,
                                "_restore_temp_"
                                + datetime.now().strftime(
                                    '%Y%m%d_%H%M%S'
                                )
                                + ".sql"
                            )

                            with open(temp_sql_path, 'wb') as f:
                                f.write(decrypted_data)

                            try:
                                with open(
                                    temp_sql_path,
                                    'rb'
                                ) as sql_file:

                                    result = subprocess.run(
                                        [
                                            MYSQL_PATH,
                                            '-h', DB_BACKUP_HOST,
                                            '-u', DB_BACKUP_USER,
                                            f'-p{DB_BACKUP_PASSWORD}',
                                            DB_BACKUP_NAME
                                        ],
                                        stdin=sql_file,
                                        stderr=subprocess.PIPE
                                    )

                                if result.returncode != 0:
                                    message = (
                                        "Restore failed: "
                                        + result.stderr.decode(
                                            errors='replace'
                                        )
                                    )

                                else:
                                    message = (
                                        "Database restored "
                                        "successfully."
                                    )

                            finally:
                                # ---- Never leave a plaintext ----
                                # ---- SQL dump on disk.        ----
                                if os.path.exists(temp_sql_path):
                                    os.remove(temp_sql_path)

            except FileNotFoundError:
                message = (
                    "mysql client not found. Check "
                    "MYSQL_PATH in app.py."
                )

            except Exception as e:
                message = f"Restore failed: {str(e)}"

    backups = []

    if os.path.exists(BACKUP_FOLDER):
        for filename in sorted(
            os.listdir(BACKUP_FOLDER),
            reverse=True
        ):
            if filename.endswith('.enc'):
                full_path = os.path.join(
                    BACKUP_FOLDER,
                    filename
                )

                size_kb = round(
                    os.path.getsize(full_path) / 1024,
                    1
                )

                backups.append({
                    'name': filename,
                    'size_kb': size_kb
                })

    return render_template(
        'data_restore.html',
        message=message,
        backups=backups
    )


# =====================================================
# STUDENT NOTIFICATIONS
# =====================================================

@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return "Please login first. <a href='/login'>Login</a>"

    notes = get_user_notifications(session['user_id'])
    mark_notifications_read(session['user_id'])
    return render_template('notifications.html', notifications=notes)


# =====================================================
# SUPER ADMIN — SYSTEM SETTINGS (Risk Thresholds)
# =====================================================

@app.route('/admin/settings', methods=['GET', 'POST'])
@super_admin_required
def system_settings():
    message = None
    if request.method == 'POST':
        for key in request.form:
            value = request.form[key].strip()
            if value:
                update_setting(key, value)
        message = "Settings updated successfully."

    settings = get_all_settings()
    return render_template('system_settings.html', settings=settings, message=message)


# =====================================================
# ADMIN — IMPORT DATA (Bulk Course Import)
# =====================================================

@app.route('/admin/import', methods=['GET', 'POST'])
@admin_required
def import_data():
    message = None
    if request.method == 'POST':
        file = request.files.get('csv_file')
        if not file or not file.filename.endswith('.csv'):
            message = "Please upload a valid .csv file."
        else:
            try:
                stream = io.StringIO(file.stream.read().decode('utf-8'))
                reader = csv.reader(stream)
                next(reader, None)  # skip header row
                course_list = [
                    (row[0].strip(), row[1].strip() if len(row) > 1 else '')
                    for row in reader if row
                ]
                inserted, skipped = bulk_import_courses(course_list)
                message = f"Import complete: {inserted} course(s) added, {skipped} duplicate(s) skipped."
            except Exception as e:
                message = f"Import failed: {str(e)}"

    return render_template('import_data.html', message=message)


# =====================================================
# SESSION TIMEOUT HANDLER
# =====================================================
# Refreshes the sliding-expiration timer on every request, so an
# active user never gets logged out mid-use. If MAX inactivity
# (app.permanent_session_lifetime) is exceeded, Flask's session
# cookie will have already expired and 'user_id' will no longer be
# present, so the @student_required / @admin_required decorators
# will naturally redirect to login.

@app.before_request
def refresh_session():
    session.permanent = True
    session.modified = True


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == '__main__':
    app.run(
        debug=False,
        port=9000
    )