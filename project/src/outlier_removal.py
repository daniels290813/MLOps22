import pandas as pd
import os
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from scipy.stats import norm
from scipy.stats import multivariate_normal as mn
import re 
import typing
import mlrun

from pyod.models.lof import LOF
from pyod.models.abod import ABOD
from collections import defaultdict

def remove_outliers_iqr(df: pd.DataFrame, args: dict) -> list:
    """
    Detect outliers from the given data using IQR calculation
    :param df: pandas DataFrame with data (shape: (n_samples, n_features))
    :param args: dict with the following arguments:
    :param low_quantile: Integer 
    :param high_quantile: Integer 
    :param max_removal_percent_per_column: Integer 
    """
    low_quantile = args['low_quantile']
    high_quantile = args['high_quantile']
    max_removal_percent_per_column = args['max_removal_percent_per_column']
    
    idx_to_remove = list()
    for col in df.columns:

        if df[col].dtype != object:
            col = str(col)
            q_low = df[col].quantile(low_quantile)
            q_hi  = df[col].quantile(high_quantile)
            old_df_len = len(df)
            good = (df[col] < q_hi) & (df[col] > q_low)
            cleaned_df = df[good]
            
            if len(cleaned_df) > 0 and len(cleaned_df)/old_df_len>max_removal_percent_per_column:
                idx_to_remove.extend(df[~good].index)
                
    return idx_to_remove



def z_score(df: pd.DataFrame, threshold: int) -> pd.DataFrame:
    """
    Calculate Z-score for each sample and return the good samples
    :param df: pandas DataFrame with data (shape: (n_samples, n_features))
    :param threshold: Integer 
    """
    mean, std = np.mean(df), np.std(df)
    z_score = np.abs((df - mean) / std)
    good = z_score < threshold

    return good

def remove_outliers_z_score(df: pd.DataFrame, args: dict) -> list:
    """
    Remove outliers from the given data using Z-score calculation
    :param df: pandas DataFrame with data (shape: (n_samples, n_features))
    :param args: dict with the following arguments:
    :param threshold: Integer 
    """
    threshold = args['threshold']
    idx_to_remove = list()
    idx_to_remove_per_col = dict()
    for column in df.columns:
        try:
            good = z_score(df[column], threshold=threshold)
            idx_to_remove.extend(df[~good].index)
        except Exception as e:
            pass
    return idx_to_remove

def remove_outliers_LOF(X: pd.DataFrame, args: dict) -> list:
    """
    Remove outliers from the given data using the LOF algorithm from pyOD.
    :param X: pandas DataFrame with data (shape: (n_samples, n_features))
    :param args: dict with the following arguments:
        :param contamination: proportion of outliers in the data
    """
    contamination = args['contamination']
    # Create LOF detector object
    detector = LOF(contamination=contamination)
    # Fit the detector to the data
    detector.fit(X)
    # Get the outlier labels (0: inliers, 1: outliers)
    labels = detector.labels_
    
    # Return only the inliers (i.e. remove the outliers)
    return list(X[labels == 1].index)

def remove_outliers_ABOD(X: pd.DataFrame, args: dict) -> list:
    """
    Remove outliers from the given data using the LOF algorithm from pyOD.
    :param X: pandas DataFrame with data (shape: (n_samples, n_features))
    :param args: dict with the following arguments:
        :param contamination: proportion of outliers in the data
    """

    contamination = args['contamination']
    # Create LOF detector object
    detector = ABOD(contamination=contamination)
    # Fit the detector to the data
    detector.fit(X)
    # Get the outlier labels (0: inliers, 1: outliers)
    labels = detector.labels_
    
    # Return only the inliers (i.e. remove the outliers)
    return list(X[labels == 1].index)

def remove_outliers_HBOS(X: pd.DataFrame, args: dict) -> list:
    """
    Remove outliers from the given data using the LOF algorithm from pyOD.
    :param X: pandas DataFrame with data (shape: (n_samples, n_features))
    :param args: dict with the following arguments:
    :param contamination: proportion of outliers in the data
    """
    from pyod.models.hbos import HBOS
    contamination = args['contamination']
    # Create LOF detector object
    detector = HBOS(contamination=contamination)
    # Fit the detector to the data
    detector.fit(X)
    # Get the outlier labels (0: inliers, 1: outliers)
    labels = detector.labels_
    
    # Return only the inliers (i.e. remove the outliers)
    return list(X[labels == 1].index)


class OutliersDetector:

    def __init__(self, X, y, numerical_cols, outliers_detectors):
        
        self._X = X
        self._y = y 
        self._numerical_cols = numerical_cols
        self._outliers_detectors = outliers_detectors
        self._items_to_remove_per_strategy = dict() # dict
        self.detect_outliers()
        
    def detect_outliers(self):
        
        for outlier_detector_func, outlier_detector_args in self._outliers_detectors:
            func_name = outlier_detector_func.__name__
            self.items_to_remove_per_strategy[func_name] = outlier_detector_func(self._X[self._numerical_cols], outlier_detector_args)
    
    def remove_outliers_using_intersection(self, funcs_list):
        idx_to_remove = list()
        for i, func_name in enumerate(funcs_list):
            if i > 0:
                idx_to_remove = list(set(idx_to_remove) & set(self.items_to_remove_per_strategy[func_name]))
            else:
                idx_to_remove = self.items_to_remove_per_strategy[func_name]
        
        clean_X = self._X.drop(index=idx_to_remove)
        clean_y = self._y.drop(index=idx_to_remove)
        
        return clean_X, clean_y
    
    def remove_outliers_using_votes(self, funcs_list, votes_thresholds=2):
        idx_to_remove = defaultdict(int)
        idx_f = list()
        for i, func_name in enumerate(funcs_list):
            for idx in self.items_to_remove_per_strategy[func_name]:
                idx_to_remove[idx] += 1
                if idx_to_remove[idx] > votes_thresholds:
                    idx_f.append(idx)
        
        print('Removed:', len(idx_f))
        clean_X = self._X.drop(index=idx_f)
        clean_y = self._y.drop(index=idx_f)
        
        return clean_X, clean_y
    
    @property
    def items_to_remove_per_strategy(self):
        return self._items_to_remove_per_strategy
    
    
def run(context: mlrun.MLClientCtx, dataitem,random_state, remove_outliers_functions, remove_outlier, votes_thresholds, label_column):
    X = dataitem.as_df()
    
    y = X[label_column]
    X = X.drop(label_column,axis=1)
        
    X_train_full, X_valid_full, y_train, y_valid = train_test_split(X, y, train_size=0.8, test_size=0.2, random_state=random_state)
    
    before_drop = X_train_full.shape[0]
    
    numerical_cols = [cname for cname in X.columns if X[cname].dtype in ['int64', 'float64']]
    
    if remove_outlier:
        outlier_detector = OutliersDetector(X_train_full, y_train, numerical_cols, remove_outliers_functions)
        remove_outliers_functions_choices = [func.__name__ for func, _ in remove_outliers_functions]
        X_train_full, y_train = outlier_detector.remove_outliers_using_votes(funcs_list=remove_outliers_functions_choices, votes_thresholds=votes_thresholds)
        
    X_train_full[label_column] = y_train
    
    X_valid_full[label_column] = y_valid
    
    context.logger.info(f'Outlier removal function removed successfully {before_drop - X_train_full.shape[0]}')
    context.log_dataset(key='outlier_removal', df = X_train_full)
    context.log_dataset(key='outlier_removal_test', df = X_valid_full)