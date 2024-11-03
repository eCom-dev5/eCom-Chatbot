import os
import json
import redis
import uvicorn
import asyncio
import pandas as pd
from typing import Any
from sqlalchemy import text
from pydantic import BaseModel
from graph import create_graph
from utils import database as db
from collections.abc import AsyncGenerator
from langfuse.callback import CallbackHandler
from langchain_community.vectorstores import FAISS
from langgraph.graph.state import CompiledStateGraph
from langchain_huggingface import HuggingFaceEmbeddings
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from langchain_community.document_loaders import DataFrameLoader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

## load the API Keys
os.environ['HF_TOKEN']=os.getenv("HF_TOKEN")
os.environ['OPENAI_API_KEY']=os.getenv("OPENAI_API_KEY")
os.environ['GROQ_API_KEY']=os.getenv("GROQ_API_KEY")

## Langfuse
os.environ['LANGFUSE_PUBLIC_KEY']=os.getenv("LANGFUSE_PUBLIC_KEY")
os.environ['LANGFUSE_SECRET_KEY']=os.getenv("LANGFUSE_SECRET_KEY")
os.environ['LANGFUSE_HOST']=os.getenv("LANGFUSE_HOST")
langfuse_handler = CallbackHandler()

## Postgres DB
credentials = {
    'INSTANCE_CONNECTION_NAME': os.getenv("INSTANCE_CONNECTION_NAME"),
    'DB_USER': os.getenv("DB_USER"),
    'DB_PASS': os.getenv("DB_PASS"),
    'DB_NAME': os.getenv("DB_NAME")
}

app = FastAPI()
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
engine = db.connect_with_db(credentials)

async def create_retriever(asin: str):
    # Otherwise, create a new retriever
    with engine.begin() as connection:
        try:
            # Fetch reviews
            review_query = text(f"""
                SELECT parent_asin, asin, helpful_vote, timestamp, verified_purchase, title, text
                FROM userreviews ur 
                WHERE ur.parent_asin = '{asin}';
            """)
            review_result = connection.execute(review_query)
            review_df = pd.DataFrame(review_result.fetchall(), columns=review_result.keys())

            # Fetch metadata
            meta_query = text(f"""
                SELECT parent_asin, main_category, title, average_rating, rating_number, features, description, price, store, categories, details
                FROM metadata md 
                WHERE md.parent_asin = '{asin}';
            """)
            meta_result = connection.execute(meta_query)
            meta_df = pd.DataFrame(meta_result.fetchall(), columns=meta_result.keys())

        except Exception as e:
            print("Error:", e)
            return None, None

    # Load and process reviews
    loader = DataFrameLoader(review_df)
    review_docs = loader.load()

    # Initialize FAISS retriever
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(documents=review_docs, embedding=embeddings)
    retriever = vectordb.as_retriever()

    return retriever, meta_df


async def get_retriever_for_asin(asin: str):
    print("1")
    retriever = redis_client.get(f"retriever:{asin}")
    meta_df = redis_client.get(f"meta_df:{asin}")

    
    if retriever and meta_df:
        return retriever, meta_df  # Return cached retriever and metadata
    
    # Create new retriever if not cached
    retriever, meta_df = await create_retriever(asin)
    if retriever and meta_df:
        redis_client.set(f"retriever:{asin}", retriever)
        redis_client.set(f"meta_df:{asin}", meta_df)
    return retriever, meta_df

#old app get request
# @app.get("/initialize")
# async def initialize(asin: str):
#     retriever, meta_df = await get_retriever_for_asin(asin)
#     if retriever is None:
#         return JSONResponse(content={"status": "failed to initialize retriever"}, status_code=500)
#     return JSONResponse(content={"status": "retriever initialized", "asin": asin}, status_code=200)

@app.get("/initialize")
async def initialize(asin: str):
    logger.info(f"Received request to initialize retriever for ASIN: {asin}")
    
    #retriever, meta_df = await get_retriever_for_asin(asin)
    # if retriever is None:
    #     logger.error(f"Failed to initialize retriever for ASIN: {asin}")
    #     return JSONResponse(content={"status": "failed to initialize retriever"}, status_code=500)
    
    logger.info(f"Retriever initialized successfully for ASIN: {asin}")
    return JSONResponse(content={"status": "retriever initialized", "asin": asin}, status_code=200)


class UserInput(BaseModel):
    user_input: str
    config: dict
    parent_asin: str
    log_langfuse: bool
    stream_tokens: bool


@app.post("/dev-invoke")
async def invoke(user_input: UserInput):
    """
    Invoke the agent with user input to retrieve a final response.
    """
    retriever, meta_df = await get_retriever_for_asin(user_input.parent_asin)
    if retriever is None:
        return JSONResponse(content={"status": "Retriever not initialized"}, status_code=400)
    if meta_df is None:
        return JSONResponse(content={"status": "Meta-Data not initialized"}, status_code=400)
    
    agent: CompiledStateGraph = create_graph()
    if user_input.log_langfuse:
        user_input.config.update({"callbacks": [langfuse_handler]})
    try:
        response = await agent.ainvoke({
                                        "question": user_input.user_input, 
                                        "meta_data": meta_df,
                                        "retriever": retriever
                                    }, config=user_input.config)

        output = {
            'question': response['question'],
            'answer': response['answer'].content,
            'followup_questions': response['followup_questions']
        }
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def message_generator(user_input: UserInput, stream_tokens=True) -> AsyncGenerator[str, None]:
    """
    Generate a stream of messages from the agent.

    This is the workhorse method for the /stream endpoint.
    """
    retriever, meta_df = await get_retriever_for_asin(user_input.parent_asin)
    if retriever is None:
        yield JSONResponse(content={"status": "Retriever not initialized"}, status_code=400)
    if meta_df is None:
        yield JSONResponse(content={"status": "Meta-Data not initialized"}, status_code=400)
    
    agent: CompiledStateGraph = create_graph()


    if user_input.log_langfuse:
        user_input.config.update({"callbacks": [langfuse_handler]})
    if user_input.stream_tokens == 0:
        stream_tokens = False


    # Process streamed events from the graph and yield messages over the SSE stream.
    async for event in agent.astream_events({"question": user_input.user_input, 
                                            "meta_data": meta_df,
                                            "retriever": retriever
                                        }, version="v2", config=user_input.config):
        if not event:
            continue
             
        # Yield tokens streamed from LLMs.
        if (
            event["event"] == "on_chat_model_stream"
            and stream_tokens == True
            and any(t.startswith('seq:step:2') for t in event.get("tags", []))
            and event['metadata']['langgraph_node'] == 'generate'
        ):
            content = event["data"]["chunk"].content
            if content:
                yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
            continue

        # Yield messages written to the graph state after node execution finishes.
        if (
            (event["event"] == "on_chain_end")
            and ((any(t.startswith('seq:step:2') for t in event.get("tags", [])))
            and ((event['metadata']['langgraph_node'] == 'final')
            and (event['metadata']['langgraph_triggers'] == ['generate'])))
        ):
            answer = event["data"]["output"]["answer"].content
            followup_questions = event["data"]["output"]["followup_questions"]
            output = {
                "question": user_input.user_input,
                "answer": answer,
                "followup_questions": followup_questions
            }
            # Yield the final structured response (after processing all streaming tokens)
            yield f"data: {json.dumps({'type': 'message', 'content': output})}\n\n"

    yield "data: [DONE]\n\n"


def _sse_response_example() -> dict[int, Any]:
    return {
        status.HTTP_200_OK: {
            "description": "Server Sent Event Response",
            "content": {
                "text/event-stream": {
                    "example": "data: {'type': 'token', 'content': 'Hello'}\n\ndata: {'type': 'token', 'content': ' World'}\n\ndata: [DONE]\n\n",
                    "schema": {"type": "string"},
                }
            },
        }
    }


@app.post("/dev-stream", response_class=StreamingResponse, responses=_sse_response_example())
async def stream_agent(user_input: UserInput) -> StreamingResponse:
    """
    Stream the agent's response to a user input, including intermediate messages and tokens.

    Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
    is also attached to all messages for recording feedback.
    """
    return StreamingResponse(message_generator(user_input), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
