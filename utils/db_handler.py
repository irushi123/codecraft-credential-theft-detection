import pymysql

def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='codecraft_db',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


def check_email_exists(email):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE Email = %s", (email,))
        result = cursor.fetchone()
    conn.close()
    return result is not None


def create_user(first_name, last_name, email, hashed_password):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (First_name, Last_name, Email, Password) VALUES (%s, %s, %s, %s)",
            (first_name, last_name, email, hashed_password)
        )
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO normal_user (User_ID) VALUES (%s)", (user_id,))
    conn.commit()
    conn.close()
    return user_id


def enroll_user_in_all_courses(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT Course_ID FROM course")
        courses = cursor.fetchall()
        for course in courses:
            cursor.execute(
                "INSERT INTO enrollment (User_ID, Course_ID) VALUES (%s, %s)",
                (user_id, course['Course_ID'])
            )
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE Email = %s", (email,))
        result = cursor.fetchone()
    conn.close()
    return result


def get_user_by_id(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE User_ID = %s", (user_id,))
        result = cursor.fetchone()
    conn.close()
    return result


def is_admin_user(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM admin WHERE User_ID = %s", (user_id,))
        result = cursor.fetchone()
    conn.close()
    return result is not None


def create_admin(first_name, last_name, email, hashed_password, admin_role='SecurityAdmin'):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (First_name, Last_name, Email, Password) VALUES (%s, %s, %s, %s)",
            (first_name, last_name, email, hashed_password)
        )
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO admin (User_ID, Admin_role) VALUES (%s, %s)", (user_id, admin_role))
    conn.commit()
    conn.close()
    return user_id


def save_login_attempt(user_id, ip_address, user_agent, login_status):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO login_attempt (User_ID, IP_address, User_agent, Login_status) VALUES (%s, %s, %s, %s)",
            (user_id, ip_address, user_agent, login_status)
        )
        login_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return login_id


def get_recent_failed_attempt_count(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT Login_status FROM login_attempt WHERE User_ID = %s ORDER BY Login_time DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
    conn.close()

    count = 0
    for row in rows:
        if row['Login_status'] == 'Failed':
            count += 1
        else:
            break
    return count


def lock_account_by_user_id(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET Account_status = 'Locked' WHERE User_ID = %s",
            (user_id,)
        )
    conn.commit()
    conn.close()


def is_account_locked(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT Account_status FROM users WHERE User_ID = %s", (user_id,))
        result = cursor.fetchone()
    conn.close()
    return result and result['Account_status'] == 'Locked'


def save_risk_assessment(login_id, risk_score, risk_level):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO risk_assessment (Login_ID, Risk_score, Risk_level) VALUES (%s, %s, %s)",
            (login_id, risk_score, risk_level)
        )
        risk_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return risk_id


def save_explanation(risk_id, summary, key_factors, confidence):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO explanation (Risk_ID, Explanation_summary, Key_factors, Confidence_level) VALUES (%s, %s, %s, %s)",
            (risk_id, summary, key_factors, confidence)
        )
    conn.commit()
    conn.close()


def get_all_login_attempts():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT la.Login_ID, u.Email, la.Login_time, la.IP_address, 
                   la.Login_status, ra.Risk_score, ra.Risk_level
            FROM login_attempt la
            JOIN users u ON la.User_ID = u.User_ID
            LEFT JOIN risk_assessment ra ON la.Login_ID = ra.Login_ID
            ORDER BY la.Login_time DESC
        """)
        results = cursor.fetchall()
    conn.close()
    return results


def get_all_explanations():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT e.Explanation_ID, u.Email, ra.Risk_score, ra.Risk_level,
                   e.Explanation_summary, e.Key_factors, e.Confidence_level
            FROM explanation e
            JOIN risk_assessment ra ON e.Risk_ID = ra.Risk_ID
            JOIN login_attempt la ON ra.Login_ID = la.Login_ID
            JOIN users u ON la.User_ID = u.User_ID
            ORDER BY e.Explanation_ID DESC
        """)
        results = cursor.fetchall()
    conn.close()
    return results


def create_security_alert(risk_id, alert_message):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO security_alert (Risk_ID, Alert_message, Alert_status) VALUES (%s, %s, %s)",
            (risk_id, alert_message, 'Pending')
        )
    conn.commit()
    conn.close()


def get_all_alerts():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT sa.Alert_ID, u.User_ID, u.Email, ra.Risk_score, ra.Risk_level,
                   sa.Alert_message, sa.Alert_status, sa.Alert_time
            FROM security_alert sa
            JOIN risk_assessment ra ON sa.Risk_ID = ra.Risk_ID
            JOIN login_attempt la ON ra.Login_ID = la.Login_ID
            JOIN users u ON la.User_ID = u.User_ID
            ORDER BY sa.Alert_time DESC
        """)
        results = cursor.fetchall()
    conn.close()
    return results


def get_security_alerts_for_user(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT sa.Alert_ID, ra.Risk_score, ra.Risk_level,
                   sa.Alert_message, sa.Alert_status, sa.Alert_time
            FROM security_alert sa
            JOIN risk_assessment ra ON sa.Risk_ID = ra.Risk_ID
            JOIN login_attempt la ON ra.Login_ID = la.Login_ID
            WHERE la.User_ID = %s
            ORDER BY sa.Alert_time DESC
        """, (user_id,))
        results = cursor.fetchall()
    conn.close()
    return results


def get_alert_by_id(alert_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT sa.Alert_ID, sa.Risk_ID, u.User_ID, u.Email, ra.Risk_score,
                   sa.Alert_message, sa.Alert_status
            FROM security_alert sa
            JOIN risk_assessment ra ON sa.Risk_ID = ra.Risk_ID
            JOIN login_attempt la ON ra.Login_ID = la.Login_ID
            JOIN users u ON la.User_ID = u.User_ID
            WHERE sa.Alert_ID = %s
        """, (alert_id,))
        result = cursor.fetchone()
    conn.close()
    return result


def lock_user_account(user_id, admin_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET Account_status = 'Locked' WHERE User_ID = %s",
            (user_id,)
        )
        cursor.execute(
            "INSERT INTO admin_action (Admin_ID, Target_User_ID, Action_type) VALUES (%s, %s, %s)",
            (admin_id, user_id, 'lock_account')
        )
    conn.commit()
    conn.close()


def mark_alert_false_positive(alert_id, admin_id, target_user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE security_alert SET Alert_status = 'Resolved' WHERE Alert_ID = %s",
            (alert_id,)
        )
        cursor.execute(
            "INSERT INTO admin_action (Admin_ID, Target_User_ID, Action_type) VALUES (%s, %s, %s)",
            (admin_id, target_user_id, 'Mark_False_Positive')
        )
    conn.commit()
    conn.close()


def get_user_login_history(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT la.Login_ID, la.Login_time, la.IP_address, 
                   la.Login_status, ra.Risk_score, ra.Risk_level
            FROM login_attempt la
            LEFT JOIN risk_assessment ra ON la.Login_ID = ra.Login_ID
            WHERE la.User_ID = %s
            ORDER BY la.Login_time DESC
        """, (user_id,))
        results = cursor.fetchall()
    conn.close()
    return results


def get_all_users():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT u.User_ID, u.First_name, u.Email, u.Account_status
            FROM users u
            JOIN normal_user nu ON u.User_ID = nu.User_ID
            ORDER BY u.Account_status DESC, u.User_ID
        """)
        results = cursor.fetchall()
    conn.close()
    return results


def unlock_user_account(user_id, admin_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET Account_status = 'Active' WHERE User_ID = %s",
            (user_id,)
        )
        cursor.execute(
            "INSERT INTO admin_action (Admin_ID, Target_User_ID, Action_type) VALUES (%s, %s, %s)",
            (admin_id, user_id, 'unlock_account')
        )
    conn.commit()
    conn.close()


def get_enrolled_courses(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT c.Course_ID, c.Course_name, c.Description
            FROM enrollment e
            JOIN course c ON e.Course_ID = c.Course_ID
            WHERE e.User_ID = %s
        """, (user_id,))
        results = cursor.fetchall()
    conn.close()
    return results


def get_course_by_id(course_id, user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT c.Course_ID, c.Course_name, c.Description
            FROM enrollment e
            JOIN course c ON e.Course_ID = c.Course_ID
            WHERE e.User_ID = %s AND c.Course_ID = %s
        """, (user_id, course_id))
        result = cursor.fetchone()
    conn.close()
    return result


def get_latest_risk_score(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT ra.Risk_score, ra.Risk_level
            FROM login_attempt la
            JOIN risk_assessment ra ON la.Login_ID = ra.Login_ID
            WHERE la.User_ID = %s
            ORDER BY la.Login_time DESC
            LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
    conn.close()
    return result


def get_all_students_latest_risk():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT u.User_ID, u.First_name, u.Email, ra.Risk_score, ra.Risk_level
            FROM users u
            JOIN normal_user nu ON u.User_ID = nu.User_ID
            JOIN login_attempt la ON la.User_ID = u.User_ID
            JOIN risk_assessment ra ON ra.Login_ID = la.Login_ID
            WHERE la.Login_ID = (
                SELECT la2.Login_ID FROM login_attempt la2
                JOIN risk_assessment ra2 ON la2.Login_ID = ra2.Login_ID
                WHERE la2.User_ID = u.User_ID
                ORDER BY la2.Login_time DESC LIMIT 1
            )
            ORDER BY ra.Risk_score DESC
        """)
        results = cursor.fetchall()
    conn.close()
    return results


def get_admin_dashboard_stats():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS cnt FROM login_attempt")
        total_attempts = cursor.fetchone()['cnt']

        cursor.execute("SELECT COUNT(*) AS cnt FROM risk_assessment WHERE Risk_level = 'High'")
        high_risk = cursor.fetchone()['cnt']

        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM users u
            JOIN normal_user nu ON u.User_ID = nu.User_ID
            WHERE u.Account_status = 'Active'
        """)
        active_users = cursor.fetchone()['cnt']

        cursor.execute("SELECT COUNT(*) AS cnt FROM security_alert WHERE Alert_status = 'Pending'")
        total_alerts = cursor.fetchone()['cnt']
    conn.close()
    return {
        'total_attempts': total_attempts,
        'high_risk': high_risk,
        'active_users': active_users,
        'total_alerts': total_alerts
    }