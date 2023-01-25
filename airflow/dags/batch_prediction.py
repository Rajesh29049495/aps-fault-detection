from asyncio import tasks
import json
from textwrap import dedent
import pendulum
import os
from airflow import DAG
from airflow.operators.python import PythonOperator


with DAG(
    'batch_prediction',
    default_args={'retries': 2},
    # [END default_args]
    description='Sensor Fault Detection',
    schedule_interval="@weekly",
    start_date=pendulum.datetime(2022, 12, 11, tz="UTC"),
    catchup=False,
    tags=['example'],
) as dag:

    
    def download_files(**kwargs):
        bucket_name = os.getenv("BUCKET_NAME")
        input_dir = "/app/input_files"          ##mention the path where we going to downoad the ".csv" file on which we will make prediction
        os.makedirs(input_dir,exist_ok=True)    ##this will create the "input_files" folder inside "app" folder, if it does not exists
        os.system(f"aws s3 sync s3://{bucket_name}/input_files /app/input_files")     ##this will download the ".csv" file inisde the "/app/input_files" location of th eEC2 machine from "s3://{bucket_name}/input_files" by syncing.,,,,,,,,note we created that"input_files" folder inside the s3 bucket "sensor-faultt-bucket" manually

    def batch_prediction(**kwargs):
        from sensor.pipeline.batch_prediction import start_batch_prediction
        input_dir = "/app/input_files"
        for file_name in os.listdir(input_dir):      ##this will list down files that are there inside the "input_files" folder,,,{although the way i gave path inside os.listdir() function as arguemnet is optional but if didn't have given then it would have listed the files inside the current working directry that is "app"}
            #make prediction
            start_batch_prediction(input_file_path=os.path.join(input_dir,file_name))
    
    def sync_prediction_dir_to_s3_bucket(**kwargs):
        bucket_name = os.getenv("BUCKET_NAME")
        #upload prediction folder{that got created in the working directory "/app" on running the batch_prediction pipeline} to predictionfiles folder{"prediction_files" that we have manually created} in s3 bucket
        os.system(f"aws s3 sync /app/prediction s3://{bucket_name}/prediction_files")
    

    download_input_files  = PythonOperator(
            task_id="download_file",
            python_callable=download_files

    )

    generate_prediction_files = PythonOperator(
            task_id="prediction",
            python_callable=batch_prediction

    )

    upload_prediction_files = PythonOperator(
            task_id="upload_prediction_files",
            python_callable=sync_prediction_dir_to_s3_bucket

    )

    download_input_files >> generate_prediction_files >> upload_prediction_files   ##the flow this batch prediction pipeline will follow