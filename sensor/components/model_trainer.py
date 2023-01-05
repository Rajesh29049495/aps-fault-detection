from sensor.entity import artifact_entity, config_entity
from sensor.exception import SensorException
from sensor.logger import logging
from typing import Optional
import os, sys
from xgboost import XGBClassifier
from sensor import utils
from sklearn.metrics import f1_score


class ModelTrainer:

    def __init__(self, model_trainer_config: config_entity.ModelTrainerConfig,
                 data_transformation_artifact: artifact_entity.DataTransformationArtifact
                 ####here varaiables that we have taken is from ModelTrainerConfig as it contains the path and all to store the model,,,and the other variable is DataTransformationArtifact, beacuse we want to use the transformed data
                 ):
        try:
            logging.info(f"{'>>' * 20} Model Trainer {'<<' * 20}")
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact

        except Exception as e:
            raise SensorException(e, sys)

    # function to train the model
    def train_model(self, x, y):
        try:
            xgb_clf = XGBClassifier()  ###training the model by using this classifier ,because during th eexperiment stage found this algorithm to b ethe best for the problem
            xgb_clf.fit(x,y)
            return xgb_clf
        except Exception as e:
            raise SensorException(e, sys)

    def initiate_model_trainer(self) -> artifact_entity.ModelTrainerArtifact:
        try:
            logging.info(f"loading train and test array")
            train_arr = utils.load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_train_path)
            test_arr = utils.load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_test_path)

            logging.info(f"Splitting input and target feature from both train and test arr.")
            x_train, y_train = train_arr[:,:-1], train_arr[:,-1]  ##we concatenated it in previuos component, so to get x_train we will extract it in such a way that we need each row, and ech column except the last one, and for y_train{i.e., the target feature}, we will extract such that we need all the rows but only one column
            x_test, y_test = test_arr[:,:-1], train_arr[:,-1]

            logging.info(f"Train the model")
            model = self.train_model(x=x_train, y=y_train)

            ##calculating the naccuracy score, for that we will be using the f1 score, because we wanted to giv eimportane to both precision and recall hence we used the f1 score as it i steh harmonic mean of both,,,,,,,note in case of regeression problem we would have used r1 score
            logging.info(f"Calculating f1 train score")
            yhat_train = model.predict(x_train)
            f1_train_score = f1_score(y_true=y_train, y_pred=yhat_train)

            logging.info(f"Calculating f1 test score")
            yhat_test = model.predict(x_test)
            f1_test_score = f1_score(y_true=y_test, y_pred=yhat_test)

            logging.info(f"train score:{f1_train_score} and tests score {f1_test_score}")

            # check for overfitting or underfiiting or expected score
            logging.info(f"Checking if our model is underfitting or not")
            if f1_test_score < self.model_trainer_config.expected_score:
                raise Exception(f"Model is not good as it is not able to give \
                expected accuracy: {self.model_trainer_config.expected_score}: model actual score: {f1_test_score}")

            logging.info(f"Checking if our model is overfiiting or not")
            diff = abs(f1_train_score - f1_test_score)
            if diff > self.model_trainer_config.overfitting_threshold:
                raise Exception(
                    f"Train and test score diff: {diff} is more than overfitting threshold {self.model_trainer_config.overfitting_threshold}")

            # save the trained model
            logging.info(f"Saving mode object")
            utils.save_object(file_path=self.model_trainer_config.model_path, obj=model)

            # prepare artifact
            logging.info(f"Prepare the artifact")
            model_trainer_artifact = artifact_entity.ModelTrainerArtifact(
                model_path=self.model_trainer_config.model_path,
                f1_train_score=f1_train_score, f1_test_score=f1_test_score)
            logging.info(f"Model trainer artifact: {model_trainer_artifact}")
            return model_trainer_artifact

        except Exception as e:
            raise SensorException(e, sys)