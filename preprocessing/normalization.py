import numpy as np

class DataNormalizer:
    @staticmethod
    def min_max_scale(series, min_val=0, max_val=100):
        s_min = series.min()
        s_max = series.max()
        if s_max == s_min:
            return np.zeros_like(series)
        return (series - s_min) / (s_max - s_min) * (max_val - min_val) + min_val

    @staticmethod
    def z_score_scale(series):
        std = series.std()
        if std == 0:
            return np.zeros_like(series)
        return (series - series.mean()) / std
