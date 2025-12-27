import os
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState
from .tools import search_web, scrape_article
import json

# Node Definitions
def planner_node(state: AgentState):
    """Decides what to research based on the topic."""
    topic = state['topic']
    # Simple planner: generating search queries
    print(f"--- Planning research for: {topic} ---")
    return {"messages": [f"Researching {topic}"]}

def researcher_node(state: AgentState):
    """Executes search and scrape."""
    topic = state['topic']
    print(f"--- Researching: {topic} ---")
    
    # 1. Search
    results = search_web.invoke(f"{topic} news 2024")
    
    return {"research_results": [f"Search Results for {topic}:\n{results}"]}

def writer_node(state: AgentState):
    """Synthesizes the findings."""
    print(f"--- Writing summary for: {state['topic']} ---")
    
    model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview", api_key=os.getenv("GOOGLE_API_KEY"))
    
    context = "\n\n".join(state['research_results'])
    sys_msg = SystemMessage(content="You are an expert news analyst. Summarize the provided research context into a concise daily briefing with html formatting.")
    user_msg = HumanMessage(content=f"Topic: {state['topic']}\n\nContext:\n{context}")
    
    response = model.invoke([sys_msg, user_msg])
    
    return {"summary": response.text}


# Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)

workflow.set_entry_point("planner")

workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", END)

app = workflow.compile()
