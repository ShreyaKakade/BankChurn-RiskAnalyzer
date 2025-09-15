import pickle
import numpy as np
from utils.preprocess import load_artifacts, build_feature_vector

# Example input (same as provided earlier)
form_data = {
    'credit_score': '550',
    'geography': 'Germany',
    'gender': 'Female',
    'age': '45',
    'tenure': '2',
    'balance': '120000',
    'num_products': '1',
    'has_cr_card': 'No',
    'is_active': 'No',
    'estimated_salary': '75000'
}

# Load artifacts
try:
    model, geo_encoder, feature_order = load_artifacts()
except Exception as e:
    print(f"Error loading artifacts: {e}")
    exit()

# Build feature vector
X = build_feature_vector(form_data, feature_order, geo_encoder)
print("Feature vector:", X)

# Predict
prediction = model.predict(X)[0]
print(f"Prediction: {'Customer Will Churn' if prediction == 1 else 'Customer Will Stay'}")

# Check probability (if supported)
if hasattr(model, 'predict_proba'):
    proba = model.predict_proba(X)[0][1]
    print(f"Churn Probability: {round(proba * 100, 2)}%")
else:
    print("Model does not support predict_proba")