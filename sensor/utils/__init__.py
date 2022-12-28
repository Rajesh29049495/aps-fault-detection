##this contains the code of a function to get dataframe from mongodb

import pandas as pd
from sensor.logger import logging
from sensor.exception import SensorException
from sensor.config import mongo_client  ##to call the client that we have created w.r.t. mongodb in the config file
import os,sys

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
        if "_id" in df.columns:                     ##to drop an 'id column which is mostly useless, so first find if it is there,if present the drop it'
            logging.info(f"Dropping column: _id ")
            df = df.drop("_id",axis=1)
        logging.info(f"Row and columns in df: {df.shape}")
        return df
    except Exception as e:
        raise SensorException(e, sys)