import pymongo
import pandas as pd
import json

from sensor.config import mongo_client   ##using this we are using the client we created to connect to the mongodb using my own URL, by mentioning that URL inside the ".env file", and which was called inside the config.py file after loading the environment variable using the ".init.py" file inside the sensor directory,,,,now don't have to separately form to client to establish connection of the vscode{ which is being used to use the python language} with the mongodb 

"""
##not needed now##
#Provide the mongodb localhost url to connect python to mongodb.
#client = pymongo.MongoClient("mongodb://localhost:27017/neurolabDB")
##
"""

data_file_path="/config/workspace/aps_failure_training_set1.csv"
database_name="aps"
collection_name="sensor"


if __name__=="__main__":
    df = pd.read_csv(data_file_path)
    print(f"Rows and columns: {df.shape}")

    # Convert dataframe to json so that we can dump these records in mongo db
    df.reset_index(drop=True, inplace= True)     ## done as a general practise, so that if index are not in proper form, to corect them

    json_record = list(json.loads(df.T.to_json()).values())   ###transpose kia becuase if iske baad they do the json conversion then the whole dictionary type format keys will be indexes and the values of that index will be a dictionary with keys as current columns and values of that index w.r.t. each columns , so that we get a single set of data w.r.t. a particular index/instance, so that later on it will be easily identifiable.,, then using jason.loads() to convert this json data into python dictionary format{to make it readable}, then extrcat the values of this dictionary data formed which is mostly dixtionaries, each containing the wholistic data i.e., each column value w.r.t. each index,,, then form list of it ,,, that will make those list with elements of dictionary form ,,, making it more easily identifiable, readable, separable etc
    print(json_record[0])

    #insert converted json record to mongo db
    mongo_client[database_name][collection_name].insert_many(json_record)

