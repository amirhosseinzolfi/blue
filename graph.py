from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from logger_config import setup_logger
import os

logger = setup_logger("graph_processor")

# --- Initialize LLM and Embeddings ---
llm = ChatOpenAI(
    base_url="http://141.98.210.15:15203/v1",
    model_name="gpt-4o",
    temperature=0.5,
    api_key="324"
)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

logger.info("LLM and embeddings initialized")

# --- Define State ---
class AgentState(TypedDict):
    question: str
    answer: str

# --- Define Nodes ---
def call_llm(state):
    question = state['question']
    logger.info(f"Processing question: {question[:100]}...")
    
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful, professional assistant.",
            ),
            ("human", "{question}"),
        ]
    )
    
    try:
        runnable = prompt | llm | StrOutputParser()
        answer = runnable.invoke({"question": question})
        logger.info(f"LLM response generated: {answer[:100]}...")
        return {"answer": answer}
        
    except Exception as e:
        logger.error(f"Error in LLM call: {e}")
        return {"answer": "Sorry, I encountered an error processing your request."}

# --- Define Graph ---
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_llm)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

app = workflow.compile()
logger.info("Graph workflow compiled successfully")
