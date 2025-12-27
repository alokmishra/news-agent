from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    topic: str
    messages: List[str]
    research_results: Annotated[List[str], operator.add]
    sources: Annotated[List[str], operator.add]
    summary: str
