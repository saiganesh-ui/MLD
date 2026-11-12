import pandas as pd
import numpy as np

class FeatureEngineer:
    @staticmethod
    def extract_transaction_features(df):
        """
        Extracts temporal and behavioral feature columns from raw transactions DataFrame.
        """
        features = df.copy()

        # Cross-border flag
        features['is_cross_border'] = (features['sender_country'].str.strip().str.lower() != features['receiver_country'].str.strip().str.lower()).astype(int)

        # Log amount
        features['log_amount'] = np.log1p(features['amount'])

        # Hour of day / day of week
        if 'transaction_date' in features.columns:
            dt = pd.to_datetime(features['transaction_date'])
            features['hour'] = dt.dt.hour
            features['day_of_week'] = dt.dt.dayofweek
        else:
            features['hour'] = 12
            features['day_of_week'] = 2

        return features
