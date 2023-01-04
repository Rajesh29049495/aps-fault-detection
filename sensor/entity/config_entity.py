import os,sys
from sensor.exception import SensorException
from sensor.logger import logging
from datetime import datetime

##here we have mentioned these constant variables, we did it, as these are constant file names, i.e., these are not files whose name are contain timestamp, so these will always have same name,,,so if we  call them again again, we may face typo error, so to avoid it we have mentioned them here 
FILE_NAME = "sensor.csv"
TRAIN_FILE_NAME = "train.csv"
TEST_FILE_NAME = "test.csv"
TRANSFORMER_OBJECT_FILE_NAME = "transformer.pkl"
TARGET_ENCODER_OBJECT_FILE_NAME = "target_encoder.pkl"
MODEL_FILE_NAME = "model.pkl"


class TrainingPipelineConfig:   ##this whole class will just create a path name where all the output will stored each time training pipeline is going to run

    def __init__(self):
        try:
            self.artifact_dir = os.path.join(os.getcwd(),"artifact",f"{datetime.now().strftime('%m%d%Y__%H%M%S')}")  ##it is going to create a location in the current directory with a format mentioned in this code only,,using this created location and format in which outputs will be stored each tim etraining pipeline going to run like we created the logs
        except Exception  as e:
            raise SensorException(e,sys) 


class DataIngestionConfig:
    def __init__(self,training_pipeline_config:TrainingPipelineConfig):   ##note every componenet will take object of class trainingpipelineconfig as input
        try:
            self.database_name="aps"
            self.collection_name="sensor"
            self.data_ingestion_dir = os.path.join(training_pipeline_config.artifact_dir , "data_ingestion")  ##it will create a path which lead to 'data_ingestion' folder
            self.feature_store_file_path = os.path.join(self.data_ingestion_dir,"feature_store",FILE_NAME)  ##this will create path cwd/artifact/atimestampedfolder/data_ingestion/feature_store/sensor.csv
            self.train_file_path = os.path.join(self.data_ingestion_dir,"dataset",TRAIN_FILE_NAME)          ##this will create path cwd/artifact/atimestampedfolder/data_ingestion/dataset/train.csv
            self.test_file_path = os.path.join(self.data_ingestion_dir,"dataset",TEST_FILE_NAME)            ##this will create path cwd/artifact/atimestampedfolder/data_ingestion/dataset/test.csv
            self.test_size = 0.2
        except Exception  as e:
            raise SensorException(e,sys)     

    def to_dict(self)->dict:
        try:
            return self.__dict__
        except Exception  as e:
            raise SensorException(e,sys) 


class DataValidationConfig:
    def __init__(self,training_pipeline_config:TrainingPipelineConfig): 
        try:
            self.data_validation_dir = os.path.join(training_pipeline_config.artifact_dir , "data_validation")  ##it will create a point/location where the data validation foler will be located
            self.report_file_path= os.path.join(self.data_validation_dir,"report.yaml")                          ##in it we will store a report{can be .yaml, .csv or.json format}, which will contain all the report whether there is drift and not, whose location/path is being mentioned here.
            self.missing_threshold:float = 0.2
            self.base_file_path = os.path.join("aps_failure_training_set1.csv") 
        except Exception  as e:
            raise SensorException(e,sys)


class DataTransformationConfig:

    def __init__(self,training_pipeline_config:TrainingPipelineConfig):
        self.data_transformation_dir = os.path.join(training_pipeline_config.artifact_dir , "data_transformation")
        self.transform_object_path = os.path.join(self.data_transformation_dir,"transformer",TRANSFORMER_OBJECT_FILE_NAME)
        self.transformed_train_path =  os.path.join(self.data_transformation_dir,"transformed",TRAIN_FILE_NAME.replace("csv","npz"))
        self.transformed_test_path =os.path.join(self.data_transformation_dir,"transformed",TEST_FILE_NAME.replace("csv","npz"))
        self.target_encoder_path = os.path.join(self.data_transformation_dir,"target_encoder",TARGET_ENCODER_OBJECT_FILE_NAME)



class ModelTrainingConfig:...
class ModelEvaluationConfig:...
class ModelPusherConfig:...
