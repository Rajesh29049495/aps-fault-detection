import logging
import os
from datetime import datetime

#log file name{each time for any execution log with this filename format created}
LOG_FILE_NAME = f"{datetime.now().strftime('%m%d%Y__%H%M%S')}.log"

#log directory{using the os.path.join we joined the current working directpry address got by using os.getcwd() and "logs", suppose in my systme if i was writing this code in jupyter notebook, then current working directory "C:\\Users\\Rajesh Singh", then after joining path will be "C:\\Users\\Rajesh Singh\\logs",,,,,,,now in this line of code we have assigned the location to "LOG_FILE_DIR" variable}
LOG_FILE_DIR = os.path.join(os.getcwd(),"logs")

#create folder if not available{this command will create the "logs" directory to which we have assigned variable name above "LOG_FILE_DIR",,,now use of 'exist_ok' parameter is to create this "logs" directory if it does not exist }
os.makedirs(LOG_FILE_DIR,exist_ok=True)

#log file path{path were the log file will be stored}
LOG_FILE_PATH = os.path.join(LOG_FILE_DIR,LOG_FILE_NAME)

#basicConfig is a function that does basic configuration for logging of the project,,,basically it configures{setup/arrange} the logs,,,,,in it first i specifies the location were log will be created,,second the format in which the logging meassage will be created inside the log,,,in level we define the logging level which is to be logged, like here i have chosen INFO logging level out of CRITICAL,ERROR,WARNING,INFO,DEBUG and NOTSET 
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)