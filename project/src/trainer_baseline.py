import mlrun
from kfp import dsl
import sklearn
from src.outlier_removal import *

@dsl.pipeline(
    name="Automatic Pipeline",
    description="Train & Evaluate"
)
def kfpipeline(dataset: str='housing',
               path: str='/home/jovyan/data/src/housing.csv',
               label_column:str='MEDV',
               remove_outlier:bool= False):
    
    project = mlrun.get_current_project()
        
    get_data_run = mlrun.run_function(name='get_data',
                                      function='gen-dataset',
                                      params={'dataset': dataset,
                                              'path': path},
                                      outputs=[dataset])

    # Setting outlier removal params
    votes_thresholds = 3
    pyod_contamination=0.2 # + (0,0.5)
    z_score_threshold=3
    iqr_low=0.01
    iqr_high=0.99
    iqr_max_removal_percent_per_column=0.95
    remove_outliers_functions = [(remove_outliers_z_score, {'threshold': z_score_threshold}),
                        (remove_outliers_iqr, {'low_quantile': iqr_low, 'high_quantile':iqr_high, 'max_removal_percent_per_column':iqr_max_removal_percent_per_column}),
                        (remove_outliers_LOF, {'contamination': pyod_contamination}),
                        (remove_outliers_ABOD, {'contamination': pyod_contamination}),
                           (remove_outliers_HBOS, {'contamination': pyod_contamination})
                            ]
    
    outlier_removal_run = mlrun.run_function(name='outlier_removal',
                                            function='outlier-removal',
                                            inputs={'dataitem': get_data_run.outputs[dataset]},
                                            params={'remove_outliers_functions': remove_outliers_functions, 
                                                    'remove_outlier': remove_outlier,
                                                    'votes_thresholds': votes_thresholds,
                                                    'label_column': label_column,
                                                    'random_state': 50},
                                            outputs=['outlier_removal', 'outlier_removal_test'])
    
    
    # Train a model using the auto_trainer hub function
    train_run = mlrun.run_function("hub://auto_trainer",
                                   inputs={"dataset": outlier_removal_run.outputs['outlier_removal'],
                                           "test_set": outlier_removal_run.outputs['outlier_removal_test']},
                                   params = {
                                       "model_class": "xgboost.XGBRegressor",
                                       "label_columns": label_column,
                                       "model_name": dataset,                                       
                                   }, 
                                   handler='train',
                                   outputs=["model"],
                               )
