from sensor.exception import SensorException
from sensor.logger import logging
from sensor.predictor import ModelResolver
import pandas as pd
import numpy as np
from sensor.utils import load_object, convert_columns_float
import os,sys
from datetime import datetime
PREDICTION_DIR ="prediction"                   ##in this folder we will store our prediction file made after doing predictions on the input file
from sensor.config import TARGET_COLUMN
from scipy.stats import ks_2samp


def start_batch_prediction(input_file_path):  ##to this function, input file path needs to be provided,, the path were input file{the dataset on which prediction is asked to be made by the clients} present
    try:
        os.makedirs(PREDICTION_DIR,exist_ok=True)                      ##this will creae the prediction directory if it does not exist to store prediction file
        logging.info(f"Creating model resolver object")
        model_resolver = ModelResolver(model_registry="saved_models")   ##using this object to get the location of the latest models inside the "saved_models" folder
        logging.info(f"Reading file :{input_file_path}")
        df = pd.read_csv(input_file_path)
        df.replace({"na":np.NAN},inplace=True)               ##did it with almost all the dataframe, to have a common value for none values,,,,,,,,also if 'na' would have been there then it would have created problem during some type of transformation and giving errors like "couldn't convert string to float: 'na'"


        
        ###now we will check the validity of the data by performing some of the data validation operations
        
        ##so first we will load the latest dataset "sensor.csv" from the artifact folder, as this will be the base dataset using which the current model was built, that we will be using to form the prediction file
        base_file_dir = os.path.join(os.getcwd(),"artifact")
        dir_names = os.listdir(base_file_dir)                    ##list all the files inside the artifact directory
        dir_names.sort()                                         ##sort the files name is time stamped, so if that sorted then it will sort them as from the file forst created to the last created
        latest_dir_name = dir_names[len(dir_names)-1]         ##from the sorted dir_names list i am extracting the last one from the list as that is the latest one
        base_file_path = os.path.join(base_file_dir,f"{latest_dir_name}","data_ingestion/feature_store/sensor.csv")
        logging.info(f"Reading base file :{base_file_path}")    
        base_df = pd.read_csv(base_file_path)
        
        base_df.replace({"na":np.NAN},inplace=True)

        ##now drop the column with null values more than 20 percent
        #base dataframe
        logging.info(f"Drop null values colums from base df")
        base_df_null_report = base_df.isna().sum()/base_df.shape[0]
        base_df_drop_column_names = base_df_null_report[base_df_null_report>0.2].index
        base_df.drop(list(base_df_drop_column_names),axis=1, inplace = True)
        #input file
        logging.info(f"Drop null values colums from input df")
        null_report = df.isna().sum()/df.shape[0]
        drop_column_names = null_report[null_report>0.2].index
        df1 = df.drop(list(drop_column_names),axis=1)   ##we made this separate datafarem with removed column{those column which have more than 20 percent null values}, although normally i should applied transformation to this dataframe, but since sir didn't applied transformation on this typ eo dataframe in the training pipeline, he separately again loaded teh training and testing dataframe and then applied the transformation       
        #return None if no columns left
        if len(df1.columns)==0:
            logging.info(f"no column left after removing those with more than 20 percent null values")
            raise Exception("no column left after removing those with more than 20 percent null values")
        
        #else we do further data validation
        ##now we change the datatye of all the columns to float except the target column, did it to avoid datatype mismatch error while testing the distribution of the features
        exclude_columns = [TARGET_COLUMN]
        base_df = convert_columns_float(df=base_df, exclude_columns=exclude_columns)
        df1 = convert_columns_float(df=df1, exclude_columns=exclude_columns)                       ##as input file has no target feature given, but right now i am just using the main dataset using which we have formed this model, and it has target column, so we will exclude that, otherwise we would have passed "[]" as arguement to the exclude_columns parameter of convert_columns_float function we called from utils module{that we created} 

        ##now we will validate the presence of required number of columns
        logging.info(f"checking the presence of required number of columns")    
        base_columns = base_df.columns
        current_columns = df1.columns

        missing_columns = []
        for base_column in base_columns:
            if base_column not in current_columns:
                missing_columns.append(base_column)
        if len(missing_columns)>0:
            raise Exception("required number of columns are not present")
        
        #otherwise carry on with the data validation operations
        logging.info(f"As all columns are available in input df hence detecting data drift")
        for base_column in base_columns:
            base_data,current_data = base_df[base_column],df1[base_column]    ##as uptil now its confirmed that both have same columns
            #Null hypothesis is that both column data drawn from same distrubtion
                
            same_distribution =ks_2samp(base_data,current_data)

            if same_distribution.pvalue>0.05:
                #We are accepting null hypothesis, i.e. same distribution
                logging.info(f"no data drift")
            else:
                raise Exception("data drift present")
                #different distribution


        
        ##transformation
        logging.info(f"Loading transformer to transform dataset")
        transformer = load_object(file_path=model_resolver.get_latest_transformer_path())

        input_feature_names =  list(transformer.feature_names_in_)
        input_arr = transformer.transform(df[input_feature_names])


        logging.info(f"Loading model to make prediction")
        model = load_object(file_path=model_resolver.get_latest_model_path())
        prediction = model.predict(input_arr)

        logging.info(f"Target encoder to convert predicted column into categorical")
        target_encoder = load_object(file_path=model_resolver.get_latest_target_encoder_path())

        cat_prediction = target_encoder.inverse_transform(prediction)

        df["prediction"]=prediction            ##now we appended the prediction column and cat_pred column to the input file dataframe,, i.e., both prediction made in numerical form and in categorical form appended to the input file dataframe provided by the client
        df["cat_pred"]=cat_prediction


        prediction_file_name = os.path.basename(input_file_path).replace(".csv",f"{datetime.now().strftime('%m%d%Y__%H%M%S')}.csv")  ##this will name to the prediction file,,, this code will first get the basename from the input_file_path{i.e., if path of input file is x/y/z/abc.csv, then it will return abc.csv}, then replace the ".csv" with "{timestamp}.csv"
        prediction_file_path = os.path.join(PREDICTION_DIR,prediction_file_name)                                                     ##path where prediction file will be saved
        df.to_csv(prediction_file_path,index=False,header=True)                                                                      ##this will save the prediction file in csv format at the location passed as an arguement,,, and in the file didn't save index values{index = False} but saved the headings of the columns{header = True}
        return prediction_file_path

    except Exception as e:
        raise SensorException(e, sys)