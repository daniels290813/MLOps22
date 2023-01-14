from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
import xgboost as xgb
import pandas as pd
import sklearn
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, accuracy_score
import numpy as np
import dalex as dx
from dalex.fairness import resample, reweight, roc_pivot
from copy import copy
import warnings
warnings.filterwarnings('ignore')
import mlrun
import json

class dalex_fairness:
    def __init__(self, target, df_train, df_test, target_type='regression'):
        df_train = df_train.reset_index(drop=True)
        df_test = df_test.reset_index(drop=True)
        print(f'dataframe shape before dalex : {df_train.shape}')
        
        self.X_train = df_train.drop(target,axis=1)
        self.X_test = df_test.drop(target,axis=1)
        self.y_train = df_train[target]
        self.y_test = df_test[target]
        self.df = df_train.append(df_test)        
        self.target, self.target_type = target, target_type
        self.categorical_cols, self.column_names, self.results = None, None, None
        self.baseline_pipeline, self.baseline_score, self.base_preprocessor = None, None, None
        self.exp, self.feature_weights = None, {}
        self.split_dataset()
        self.get_baseline_pipeline()
        self.fairness_checker()
        self.get_upgraded_data()
        self.results.round(2)

    def split_dataset(self):
        self.numerical_cols = [cname for cname in self.X_train.columns if self.X_train[cname].dtype in ['int64', 'float64']]
        self.categorical_cols = [cname for cname in self.X_train.columns if self.X_train[cname].dtype == "object"]        

    def get_baseline_pipeline(self):
        numerical_transformer = SimpleImputer(strategy='constant')
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])

        self.base_preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, self.numerical_cols),
                ('cat', categorical_transformer, self.categorical_cols)
            ])
        self.baseline_pipeline = self.get_pipeline_by_target_type()

        self.baseline_pipeline.fit(self.X_train, self.y_train)
        self.baseline_score = self.get_model_metrics_accuracy()

        self.exp = dx.Explainer(self.baseline_pipeline, self.X_train, self.y_train)

    def get_pipeline_by_target_type(self):
      """
        this function checks whether the model is a regression or classification
        task, and defines its pipeline as is
      """
      if self.target_type == 'regression':
        return Pipeline(steps=[('preprocessor', self.base_preprocessor),
                               ('model', xgb.XGBRegressor(objective='reg:squarederror', n_jobs=-1))])
      else:
        ''' self.target_type == 'classification' '''
        return Pipeline(steps=[('preprocessor', self.base_preprocessor),
                               ('model', xgb.XGBRFClassifier(n_jobs=-1))])
    
    def custom_reweight(self, protected, y):
      weights = np.repeat(None, len(y))

      for subgroup in np.unique(protected):
          for c in np.unique(y):

              Xs = np.sum(protected == subgroup)
              Xc = np.sum(y == c)
              Xsc = np.sum((protected == subgroup) & (c == y))
              Wsc = (Xs / len(y)) * (Xc / Xsc)
              weights[(protected == subgroup) & (y == c)] = Wsc

      return weights

    def resample_custom(self, protected, y_train):
      weights = reweight(protected, y_train, verbose=False)
      expected_size =  dict.fromkeys(np.unique(protected))
      for key in expected_size.keys():
          expected_size[key] = dict.fromkeys(np.unique(y_train))

      for subgroup in expected_size.keys():
          for value in np.unique(y_train):
              case_weights = weights[(subgroup == protected) & (value == y_train)]
              if len(case_weights > 0):
                case_size = len(case_weights)
                weight = case_weights[0]
                expected_size[subgroup][value] = round(case_size * weight)

      indices = []

      for subgroup in expected_size.keys():
          for value in np.unique(y_train):
              if np.count_nonzero((protected == subgroup) & (y_train == value)) > 0:
                current_case = y_train[(protected == subgroup) & (y_train == value)].index
                expected = expected_size[subgroup][value]
                actual = np.sum((protected == subgroup) & (y_train == value))
                if expected == actual:
                    indices += list(current_case)

                elif expected < actual:
                    if type == 'uniform':
                        indices += list(np.random.choice(current_case, expected, replace=False))

                else:
                    if type == 'uniform':
                        u_ind = list(np.repeat(current_case, expected // actual))
                        u_ind += list(np.random.choice(current_case, expected % actual))

                        indices += u_ind

      return np.array(indices)

    def fairness_checker(self):
        """
          this function is used to calculate the new model's perfoormance based on
          resampling/reweighting method. it will iterate over the numerica columns,
          calc the median for each and wil use resample and reweight method for each.
        """
        self.results = pd.DataFrame(
            columns=['Baseline Score', 'Reweight_score', 'Reweight Delta %', 'Resample_score', 'Resample Delta %', 'Improved'])
        
        for tester_col in self.X_train.columns:
            if tester_col in self.categorical_cols or 'ID' in tester_col:
                continue
            
            copied_X_train, copied_y_train = self.X_train.copy(), self.y_train.copy()
            if len(np.unique(self.df[tester_col])) == 2:
                ''' cases of 0/1 values of categorial features '''
                col_median = 0.5
            else:
                col_median = copied_X_train[tester_col].median()

            copied_X_train['bias_check'] = np.where(copied_X_train[tester_col] > col_median, 'majority', 'minority')
            privileged, protected = 'minority', copied_X_train.bias_check

            resample_score = None
            resampled_delta_pct = None

            reweight_score = None
            reweight_delta_pct = None
            
            resample_score = np.inf
            resampled_delta_pct = -np.inf

            reweight_score = np.inf
            reweight_delta_pct = -np.inf

            resampled_indices = self.resample_custom(protected, self.y_train)
            if len(resampled_indices) >= 0.7 * len(self.X_train):
              ''' taking resample iff the resampled data is over 70% of the data '''
              clf_resmaple = self.get_pipeline_by_target_type()
              clf_resmaple.fit(copied_X_train.loc[resampled_indices, :], copied_y_train[resampled_indices])
              resample_score = self.get_model_metrics_accuracy(pipeline=clf_resmaple)
              resampled_delta_pct = self.calc_pct_improvement(resample_score)
              self.feature_weights[tester_col] = {'resample': resampled_indices}

            weights = self.custom_reweight(protected, self.y_train)
            clf_weighted = self.get_pipeline_by_target_type()

            kwargs = {clf_weighted.steps[-1][0] + '__sample_weight': weights}
            if tester_col not in self.feature_weights:
              self.feature_weights[tester_col] = {'reweight': kwargs}
            else:
              self.feature_weights[tester_col]['reweight'] = kwargs

            clf_weighted.fit(self.X_train, self.y_train, **kwargs)

            reweight_score = self.get_model_metrics_accuracy(pipeline=clf_weighted)
            reweight_delta_pct = self.calc_pct_improvement(reweight_score)

            improved = self.improve_status(reweight_delta_pct, resampled_delta_pct)
            #reweight_score = round(reweight_score, 2) if reweight_score is not None else None
            #resample_score = round(resample_score, 2) if resample_score is not None else None  
            self.results.loc[tester_col] = [round(self.baseline_score, 2),
                                            reweight_score,
                                            reweight_delta_pct,
                                            resample_score,
                                            resampled_delta_pct, improved]

    def improve_status(self, reweight_delta_pct, resampled_delta_pct):
      if reweight_delta_pct is None:
        if resampled_delta_pct is None or resampled_delta_pct <= 0:
          return 'No'
        else:
          return 'Yes'

      elif reweight_delta_pct > 0:
        return 'Yes'
      else:
        if resampled_delta_pct is None or resampled_delta_pct <= 0:
          return 'No'
        else:
          return 'Yes'

    def calc_pct_improvement(self, new_score):
        if self.target_type == 'regression':
          return round(((self.baseline_score - new_score) / self.baseline_score * 100), 1)
        else:
          ''' self.target_type == 'classification' '''
          return round(new_score - self.baseline_score, 1)

    def get_model_metrics_accuracy(self, pipeline=None):
      if pipeline is None:
        if self.target_type == 'regression':
          return mean_absolute_error(self.baseline_pipeline.predict(self.X_test), self.y_test)

        else:
          ''' self.target_type = classification '''
          return accuracy_score(self.baseline_pipeline.predict(self.X_test), self.y_test)
      
      else:
        if self.target_type == 'regression':
          return mean_absolute_error(pipeline.predict(self.X_test), self.y_test)

        else:
          ''' self.target_type = classification '''
          return accuracy_score(pipeline.predict(self.X_test), self.y_test)

    def get_upgraded_data(self):
        """
          this function is used to to get the most influenced feature's weights,
          for later use pipeline.
        """
        self.improved_results = self.results[self.results['Improved'] == 'Yes']
        if len(self.improved_results) == 0:
          self.best_approach = None
        print(self.improved_results,'@@@@@@')
        best_reweight = np.nanmax(self.improved_results['Reweight Delta %'])
        best_resample = np.nanmax(self.improved_results['Resample Delta %'])
        if best_reweight > best_resample:
          best_feature = self.improved_results['Reweight Delta %'].idxmax()
          print('best feature : ',best_feature)
          self.best_approach = {f'reweight': self.feature_weights[best_feature]['reweight']}
        else:
          best_feature = self.improved_results['Resample Delta %'].idxmax()
          print('best feature : ',best_feature)
          self.best_approach = {f'resample': self.feature_weights[best_feature]['resample']}

            
def run_dalex(context: mlrun.MLClientCtx,
              df_train,
              df_test = None,
              target:str = 'MEDV',
              target_type='regression'): 
    
    log_new_data=False
    if type(df_train) == str:
        df_train = mlrun.get_dataitem(df_train)
    df_train = df_train.as_df()
    
    if df_test == None:
        log_new_data=True
        X_train_full, X_valid_full, y_train, y_valid = train_test_split(df_train.drop(target, axis=1), df_train[target], train_size=0.8, test_size=0.2, random_state=10)
        X_train_full[target] = y_train
        X_valid_full[target] = y_valid
        df_train = X_train_full
        df_test = X_valid_full
    else:
        if type(df_test)==str:
            df_test = mlrun.get_dataitem(df_test)
        df_test = df_test.as_df()
    
    house_model = dalex_fairness(target=target, df_train=df_train, df_test=df_test, target_type=target_type)     
    best_approach = house_model.best_approach
    
#     dalex_output = {}
    kwargs = list(best_approach.values())[0]
    for key,val in kwargs.items():
        kwargs[key] = val.tolist()
        
        
    if list(best_approach.keys())[0] == 'reweight':
        context.logger.info('dalex selects reweighting')
        context.log_artifact('dalex_output', body=json.dumps(kwargs))
        context.log_dataset('train_data', df_train) 
        context.log_dataset('test_data', df_test)  
    else:
        context.logger.info('dalex selects resampling')
        context.log_dataset('train_data', df_train.reset_index(drop=True).iloc[list(kwargs.values())[0]]) 
        context.log_dataset('test_data', df_test.reset_index(drop=True)) 