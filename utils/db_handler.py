import pymysql
from datetime import datetime, timedelta


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db_connection():
    connection = pymysql.connect( 
        host="localhost",
        user="root",
        password="root",
        database="codecraft_db", 
        cursorclass=pymysql.cursors.DictCursor,
    )

    return connection


# =====================================================
# USER FUNCTIONS
# =====================================================

def check_email_exists(email):
    conn = get_db_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE Email = %s",
            (email,),
        )

        result = cursor.fetchone()

    conn.close()

    return result is not None


def create_user(
    first_name,
    last_name,
    email,
    hashed_password,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO users
            (First_name, Last_name, Email, Password)
            VALUES (%s, %s, %s, %s)
            """,
            (
                first_name,
                last_name,
                email,
                hashed_password,
            ),
        )

        user_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO normal_user (User_ID)
            VALUES (%s)
            """,
            (user_id,),
        )

    conn.commit()
    conn.close()

    return user_id


def create_admin(
    first_name,
    last_name,
    email,
    hashed_password,
    admin_role="SecurityAdmin",
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO users
            (First_name, Last_name, Email, Password)
            VALUES (%s, %s, %s, %s)
            """,
            (
                first_name,
                last_name,
                email,
                hashed_password,
            ),
        )

        user_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO admin
            (
                User_ID,
                Admin_role,
                Approval_status,
                Is_super_admin
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                user_id,
                admin_role,
                "Pending",
                False,
            ),
        )

    conn.commit()
    conn.close()

    return user_id


def get_user_by_email(email):
    conn = get_db_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE Email = %s",
            (email,),
        )

        result = cursor.fetchone()

    conn.close()

    return result


def get_user_by_id(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE User_ID = %s",
            (user_id,),
        )

        result = cursor.fetchone()

    conn.close()

    return result


def is_admin_user(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM admin WHERE User_ID = %s",
            (user_id,),
        )

        result = cursor.fetchone()

    conn.close()

    return result is not None


# =====================================================
# COURSE FUNCTIONS
# =====================================================

def enroll_user_in_all_courses(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            "SELECT Course_ID FROM course"
        )

        courses = cursor.fetchall()

        for course in courses:

            cursor.execute(
                """
                INSERT INTO enrollment
                (User_ID, Course_ID)
                VALUES (%s, %s)
                """,
                (
                    user_id,
                    course["Course_ID"],
                ),
            )

    conn.commit()
    conn.close()


def get_enrolled_courses(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                c.Course_ID,
                c.Course_name,
                c.Description
            FROM enrollment e
            JOIN course c
                ON e.Course_ID = c.Course_ID
            WHERE e.User_ID = %s
            """,
            (user_id,),
        )

        results = cursor.fetchall()

    conn.close()

    return results


def get_course_by_id(course_id, user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                c.Course_ID,
                c.Course_name,
                c.Description
            FROM enrollment e
            JOIN course c
                ON e.Course_ID = c.Course_ID
            WHERE e.User_ID = %s
              AND c.Course_ID = %s
            """,
            (
                user_id,
                course_id,
            ),
        )

        result = cursor.fetchone()

    conn.close()

    return result


# =====================================================
# LOGIN FUNCTIONS
# =====================================================

def save_login_attempt(
    user_id,
    ip_address,
    user_agent,
    login_status,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO login_attempt
            (
                User_ID,
                IP_address,
                User_agent,
                Login_status
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                user_id,
                ip_address,
                user_agent,
                login_status,
            ),
        )

        login_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return login_id


def get_recent_failed_attempt_count(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT Login_status
            FROM login_attempt
            WHERE User_ID = %s
            ORDER BY Login_time DESC
            """,
            (user_id,),
        )

        rows = cursor.fetchall()

    conn.close()

    count = 0

    for row in rows:

        if row["Login_status"] == "Failed":
            count += 1
        else:
            break

    return count


def lock_account_by_user_id(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            UPDATE users
            SET Account_status = 'Locked'
            WHERE User_ID = %s
            """,
            (user_id,),
        )

    conn.commit()
    conn.close()


def is_account_locked(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT Account_status
            FROM users
            WHERE User_ID = %s
            """,
            (user_id,),
        )

        result = cursor.fetchone()

    conn.close()

    return (
        result
        and result["Account_status"] == "Locked"
    )


def get_user_login_history(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                la.Login_ID,
                la.Login_time,
                la.IP_address,
                la.Login_status,
                ra.Risk_score,
                ra.Risk_level
            FROM login_attempt la
            LEFT JOIN risk_assessment ra
                ON la.Login_ID = ra.Login_ID
            WHERE la.User_ID = %s
            ORDER BY la.Login_time DESC
            """,
            (user_id,),
        )

        results = cursor.fetchall()

    conn.close()

    return results


# =====================================================
# RISK FUNCTIONS
# =====================================================

def save_risk_assessment(
    login_id,
    risk_score,
    risk_level,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO risk_assessment
            (
                Login_ID,
                Risk_score,
                Risk_level
            )
            VALUES (%s, %s, %s)
            """,
            (
                login_id,
                risk_score,
                risk_level,
            ),
        )

        risk_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return risk_id


def save_explanation(
    risk_id,
    summary,
    key_factors,
    confidence,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO explanation
            (
                Risk_ID,
                Explanation_summary,
                Key_factors,
                Confidence_level
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                risk_id,
                summary,
                key_factors,
                confidence,
            ),
        )

    conn.commit()
    conn.close()


def get_latest_risk_score(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                ra.Risk_score,
                ra.Risk_level
            FROM login_attempt la
            JOIN risk_assessment ra
                ON la.Login_ID = ra.Login_ID
            WHERE la.User_ID = %s
            ORDER BY la.Login_time DESC
            LIMIT 1
            """,
            (user_id,),
        )

        result = cursor.fetchone()

    conn.close()

    return result


def get_all_students_latest_risk():
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                u.User_ID,
                u.First_name,
                u.Email,
                ra.Risk_score,
                ra.Risk_level
            FROM users u
            JOIN normal_user nu
                ON u.User_ID = nu.User_ID
            JOIN login_attempt la
                ON la.User_ID = u.User_ID
            JOIN risk_assessment ra
                ON ra.Login_ID = la.Login_ID
            WHERE la.Login_ID = (
                SELECT la2.Login_ID
                FROM login_attempt la2
                JOIN risk_assessment ra2
                    ON la2.Login_ID = ra2.Login_ID
                WHERE la2.User_ID = u.User_ID
                ORDER BY la2.Login_time DESC
                LIMIT 1
            )
            ORDER BY ra.Risk_score DESC
            """
        )

        results = cursor.fetchall()

    conn.close()

    return results


# =====================================================
# ADMIN DASHBOARD
# =====================================================

def get_admin_dashboard_stats():
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM login_attempt
            """
        )

        total_attempts = cursor.fetchone()["cnt"]

        cursor.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM risk_assessment
            WHERE Risk_level = 'High'
            """
        )

        high_risk = cursor.fetchone()["cnt"]

        cursor.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM users u
            JOIN normal_user nu
                ON u.User_ID = nu.User_ID
            WHERE u.Account_status = 'Active'
            """
        )

        active_users = cursor.fetchone()["cnt"]

        cursor.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM security_alert
            WHERE Alert_status = 'Pending'
            """
        )

        total_alerts = cursor.fetchone()["cnt"]

    conn.close()

    return {
        "total_attempts": total_attempts,
        "high_risk": high_risk,
        "active_users": active_users,
        "total_alerts": total_alerts,
    }


# =====================================================
# LOGIN ATTEMPTS / EXPLANATIONS
# =====================================================

def get_all_login_attempts():
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                la.Login_ID,
                u.Email,
                la.Login_time,
                la.IP_address,
                la.Login_status,
                ra.Risk_score,
                ra.Risk_level
            FROM login_attempt la
            JOIN users u
                ON la.User_ID = u.User_ID
            LEFT JOIN risk_assessment ra
                ON la.Login_ID = ra.Login_ID
            ORDER BY la.Login_time DESC
            """
        )

        results = cursor.fetchall()

    conn.close()

    return results


def get_all_explanations():
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                e.Explanation_ID,
                u.Email,
                ra.Risk_score,
                ra.Risk_level,
                e.Explanation_summary,
                e.Key_factors,
                e.Confidence_level
            FROM explanation e
            JOIN risk_assessment ra
                ON e.Risk_ID = ra.Risk_ID
            JOIN login_attempt la
                ON ra.Login_ID = la.Login_ID
            JOIN users u
                ON la.User_ID = u.User_ID
            ORDER BY e.Explanation_ID DESC
            """
        )

        results = cursor.fetchall()

    conn.close()

    return results


# =====================================================
# SECURITY ALERTS
# =====================================================

def create_security_alert(
    risk_id,
    alert_message,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO security_alert
            (
                Risk_ID,
                Alert_message,
                Alert_status
            )
            VALUES (%s, %s, %s)
            """,
            (
                risk_id,
                alert_message,
                "Pending",
            ),
        )

    conn.commit()
    conn.close()


def get_all_alerts():
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                sa.Alert_ID,
                u.User_ID,
                u.Email,
                ra.Risk_score,
                ra.Risk_level,
                sa.Alert_message,
                sa.Alert_status,
                sa.Alert_time
            FROM security_alert sa
            JOIN risk_assessment ra
                ON sa.Risk_ID = ra.Risk_ID
            JOIN login_attempt la
                ON ra.Login_ID = la.Login_ID
            JOIN users u
                ON la.User_ID = u.User_ID
            ORDER BY sa.Alert_time DESC
            """
        )

        results = cursor.fetchall()

    conn.close()

    return results


def get_security_alerts_for_user(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                sa.Alert_ID,
                ra.Risk_score,
                ra.Risk_level,
                sa.Alert_message,
                sa.Alert_status,
                sa.Alert_time
            FROM security_alert sa
            JOIN risk_assessment ra
                ON sa.Risk_ID = ra.Risk_ID
            JOIN login_attempt la
                ON ra.Login_ID = la.Login_ID
            WHERE la.User_ID = %s
            ORDER BY sa.Alert_time DESC
            """,
            (user_id,),
        )

        results = cursor.fetchall()

    conn.close()

    return results


def get_alert_by_id(alert_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                sa.Alert_ID,
                sa.Risk_ID,
                u.User_ID,
                u.Email,
                ra.Risk_score,
                sa.Alert_message,
                sa.Alert_status
            FROM security_alert sa
            JOIN risk_assessment ra
                ON sa.Risk_ID = ra.Risk_ID
            JOIN login_attempt la
                ON ra.Login_ID = la.Login_ID
            JOIN users u
                ON la.User_ID = u.User_ID
            WHERE sa.Alert_ID = %s
            """,
            (alert_id,),
        )

        result = cursor.fetchone()

    conn.close()

    return result


# =====================================================
# ADMIN ACTIONS
# =====================================================

def lock_user_account(user_id, admin_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            UPDATE users
            SET Account_status = 'Locked'
            WHERE User_ID = %s
            """,
            (user_id,),
        )

        cursor.execute(
            """
            INSERT INTO admin_action
            (
                Admin_ID,
                Target_User_ID,
                Action_type
            )
            VALUES (%s, %s, %s)
            """,
            (
                admin_id,
                user_id,
                "lock_account",
            ),
        )

    conn.commit()
    conn.close()


def unlock_user_account(user_id, admin_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            UPDATE users
            SET Account_status = 'Active'
            WHERE User_ID = %s
            """,
            (user_id,),
        )

        cursor.execute(
            """
            INSERT INTO admin_action
            (
                Admin_ID,
                Target_User_ID,
                Action_type
            )
            VALUES (%s, %s, %s)
            """,
            (
                admin_id,
                user_id,
                "unlock_account",
            ),
        )

    conn.commit()
    conn.close()


def mark_alert_false_positive(
    alert_id,
    admin_id,
    target_user_id,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            UPDATE security_alert
            SET Alert_status = 'Resolved'
            WHERE Alert_ID = %s
            """,
            (alert_id,),
        )

        cursor.execute(
            """
            INSERT INTO admin_action
            (
                Admin_ID,
                Target_User_ID,
                Action_type
            )
            VALUES (%s, %s, %s)
            """,
            (
                admin_id,
                target_user_id,
                "Mark_False_Positive",
            ),
        )

    conn.commit()
    conn.close()


def get_all_admin_actions():
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                aa.Action_ID,
                admin_u.Email AS Admin_Email,
                target_u.Email AS Target_Email,
                aa.Action_type,
                aa.Action_time
            FROM admin_action aa
            JOIN users admin_u
                ON aa.Admin_ID = admin_u.User_ID
            JOIN users target_u
                ON aa.Target_User_ID = target_u.User_ID
            ORDER BY aa.Action_time DESC
            """
        )

        results = cursor.fetchall()

    conn.close()

    return results


# =====================================================
# USERS
# =====================================================

def get_all_users():
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                u.User_ID,
                u.First_name,
                u.Email,
                u.Account_status
            FROM users u
            JOIN normal_user nu
                ON u.User_ID = nu.User_ID
            ORDER BY
                u.Account_status DESC,
                u.User_ID
            """
        )

        results = cursor.fetchall()

    conn.close()

    return results


# =====================================================
# PASSWORD
# =====================================================

def update_user_password(
    user_id,
    new_hashed_password,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            UPDATE users
            SET Password = %s
            WHERE User_ID = %s
            """,
            (
                new_hashed_password,
                user_id,
            ),
        )

    conn.commit()
    conn.close()


# =====================================================
# EXPORT
# =====================================================

def get_login_attempts_for_export(
    start_date=None,
    end_date=None,
    risk_level=None,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        query = """
            SELECT
                la.Login_ID,
                u.Email,
                la.Login_time,
                la.IP_address,
                la.Login_status,
                ra.Risk_score,
                ra.Risk_level
            FROM login_attempt la
            JOIN users u
                ON la.User_ID = u.User_ID
            LEFT JOIN risk_assessment ra
                ON la.Login_ID = ra.Login_ID
            WHERE 1=1
        """

        params = []

        if start_date:

            query += (
                " AND la.Login_time >= %s"
            )

            params.append(start_date)

        if end_date:

            query += (
                " AND la.Login_time <= %s"
            )

            params.append(end_date)

        if risk_level:

            query += (
                " AND ra.Risk_level = %s"
            )

            params.append(risk_level)

        query += (
            " ORDER BY la.Login_time DESC"
        )

        cursor.execute(
            query,
            params,
        )

        results = cursor.fetchall()

    conn.close()

    return results


# =====================================================
# REPORTS
# =====================================================

def get_report_data(
    start_date=None,
    end_date=None,
    risk_level=None,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        base_where = "WHERE 1=1"
        params = []

        if start_date:

            base_where += (
                " AND la.Login_time >= %s"
            )

            params.append(start_date)

        if end_date:

            base_where += (
                " AND la.Login_time <= %s"
            )

            params.append(end_date)

        if risk_level:

            base_where += (
                " AND ra.Risk_level = %s"
            )

            params.append(risk_level)

        cursor.execute(
            f"""
            SELECT
                COUNT(*) AS total_logins,

                SUM(
                    CASE
                        WHEN la.Login_status = 'Success'
                        THEN 1
                        ELSE 0
                    END
                ) AS successful_logins,

                SUM(
                    CASE
                        WHEN la.Login_status = 'Failed'
                        THEN 1
                        ELSE 0
                    END
                ) AS failed_logins,

                SUM(
                    CASE
                        WHEN ra.Risk_level = 'High'
                        THEN 1
                        ELSE 0
                    END
                ) AS high_risk_count,

                SUM(
                    CASE
                        WHEN ra.Risk_level = 'Medium'
                        THEN 1
                        ELSE 0
                    END
                ) AS medium_risk_count,

                SUM(
                    CASE
                        WHEN ra.Risk_level = 'Low'
                        THEN 1
                        ELSE 0
                    END
                ) AS low_risk_count,

                ROUND(
                    AVG(ra.Risk_score),
                    2
                ) AS avg_risk_score

            FROM login_attempt la

            LEFT JOIN risk_assessment ra
                ON la.Login_ID = ra.Login_ID

            {base_where}
            """,
            params,
        )

        summary = cursor.fetchone()

        cursor.execute(
            f"""
            SELECT
                la.Login_ID,
                u.Email,
                la.Login_time,
                la.IP_address,
                la.Login_status,
                ra.Risk_score,
                ra.Risk_level

            FROM login_attempt la

            JOIN users u
                ON la.User_ID = u.User_ID

            LEFT JOIN risk_assessment ra
                ON la.Login_ID = ra.Login_ID

            {base_where}

            ORDER BY la.Login_time DESC
            """,
            params,
        )

        rows = cursor.fetchall()

    conn.close()

    return {
        "summary": summary,
        "rows": rows,
    }


# =====================================================
# FEEDBACK
# =====================================================

def submit_feedback(
    user_id,
    feedback_text,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO feedback
            (
                User_ID,
                Feedback_text
            )
            VALUES (%s, %s)
            """,
            (
                user_id,
                feedback_text,
            ),
        )

    conn.commit()
    conn.close()


def get_user_feedback(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT *
            FROM feedback
            WHERE User_ID = %s
            ORDER BY Submitted_at DESC
            """,
            (user_id,),
        )

        results = cursor.fetchall()

    conn.close()

    return results


# =====================================================
# SUPER ADMIN
# =====================================================

def is_super_admin(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT Is_super_admin
            FROM admin
            WHERE User_ID = %s
            """,
            (user_id,),
        )

        result = cursor.fetchone()

    conn.close()

    return bool(
        result
        and result["Is_super_admin"]
    )


def get_admin_approval_status(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT Approval_status
            FROM admin
            WHERE User_ID = %s
            """,
            (user_id,),
        )

        result = cursor.fetchone()

    conn.close()

    return (
        result["Approval_status"]
        if result
        else None
    )


def get_pending_admins():
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                u.User_ID,
                u.First_name,
                u.Email,
                a.Admin_role,
                a.Approval_status
            FROM admin a
            JOIN users u
                ON a.User_ID = u.User_ID
            WHERE a.Approval_status IN ('Pending', 'OTP_Sent')
            ORDER BY
                a.Approval_status ASC,
                u.User_ID DESC
            """
        )

        results = cursor.fetchall()

    conn.close()

    return results


def approve_admin(
    user_id,
    approver_id,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            UPDATE admin
            SET Approval_status = 'Approved'
            WHERE User_ID = %s
            """,
            (user_id,),
        )

        cursor.execute(
            """
            INSERT INTO admin_action
            (
                Admin_ID,
                Target_User_ID,
                Action_type
            )
            VALUES (%s, %s, %s)
            """,
            (
                approver_id,
                user_id,
                "approve_admin",
            ),
        )

    conn.commit()
    conn.close()


# =====================================================
# ADMIN OTP
# =====================================================

def save_admin_otp(
    user_id,
    otp_code,
    expiry_minutes=10,
):
    expiry = (
        datetime.now()
        + timedelta(minutes=expiry_minutes)
    )

    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            UPDATE admin
            SET
                Otp_code = %s,
                Otp_expiry = %s,
                Approval_status = 'OTP_Sent'
            WHERE User_ID = %s
            """,
            (
                otp_code,
                expiry,
                user_id,
            ),
        )

    conn.commit()
    conn.close()


def verify_admin_otp(
    email,
    otp_code,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                u.User_ID,
                a.Otp_code,
                a.Otp_expiry,
                a.Approval_status
            FROM users u
            JOIN admin a
                ON u.User_ID = a.User_ID
            WHERE u.Email = %s
            """,
            (email,),
        )

        row = cursor.fetchone()

        if not row:

            conn.close()

            return (
                False,
                "No pending admin request found for this email.",
            )

        if row["Approval_status"] != "OTP_Sent":

            conn.close()

            return (
                False,
                "No verification code has been sent for this account yet.",
            )

        if row["Otp_code"] != otp_code:

            conn.close()

            return (
                False,
                "Incorrect verification code.",
            )

        if (
            row["Otp_expiry"] is None
            or datetime.now() > row["Otp_expiry"]
        ):

            conn.close()

            return (
                False,
                "This code has expired. "
                "Ask a Super Admin to resend it.",
            )

        cursor.execute(
            """
            UPDATE admin
            SET
                Approval_status = 'Approved',
                Otp_code = NULL,
                Otp_expiry = NULL
            WHERE User_ID = %s
            """,
            (row["User_ID"],),
        )

    conn.commit()
    conn.close()

    return (
        True,
        "Email verified successfully! "
        "Your admin account is now approved. "
        "You can log in.",
    )


def get_admin_name_email(user_id):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                First_name,
                Email
            FROM users
            WHERE User_ID = %s
            """,
            (user_id,),
        )

        result = cursor.fetchone()

    conn.close()

    return result


# =====================================================
# ADMIN REJECTION
# =====================================================

def reject_admin_with_reason(
    user_id,
    approver_id,
    reason,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                First_name,
                Email
            FROM users
            WHERE User_ID = %s
            """,
            (user_id,),
        )

        person = cursor.fetchone()

        if not person:

            conn.close()

            return False

        cursor.execute(
            """
            INSERT INTO admin_rejection_log
            (
                Rejected_Email,
                Rejected_Name,
                Reason,
                Rejected_By
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                person["Email"],
                person["First_name"],
                reason,
                approver_id,
            ),
        )

        cursor.execute(
            """
            INSERT INTO admin_action
            (
                Admin_ID,
                Target_User_ID,
                Action_type
            )
            VALUES (%s, %s, %s)
            """,
            (
                approver_id,
                user_id,
                "reject_admin",
            ),
        )

        cursor.execute(
            """
            DELETE FROM admin
            WHERE User_ID = %s
            """,
            (user_id,),
        )

        cursor.execute(
            """
            DELETE FROM users
            WHERE User_ID = %s
            """,
            (user_id,),
        )

    conn.commit()
    conn.close()

    return True


def get_rejection_log():
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                rl.Rejected_Name,
                rl.Rejected_Email,
                rl.Reason,
                rl.Rejected_At,
                u.Email AS Rejected_By_Email
            FROM admin_rejection_log rl
            JOIN users u
                ON rl.Rejected_By = u.User_ID
            ORDER BY rl.Rejected_At DESC
            """
        )

        results = cursor.fetchall()

    conn.close()

    return results


# =====================================================
# UPDATE USER PROFILE
# =====================================================

def update_user_profile(
    user_id,
    first_name,
    email,
    profile_image=None,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        if profile_image:

            cursor.execute(
                """
                UPDATE users
                SET
                    First_name = %s,
                    Email = %s,
                    Profile_image = %s
                WHERE User_ID = %s
                """,
                (
                    first_name,
                    email,
                    profile_image,
                    user_id,
                ),
            )

        else:

            cursor.execute(
                """
                UPDATE users
                SET
                    First_name = %s,
                    Email = %s
                WHERE User_ID = %s
                """,
                (
                    first_name,
                    email,
                    user_id,
                ),
            )

    conn.commit()
    conn.close()


# =====================================================
# FORGOT PASSWORD
# =====================================================

def save_password_reset_otp(
    email,
    otp_code,
    expiry_minutes=10,
):
    expiry = (
        datetime.now()
        + timedelta(minutes=expiry_minutes)
    )

    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            UPDATE users
            SET
                Password_Reset_OTP = %s,
                Password_Reset_Expiry = %s
            WHERE Email = %s
            """,
            (
                otp_code,
                expiry,
                email,
            )
        )

    conn.commit()
    conn.close()


def verify_password_reset_otp(
    email,
    otp_code,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                User_ID,
                Password_Reset_OTP,
                Password_Reset_Expiry
            FROM users
            WHERE Email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:

            conn.close()

            return (
                False,
                "Invalid email address."
            )

        if not user["Password_Reset_OTP"]:

            conn.close()

            return (
                False,
                "No password reset code was requested."
            )

        if user["Password_Reset_OTP"] != otp_code:

            conn.close()

            return (
                False,
                "Incorrect verification code."
            )

        if (
            user["Password_Reset_Expiry"] is None
            or datetime.now() > user["Password_Reset_Expiry"]
        ):

            conn.close()

            return (
                False,
                "Verification code has expired."
            )

        conn.close()

        return (
            True,
            "OTP verified successfully."
        )


def reset_user_password(
    email,
    new_hashed_password,
):
    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            """
            UPDATE users
            SET
                Password = %s,
                Password_Reset_OTP = NULL,
                Password_Reset_Expiry = NULL
            WHERE Email = %s
            """,
            (
                new_hashed_password,
                email,
            )
        )

    conn.commit()
    conn.close()


# =====================================================
# SYSTEM SETTINGS (Risk Thresholds)
# =====================================================

def get_setting(key, default=None):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT Setting_value FROM system_settings WHERE Setting_key = %s",
            (key,)
        )
        result = cursor.fetchone()
    conn.close()
    return result['Setting_value'] if result else default


def get_all_settings():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM system_settings ORDER BY Setting_key")
        results = cursor.fetchall()
    conn.close()
    return results


def update_setting(key, value):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE system_settings SET Setting_value = %s WHERE Setting_key = %s",
            (value, key)
        )
    conn.commit()
    conn.close()


# =====================================================
# NOTIFICATIONS
# =====================================================

def create_notification(user_id, message):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO notification (User_ID, Message) VALUES (%s, %s)",
            (user_id, message)
        )
    conn.commit()
    conn.close()


def get_user_notifications(user_id, unread_only=False):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        query = "SELECT * FROM notification WHERE User_ID = %s"
        if unread_only:
            query += " AND Is_read = 0"
        query += " ORDER BY Created_at DESC"
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
    conn.close()
    return results


def mark_notifications_read(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE notification SET Is_read = 1 WHERE User_ID = %s", (user_id,))
    conn.commit()
    conn.close()


def get_unread_count(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM notification WHERE User_ID = %s AND Is_read = 0",
            (user_id,)
        )
        result = cursor.fetchone()
    conn.close()
    return result['cnt']


# =====================================================
# IMPORT DATA (Bulk Course Import)
# =====================================================

def bulk_import_courses(course_list):
    conn = get_db_connection()
    inserted, skipped = 0, 0
    with conn.cursor() as cursor:
        for course_name, description in course_list:
            cursor.execute("SELECT Course_ID FROM course WHERE Course_name = %s", (course_name,))
            if cursor.fetchone():
                skipped += 1
                continue
            cursor.execute(
                "INSERT INTO course (Course_name, Description) VALUES (%s, %s)",
                (course_name, description)
            )
            inserted += 1
    conn.commit()
    conn.close()
    return inserted, skipped   


# =====================================================
# PASSWORD RESET RATE LIMITING
# =====================================================

MAX_RESET_REQUESTS = 3
RESET_WINDOW_MINUTES = 15


def check_and_update_reset_rate_limit(email):
    """
    Returns (allowed: bool, wait_message: str or None).
    Limits a single email to MAX_RESET_REQUESTS OTP requests
    within a RESET_WINDOW_MINUTES rolling window.
    """
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT Password_Reset_Request_Count, Password_Reset_Window_Start
            FROM users WHERE Email = %s
            """,
            (email,)
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            return True, None

        now = datetime.now()
        window_start = row['Password_Reset_Window_Start']
        count = row['Password_Reset_Request_Count'] or 0

        # No window yet, or window expired -> start a fresh one
        if window_start is None or (now - window_start) > timedelta(minutes=RESET_WINDOW_MINUTES):
            cursor.execute(
                """
                UPDATE users
                SET Password_Reset_Request_Count = 1,
                    Password_Reset_Window_Start = %s
                WHERE Email = %s
                """,
                (now, email)
            )
            conn.commit()
            conn.close()
            return True, None

        # Still inside window -> check limit
        if count >= MAX_RESET_REQUESTS:
            minutes_left = RESET_WINDOW_MINUTES - int((now - window_start).total_seconds() // 60)
            conn.close()
            return False, (
                f"Too many verification code requests. "
                f"Please try again in {max(minutes_left, 1)} minute(s)."
            )

        cursor.execute(
            """
            UPDATE users
            SET Password_Reset_Request_Count = Password_Reset_Request_Count + 1
            WHERE Email = %s
            """,
            (email,)
        )
        conn.commit()
        conn.close()
        return True, None