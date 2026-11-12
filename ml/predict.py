import os
import pickle
import numpy as np
from config import Config
from ml.train import train_anomaly_model

class MLAnomalyPredictor:
    def __init__(self, model_path=None):
        self.model_path = model_path or Config.ML_MODEL_PATH
        self.model = None
        self.scaler = None
        self.load_model()

    def load_model(self):
        if not os.path.exists(self.model_path):
            print("ML model file missing. Training initial model...")
            payload = train_anomaly_model(output_path=self.model_path)
            self.model = payload['model']
            self.scaler = payload['scaler']
        else:
            try:
                with open(self.model_path, 'rb') as f:
                    payload = pickle.load(f)
                    self.model = payload['model']
                    self.scaler = payload['scaler']
            except Exception as e:
                print(f"Error loading ML model: {e}. Retraining...")
                payload = train_anomaly_model(output_path=self.model_path)
                self.model = payload['model']
                self.scaler = payload['scaler']

    def predict_anomaly(self, amount, frequency, cross_border):
        """
        Predicts anomaly status and returns normalized anomaly score (0-100).
        """
        if self.model is None or self.scaler is None:
            self.load_model()

        X = np.array([[float(amount), float(frequency), 1.0 if cross_border else 0.0]])
        X_scaled = self.scaler.transform(X)

        # Isolation forest decision_function returns negative for anomalies, positive for normal
        raw_score = self.model.decision_function(X_scaled)[0]
        prediction = self.model.predict(X_scaled)[0]  # -1 for anomaly, 1 for normal

        # Map decision score to 0..100 range (lower decision score -> higher anomaly score)
        # raw_score is typically between -0.3 and 0.3
        normalized_score = float(np.clip((0.3 - raw_score) / 0.6 * 100, 0, 100))
        is_anomaly = bool(prediction == -1 or normalized_score > 60)

        return {
            'is_anomaly': is_anomaly,
            'raw_decision_score': float(raw_score),
            'anomaly_score': round(normalized_score, 2),
            'status': 'ANOMALOUS' if is_anomaly else 'NORMAL'
        }
