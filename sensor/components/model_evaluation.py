from sensor.predictor import ModelResolver
from sensor.entity import config_entity,artifact_entity
from sensor.exception import SensorException
from sensor.logger import logging
from sensor.utils import load_object
from sklearn.metrics import f1_score
import pandas  as pd
import sys,os
from sensor.config import TARGET_COLUMN

class ModelEvaluation:

    def __init__(self,
                model_eval_config:config_entity.ModelEvaluationConfig,
                data_ingestion_artifact:artifact_entity.DataIngestionArtifact,
                data_transformation_artifact:artifact_entity.DataTransformationArtifact,
                model_trainer_artifact:artifact_entity.ModelTrainerArtifact
                ):
                try:
                    logging.info(f"{'>>'*20}  Model Evaluation {'<<'*20}")
                    self.model_eval_config=model_eval_config
                    self.data_ingestion_artifact=data_ingestion_artifact
                    self.data_transformation_artifact=data_transformation_artifact
                    self.model_trainer_artifact=model_trainer_artifact
                    self.model_resolver = ModelResolver()
                except Exception as e:
                    raise SensorException(e,sys)
    

    def initiate_model_evaluation(self)->artifact_entity.ModelEvaluationArtifact:
        try:
            #if 'saved model' folder has model then we will compare which model is best, trained or the model from the 'saved model' folder

            logging.info("if saved model folder has model then we will compare which model is best, trained or the model from the 'saved model' folder")
            latest_dir_path = self.model_resolver.get_latest_dir_path()
            if latest_dir_path==None:   ##if none{i.e., no model present} then there is no comaparison, we will prepare the model_eval_artifact, ie., details that the current trained mode is accepted 
                model_eval_artifact = artifact_entity.ModelEvaluationArtifact(is_model_accepted=True,improved_accuracy=None)
                logging.info(f"Model evaluation artifact: {model_eval_artifact}")
                return model_eval_artifact

            
            #but if there model is present, then i need to load those models{i.e., transformer, model and target encoder},,,
            #first knowing their location by using model_resolver class
            logging.info("Finding location of transformer model and target encoder")
            transformer_path =self.model_resolver.get_latest_transformer_path()
            model_path =self.model_resolver.get_latest_model_path()
            target_encoder_path = self.model_resolver.get_latest_target_encoder_path()

            
            logging.info("Previous trained objects of transformer, model and target encoder")
            #Previous trained  objects, which were in use in production
            transformer = load_object(file_path=transformer_path)
            model = load_object(file_path=model_path)
            target_encoder = load_object(file_path=target_encoder_path)


            logging.info("Currently trained model objects")
            #Currently trained model objects
            current_transformer = load_object(file_path=self.data_transformation_artifact.transform_object_path)
            current_model  = load_object(file_path=self.model_trainer_artifact.model_path)
            current_target_encoder = load_object(file_path=self.data_transformation_artifact.target_encoder_path)


            
            ##now will read the test.csv file ingested during the data_ingestion component, then make it go throgh transformation, target_encoder then will predict values for that and then find accuracy using both the newly trained model and the model already in production and then compare their accuracies
            
            #reading the test file on which comparison will be done
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            target_df = test_df[TARGET_COLUMN]

            #first we encode the categorical values of the target feature, because it will be needed in numerical form while calculating the f1 score
            y_true =target_encoder.transform(target_df)
            ##accuracy using previous trained model
            input_feature_name = list(transformer.feature_names_in_)    ##this is done to get the features that were used to fit the transform object formed in the data_transformation.py file, and there we saw that only input featues where used not the target features so basically with thi sline of code we will get all the input features excluding the target feature "class", then we will transform the dataset to do the validation
            input_arr =transformer.transform(test_df[input_feature_name])
            y_pred = model.predict(input_arr)
            print(f"Prediction using previous model: {target_encoder.inverse_transform(y_pred[:5])}") ##just to print the predictions done of five records, and showing the prediction after using encoder's reverse transform function to show predictions into its original categorical form,,, {this print function is just to show that predictions has been done}

            previous_model_score = f1_score(y_true,y_pred) 
            logging.info(f"Accuracy using previous trained model: {previous_model_score}")
            
            #accuracy using current trained model
            input_feature_name = list(current_transformer.feature_names_in_)
            input_arr =current_transformer.transform(test_df[input_feature_name])
            y_pred = current_model.predict(input_arr)
            y_true = current_target_encoder.transform(target_df)
            print(f"Prediction using trained model: {current_target_encoder.inverse_transform(y_pred[:5])}")
            current_model_score = f1_score(y_true=y_true, y_pred=y_pred)
            logging.info(f"Accuracy using current trained model: {current_model_score}")


            if current_model_score<=previous_model_score:
                logging.info(f"Current trained model is not better than previous model")
                raise Exception("Current trained model is not better than previous model")

            model_eval_artifact = artifact_entity.ModelEvaluationArtifact(is_model_accepted=True,
                                                                          improved_accuracy=current_model_score-previous_model_score)
            logging.info(f"Model eval artifact: {model_eval_artifact}")
            return model_eval_artifact
        

        except Exception as e:
                    raise SensorException(e,sys)
            
            