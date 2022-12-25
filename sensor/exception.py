import sys,os

def error_message_detail(error, error_detail: sys):
    _, _, exc_tb = error_detail.exc_info()             ##using datatyping to assign the varibale "error_detail", sys as a type so that it can use exc_info() function of sys module, which provide excepton info in detail that includes exception class, exception message, and function object location,,,,in thbis line assigning the function object location{basically location where error occured} to exc_tb variable.
    file_name = exc_tb.tb_frame.f_code.co_filename     ##this will assign name of the file where the exception/error occured to "file_name" variable
    error_message = "Error occurred python script name [{0}] line number [{1}] error message [{2}]".format(
        file_name, exc_tb.tb_lineno, str(error)        ##using ".tb_lineno" can get the linenumber in a simple manner 
    )                                                  ##this whole error mesage will give the file name in which error/exception has occured, line number of the file where it has occured and the error/exception that has occured.
    return error_message



class SensorException(Exception):   ##we are creating our own exception class "SensorException" by inheriting Exception class

    def __init__(self,error_message, error_detail:sys):
        self.error_message = error_message_detail(               ##here we are initializing the variables
            error_message, error_detail=error_detail)

    def __str__(self):
        return self.error_message

##note: when we call the class then it will go to "__str__" of the class first then it will go to the "error_message" variable through which it will call the "error_message_detail" function, through which we will get the error message that we want out of this containing the filename, linenumber and error.