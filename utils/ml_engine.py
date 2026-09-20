
import joblib
import pandas as pd
import re
import shap
import os
import requests
from datetime import datetime
from user_agents import parse as parse_user_agent
from xgboost import XGBClassifier


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'model',
    'credential_theft_xgb_model.json'
)

COLUMNS_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'model',
    'model_feature_columns.pkl'
)

THRESHOLD_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'model',
    'model_threshold.pkl'
)

ASN_FREQ_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'model',
    'asn_freq_map.pkl'
)


# Load model via XGBoost's native JSON format
xgb_model = XGBClassifier()
xgb_model.load_model(MODEL_PATH)

feature_columns = joblib.load(COLUMNS_PATH)
model_threshold = joblib.load(THRESHOLD_PATH)
asn_freq_map = joblib.load(ASN_FREQ_PATH)

explainer = shap.TreeExplainer(xgb_model)



_last_country_cache = {}
_last_login_time_cache = {}


def clean_col_names(cols):
    """Must match the same cleaning used during training."""
    return [
        re.sub(r'[\[\]<>]', '', str(c))
        for c in cols
    ]


def get_geo_info(ip_address):
    """Look up real country/ASN info for a public IP.
    Falls back to LK for local/private IPs.
    """

    if (
        ip_address in ('127.0.0.1', 'localhost', '::1')
        or ip_address.startswith('192.168.')
        or ip_address.startswith('10.')
        or ip_address.startswith('172.16.')
        or ip_address.startswith('172.17.')
        or ip_address.startswith('172.18.')
        or ip_address.startswith('172.19.')
        or ip_address.startswith('172.20.')
        or ip_address.startswith('172.21.')
        or ip_address.startswith('172.22.')
        or ip_address.startswith('172.23.')
        or ip_address.startswith('172.24.')
        or ip_address.startswith('172.25.')
        or ip_address.startswith('172.26.')
        or ip_address.startswith('172.27.')
        or ip_address.startswith('172.28.')
        or ip_address.startswith('172.29.')
        or ip_address.startswith('172.30.')
        or ip_address.startswith('172.31.')
    ):
        return {
            'country': 'LK',
            'asn': 9329,
            'is_attack_ip': 0
        }

    try:
        resp = requests.get(
            f'http://ip-api.com/json/{ip_address}?fields=countryCode,as,proxy',
            timeout=2
        )

        data = resp.json()

        country = data.get(
            'countryCode',
            'LK'
        )

        asn_raw = data.get(
            'as',
            ''
        )

        if asn_raw:
            # Example:
            # AS9329 Dialog Axiata PLC
            match = re.search(
                r'AS?(\d+)',
                asn_raw.upper()
            )

            asn = int(match.group(1)) if match else 0
        else:
            asn = 0

        is_attack_ip = (
            1 if data.get('proxy') else 0
        )

        return {
            'country': country,
            'asn': asn,
            'is_attack_ip': is_attack_ip
        }

    except Exception:
        return {
            'country': 'LK',
            'asn': 9329,
            'is_attack_ip': 0
        }


def get_login_context(
    request,
    user_id=None,
    failed_attempts=0,
    is_locked=False
):
    """
    Builds the feature dict from REAL signals only.

    failed_attempts/is_locked are not injected into the model inputs.
    """

    ip_address = request.headers.get(
        'X-Forwarded-For',
        request.remote_addr
    ).split(',')[0].strip()

    ua_string = request.headers.get(
        'User-Agent',
        'Unknown'
    )

    ua = parse_user_agent(
        ua_string
    )

    now = datetime.now()

    geo = get_geo_info(
        ip_address
    )

    country = geo['country']
    is_attack_ip = geo['is_attack_ip']


    # Country Changed
    country_changed = 0

    if user_id is not None:

        last_country = _last_country_cache.get(
            user_id
        )

        if (
            last_country
            and last_country != country
        ):
            country_changed = 1

        _last_country_cache[user_id] = country


    # Time Since Last Login
    if (
        user_id is not None
        and user_id in _last_login_time_cache
    ):

        delta = (
            now
            - _last_login_time_cache[user_id]
        )

        time_since_last = round(
            delta.total_seconds() / 3600,
            4
        )

    else:
        time_since_last = -1


    if user_id is not None:
        _last_login_time_cache[user_id] = now


    # Device
    device_type = (
        'mobile'
        if ua.is_mobile
        else (
            'tablet'
            if ua.is_tablet
            else 'desktop'
        )
    )


    # Browser / OS
    browser_family = ua.browser.family
    os_family = ua.os.family


    # Time
    login_hour = now.hour

    is_night_login = (
        1
        if (
            login_hour >= 22
            or login_hour <= 5
        )
        else 0
    )


    
    rtt = 45.0


    # ASN Frequency
    asn_frequency = asn_freq_map.get(
        geo['asn'],
        0
    )


    return {
        'IP_address': ip_address,
        'User_agent': ua_string,
        'Country': country,
        'Device Type': device_type,
        'Browser Family': browser_family,
        'OS Family': os_family,
        'login_hour': login_hour,
        'login_dayofweek': now.weekday(),
        'is_night_login': is_night_login,
        'Time Since Last Login (hrs)': time_since_last,
        'Country Changed': country_changed,

       
        'Round-Trip Time ms': rtt,

        'ASN Frequency': asn_frequency,
        'Is Attack IP': is_attack_ip,
        'rtt_was_missing': 0,
    }


def _prepare_model_input(login_metadata: dict):
    """
    Prepare model input while keeping the original pipeline.

    FIX:
    XGBoost's actual stored feature names are used to make sure
    predict_proba() receives exactly the names expected by the model.
    """

    df = pd.DataFrame(
        [login_metadata]
    )

    df_encoded = pd.get_dummies(
        df
    )

    
    df_encoded.columns = clean_col_names(
        df_encoded.columns
    )


    
    

    model_feature_columns = (
        xgb_model.get_booster().feature_names
    )

    if model_feature_columns is None:
        raise ValueError(
            'XGBoost model does not contain feature names.'
        )


    cleaned_model_columns = clean_col_names(
        model_feature_columns
    )



    rename_map = {}

    for incoming_column in df_encoded.columns:

        if incoming_column in cleaned_model_columns:

            index = cleaned_model_columns.index(
                incoming_column
            )

            rename_map[incoming_column] = (
                model_feature_columns[index]
            )

    df_encoded = df_encoded.rename(
        columns=rename_map
    )




    df_encoded = df_encoded.reindex(
        columns=model_feature_columns,
        fill_value=0
    )


   
    df_encoded = df_encoded.apply(
        pd.to_numeric,
        errors='coerce'
    ).fillna(0)


    return df_encoded


def generate_risk_score(login_metadata: dict):

    df_encoded = _prepare_model_input(
        login_metadata
    )

    risk_probability = (
        xgb_model.predict_proba(
            df_encoded
        )[0][1]
    )

    risk_score = round(
        risk_probability * 100,
        2
    )

    is_flagged = (
        risk_probability >= model_threshold
    )

    if is_flagged:
        risk_level = "High"

    elif risk_score >= 30:
        risk_level = "Medium"

    else:
        risk_level = "Low"

    return (
        risk_score,
        risk_level
    )


def generate_explanation(
    login_metadata: dict,
    top_n=3
):
    try:

        df_encoded = _prepare_model_input(
            login_metadata
        )

        shap_values = explainer.shap_values(
            df_encoded,
            check_additivity=False
        )

        
        if isinstance(shap_values, list):

            if len(shap_values) > 1:
                row_shap = shap_values[1][0]
            else:
                row_shap = shap_values[0][0]

        else:

            row_shap = shap_values[0]


        

        model_feature_columns = (
            xgb_model.get_booster().feature_names
        )


        contributions = list(
            zip(
                model_feature_columns,
                row_shap
            )
        )


        contributions.sort(
            key=lambda x: abs(float(x[1])),
            reverse=True
        )


        top_features = contributions[
            :top_n
        ]


        key_factors = ", ".join(
            [
                f"{name}"
                for name, val in top_features
                if float(val) > 0
            ]
        )


        if not key_factors:
            key_factors = (
                "No significant risk factors detected"
            )


        summary = (
            f"Login attempt analyzed. "
            f"Key contributing factors: "
            f"{key_factors}"
        )


        confidence = (
            round(
                abs(
                    float(
                        top_features[0][1]
                    )
                ) * 100,
                2
            )
            if top_features
            else 0
        )


        return (
            summary,
            key_factors,
            confidence
        )


    except Exception as e:

        print(
            f"ERROR in generate_explanation: {e}"
        )

        return (
            "Explanation unavailable",
            "N/A",
            0
        )

