##code to understand the use of exception.py and logger.py
from sensor.exception import SensorException 
from sensor.logger import logging
import sys,os
from sensor.__init__ import get_collection_as_dataframe


if __name__=="__main__":
    try:
        get_collection_as_dataframe(database_name='aps',collection_name='sensor')
    except Exception as e:
        print(e)

