import os
import graph
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
from langfuse.callback import CallbackHandler
from constants import META_TABLE, REVIEW_TABLE
from langchain.document_loaders import DataFrameLoader

from dotenv import load_dotenv
load_dotenv()

## load the API Keys
os.environ['HF_TOKEN']=os.getenv("HF_TOKEN")
os.environ['OPENAI_API_KEY']=os.getenv("OPENAI_API_KEY")
os.environ['GROQ_API_KEY']=os.getenv("GROQ_API_KEY")
os.environ['LANGFUSE_PUBLIC_KEY']=os.getenv("LANGFUSE_PUBLIC_KEY")
os.environ['LANGFUSE_SECRET_KEY']=os.getenv("LANGFUSE_SECRET_KEY")
os.environ['LANGFUSE_HOST']=os.getenv("LANGFUSE_HOST")

credentials = service_account.Credentials.from_service_account_file('big_credentials.json')
client = bigquery.Client(credentials=credentials)
langfuse_handler = CallbackHandler()
config = {"callbacks": [langfuse_handler]}

## set up Streamlit 
st.set_page_config(page_title="Verta", page_icon="🧑‍💻")
st.title("Verta")
st.subheader("Your Intelligent eCommerce Companion")

## Name
name = st.text_input("Enter your product ASIN:")

if name:
    # Perform a review query.
    QUERY = (f'''SELECT *
            FROM `{REVIEW_TABLE}` 
            WHERE parent_asin='{str(name)}'
            ''')
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish
    review_df = rows.to_dataframe()

    # Load the Reviews
    loader = DataFrameLoader(review_df) 
    review_documents = loader.load()

    # Perform a metadata query.
    meta_query = (f'''SELECT *
            FROM {META_TABLE} 
            WHERE parent_asin='{str(name)}'
            ''')
    query_job = client.query(meta_query)  # API request
    meta = query_job.result()  # Waits for query to finish
    meta_df = meta.to_dataframe()

    review_df.drop(columns=['user_id', 'images'], inplace = True)
    meta_df.drop(columns=['images', 'videos', 'bought_together'], inplace = True)

    st.write("Fetched Review Data", review_df)
    st.write("Fetched Meta Data", meta_df)

    app = graph.create_graph(isMemory=False)

    user_input = st.text_input("Your question:")

    if user_input:
        response = app.invoke({
            "question": st.session_state['question'],
            "meta_data": meta_df,
            "review_docs": review_documents,
        }, config=config)

        st.write("Verta:", response['answer'].content)
        
                
                



