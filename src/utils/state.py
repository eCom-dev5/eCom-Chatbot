from pandas import DataFrame
from operator import add
from constants import OPTIONS
from pydantic import BaseModel
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_core.vectorstores.base import VectorStoreRetriever

class MultiAgentState(TypedDict):
    question: str
    question_type: str
    answer: str 
    documents: Annotated[list[str], add]
    meta_data: DataFrame
    retriever: VectorStoreRetriever
    followup_questions: list[str]

class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""
    datasource: Literal[*OPTIONS] # type: ignore
