import mlrun
from kfp import dsl
import sklearn

@dsl.pipeline(
    name="Automatic Pipeline",
    description="Train & Evaluate"
)
def kfpipeline(dataset: str='housing',
               path: str='/home/jovyan/data/src/housing.csv',
               label_column:str='MEDV'):
    
    project = mlrun.get_current_project()
        
    get_data_run = mlrun.run_function(name='get_data',
                                      function='gen-dataset',
                                      params={'dataset': dataset,
                                              'path': path},
                                      outputs=[dataset])

    
    # Train a model using the auto_trainer hub function
    train_run = mlrun.run_function("hub://auto_trainer",
                                   inputs={"dataset": get_data_run.outputs[dataset]},
                                   params = {
                                       "model_class": "xgboost.XGBRegressor",
                                       "label_columns": label_column,
                                       "model_name": dataset,
                                       "random_state": 0
                                   }, 
                                   handler='train',
                                   outputs=["model"],
                               )
