##code to understand the use of exception.py and logger.py
from sensor.exception import SensorException 
from sensor.logger import logging
import sys,os

def test_logger_and_exception():
    try:
        logging.info("starting the test_logger_and_exception")
        result =3/0
        print(result)
        logging.info("stopping the test_logger_and_exception")
    except Exception as e:
        logging.debug(e)
        raise SensorException(e, sys)


if __name__=="__main__":
    try:
        test_logger_and_exception()
    except Exception as e:
        print(e)
