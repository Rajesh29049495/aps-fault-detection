##whenever we going to run this code from airflow pipeline it is going to run 'start_training_pipeline' function

from asyncio import tasks
import json
from textwrap import dedent
import pendulum
import os
from airflow import DAG                              #to instantiate a DAG
from airflow.operators.python import PythonOperator  #this opearator is used to call and run python functions


##if we want to schedule somethimg on airflow, we have define/declare a DAG for that
with DAG(                                                ##in DAG we need to pass these parameters
    'sensor_training',                                     #this is the name given to DAG
    default_args={'retries': 2},                           #default_args we have to pass, in it retries=2 means this pipeline will run two time, 2nd time if failed the first time, but if failed the second time also, it is considered as a failure 
    # [END default_args]
    description='Sensor Fault Detection',                  #just a description{just a normal text, can write anything} 
    schedule_interval="@weekly",                           #this parameter schedules the interval
    start_date=pendulum.datetime(2022, 12, 11, tz="UTC"),  #start date of the scheduler
    catchup=False,
    tags=['example'],
) as dag:

    
    def training(**kwargs):     ##we are creating a function named 'training', inside we going to import the "start_training_pipeline" function, then called it
        from sensor.pipeline.training_pipeline import start_training_pipeline
        start_training_pipeline()
    
    def sync_artifact_to_s3_bucket(**kwargs):         ##another function, it will sync the 'artifact' and 'saved_models' that will be created here in '/app' folder when we going to run this training pipeline to a s3 bucket
        bucket_name = os.getenv("BUCKET_NAME")        ##i have mentioned it inside ".env" file, so using os.getenv() function i am calling the value of key 'BUCKET_NAME', if there exist the value which exist then it will give return that value otherwise it will return None
        os.system(f"aws s3 sync /app/artifact s3://{bucket_name}/artifacts")                  #os.system() function,,,os.system() method execute the command (a string) in a subshell,,,,If command generates any output, it is sent to the interpreter standard output stream. Whenever this method is used then the respective shell of the Operating system is opened and the command is executed on it,,,,,,Syntax is os.system(command), where command is of string type that tells which command to execute.
        os.system(f"aws s3 sync /app/saved_models s3://{bucket_name}/saved_models")

    #note that everytime we going to create a DAG, within that DAG we need use some operators from airflow, like here we are using python operator as we have some python functions that we want to call here
    training_pipeline  = PythonOperator(
            task_id="train_pipeline",          #task name/task id you can give
            python_callable=training           #the function this operator will call is mentioned here 

    )
    #another operator/node to run the other function 
    sync_data_to_s3 = PythonOperator(
            task_id="sync_data_to_s3",
            python_callable=sync_artifact_to_s3_bucket

    )

    training_pipeline >> sync_data_to_s3      ##what we want to run{basically the flow to be followed} is written here, we will be running the "training_pipeline" called by the PythonOperator on starting the airflow scheduler, then we will sync the folders got created out of it with the s3 bucket