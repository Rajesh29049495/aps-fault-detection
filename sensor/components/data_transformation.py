from sensor.entity import artifact_entity, config_entity
from sensor.exception import SensorException
from sensor.logger import logging
from typing import Optional
import os, sys
from sklearn.pipeline import Pipeline
import pandas as pd
from sensor import utils
import numpy as np
from sklearn.preprocessing import LabelEncoder
from imblearn.combine import SMOTETomek
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler
from sensor.config import TARGET_COLUMN  ##note this target column always have to be declared somewhere{a good practice as it will be used again during the training component/stage, so if we use it again and again, then if in future the target column is renamed thenwe will have to rename it at every place, so to avoid this decalred it one place so that simply rename it at that one place only}, so here in this project we have declared it in config file, so to call it we have imported the config file from sensor folder


class DataTransformation:

    def __init__(self, data_transformation_config: config_entity.DataTransformationConfig,
                 data_ingestion_artifact: artifact_entity.DataIngestionArtifact):
        try:
            logging.info(f"{'>>' * 20} Data Transformation {'<<' * 20}")
            self.data_transformation_config = data_transformation_config
            self.data_ingestion_artifact = data_ingestion_artifact
        except Exception as e:
            raise SensorException(e, sys)


##defining the transformer object using which transformation will be done
    @classmethod                                     ##using class method, because wanted to create a shared resource, and also this function will be called by the class, as has no dependency on insatance variables{initialised varibles}, so created thi sfunction as a class method to save space{as a class method will have only one copy in the lifecycle of that class, whereas, instance method will have a copy for each and every instance}
    def get_data_transformer_object(cls) -> Pipeline:  ##'cls' used just to refer to the class{although this is optional},,,,,, and whenever someone going to call this function, they are going to get pipeline
        try:                                          ##we will create object of the transformation operations we going to do
            simple_imputer = SimpleImputer(strategy='constant', fill_value=0)   ###we hav used 'constant' strategy beacsue based on experiment done in jupyter notebook, found the best strategy to be used is 'constant', and 'fill_value' parameter is used when the strategy=constant and a constant value that is to be filled is needed to be supplied.
            robust_scaler = RobustScaler()
            pipeline = Pipeline(steps=[
                ('Imputer', simple_imputer),
                ('RobustScaler', robust_scaler)
            ])
            return pipeline
        except Exception as e:
            raise SensorException(e, sys)


    ##after creating the pipeline, now we can define the transformation function
    def initiate_data_transformation(self) -> artifact_entity.DataTransformationArtifact:
        try:
            # reading training and testing data
            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)

            # now its time for us to split out data into two part, input features and target feature
            # selecting input feature for train and test dataframe
            input_feature_train_df = train_df.drop(TARGET_COLUMN, axis=1)
            input_feature_test_df = test_df.drop(TARGET_COLUMN, axis=1)

            # selecting target feature for train ad test dataframe
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_test_df = test_df[TARGET_COLUMN]

            # we will apply the labelencoder now on the target features and will save the encoded data in a folder that we have already declared in the config_entity.py file
            label_encoder = LabelEncoder()
            label_encoder.fit(target_feature_train_df)

            # transformation on target columns,,,{and it is going to return an array}
            target_feature_train_arr = label_encoder.transform(target_feature_train_df)
            target_feature_test_arr = label_encoder.transform(target_feature_test_df)

            # now transformation pipeine will be applied to the input fetures of train and test data
            transformation_pipeline = DataTransformation.get_data_transformer_object()
            transformation_pipeline.fit(input_feature_train_df)

            # transforming input features
            input_feature_train_arr = transformation_pipeline.transform(input_feature_train_df)
            input_feature_test_arr = transformation_pipeline.transform(input_feature_test_df)

            # now resampling, to balance the dataset
            smt = SMOTETomek(random_state=42)
            logging.info(f"Before resampling in training set Input: {input_feature_train_arr.shape} Target:{target_feature_train_arr.shape}")
            input_feature_train_arr, target_feature_train_arr = smt.fit_resample(input_feature_train_arr,
                                                                             target_feature_train_arr)
            logging.info(f"After resampling in training set Input: {input_feature_train_arr.shape} Target:{target_feature_train_arr.shape}")

            logging.info(f"Before resampling in testing set Input: {input_feature_test_arr.shape} Target:{target_feature_test_arr.shape}")
            input_feature_test_arr, target_feature_test_arr = smt.fit_resample(input_feature_test_arr,
                                                                           target_feature_test_arr)
            logging.info(f"After resampling in testing set Input: {input_feature_test_arr.shape} Target:{target_feature_test_arr.shape}")

            ##now we going to save all these{objects and datas} one by one

            # first concatenating the input and target features of the train and test data
            train_arr = np.c_[input_feature_train_arr, target_feature_train_arr]
            test_arr = np.c_[input_feature_test_arr, target_feature_test_arr]

            # saving the data
            utils.save_numpy_array_data(file_path=self.data_transformation_config.transformed_train_path,
                                    array=train_arr)

            utils.save_numpy_array_data(file_path=self.data_transformation_config.transformed_test_path,
                                    array=test_arr)

            # saving the objects
            utils.save_object(file_path=self.data_transformation_config.transform_object_path,
                          obj=transformation_pipeline)

            utils.save_object(file_path=self.data_transformation_config.target_encoder_path,
                          obj=label_encoder)

            # now finally prepare the data transformation artifact
            data_transformation_artifact = artifact_entity.DataTransformationArtifact(
            transform_object_path=self.data_transformation_config.transform_object_path,
            transformed_train_path=self.data_transformation_config.transformed_train_path,
            transformed_test_path=self.data_transformation_config.transformed_test_path,
            target_encoder_path=self.data_transformation_config.target_encoder_path

            )

            logging.info(f"Data transformation object {data_transformation_artifact}")
            return data_transformation_artifact

        except Exception as e:
            raise SensorException(e, sys)
