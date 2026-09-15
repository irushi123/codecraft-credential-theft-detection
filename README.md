# CodeCraft — Credential Theft Detection

A web-based application for detecting and managing credential theft risks, built with Flask. The system helps monitor and respond to potential credential compromise through configurable risk thresholds, real-time notifications, and data import capabilities.

## Features

- **Risk Thresholds** — Configure and manage risk level thresholds for credential monitoring
- **Notifications** — Real-time alerts for detected risks and system events
- **Import Data** — Bulk data import functionality for credential/log analysis
- **Password Reset (OTP-based)** — Secure password recovery flow using one-time passwords sent via email
- **Rate Limiting** — Protects password reset requests from abuse

## Tech Stack

- **Backend:** Python (Flask)
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript
- **Email:** SMTP (for OTP delivery)

## Prerequisites

- Python 3.10+
- MySQL server
- pip

## Installation

```bash
git clone https://github.com/irushi123/codecraft-credential-theft-detection.git
cd codecraft-credential-theft-detection
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with the following variables:

```
DB_HOST=localhost
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_NAME=codecraft_db

EMAIL_USER=your_email@example.com
EMAIL_PASSWORD=your_email_app_password

SECRET_KEY=your_flask_secret_key
```

> ⚠️ Never commit your `.env` file or real credentials to GitHub. Add `.env` to your `.gitignore`.

## Database Setup

1. Create a MySQL database (e.g. `codecraft_db`)
2. Import the provided SQL schema:

```bash
mysql -u your_db_username -p codecraft_db < codecraft_db.sql
```

## Running the App

```bash
python app.py
```

The app will be available at:

```
http://127.0.0.1:5000
```

## Project Structure

```
codecraft-app/
├── app.py                 # Main Flask application and routes
├── db_handler.py           # Database connection and query functions
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
├── requirements.txt         # Python dependencies
└── README.md
```

## Known Issues / Notes

- Ensure the `/reset-password` route accepts both `GET` and `POST` methods.
- OTPs are sent via email and are never displayed directly in the browser response.

## Team / Author

- Irushi (irushi123)

## License

This project is for academic/educational purposes.
