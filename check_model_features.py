"""
Diagnostic script — checks which Country values the trained model
actually recognizes as one-hot encoded features. Run this from your
project root (where the model/ folder is).
"""

import joblib
from xgboost import XGBClassifier

MODEL_PATH = 'model/credential_theft_xgb_model.json'
COLUMNS_PATH = 'model/model_feature_columns.pkl'

xgb_model = XGBClassifier()
xgb_model.load_model(MODEL_PATH)

feature_columns = xgb_model.get_booster().feature_names

print(f"\nTotal features the model was trained on: {len(feature_columns)}\n")

print("=== Country-related features ===")
country_features = [f for f in feature_columns if 'Country' in f]
for f in country_features:
    print(f"  {f}")

print(f"\n=== Device Type features ===")
device_features = [f for f in feature_columns if 'Device' in f]
for f in device_features:
    print(f"  {f}")

print(f"\n=== Browser features ===")
browser_features = [f for f in feature_columns if 'Browser' in f]
for f in browser_features:
    print(f"  {f}")

print(f"\n=== OS features ===")
os_features = [f for f in feature_columns if 'OS' in f]
for f in os_features:
    print(f"  {f}")

print(f"\n=== All numeric/other features ===")
categorical_prefixes = ('Country', 'Device', 'Browser', 'OS')
other_features = [
    f for f in feature_columns
    if not f.startswith(categorical_prefixes)
]
for f in other_features:
    print(f"  {f}")
