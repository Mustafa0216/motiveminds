import streamlit as st
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="MotiveMinds Support Portal",
    page_icon="🤖",
    layout="centered"
)

from src.auth import login_widget
from src.agent import create_agent_graph, execute_agent_turn, extract_text_content
from langchain_core.messages import HumanMessage, AIMessage

# Sidebar Styling & Config overrides
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.title("MotiveMinds Admin")
    st.markdown("---")
    
    # Allow manual API override
    api_key_override = st.text_input("Override Google API Key", type="password", help="Overrides the server .env key if provided")
    if api_key_override:
        st.session_state.google_api_key_override = api_key_override
    else:
        st.session_state.google_api_key_override = None
        
    st.markdown("---")
    st.info("Secure Multi-Agent RAG Customer Support agent with memory persisted in Redis.")
    
    if st.session_state.get("authenticated", False):
        st.write(f"Logged in as: **{st.session_state.username}**")
        if st.button("Logout", type="primary", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()

# Run authentication widget
if login_widget():
    # User is authenticated
    st.title("🤖 MotiveMinds Support Center")
    st.write("Ask any questions regarding account settings, pricing, refund policies, CRM integration, and technical setup.")

    # 1. Establish Thread ID based on username to isolate memory
    username = st.session_state.username
    thread_id = f"motiveminds_thread_{username}"
    config = {"configurable": {"thread_id": thread_id}}
    
    # 2. Compile/Load agent graph and fetch existing state from checkpointer
    try:
        from src.redis_checkpointer import init_redis_saver
        checkpointer = init_redis_saver()
        app = create_agent_graph(checkpointer=checkpointer)
        current_state = app.get_state(config)
    except Exception as e:
        st.error(f"Failed to initialize agent graph: {e}")
        st.stop()

    # 3. Retrieve messages history from Redis state
    messages = current_state.values.get("messages", []) if current_state and current_state.values else []

    # 4. Display chat history
    for msg in messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.write(extract_text_content(msg.content))
        elif isinstance(msg, AIMessage):
            # Only display messages that actually have text content (ignore tool call helper messages)
            clean_text = extract_text_content(msg.content)
            if clean_text:
                with st.chat_message("assistant"):
                    st.write(clean_text)

    # 5. Handle user input
    if prompt := st.chat_input("How can I help you today?"):
        # Immediately display user message in UI
        with st.chat_message("user"):
            st.write(prompt)

        # Run agent graph with Redis checkpointer memory
        with st.spinner("Support agent is thinking..."):
            try:
                # execute_agent_turn runs graph, verifies stateresponse, and returns final state
                final_state = execute_agent_turn(thread_id, prompt, checkpointer=checkpointer)
                
                # Fetch only the final assistant message
                final_messages = final_state.get("messages", [])
                if final_messages:
                    last_assistant_msg = final_messages[-1]
                    if isinstance(last_assistant_msg, AIMessage):
                        clean_response = extract_text_content(last_assistant_msg.content)
                        if clean_response:
                            with st.chat_message("assistant"):
                                st.write(clean_response)
                                st.rerun()
            except Exception as e:
                st.error(f"Error executing agent turn: {e}")
