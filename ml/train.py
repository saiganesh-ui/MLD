import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from config import Config

def train_anomaly_model(data_df=None, output_path=None):
    """
    Trains an Isolation Forest anomaly detection model.
    """
    output_path = output_path or Config.ML_MODEL_PATH
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if data_df is None or len(data_df) < 20:
        # Generate synthetic training feature distributions
        np.random.seed(42)
        normal_amounts = np.random.exponential(scale=1500, size=2000)
        suspicious_amounts = np.random.uniform(8000, 200000, size=100)
        amounts = np.hstack([normal_amounts, suspicious_amounts])

        freqs = np.random.poisson(lam=1.5, size=2100)
        freqs[-100:] += np.random.randint(5, 15, size=100)

        cross_border = np.random.binomial(n=1, p=0.1, size=2100)
        cross_border[-100:] = np.random.binomial(n=1, p=0.8, size=100)

        data = pd.DataFrame({
            'amount': amounts,
            'frequency': freqs,
            'cross_border': cross_border
        })
    else:
        data = data_df[['amount', 'frequency', 'cross_border']].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data)

    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X_scaled)

    payload = {
        'model': model,
        'scaler': scaler,
        'feature_names': ['amount', 'frequency', 'cross_border']
    }

    with open(output_path, 'wb') as f:
        pickle.dump(payload, f)

    print(f"ML Anomaly detection model trained and saved to {output_path}")
    return payload

if __name__ == '__main__':
    train_anomaly_model()
