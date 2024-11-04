from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow import configuration as conf

from src.db_connection import *
from src.json_to_csv import *
from src.CSV_to_DB import *
from src.db_to_schema import *
from src.download_data import *

default_args = {
    'owner': 'your_name',
    'start_date': datetime(2024, 10, 30),
    'retries': 2, 
    'retry_delay': timedelta(minutes=0.3), 
    'email': 'ecomchat5@gmail.com',
    'email_on_failure': True,
    'email_on_retry': False
}

dag = DAG(
    'data_pipeline',
    default_args=default_args,
    description='Dag for data pipeline',
    schedule_interval=None,  
    catchup=False,
)




get_metadata = PythonOperator(
    task_id='get_metadata',
    python_callable=ingest_data_meta,
    op_args=['https://github.com/SoumyaeCodes/DockDecoder/raw/refs/heads/master/test_metadata.json.zip'],
    dag=dag,
)

get_review_data = PythonOperator(
    task_id='get_review_data',
    python_callable=ingest_data_review,
    op_args=['https://github.com/SoumyaeCodes/DockDecoder/raw/refs/heads/master/test_user_reviews.json.zip'],
    dag=dag,
)






json_to_csv_review_data = PythonOperator(
    task_id='json_to_csv_review_data',
    python_callable=json_to_csv_review,
    op_args=['Data/Raw/TEST/test_user_reviews.json', 'Data/Raw_CSV/TEST/'],
    dag=dag,
) 

json_to_csv_meta_data = PythonOperator(
    task_id='json_to_csv_meta_data',
    python_callable=json_to_csv_meta,
    op_args=['Data/Raw/TEST/test_metadata.json','Data/Raw_CSV/TEST/'],
    dag=dag,
)



createtableuserreview = PythonOperator(
    task_id='createtableuserreview',
    python_callable=create_table_user_review,
    dag=dag,
)

createtablemetadata = PythonOperator(
    task_id='createtablemetadata',
    python_callable=create_table_meta_data,
    dag=dag,
)



transfer_task_meta = PythonOperator(
        task_id='transfer_task_meta',
        python_callable=add_meta_data,
        dag=dag,
    )

transfer_task_review = PythonOperator(
        task_id='transfer_task_review',
        python_callable=add_review_data,
        dag=dag,
    )




dbtoschema = PythonOperator(
    task_id='dbtoschema',
    python_callable=db_to_schema,
    dag=dag,
)







parallel_tasks_1 = [get_review_data, get_metadata]
parallel_tasks_2 = [json_to_csv_review_data, json_to_csv_meta_data, createtableuserreview, createtablemetadata]    
parallel_tasks_3 = [transfer_task_review, transfer_task_meta]

for task in parallel_tasks_1:
        task >> parallel_tasks_2

for task in parallel_tasks_2:
        task >> parallel_tasks_3

for task in parallel_tasks_3:
        task >> dbtoschema




if __name__ == "__main__":
    dag.cli()


