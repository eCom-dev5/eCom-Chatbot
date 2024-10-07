import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
from langchain.document_loaders import DataFrameLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os

from dotenv import load_dotenv
load_dotenv()

## load the GROQ and HF API Key 
os.environ['HF_TOKEN']=os.getenv("HF_TOKEN")
os.environ['GROQ_API_KEY']=os.getenv("GROQ_API_KEY")

## Loading the Model
llm = ChatGroq(model_name="llama-3.1-70b-versatile")
meta_llm = ChatGroq(model_name="llama-3.1-8b-instant")

credentials = service_account.Credentials.from_service_account_file('big_credentials.json')
client = bigquery.Client(credentials=credentials)

## Getting the embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

## set up Streamlit 
st.set_page_config(page_title="Aster", page_icon="🧑‍💻")
st.title("Aster")
st.subheader("Your Intelligent eCommerce Companion")

## Name
name=st.text_input("Enter your product ASIN:")

if name:
    # Perform a query.
    QUERY = (f'''SELECT *
            FROM `ecom-chat-437005.ecom_chat.review` 
            WHERE parent_asin='{str(name)}'
            ''')
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish

    review_df = rows.to_dataframe()
    review_df.drop(columns=['user_id', 'images'], inplace = True)

    st.write("Fetched Review Data", review_df)

    # Perform a query.
    QUERY = (f'''SELECT *
            FROM `ecom-chat-437005.ecom_chat.meta` 
            WHERE parent_asin='{str(name)}'
            ''')
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish

    meta_df = rows.to_dataframe()

    meta_df.drop(columns=['images', 'videos', 'bought_together'], inplace = True)
    
    st.write("Fetched Meta Data", meta_df)

    review_loader = DataFrameLoader(review_df) 
    review_docs = review_loader.load()
    vectorstore = FAISS.from_documents(documents=review_docs, embedding=embeddings)
    retriever = vectorstore.as_retriever()
    modified_details = meta_df['details'].astype(str).str.replace('{', '[')
    modified_details = modified_details.str.replace('}', ']')
    # Answer question
    meta_system_prompt =( 
        f'''
        You are a great Data Interpreter and Summarizer. Read the Product Meta Data sent to you and Produce it in 500 words.
        
        Meta Data:
        main_category: {meta_df['main_category']}
        title: {meta_df['title']}
        average_rating: {meta_df['average_rating']}
        rating_number: {meta_df['rating_number']}
        features: {meta_df['features']}
        description: {meta_df['description']}
        price: {meta_df['price']}
        store: {meta_df['store']}
        categories: {meta_df['categories']}	
        details: {modified_details}

        Return in a proper format:
        main_category: Same 
        title: Same
        average_rating: Same
        rating_number: Same
        features: Summarize	
        description: Summarize
        price: Same
        store: Same	
        categories: Same	
        details: Same/Summarize where necessary	
        
        Here is the product information.
        '''
    )
    meta_qa_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", meta_system_prompt),
                    ("human", "{input}")
                ]
            )
    parser = StrOutputParser()

    chain = meta_qa_prompt | meta_llm | parser
    meta_summary = chain.invoke({"input": " "})

    # Answer question
    system_prompt = (
        f'''
        You are Alpha. You are a sales person selling eCommerce Products.

        Here is the product information:

        {meta_summary}
        '''
        "{context}"
        '''
        Help user answer any question regarding the product. 
        Just answer the questions in brief.

        Your responses should be clear, concise, and insightful.
        '''
    )

    user_input = st.text_input("Your question:")

    if user_input:
        qa_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", system_prompt),
                        ("human", "{input}")
                    ]
                )
        
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        response = rag_chain.invoke({"input": user_input})

        st.write("Aster:", response['answer'])



