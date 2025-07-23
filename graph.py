from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import os

# --- Initialize LLM and Embeddings ---
llm = ChatOpenAI(
    base_url="http://141.98.210.15:15203/v1",
    model_name="gpt-4o",
    temperature=0.5,
    api_key="324"
)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# --- Define State ---
class AgentState(TypedDict):
    question: str
    answer: str

# --- Define Nodes ---
def call_llm(state):
    question = state['question']
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful, professional assistant.",
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | llm | StrOutputParser()
    answer = runnable.invoke({"question": question})
    return {"answer": answer}

# --- Define Graph ---
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_llm)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

app = workflow.compile()
