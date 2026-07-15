import os
import streamlit as st
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from src.vector_store import get_retriever
from dotenv import load_dotenv

load_dotenv()

# Define State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# 1. Create Retriever Tool
@tool
def retrieve_faq(query: str) -> str:
    """Useful for searching the MotiveMinds Knowledge Base FAQ.
    Use this tool to find information about billing, refund policy, system requirements,
    password resets, CRM integration, and general company policies.
    """
    # No console print statements to keep the retrieval process completely silent
    try:
        retriever = get_retriever()
        docs = retriever.invoke(query)
        # Format the retrieved documents into a single text block
        formatted_docs = []
        for i, doc in enumerate(docs):
            formatted_docs.append(f"Document chunk {i+1}:\n{doc.page_content}")
        return "\n\n".join(formatted_docs)
    except Exception:
        # Silently return error message to LLM without logging to console
        return "Error: Could not retrieve information from the knowledge base."

# 2. Get LLM Instance
def get_llm():
    """Initializes and returns the Chat LLM based on environment or Streamlit override."""
    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Check Streamlit overrides
    if "google_api_key_override" in st.session_state and st.session_state.google_api_key_override:
        google_api_key = st.session_state.google_api_key_override
    if "openai_api_key_override" in st.session_state and st.session_state.openai_api_key_override:
        openai_api_key = st.session_state.openai_api_key_override

    if google_api_key and google_api_key != "your_api_key_here":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=0,
            streaming=False
        )
    elif openai_api_key and openai_api_key != "your_openai_api_key_here":
        from langchain_openai import ChatOpenAI
        openai_api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        return ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=openai_api_key,
            openai_api_base=openai_api_base,
            temperature=0,
            streaming=False
        )
    else:
        raise ValueError("No valid API Key (GOOGLE_API_KEY or OPENAI_API_KEY) found.")

# 3. Define the Agent Node
def support_agent_node(state: AgentState):
    """Executes the core support agent reasoning.
    No console log is written to prevent data leakage.
    """
    messages = state["messages"]
    
    # Define a clean System Message with explicit topic restrictions (guardrails)
    system_msg = SystemMessage(
        content=(
            "You are the MotiveMinds Customer Support Agent. Your job is strictly limited to helping users with "
            "account management, billing, refunds, CRM integration, and technical questions regarding MotiveMinds.\n\n"
            "CRITICAL TOPIC RESTRICTION:\n"
            "- You must ONLY answer questions directly related to MotiveMinds, its features, policies, or customer support.\n"
            "- If the user asks unrelated questions (e.g. general knowledge, programming help, creative writing, "
            "unrelated calculations, or general chat), you must politely decline to answer, explaining that your "
            "expertise is restricted to MotiveMinds customer support.\n\n"
            "You have access to the `retrieve_faq` tool. Use this tool whenever a user asks questions that "
            "require factual information from the MotiveMinds Knowledge Base.\n"
            "Do NOT reference the tool, database, or retrieval process in your answers. Present the retrieved "
            "facts naturally as your own knowledge. If the retrieved documents do not contain the answer, "
            "politely inform the user that you don't have that information but they can reach out to "
            "support@motiveminds.com.\n\n"
            "Keep your tone professional, helpful, and concise. Utilize conversation history to track "
            "the context of the conversation."
        )
    )
    
    # Load LLM and bind it with the tools
    llm = get_llm()
    tools = [retrieve_faq]
    llm_with_tools = llm.bind_tools(tools)
    
    # Inject system message at the beginning
    response = llm_with_tools.invoke([system_msg] + list(messages))
    
    return {"messages": [response]}

# 4. Routing Decision Node
def should_continue(state: AgentState) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    
    # If LLM wants to call a tool, route to "tools" node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    return END

# 5. Compile Graph
def create_agent_graph(checkpointer=None):
    """Builds and compiles the LangGraph StateGraph."""
    workflow = StateGraph(AgentState)
    
    # Define Nodes
    workflow.add_node("agent", support_agent_node)
    
    tools = [retrieve_faq]
    tool_node = ToolNode(tools)
    workflow.add_node("tools", tool_node)
    
    # Define Edges
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {
        "tools": "tools",
        END: END
    })
    workflow.add_edge("tools", "agent")
    
    return workflow.compile(checkpointer=checkpointer)

# 6. Verify State Response
def execute_agent_turn(thread_id: str, user_message: str, checkpointer=None) -> dict:
    """Executes a single turn of the agent graph.
    Performs verification on the returned state (stateresponse).
    No console log is written to prevent data leakage.
    """
    app = create_agent_graph(checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": thread_id}}
    
    # Send user message
    input_state = {"messages": [HumanMessage(content=user_message)]}
    
    # Stream/Execute graph turns synchronously
    result_state = app.invoke(input_state, config=config)
    
    # Verify the structure of stateresponse
    verify_state_response(result_state)
    
    return result_state

def extract_text_content(content) -> str:
    """Helper to extract raw text content from message content,
    which can be a string or a list of content blocks (dicts).
    """
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            elif isinstance(block, str):
                text_parts.append(block)
        return "".join(text_parts)
    return str(content)

def verify_state_response(state: dict):
    """Verifies that the state response conforms to the expected structure.
    Raises ValueError if validation fails.
    """
    if not state:
        raise ValueError("State response is empty.")
    if "messages" not in state:
        raise ValueError("State response is missing 'messages' key.")
    if not isinstance(state["messages"], list) or len(state["messages"]) == 0:
        raise ValueError("State response messages is empty or not a list.")
    
    # Verify the final message is an Assistant message
    last_msg = state["messages"][-1]
    if not isinstance(last_msg, AIMessage):
        raise ValueError("The final message in state response must be an Assistant Message (AIMessage).")
    if not extract_text_content(last_msg.content).strip():
        raise ValueError("The final assistant message text content is empty.")

