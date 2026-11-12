import pandas as pd
import numpy as np
from datetime import datetime

class DataCleaner:
    @staticmethod
    def clean_transactions_df(df):
        """
        Validates and cleans transaction DataFrame.
        Required columns: sender_account, receiver_account, amount, sender_country, receiver_country
        """
        cleaned = df.copy()

        # Fill missing values
        cleaned['currency'] = cleaned.get('currency', 'USD').fillna('USD')
        cleaned['transaction_type'] = cleaned.get('transaction_type', 'WIRE').fillna('WIRE')
        cleaned['description'] = cleaned.get('description', 'Standard Transfer').fillna('Standard Transfer')
        cleaned['sender_country'] = cleaned.get('sender_country', 'United States').fillna('United States')
        cleaned['receiver_country'] = cleaned.get('receiver_country', 'United States').fillna('United States')

        # Clean numerical amount
        cleaned['amount'] = pd.to_numeric(cleaned['amount'], errors='coerce').fillna(0.0)
        cleaned = cleaned[cleaned['amount'] > 0]

        # Standardize dates
        if 'transaction_date' in cleaned.columns:
            cleaned['transaction_date'] = pd.to_datetime(cleaned['transaction_date'], errors='coerce').fillna(datetime.utcnow())
        else:
            cleaned['transaction_date'] = datetime.utcnow()

        return cleaned

    @staticmethod
    def clean_customers_df(df):
        cleaned = df.copy()
        cleaned['name'] = cleaned.get('name', 'Unknown Customer').fillna('Unknown Customer')
        cleaned['age'] = pd.to_numeric(cleaned.get('age', 35), errors='coerce').fillna(35).astype(int)
        cleaned['occupation'] = cleaned.get('occupation', 'Unspecified').fillna('Unspecified')
        cleaned['country'] = cleaned.get('country', 'United States').fillna('United States')
        return cleaned
