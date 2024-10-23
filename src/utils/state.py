from operator import add
from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel
import pandas as pd
from constants import OPTIONS

class MultiAgentState(TypedDict):
    question: str
    question_type: str
    answer: str 
    documents: Annotated[list[str], add]
    meta_data: pd.DataFrame
    review_docs: list
    followup_questions: list[str]

class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal[*OPTIONS]
