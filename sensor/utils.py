##this contains the code of a function to get dataframe from mongodb, function to save data/report in '.yaml' file{the format}, function to convert datatype of all the columns to float except the 'class' column, function to save object in  pickle file{serialisation process}, function to load object from a pickle file{deserilaisation process}, and functions to save and load numpy_array data respectively

import pandas as pd
from sensor.logger import logging
from sensor.exception import SensorException
from sensor.config import mongo_client  ##to call the client that we have created w.r.t. mongodb in the config file
import os,sys
import numpy as np
import yaml
import dill  ##it is used to save your object/model in pickle format file, this library does the same function that pickle library does

def get_collection_as_dataframe(database_name: str, collection_name: str)->pd.DataFrame:
    """
    Description: This function return collection as dataframe
    =========================================================
    Params:
    database_name: database name
    collection_name: collection name
    =========================================================
    return Pandas dataframe of a collection
    """
    try:
        logging.info(f"Reading data from database: {database_name} and collection: {collection_name}")
        df = pd.DataFrame(list(mongo_client[database_name][collection_name].find()))  ##this will give all the documents from the database
        logging.info(f"Found columns: {df.columns}")
        if "_id" in df.columns:                     ##to drop an 'id column which is mostly useless as it is introduced by the mongodb whenever a data is stored in it, so first find if it is there,if present the drop it'
            logging.info(f"Dropping column: _id ")
            df = df.drop("_id",axis=1)
        logging.info(f"Row and columns in df: {df.shape}")
        return df
    except Exception as e:
        raise SensorException(e, sys)



##function to save data/report in '.yaml' file{the format}
def write_yaml_file(file_path,data:dict):
    try:
        file_dir = os.path.dirname(file_path)
        os.makedirs(file_dir,exist_ok=True)
        with open(file_path,"w") as file_writer:  ##'file_writer' just an alias
            yaml.dump(data,file_writer)           ##using file_writer the data will be written in above mentioned file path
    except Exception as e:
        raise SensorException(e, sys)


## convert datatype of all the columns to float except the 'class' column datatype.
def convert_columns_float(df:pd.DataFrame,exclude_columns:list)->pd.DataFrame:
    try:
        for column in df.columns:
            if column not in exclude_columns:
                df[column]=df[column].astype('float')
        return df
    except Exception as e:
        raise e
    
## function to save object in a pickle file
def save_object(file_path: str, obj: object) -> None:  ##'file_path' is the location where we going to save the object, and 'obj' is the object to be saved
    try:
        logging.info("Entered the save_object method of utils")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  #to make directory passed for 'file_path' variable, if not exist
        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)
        logging.info("Exited the save_object method of utils")
    except Exception as e:
        raise SensorException(e, sys) from e

##function to load ypur object from a pickle file
def load_object(file_path: str ) -> object:
    try:
        if not os.path.exists(file_path):
            raise Exception(f"The file: {file_path} does not exists")
        with open(file_path, "rb") as file_obj:
            return dill.load(file_obj)
    except Exception as e:
        raise SensorException(e, sys) from e

## functions to save and load numpy_array data respectively
def save_numpy_array_data(file_path: str, array: np.array):
    """
    Save numpy array data to file
    file_path: str location of file to save
    array: np.array data to save
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise SensorException(e, sys) from e

def load_numpy_array_data(file_path: str) -> np.array:
    """
    load numpy array data from file
    file_path: str location of file to load
    return: np.array data loaded
    """
    try:
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise SensorException(e, sys) from e