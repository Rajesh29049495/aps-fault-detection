import pymongo
import pandas as pd
import json 
from dataclasses import dataclass
import os
 

#we creating this environment variable class to call the urls stored in the ".env" file, so that we can connect using them
@dataclass                                ##here we will use dataclasses module to avoid bulky codes
class EnvironmentVariable():
    mongo_db_url: str = os.getenv("MONGO_DB_URL")  ##here reading the mongodb url from '.env file' by passing the key w.r.t it as parameter,,,here str is just to mention the type of the url{just for the convenience}


env_var = EnvironmentVariable() ##object of EnvironmentVariable class
mongo_client = pymongo.MongoClient(env_var.mongo_db_url)   ##now i don't have to create mongoclient again and again, simply will use it from here