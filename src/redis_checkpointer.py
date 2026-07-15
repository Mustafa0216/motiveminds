import os
import streamlit as st
from redis import Redis
from langgraph.checkpoint.redis import RedisSaver
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

@st.cache_resource
def init_redis_saver():
    """Initializes and returns a RedisSaver checkpointer.
    Raises exception if Redis connection fails.
    """
    try:
        # Check connection first
        client = Redis.from_url(REDIS_URL, socket_timeout=2.0)
        client.ping()
        
        saver = RedisSaver.from_conn_string(REDIS_URL)
        saver.setup()
        return saver
    except Exception as e:
        from langgraph.checkpoint.memory import MemorySaver
        # Graceful fallback warning
        try:
            st.sidebar.warning("Redis not reachable. Memory is running in-memory (MemorySaver) and will reset when app restarts.")
        except Exception:
            pass
        return MemorySaver()
