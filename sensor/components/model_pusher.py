##This model_pusher component will save our models in "saved_models" folder

from sensor.predictor import ModelResolver
from sensor.entity.config_entity import ModelPusherConfig
from sensor.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact,ModelPusherArtifact
from sensor.exception import SensorException
import os,sys
from sensor.utils import load_object,save_object
from sensor.logger import logging


class ModelPusher:

    def __init__(self,model_pusher_config:ModelPusherConfig,
    data_transformation_artifact:DataTransformationArtifact,
    model_trainer_artifact:ModelTrainerArtifact):
        try:
            logging.info(f"{'>>'*20} Model Pusher {'<<'*20}")
            self.model_pusher_config=model_pusher_config
            self.data_transformation_artifact=data_transformation_artifact
            self.model_trainer_artifact=model_trainer_artifact
            self.model_resolver = ModelResolver(model_registry=self.model_pusher_config.saved_model_dir)    ###now note that this class was called in model_evaluation component also but that stage/component is looking for objects/models, i.e., it is looking with a perception that these might exist inside a folder or might not, so it is not certain that that folder exist, therefore there it was not needed to pass arguement inside the class for parameter "model_registry", it will consider the value given to it inside the ModelResolver class i.e., "saved_models",,,,,,,,,,,,,,but here in this component, we want to store those models/objects i.e., here we are with an intent to store them so we ae certain of our task hence when we called this class then we passed the arguement value w.r.t. model_registry parameter of the ModelResolver class, although the name here also is "saved_models", it could have been any other name if we would have wanted to by simply mentioning it at the model_pusher_config class
        except Exception as e:
            raise SensorException(e, sys)


    def initiate_model_pusher(self,)->ModelPusherArtifact:
        try:
            #load objects trained
            logging.info(f"Loading transformer model and target encoder")
            transformer = load_object(file_path=self.data_transformation_artifact.transform_object_path)
            model = load_object(file_path=self.model_trainer_artifact.model_path)
            target_encoder = load_object(file_path=self.data_transformation_artifact.target_encoder_path)

            #saving in model pusher directory
            logging.info(f"Saving model into model pusher directory")
            save_object(file_path=self.model_pusher_config.pusher_transformer_path, obj=transformer)
            save_object(file_path=self.model_pusher_config.pusher_model_path, obj=model)
            save_object(file_path=self.model_pusher_config.pusher_target_encoder_path, obj=target_encoder)


            #getting saved_models directory's locations to save the models/objects
            logging.info(f"Saving model in saved model dir")
            transformer_path=self.model_resolver.get_latest_save_transformer_path()                   ##now in this case we are first getting the path values for each of the models/object to be stored, now we did this because if we would have directly given the path as an arguement inside the save_object function then for each save_object function it will form new folder like 0 then 1 then 2 to store ttansformer, model, and target_encoder respectively inside "saved_model" folder, as each time on calling of the model resolver's get latest path function for each object/model it will form a subfolder with a numerical name inside "saved_models" folder,, so now if we extract paths for all three first so we are basically just extracting paths not exactly creating them, that means we will be having path for all three models/objects inside a folder with same numerical name,,,, then simply later on by performing save_object function we will save them 
            model_path=self.model_resolver.get_latest_save_model_path()
            target_encoder_path=self.model_resolver.get_latest_save_target_encoder_path()
            #now saving
            save_object(file_path=transformer_path, obj=transformer) 
            save_object(file_path=model_path, obj=model)
            save_object(file_path=target_encoder_path, obj=target_encoder)

            model_pusher_artifact = ModelPusherArtifact(pusher_model_dir=self.model_pusher_config.pusher_model_dir,
             saved_model_dir=self.model_pusher_config.saved_model_dir)
            logging.info(f"Model pusher artifact: {model_pusher_artifact}")
            return model_pusher_artifact
        except Exception as e:
            raise SensorException(e, sys)
