import mlrun
import pandas as pd

def one_hot_encoding(df):
    for col in df.columns:
        if df[col].dtype == 'O':
            l = df[col].unique().tolist()
            encoded = []
            for label in df[col]:
                encoded.append(l.index(label))
            df[col] = encoded
    return df

def get_data(context: mlrun.MLClientCtx, 
             dataset:str = 'housing',
             path:str = '/home/jovyan/data/src/housing.csv'
            ):
    if dataset == 'housing':
        columns = ['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD', 'TAX', 'PTRATIO', 'B', 'LSTAT', 'MEDV']
        df = pd.read_csv(path, 
                         names = columns,
                         delimiter = r"\s+")
    
    
    elif dataset == 'motor':
        df = pd.read_csv(path)
        df = df[:-1].drop('IDpol',axis=1)
        df = one_hot_encoding(df)
        
    else:
        raise 'Unknown dataset'

        
    context.log_dataset(df=df, key=dataset, format='csv',index=False)