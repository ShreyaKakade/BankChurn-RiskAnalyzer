import os
import joblib
import pickle
import numpy as np

def _first_existing(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None

def load_artifacts():
    base = os.path.dirname(os.path.dirname(__file__))
    model_path = _first_existing([
        os.path.join(base, "models", "churn_model.pkl"),
        "/mnt/data/churn_model.pkl"
    ])
    geo_path = _first_existing([
        os.path.join(base, "models", "geography_encoder.pkl"),
        "/mnt/data/geography_encoder.pkl"
    ])
    scaler_path = _first_existing([
        os.path.join(base, "models", "scaler.pkl"),
        "/mnt/data/scaler.pkl"
    ])

    if not model_path or not geo_path or not scaler_path:
        raise FileNotFoundError("One or more model files are missing.")

    try:
        model = joblib.load(model_path)
    except Exception:
        with open(model_path, "rb") as f:
            model = pickle.load(f)

    try:
        geo_encoder = joblib.load(geo_path)
    except Exception:
        with open(geo_path, "rb") as f:
            geo_encoder = pickle.load(f)

    with open(scaler_path, "rb") as f:
        feature_order = pickle.load(f)
    scaler = None  # Placeholder for scaler (update if scaling is needed)
    return model, geo_encoder, feature_order, scaler

def build_feature_vector(form, feature_order, geo_encoder, scaler=None):
    """Build features in the exact order expected by the model."""
    geo_map = {'France': 0, 'Spain': 1, 'Germany': 2}
    gender_map = {'Female': 0, 'Male': 1}

    values = {}
    def _to_float(name, default=0.0):
        try:
            return float(form.get(name, default))
        except Exception:
            return float(default)

    def _to_int(name, default=0):
        try:
            return int(float(form.get(name, default)))
        except Exception:
            return int(default)

    values['CreditScore'] = _to_int('credit_score')
    g_str = form.get('geography', 'France')
    g_enc = geo_map.get(g_str, 0)  # Use geo_map, as geo_encoder is a numpy array
    values['Geography'] = g_enc
    values['Gender'] = gender_map.get(form.get('gender', 'Female'), 0)
    values['Age'] = _to_int('age')
    values['Tenure'] = _to_int('tenure')
    values['Balance'] = _to_float('balance')
    values['NumOfProducts'] = _to_int('num_products')
    values['HasCrCard'] = 1 if form.get('has_cr_card', 'No') == 'Yes' else 0
    values['IsActiveMember'] = 1 if form.get('is_active', 'No') == 'Yes' else 0
    values['EstimatedSalary'] = _to_float('estimated_salary')

    missing = [col for col in feature_order if col not in values]
    if missing:
        raise ValueError(f"Missing features: {missing}")

    row = [values.get(col, 0) for col in feature_order]
    X = np.array(row, dtype=float).reshape(1, -1)
    if scaler is not None:
        numerical_indices = [feature_order.index(col) for col in ['CreditScore', 'Age', 'Tenure', 'Balance', 'EstimatedSalary']]
        X[:, numerical_indices] = scaler.transform(X[:, numerical_indices])
    print("Feature vector:", X)  # Debug
    return X