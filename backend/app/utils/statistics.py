"""
Statistical calculation utilities for VitaChain
"""

from typing import List, Optional, Tuple
import numpy as np
from scipy import stats
from scipy.stats import linregress


def calculate_trend(data: List[float]) -> str:
    """
    Calculate trend direction using linear regression
    
    Args:
        data: List of numeric values
        
    Returns:
        Trend direction: 'increasing', 'decreasing', 'stable', or 'insufficient_data'
    """
    if len(data) < 2:
        return "insufficient_data"
    
    try:
        x = np.arange(len(data))
        y = np.array(data)
        
        # Remove NaN values
        valid_indices = ~np.isnan(y)
        if np.sum(valid_indices) < 2:
            return "insufficient_data"
        
        x_clean = x[valid_indices]
        y_clean = y[valid_indices]
        
        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = linregress(x_clean, y_clean)
        
        # Determine trend based on slope and statistical significance
        if p_value > 0.05:  # Not statistically significant
            return "stable"
        elif slope > 0.1:  # Positive slope with meaningful magnitude
            return "increasing"
        elif slope < -0.1:  # Negative slope with meaningful magnitude
            return "decreasing"
        else:
            return "stable"
            
    except (ValueError, TypeError, RuntimeError):
        return "stable"


def calculate_correlation(x: List[float], y: List[float]) -> float:
    """
    Calculate Pearson correlation coefficient between two variables
    
    Args:
        x: First variable data
        y: Second variable data
        
    Returns:
        Correlation coefficient (-1 to 1)
    """
    if len(x) != len(y) or len(x) < 3:
        return 0.0
    
    try:
        x_array = np.array(x)
        y_array = np.array(y)
        
        # Remove NaN values
        valid_indices = ~(np.isnan(x_array) | np.isnan(y_array))
        if np.sum(valid_indices) < 3:
            return 0.0
        
        x_clean = x_array[valid_indices]
        y_clean = y_array[valid_indices]
        
        # Calculate correlation
        correlation, _ = stats.pearsonr(x_clean, y_clean)
        
        # Return NaN as 0.0 for consistency
        return float(correlation) if not np.isnan(correlation) else 0.0
        
    except (ValueError, TypeError, RuntimeError):
        return 0.0


def detect_anomalies(data: List[float], threshold: float = 2.0) -> List[bool]:
    """
    Detect anomalies using z-score method
    
    Args:
        data: List of numeric values
        threshold: Z-score threshold for anomaly detection
        
    Returns:
        List of boolean values indicating anomalies
    """
    if len(data) < 3:
        return [False] * len(data)
    
    try:
        data_array = np.array(data)
        valid_indices = ~np.isnan(data_array)
        
        if np.sum(valid_indices) < 3:
            return [False] * len(data)
        
        clean_data = data_array[valid_indices]
        
        # Calculate z-scores
        z_scores = np.abs(stats.zscore(clean_data))
        
        # Detect anomalies
        anomalies = z_scores > threshold
        
        # Map back to original indices
        result = [False] * len(data)
        anomaly_indices = np.where(valid_indices)[0][anomalies]
        
        for idx in anomaly_indices:
            result[idx] = True
        
        return result
        
    except (ValueError, TypeError, RuntimeError):
        return [False] * len(data)


def calculate_moving_average(data: List[float], window: int = 7) -> List[Optional[float]]:
    """
    Calculate moving average for trend smoothing
    
    Args:
        data: List of numeric values
        window: Window size for moving average
        
    Returns:
        List of moving average values (None for insufficient data points)
    """
    if len(data) < window:
        return [None] * len(data)
    
    try:
        data_array = np.array(data)
        moving_avg = []
        
        for i in range(len(data)):
            if i < window - 1:
                moving_avg.append(None)
            else:
                window_data = data_array[i - window + 1:i + 1]
                valid_data = window_data[~np.isnan(window_data)]
                
                if len(valid_data) >= window // 2:
                    moving_avg.append(float(np.mean(valid_data)))
                else:
                    moving_avg.append(None)
        
        return moving_avg
        
    except (ValueError, TypeError, RuntimeError):
        return [None] * len(data)


def calculate_statistics_summary(data: List[float]) -> dict:
    """
    Calculate comprehensive statistics summary
    
    Args:
        data: List of numeric values
        
    Returns:
        Dictionary with statistical measures
    """
    if not data:
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "q25": 0.0,
            "q75": 0.0
        }
    
    try:
        data_array = np.array(data)
        valid_data = data_array[~np.isnan(data_array)]
        
        if len(valid_data) == 0:
            return {
                "count": 0,
                "mean": 0.0,
                "median": 0.0,
                "std": 0.0,
                "min": 0.0,
                "max": 0.0,
                "q25": 0.0,
                "q75": 0.0
            }
        
        return {
            "count": len(valid_data),
            "mean": float(np.mean(valid_data)),
            "median": float(np.median(valid_data)),
            "std": float(np.std(valid_data)),
            "min": float(np.min(valid_data)),
            "max": float(np.max(valid_data)),
            "q25": float(np.percentile(valid_data, 25)),
            "q75": float(np.percentile(valid_data, 75))
        }
        
    except (ValueError, TypeError, RuntimeError):
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "q25": 0.0,
            "q75": 0.0
        }
