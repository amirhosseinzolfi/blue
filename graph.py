from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
from logger_config import setup_logger
import os

logger = setup_logger("graph_processor")

# --- Initialize LLM and Embeddings ---
llm = ChatOpenAI(
    base_url="http://141.98.210.15:15203/v1",
    model_name="deepseek-r1",
    temperature=0.5,
    api_key="324"
)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

logger.info("LLM and embeddings initialized")

# --- Define State ---
class AgentState(TypedDict):
    question: str
    answer: str
    history: List[dict]  # Add history to state

# --- Define Nodes ---
def call_llm(state):
    question = state['question']
    history = state.get('history', [])
    logger.info(f"Processing question: {question[:100]}...")
    
    # Build messages from history
    messages = [SystemMessage(content="You are a helpful, professional assistant.")]
    
    # Add conversation history
    for msg in history:
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant':
            messages.append(AIMessage(content=msg['content']))
    
    # Add current question
    messages.append(HumanMessage(content=question))
    
    try:
        # Use messages directly with the LLM
        answer = llm.invoke(messages).content
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
