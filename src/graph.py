import os
import sys
from pathlib import Path
from utils.state import *
import utils.nodes as node
import utils.agents as agent
from dotenv import load_dotenv
from langfuse.callback import CallbackHandler
from constants import MEMBERS, CONDITIONAL_MAP
from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver


sys.path.append(
    str(
        Path(
            "ecom-chat"
        ).resolve()
    )
)


def create_graph(isMemory=True):
    memory = MemorySaver()
    builder = StateGraph(MultiAgentState)

    builder.add_node("Metadata", agent.metadata_node)
    builder.add_node("Review-Vectorstore", agent.retrieve)
    builder.add_node("supervisor", agent.supervisor_agent)
    builder.add_node("generate", node.final_llm_node)
    builder.add_node("final", node.followup_node)

    for member in MEMBERS:
        builder.add_edge(member, "supervisor")

    builder.add_conditional_edges("supervisor", node.route_question, CONDITIONAL_MAP)

    builder.add_edge(START, "supervisor")
    builder.add_edge("generate", "final")
    builder.add_edge("final", END)

    graph = builder.compile(checkpointer=memory) if isMemory else builder.compile()

    return graph


if __name__ == '__main__':
    _ = load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY")
    os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY")
    os.environ["LANGFUSE_HOST"] = os.getenv("LANGFUSE_HOST")

    app = create_graph()

    langfuse_handler = CallbackHandler()

    config = {"configurable": {"thread_id": "2"}, "callbacks": [langfuse_handler]}
    for s in app.stream({
        'question': "Hello",
    }, config=config
    ):
        print(s)