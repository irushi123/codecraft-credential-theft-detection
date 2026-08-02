import joblib
import pandas as pd
import shap
import os
from datetime import datetime

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model', 'credential_theft_rf_model.pkl')
COLUMNS_PATH = os.path.join(os.path.dirname(__file__), '..', 'model', 'model_feature_columns.pkl')

rf_model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(COLUMNS_PATH)

explainer = shap.TreeExplainer(rf_model)


def get_login_context(request):
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')

    if ip_address in ('127.0.0.1', 'localhost') or str(ip_address).startswith('192.168.'):
        country = 'LK'
    else:
        country = 'Unknown'

    if 'Mobile' in user_agent:
        device_type = 'mobile'
    else:
        device_type = 'desktop'

    if 'Chrome' in user_agent:
        browser_family = 'Chrome'
    elif 'Firefox' in user_agent:
        browser_family = 'Firefox'
    elif 'Safari' in user_agent:
        browser_family = 'Safari'
    else:
        browser_family = 'Other'

    if 'Windows' in user_agent:
        os_family = 'Windows'
    elif 'Mac' in user_agent:
        os_family = 'Mac OS'
    elif 'Linux' in user_agent:
        os_family = 'Linux'
    else:
        os_family = 'Other'

    now = datetime.now()

    return {
        'IP_address': ip_address,
        'User_agent': user_agent,
        'Country': country,
        'Device Type': device_type,
        'Browser Family': browser_family,
        'OS Family': os_family,
        'Login Hour': now.hour,
        'Is Weekend': now.weekday() >= 5,
        'Time Since Last Login (hrs)': -1,
        'Country Changed': 0,
        'Login Successful': 1,
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

        print("SHAP values shape:", shap_values.shape)

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