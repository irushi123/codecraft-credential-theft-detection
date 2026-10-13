# CodeCraft — Explainable ML System for Predicting Credential Theft

An explainable machine learning–based decision-support system integrated into a Learning Management System (LMS) environment. The system analyzes login behavior to assess credential theft risk, giving students a normal LMS experience while giving administrators visibility into login risk, explanations, and security alerts.

Built for the Software Requirements Specification: *Explainable Machine Learning System for Predicting Credential Theft* — Faculty of Applied Science, Rajarata University of Sri Lanka (2021/2022 Batch).

## Features

### For Students
- Register and log in with role-based access
- View enrolled courses and access LMS content
- View personal login history and risk scores
- Receive notifications for high-risk logins on their own account
- Submit feedback
- Forgot password (OTP-based reset via email)
- Help & Support / FAQ page

### For Admins
- Admin dashboard with system-wide stats (total logins, high-risk events, active users, alerts)
- **System Monitoring** — live DB connection status, server uptime, key metrics
- View and filter login attempts (by date range, risk level, email/IP)
- View risk scores and XAI (explainable AI) explanation summaries for every login
- Receive and review security alerts for high-risk logins
- Lock/unlock student accounts, mark alerts as false positives
- Manage users
- Full audit log of all admin actions (immutable)
- Generate analytical reports (filterable by date/risk level) and export login data as CSV
- Import course data in bulk via CSV
- Configure system-wide risk thresholds
- **Data Backup** — create encrypted database backups on demand
- **Data Restore** — restore the database from an encrypted backup (with confirmation)

### Admin Approval & Security
- New admin registrations start as **Pending** and require Super Admin approval
- Super Admin sends a one-time email verification code; the admin must verify their email (`/verify-admin-email`) before their account is fully approved
- Super Admin can reject an admin request with a logged reason
- **Login-time 2FA for regular admins**: after a correct password, a fresh OTP is emailed and must be verified before the session is created. Super Admins are exempt (they need direct access to manage other admins).
- Account lockout after 5 consecutive failed login attempts
- Auto-logout after 15 minutes of inactivity

### Machine Learning / Explainability
- XGBoost model predicts a credential-theft risk score (0–100%) for every login attempt, based on signals including IP/ASN reputation, country change, device/browser/OS, login time, and time since last login
- SHAP-based explanations surface the top contributing factors for each prediction in human-readable form
- Security alerts are automatically generated when a login's risk score exceeds the configured admin threshold

## Tech Stack

- **Backend:** Python (Flask)
- **Database:** MySQL
- **ML/XAI:** XGBoost, SHAP
- **Frontend:** HTML, CSS, JavaScript (Jinja2 templates)
- **Email:** SMTP (Gmail), with a console/demo fallback when SMTP isn't configured
- **Backup Encryption:** `cryptography` (Fernet)

## Prerequisites

- Python 3.10+
- MySQL Server (with `mysqldump` and `mysql` command-line clients installed, for the backup/restore feature)
- pip

## Installation

```bash
git clone https://github.com/irushi123/codecraft-credential-theft-detection.git
cd codecraft-credential-theft-detection
pip install -r requirements.txt
```

If `requirements.txt` doesn't yet include everything used, install these explicitly:

```bash
pip install flask pymysql werkzeug pandas xgboost shap joblib user-agents requests cryptography
```

## Configuration

### Database
Update the connection details in `utils/db_handler.py` (`get_db_connection()`) to match your local MySQL setup:

```python
host="localhost"
user="root"
password="root"
database="codecraft_db"
```

### Email (OTP delivery)
In `app.py`, set your SMTP credentials for real email delivery:

```python
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_gmail_app_password"
```

Leave these blank to run in **console/demo mode** — OTP codes are printed to the server terminal instead of being emailed, so the full flow can still be demoed without a live inbox.

### Data Backup / Restore
`app.py` needs the full path to your MySQL client tools if they aren't on your system PATH:

```python
MYSQLDUMP_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"
MYSQL_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
```

⚠️ **Never commit `backup.key` or the `backups/` folder to git** — add them to `.gitignore`. The key decrypts all your backups; treat it like a password.

## Database Setup

1. Create a MySQL database (e.g. `codecraft_db`)
2. Import the provided SQL schema:

```bash
mysql -u root -p codecraft_db < codecraft_db.sql
```

## Running the App

```bash
python app.py
```

The app runs at:

```
http://127.0.0.1:9000
```

## Project Structure

```
codecraft-app/
├── app.py                     # Flask application, routes, auth logic
├── utils/
│   ├── db_handler.py          # All database queries
│   └── ml_engine.py           # Risk scoring (XGBoost) + explanations (SHAP)
├── model/
│   ├── credential_theft_xgb_model.json
│   ├── model_feature_columns.pkl
│   ├── model_threshold.pkl
│   └── asn_freq_map.pkl
├── templates/                 # Jinja2 HTML templates
├── static/                    # CSS, JS, images, uploads
├── backups/                   # Encrypted DB backups (gitignored)
├── backup.key                 # Backup encryption key (gitignored, never commit)
├── requirements.txt
└── README.md
```

## Registration Rules

- **Students** can register with any valid email address.
- **Admins** must register with an official campus email (`@as.rjt.ac.lk` or `@std.rjt.ac.lk`) and go through Super Admin approval + email verification before they can log in.

## .gitignore Recommendations

```
backup.key
backups/
__pycache__/
*.pyc
.env
static/uploads/
```

## Known Notes

- The ML model's risk scoring is probability-based (not a simple additive rule system) — a single risk signal (e.g. VPN use) won't always push a login to "High" risk on its own; the score reflects the model's learned patterns across all captured signals (IP/ASN reputation, country change, device, timing, etc.).
- Sensitive data (passwords, raw OTPs) is never displayed in the UI or logs.
- All admin actions (lock/unlock, approve/reject, false-positive marking, backups/restores) are recorded in the immutable audit log.

## Team

- R.I. Kavindi — ASB/2022/112
- G.A.M.A. Dissanayake — ASB/2022/169
- E.K.H.N. Ekanayake — ICT/2022/078
- H.M.K.G. Senevirathna — ICT/2022/096
- R.M.D.S.N. Ranabahu — ICT/2022/151

Supervised by: Ms. W.B.P.N. Herath, Department of Computing, Faculty of Applied Science, Rajarata University of Sri Lanka

## License

This project is for academic purposes.