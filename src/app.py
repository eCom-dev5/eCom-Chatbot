import os
import sys
import graph
import pandas as pd
import streamlit as st
from pathlib import Path
from sqlalchemy import text
from utils import database as db
from langfuse.callback import CallbackHandler
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DataFrameLoader

from dotenv import load_dotenv
load_dotenv()

sys.path.append(
    str(
        Path(
            "ecom-chat"
        ).resolve()
    )
)

## load the API Keys
os.environ['HF_TOKEN']=os.getenv("HF_TOKEN")
os.environ['OPENAI_API_KEY']=os.getenv("OPENAI_API_KEY")
os.environ['GROQ_API_KEY']=os.getenv("GROQ_API_KEY")

## Langfuse
os.environ['LANGFUSE_PUBLIC_KEY']=os.getenv("LANGFUSE_PUBLIC_KEY")
os.environ['LANGFUSE_SECRET_KEY']=os.getenv("LANGFUSE_SECRET_KEY")
os.environ['LANGFUSE_HOST']=os.getenv("LANGFUSE_HOST")
langfuse_handler = CallbackHandler()
config = {"callbacks": [langfuse_handler]}

## Postgres DB
credentials = {
    'INSTANCE_CONNECTION_NAME': os.getenv("INSTANCE_CONNECTION_NAME"),
    'DB_USER': os.getenv("DB_USER"),
    'DB_PASS': os.getenv("DB_PASS"),
    'DB_NAME': os.getenv("DB_NAME")
}

## set up Streamlit 
st.set_page_config(page_title="Verta", page_icon="🧑‍💻")
st.title("Verta")
st.subheader("Your Intelligent eCommerce Companion")

## Create Postgres Engine
engine = db.connect_with_db(credentials)

## Function to load data and create retriever, with caching
@st.cache_resource
def create_retriever(asin, _engine):
    with _engine.begin() as connection:
        try:
            review_query = text(f"""
                        SELECT parent_asin, asin, helpful_vote, timestamp, verified_purchase, title, text
                        FROM userreviews ur 
                        WHERE ur.parent_asin = '{asin}';
                    """)
            review_result = connection.execute(review_query)
            review_df = pd.DataFrame(review_result.fetchall(), columns=review_result.keys())

            meta_query = text(f"""
                     SELECT parent_asin, main_category, title, average_rating, rating_number, features, description, price, store, categories, details
                     FROM metadata md 
                     WHERE md.parent_asin = '{asin}';
                """)
            meta_result = connection.execute(meta_query)
            meta_df = pd.DataFrame(meta_result.fetchall(), columns=meta_result.keys())

        except Exception as e:
            print(e)
            return None, None, None

    # Load the Reviews
    loader = DataFrameLoader(review_df)
    review_docs = loader.load()

    # Create and return the retriever
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(documents=review_docs, embedding=embeddings)
    retriever = vectordb.as_retriever()
    return retriever, review_df, meta_df

# ASIN input field
asin = st.text_input("Enter your product ASIN:", key="asin_input")

if asin:
    retriever, review_df, meta_df = create_retriever(asin, engine)

    if retriever:
        st.write("Fetched Review Data", review_df)
        st.write("Fetched Meta Data", meta_df)

        app = graph.create_graph(isMemory=False)

        # User question input field
        user_input = st.text_input("Your question:", key="user_question")

        if user_input:
            response = app.invoke({
                "question": asin,
                "meta_data": meta_df,
                "retriever": retriever,
            }, config=config)

            st.write("Verta:", response['aanswer'].content)
        
                
                




