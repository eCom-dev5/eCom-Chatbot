import os
import json
import uvicorn
from typing import Any
from pydantic import BaseModel
from graph import create_graph
from collections.abc import AsyncGenerator
from langfuse.callback import CallbackHandler
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, HTTPException, status
from langgraph.graph.state import CompiledStateGraph


app = FastAPI()


class UserInput(BaseModel):
    user_input: str
    config: dict
    log_langfuse: bool
    stream_tokens: bool


@app.post("/invoke")
async def invoke(user_input: UserInput):
    """
    Invoke the agent with user input to retrieve a final response.
    """
    agent: CompiledStateGraph = create_graph()
    if user_input.log_langfuse:
        user_input.config.update({"callbacks": [langfuse_handler]})
    try:
        response = await agent.ainvoke({"question": user_input.user_input}, config=user_input.config)

        output = {
            'question': response['question'],
            'answer': response['answer'].content,
            'citations': response['citations'],
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
    agent: CompiledStateGraph = create_graph()

    if user_input.log_langfuse:
        user_input.config.update({"callbacks": [langfuse_handler]})
    if user_input.stream_tokens == 0:
        stream_tokens = False


    # Process streamed events from the graph and yield messages over the SSE stream.
    async for event in agent.astream_events({'question': user_input.user_input}, version="v2", config=user_input.config):
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
            citations = event["data"]["output"]["citations"]
            followup_questions = event["data"]["output"]["followup_questions"]
            output = {
                "question": user_input.user_input,
                "answer": answer,
                "citations": citations,
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


@app.post("/stream", response_class=StreamingResponse, responses=_sse_response_example())
async def stream_agent(user_input: UserInput) -> StreamingResponse:
    """
    Stream the agent's response to a user input, including intermediate messages and tokens.

    Use thread_id to persist and continue a multi-turn conversation. run_id kwarg
    is also attached to all messages for recording feedback.
    """
    return StreamingResponse(message_generator(user_input), media_type="text/event-stream")


if __name__ == "__main__":
    os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY")
    os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY")
    os.environ["LANGFUSE_HOST"] = os.getenv("LANGFUSE_HOST")
    langfuse_handler = CallbackHandler()
    uvicorn.run(app, host="0.0.0.0", port=80)
