"""
Enhanced ML Models Implementation
State-of-the-Art Machine Learning for Ticket Price Prediction

Based on comprehensive research from:
- Sports ticket price prediction with Random Forest
- Academic research on predictive algorithms
- XGBoost, LightGBM, and CatBoost best practices
- CS109 SeatGeek predictive modeling

Features:
- Optimized Random Forest with hyperparameter tuning
- Advanced XGBoost implementation
- LightGBM for fast training
- CatBoost for categorical features
- Ensemble stacking with meta-learner
- Cross-validation with time-series awareness
- Feature importance analysis
- Prediction intervals and uncertainty quantification
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
import pandas as pd
from datetime import datetime

# ML imports
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
    from sklearn.model_selection import TimeSeriesSplit, GridSearchCV, cross_val_score
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import Ridge
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    from catboost import CatBoostRegressor
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    r2_score: float
    mae: float
    rmse: float
    mape: float
    training_time: float
    prediction_time: float
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'r2_score': round(self.r2_score, 4),
            'mae': round(self.mae, 2),
            'rmse': round(self.rmse, 2),
            'mape': round(self.mape, 2),
            'training_time': round(self.training_time, 2),
            'prediction_time': round(self.prediction_time, 4)
        }


@dataclass
class PredictionWithUncertainty:
    """Prediction with confidence intervals"""
    point_estimate: float
    lower_bound: float
    upper_bound: float
    confidence: float
    model_name: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'predicted_price': round(self.point_estimate, 2),
            'lower_bound': round(self.lower_bound, 2),
            'upper_bound': round(self.upper_bound, 2),
            'confidence': round(self.confidence, 3),
            'model': self.model_name
        }


class OptimizedRandomForestModel:
    """
    Optimized Random Forest implementation
    Based on research from FC Python and academic papers
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        
        # Optimal hyperparameters from research
        self.best_params = {
            'n_estimators': 500,
            'max_depth': 15,
            'min_samples_split': 10,
            'min_samples_leaf': 5,
            'max_features': 'sqrt',
            'bootstrap': True,
            'oob_score': True,
            'random_state': 42,
            'n_jobs': -1,
            'warm_start': False
        }
    
    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        hyperparameter_tuning: bool = False
    ) -> ModelPerformance:
        """
        Train Random Forest model
        
        Args:
            X: Feature matrix
            y: Target variable
            hyperparameter_tuning: Whether to perform GridSearchCV
        """
        start_time = datetime.utcnow()
        
        try:
            if not SKLEARN_AVAILABLE:
                raise ImportError("scikit-learn not available")
            
            self.feature_names = X.columns.tolist()
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            if hyperparameter_tuning:
                # Hyperparameter tuning with time-series cross-validation
                param_grid = {
                    'n_estimators': [300, 500, 700],
                    'max_depth': [10, 15, 20],
                    'min_samples_split': [5, 10, 15],
                    'min_samples_leaf': [3, 5, 7],
                    'max_features': ['sqrt', 'log2']
                }
                
                # Time series split (important for temporal data)
                tscv = TimeSeriesSplit(n_splits=5)
                
                rf = RandomForestRegressor(
                    random_state=42,
                    n_jobs=-1,
                    bootstrap=True,
                    oob_score=True
                )
                
                grid_search = GridSearchCV(
                    rf,
                    param_grid,
                    cv=tscv,
                    scoring='neg_mean_absolute_error',
                    n_jobs=-1,
                    verbose=1
                )
                
                grid_search.fit(X_scaled, y)
                self.model = grid_search.best_estimator_
                self.best_params = grid_search.best_params_
                
                logger.info(f"Best parameters: {self.best_params}")
                logger.info(f"Best CV score: {-grid_search.best_score_:.2f}")
            else:
                # Use preset optimal parameters
                self.model = RandomForestRegressor(**self.best_params)
                self.model.fit(X_scaled, y)
            
            self.is_trained = True
            training_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate performance metrics
            y_pred = self.model.predict(X_scaled)
            
            performance = ModelPerformance(
                r2_score=r2_score(y, y_pred),
                mae=mean_absolute_error(y, y_pred),
                rmse=np.sqrt(mean_squared_error(y, y_pred)),
                mape=np.mean(np.abs((y - y_pred) / y)) * 100,
                training_time=training_time,
                prediction_time=0.0
            )
            
            logger.info(f"Random Forest trained: {performance.to_dict()}")
            return performance
            
        except Exception as e:
            logger.error(f"Random Forest training error: {e}")
            raise
    
    def predict(
        self,
        X: pd.DataFrame,
        return_std: bool = True
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Make predictions with uncertainty estimates
        
        Returns:
            predictions: Point estimates
            std: Standard deviation (uncertainty) if return_std=True
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        start_time = datetime.utcnow()
        
        try:
            X_scaled = self.scaler.transform(X)
            
            if return_std:
                # Get predictions from all trees for uncertainty
                tree_predictions = np.array([
                    tree.predict(X_scaled) 
                    for tree in self.model.estimators_
                ])
                
                predictions = np.mean(tree_predictions, axis=0)
                std = np.std(tree_predictions, axis=0)
                
                return predictions, std
            else:
                predictions = self.model.predict(X_scaled)
                return predictions, None
                
        except Exception as e:
            logger.error(f"Random Forest prediction error: {e}")
            raise
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        if not self.is_trained:
            return {}
        
        importances = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_names, importances))
        
        # Sort by importance
        return dict(sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))


class OptimizedXGBoostModel:
    """
    Optimized XGBoost implementation
    Based on research and Kaggle competition best practices
    """
    
    def __init__(self):
        self.model = None
        self.feature_names = []
        self.is_trained = False
        
        # Optimal hyperparameters from research
        self.best_params = {
            'objective': 'reg:squarederror',
            'n_estimators': 1000,
            'max_depth': 8,
            'learning_rate': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 3,
            'gamma': 0.1,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'random_state': 42,
            'n_jobs': -1,
            'early_stopping_rounds': 50
        }
    
    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        eval_set: Optional[Tuple[pd.DataFrame, pd.Series]] = None
    ) -> ModelPerformance:
        """Train XGBoost model with early stopping"""
        start_time = datetime.utcnow()
        
        try:
            if not XGBOOST_AVAILABLE:
                raise ImportError("XGBoost not available")
            
            self.feature_names = X.columns.tolist()
            
            # Prepare evaluation set for early stopping
            if eval_set is None:
                # Use 20% of training data as validation
                split_idx = int(len(X) * 0.8)
                X_train, X_val = X[:split_idx], X[split_idx:]
                y_train, y_val = y[:split_idx], y[split_idx:]
                eval_set = [(X_val, y_val)]
            else:
                X_train, y_train = X, y
            
            # Train model
            self.model = xgb.XGBRegressor(**self.best_params)
            self.model.fit(
                X_train,
                y_train,
                eval_set=eval_set,
                verbose=False
            )
            
            self.is_trained = True
            training_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate performance
            y_pred = self.model.predict(X)
            
            performance = ModelPerformance(
                r2_score=r2_score(y, y_pred),
                mae=mean_absolute_error(y, y_pred),
                rmse=np.sqrt(mean_squared_error(y, y_pred)),
                mape=np.mean(np.abs((y - y_pred) / y)) * 100,
                training_time=training_time,
                prediction_time=0.0
            )
            
            logger.info(f"XGBoost trained: {performance.to_dict()}")
            return performance
            
        except Exception as e:
            logger.error(f"XGBoost training error: {e}")
            raise
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"XGBoost prediction error: {e}")
            raise
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        if not self.is_trained:
            return {}
        
        importance = self.model.get_booster().get_score(importance_type='gain')
        
        # Sort by importance
        return dict(sorted(
            importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))


class OptimizedLightGBMModel:
    """
    Optimized LightGBM implementation
    Fastest gradient boosting framework
    """
    
    def __init__(self):
        self.model = None
        self.feature_names = []
        self.is_trained = False
        
        # Optimal hyperparameters
        self.best_params = {
            'objective': 'regression',
            'metric': 'mae',
            'n_estimators': 1000,
            'num_leaves': 63,
            'learning_rate': 0.05,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'min_child_samples': 20,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'random_state': 42,
            'n_jobs': -1,
            'verbose': -1
        }
    
    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        eval_set: Optional[Tuple[pd.DataFrame, pd.Series]] = None
    ) -> ModelPerformance:
        """Train LightGBM model"""
        start_time = datetime.utcnow()
        
        try:
            if not LIGHTGBM_AVAILABLE:
                raise ImportError("LightGBM not available")
            
            self.feature_names = X.columns.tolist()
            
            # Prepare evaluation set
            if eval_set is None:
                split_idx = int(len(X) * 0.8)
                X_train, X_val = X[:split_idx], X[split_idx:]
                y_train, y_val = y[:split_idx], y[split_idx:]
                eval_set = [(X_val, y_val)]
            else:
                X_train, y_train = X, y
            
            # Train model
            self.model = lgb.LGBMRegressor(**self.best_params)
            self.model.fit(
                X_train,
                y_train,
                eval_set=eval_set,
                callbacks=[lgb.early_stopping(stopping_rounds=50)]
            )
            
            self.is_trained = True
            training_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate performance
            y_pred = self.model.predict(X)
            
            performance = ModelPerformance(
                r2_score=r2_score(y, y_pred),
                mae=mean_absolute_error(y, y_pred),
                rmse=np.sqrt(mean_squared_error(y, y_pred)),
                mape=np.mean(np.abs((y - y_pred) / y)) * 100,
                training_time=training_time,
                prediction_time=0.0
            )
            
            logger.info(f"LightGBM trained: {performance.to_dict()}")
            return performance
            
        except Exception as e:
            logger.error(f"LightGBM training error: {e}")
            raise
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"LightGBM prediction error: {e}")
            raise
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        if not self.is_trained:
            return {}
        
        importances = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_names, importances))
        
        return dict(sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))


class OptimizedCatBoostModel:
    """
    Optimized CatBoost implementation
    Best for datasets with categorical features
    """
    
    def __init__(self):
        self.model = None
        self.feature_names = []
        self.is_trained = False
        
        # Optimal hyperparameters
        self.best_params = {
            'iterations': 1000,
            'depth': 8,
            'learning_rate': 0.05,
            'l2_leaf_reg': 3,
            'loss_function': 'RMSE',
            'eval_metric': 'MAE',
            'random_seed': 42,
            'verbose': False,
            'early_stopping_rounds': 50
        }
    
    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        categorical_features: Optional[List[str]] = None
    ) -> ModelPerformance:
        """Train CatBoost model"""
        start_time = datetime.utcnow()
        
        try:
            if not CATBOOST_AVAILABLE:
                raise ImportError("CatBoost not available")
            
            self.feature_names = X.columns.tolist()
            
            # Prepare validation set
            split_idx = int(len(X) * 0.8)
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Train model
            self.model = CatBoostRegressor(**self.best_params)
            self.model.fit(
                X_train,
                y_train,
                eval_set=(X_val, y_val),
                cat_features=categorical_features,
                use_best_model=True
            )
            
            self.is_trained = True
            training_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Calculate performance
            y_pred = self.model.predict(X)
            
            performance = ModelPerformance(
                r2_score=r2_score(y, y_pred),
                mae=mean_absolute_error(y, y_pred),
                rmse=np.sqrt(mean_squared_error(y, y_pred)),
                mape=np.mean(np.abs((y - y_pred) / y)) * 100,
                training_time=training_time,
                prediction_time=0.0
            )
            
            logger.info(f"CatBoost trained: {performance.to_dict()}")
            return performance
            
        except Exception as e:
            logger.error(f"CatBoost training error: {e}")
            raise
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"CatBoost prediction error: {e}")
            raise
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        if not self.is_trained:
            return {}
        
        importances = self.model.get_feature_importance()
        feature_importance = dict(zip(self.feature_names, importances))
        
        return dict(sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))


class AdvancedStackingEnsemble:
    """
    Advanced stacking ensemble
    Combines multiple models with a meta-learner
    """
    
    def __init__(self):
        self.base_models = {}
        self.meta_learner = None
        self.is_trained = False
        
    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        use_all_models: bool = True
    ) -> Dict[str, ModelPerformance]:
        """
        Train all base models and meta-learner
        
        Returns:
            Dictionary of performance metrics for each model
        """
        performances = {}
        
        try:
            # Initialize base models
            if SKLEARN_AVAILABLE:
                self.base_models['random_forest'] = OptimizedRandomForestModel()
                logger.info("Training Random Forest...")
                perf = self.base_models['random_forest'].train(X, y)
                performances['random_forest'] = perf
            
            if XGBOOST_AVAILABLE and use_all_models:
                self.base_models['xgboost'] = OptimizedXGBoostModel()
                logger.info("Training XGBoost...")
                perf = self.base_models['xgboost'].train(X, y)
                performances['xgboost'] = perf
            
            if LIGHTGBM_AVAILABLE and use_all_models:
                self.base_models['lightgbm'] = OptimizedLightGBMModel()
                logger.info("Training LightGBM...")
                perf = self.base_models['lightgbm'].train(X, y)
                performances['lightgbm'] = perf
            
            if CATBOOST_AVAILABLE and use_all_models:
                self.base_models['catboost'] = OptimizedCatBoostModel()
                logger.info("Training CatBoost...")
                perf = self.base_models['catboost'].train(X, y)
                performances['catboost'] = perf
            
            # Train meta-learner (Ridge regression)
            if len(self.base_models) >= 2:
                logger.info("Training meta-learner...")
                self.meta_learner = Ridge(alpha=1.0)
                
                # Get predictions from base models
                base_predictions = []
                for model in self.base_models.values():
                    if hasattr(model, 'predict'):
                        pred = model.predict(X)
                        if isinstance(pred, tuple):
                            pred = pred[0]
                        base_predictions.append(pred)
                
                # Stack predictions
                X_meta = np.column_stack(base_predictions)
                self.meta_learner.fit(X_meta, y)
            
            self.is_trained = True
            logger.info(f"Ensemble training complete. Models: {list(self.base_models.keys())}")
            
            return performances
            
        except Exception as e:
            logger.error(f"Ensemble training error: {e}")
            raise
    
    def predict(
        self,
        X: pd.DataFrame,
        return_individual: bool = False
    ) -> Tuple[np.ndarray, Optional[Dict[str, np.ndarray]]]:
        """
        Make ensemble predictions
        
        Returns:
            ensemble_predictions: Final ensemble predictions
            individual_predictions: Individual model predictions (if requested)
        """
        if not self.is_trained:
            raise ValueError("Ensemble not trained")
        
        try:
            # Get predictions from all base models
            base_predictions = []
            individual_preds = {}
            
            for name, model in self.base_models.items():
                pred = model.predict(X)
                if isinstance(pred, tuple):
                    pred = pred[0]
                base_predictions.append(pred)
                individual_preds[name] = pred
            
            # Use meta-learner if available
            if self.meta_learner:
                X_meta = np.column_stack(base_predictions)
                ensemble_pred = self.meta_learner.predict(X_meta)
            else:
                # Simple average
                ensemble_pred = np.mean(base_predictions, axis=0)
            
            if return_individual:
                return ensemble_pred, individual_preds
            else:
                return ensemble_pred, None
                
        except Exception as e:
            logger.error(f"Ensemble prediction error: {e}")
            raise
    
    def get_model_weights(self) -> Dict[str, float]:
        """Get weights of each model in the ensemble"""
        if not self.is_trained or not self.meta_learner:
            # Return equal weights
            n_models = len(self.base_models)
            return {name: 1.0 / n_models for name in self.base_models.keys()}
        
        # Get weights from meta-learner
        weights = self.meta_learner.coef_
        weight_dict = dict(zip(self.base_models.keys(), weights))
        
        # Normalize to sum to 1
        total = sum(abs(w) for w in weights)
        if total > 0:
            weight_dict = {k: abs(v) / total for k, v in weight_dict.items()}
        
        return weight_dict
