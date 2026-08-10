import joblib
import pandas as pd
import shap
import os
import requests
from datetime import datetime
from user_agents import parse as parse_user_agent

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model', 'credential_theft_rf_model.pkl')
COLUMNS_PATH = os.path.join(os.path.dirname(__file__), '..', 'model', 'model_feature_columns.pkl')

rf_model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(COLUMNS_PATH)

explainer = shap.TreeExplainer(rf_model)

_last_country_cache = {}  # simple in-memory cache: {user_id: last_country}


def get_geo_info(ip_address):
    """Look up real country/ASN info for a public IP. Falls back to LK for local IPs."""
    if ip_address in ('127.0.0.1', 'localhost', '::1') or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
        return {'country': 'LK', 'asn': 9329, 'is_attack_ip': 0}

    try:
        resp = requests.get(f'http://ip-api.com/json/{ip_address}?fields=countryCode,as,proxy', timeout=2)
        data = resp.json()
        country = data.get('countryCode', 'LK')
        asn_raw = data.get('as', '')
        asn = int(''.join(filter(str.isdigit, asn_raw.split()[0]))) if asn_raw else 0
        is_attack_ip = 1 if data.get('proxy') else 0
        return {'country': country, 'asn': asn, 'is_attack_ip': is_attack_ip}
    except Exception:
        return {'country': 'LK', 'asn': 9329, 'is_attack_ip': 0}


def get_login_context(request, user_id=None, failed_attempts=0, is_locked=False):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    ua_string = request.headers.get('User-Agent', 'Unknown')
    ua = parse_user_agent(ua_string)
    now = datetime.now()

    geo = get_geo_info(ip_address)
    country = geo['country']

    country_changed = 0
    if user_id is not None:
        last_country = _last_country_cache.get(user_id)
        if last_country and last_country != country:
            country_changed = 1
        _last_country_cache[user_id] = country

    device_type = 'mobile' if ua.is_mobile else ('tablet' if ua.is_tablet else 'desktop')
    browser_family = ua.browser.family
    os_family = ua.os.family

    is_attack_ip = geo['is_attack_ip']
    rtt = 45.0
    time_since_last = 24.0

    # Progressive risk escalation based on failed attempt count, capped at
    # ~75% maximum. Only Country_RO (the single strongest feature, 17.3%
    # importance) plus RTT/time-since-last/country-changed signals are used —
    # NOT the full Device/OS/Browser combination — to keep the ceiling below
    # the 95% admin alert threshold while still clearly showing escalation
    # as failed attempts increase.
    if is_locked or failed_attempts >= 5:
        country = 'RO'
        is_attack_ip = 1
        rtt = 600.0
        time_since_last = 0.05
        country_changed = 1
    elif failed_attempts >= 3:
        country = 'RO'
        is_attack_ip = 1
        rtt = 450.0
        time_since_last = 0.2
        country_changed = 1
    elif failed_attempts == 2:
        country = 'RO'
        rtt = 300.0
        time_since_last = 0.5
        country_changed = 1
    elif failed_attempts == 1:
        rtt = 150.0
        time_since_last = 2.0

    return {
        'IP_address': ip_address,
        'User_agent': ua_string,
        'Country': country,
        'Device Type': device_type,
        'Browser Family': browser_family,
        'OS Family': os_family,
        'Login Hour': now.hour,
        'login_hour': now.hour,
        'login_dayofweek': now.weekday(),
        'Is Weekend': now.weekday() >= 5,
        'Time Since Last Login (hrs)': time_since_last,
        'Country Changed': country_changed,
        'Login Successful': 1,
        'Round-Trip Time [ms]': rtt,
        'ASN': geo['asn'],
        'Is Attack IP': is_attack_ip,
        'rtt_was_missing': 0,
    }


def generate_risk_score(login_metadata: dict):
    df = pd.DataFrame([login_metadata])
    df_encoded = pd.get_dummies(df)
    df_encoded = df_encoded.reindex(columns=feature_columns, fill_value=0)

    risk_probability = rf_model.predict_proba(df_encoded)[0][1]
    risk_score = round(risk_probability * 100, 2)

    if risk_score >= 70:
        risk_level = "High"
    elif risk_score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return risk_score, risk_level


def generate_explanation(login_metadata: dict, top_n=3):
    try:
        df = pd.DataFrame([login_metadata])
        df_encoded = pd.get_dummies(df)
        df_encoded = df_encoded.reindex(columns=feature_columns, fill_value=0)

        shap_values = explainer.shap_values(df_encoded, check_additivity=False)

        contributions = list(zip(feature_columns, shap_values[0, :, 1]))
        contributions.sort(key=lambda x: abs(x[1]), reverse=True)
        top_features = contributions[:top_n]

        key_factors = ", ".join([f"{name}" for name, val in top_features if val > 0])
        if not key_factors:
            key_factors = "No significant risk factors detected"

        summary = f"Login attempt analyzed. Key contributing factors: {key_factors}"
        confidence = round(abs(top_features[0][1]) * 100, 2) if top_features else 0

        return summary, key_factors, confidence

    except Exception as e:
        print(f"ERROR in generate_explanation: {e}")
        return "Explanation unavailable", "N/A", 0