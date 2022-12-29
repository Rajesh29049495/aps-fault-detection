from sensor import utils
from sensor.entity import config_entity
from sensor.entity import artifact_entity
from sensor.exception import SensorException
from sensor.logger import logging
import os,sys
import pandas as pd 
import numpy as np
from sklearn.model_selection import train_test_split

class DataIngestion:
    
    def __init__(self,data_ingestion_config:config_entity.DataIngestionConfig ):   ##using this we got data ingestion configurations,,this object of class dataingestionconfig will be needed as an input in this class
        try:
            logging.info(f"{'>>'*20} Data Ingestion {'<<'*20}")
            self.data_ingestion_config = data_ingestion_config 
        except Exception as e:
            raise SensorException(e, sys)

    def initiate_data_ingestion(self)->artifact_entity.DataIngestionArtifact:
        try:
            logging.info(f"Exporting collection data as pandas dataframe")
            #Exporting collection data as pandas dataframe
            df:pd.DataFrame  = utils.get_collection_as_dataframe(
                database_name=self.data_ingestion_config.database_name, 
                collection_name=self.data_ingestion_config.collection_name)       ##here the get_collection_as_dataframe function of utils folder will return dataframe df{dataframe} of type pd.DataFrame, input to this function is database name and collection name, which we have mentioned in the dataingestionconfig class of config_entity.py file

            logging.info("Save data in feature store")

            #replace na with Nan
            df.replace(to_replace="na",value=np.NAN,inplace=True)

            #Save data in feature store
            logging.info("Create feature store folder if not available")
            #Create feature store folder if not available
            feature_store_dir = os.path.dirname(self.data_ingestion_config.feature_store_file_path)  ##.dirname will be used to get the directory name of any location
            os.makedirs(feature_store_dir,exist_ok=True)                                             ##this will ensure creation of the drectory if it does nt exist
            logging.info("Save df to feature store folder")
            #Save df to feature store folder
            df.to_csv(path_or_buf=self.data_ingestion_config.feature_store_file_path,index=False,header=True)  ##here index= Falsse means we don't want index, and header= True means want to keep column names
                                                                                                               ##this will store the dataframe in .csv form at the mentioned path passed as a parameter inside this .to_csv function

            logging.info("split dataset into train and test set")
            #split dataset into train and test set
            train_df,test_df = train_test_split(df,test_size=self.data_ingestion_config.test_size,random_state=42)
            
            logging.info("create dataset directory folder if not available")
            #create dataset directory folder if not available
            dataset_dir = os.path.dirname(self.data_ingestion_config.train_file_path)
            os.makedirs(dataset_dir,exist_ok=True)

            logging.info("Save df to feature store folder")
            #Save train and test set to the path that we have created inside data_ingestion_config class of config_entity.py file
            train_df.to_csv(path_or_buf=self.data_ingestion_config.train_file_path,index=False,header=True)
            test_df.to_csv(path_or_buf=self.data_ingestion_config.test_file_path,index=False,header=True)
            ##now till here data ingestion phase is over, now we will prepare the output/artifact
            #Prepare artifact

            data_ingestion_artifact = artifact_entity.DataIngestionArtifact(
                feature_store_file_path=self.data_ingestion_config.feature_store_file_path,
                train_file_path=self.data_ingestion_config.train_file_path, 
                test_file_path=self.data_ingestion_config.test_file_path)

            logging.info(f"Data ingestion artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact

        except Exception as e:
            raise SensorException(error_message=e, error_detail=sys)


