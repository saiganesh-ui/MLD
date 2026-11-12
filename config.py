import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ml-detection-system-super-secret-key-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "money_laundering.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Ontology paths
    ONTOLOGY_PATH = os.path.join(BASE_DIR, 'ontology', 'laundering_ontology.owl')
    
    # ML paths
    ML_MODEL_PATH = os.path.join(BASE_DIR, 'ml', 'model.pkl')
    
    # Upload config
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'csv'}
    
    # Risk Scoring Weights (Total max = 100)
    RISK_WEIGHTS = {
        'amount_anomaly': 25,
        'frequency_anomaly': 20,
        'transaction_pattern': 25,
        'geographic_factor': 15,
        'historical_behavior': 15
    }
    
    # Risk Thresholds
    RISK_THRESHOLDS = {
        'low_max': 30,
        'medium_max': 70,
        'high_min': 71
    }
    
    # Rule Thresholds
    LARGE_TRANSACTION_THRESHOLD = 50000.0  # $50,000
    STRUCTURING_MIN_AMOUNT = 8000.0       # $8,000
    STRUCTURING_MAX_AMOUNT = 9999.0       # $9,999
    HIGH_FREQUENCY_THRESHOLD = 5          # > 5 transactions in time window
    HIGH_FREQUENCY_WINDOW_HOURS = 24
    RAPID_TRANSFER_WINDOW_HOURS = 6
    DORMANT_DAYS_THRESHOLD = 90
    
    # High Risk Jurisdiction / Countries Metadata
    HIGH_RISK_COUNTRIES = [
        'Cayman Islands', 'Panama', 'Seychelles', 'North Korea',
        'Iran', 'Vanuatu', 'Bahamas', 'British Virgin Islands',
        'Belize', 'Malta', 'Cyprus', 'Marshall Islands'
    ]

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
