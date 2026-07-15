import os
import sys
import unittest
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

class TestMotiveMindsAgent(unittest.TestCase):
    
    def has_api_key(self):
        google_key = os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        return (google_key and google_key != "your_api_key_here") or \
               (openai_key and openai_key != "your_openai_api_key_here")

    def test_redis_connection(self):
        """Verifies that Redis is running and reachable."""
        from redis import Redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            client = Redis.from_url(redis_url)
            self.assertTrue(client.ping(), "Redis ping failed.")
        except Exception as e:
            self.fail(f"Could not connect to Redis at {redis_url}. Ensure Redis is running. Error: {e}")

    def test_vector_store_initialization(self):
        """Verifies that ChromaDB can be initialized and retrieves documents."""
        if not self.has_api_key():
            self.skipTest("Skipping because no API Key is configured in .env.")
        from src.vector_store import get_retriever, initialize_vector_store
        
        try:
            db = initialize_vector_store()
            self.assertIsNotNone(db, "ChromaDB initialization failed.")
            
            retriever = get_retriever()
            results = retriever.invoke("password")
            self.assertTrue(len(results) > 0, "No RAG documents retrieved for query 'password'.")
        except Exception as e:
            self.fail(f"ChromaDB / Retriever initialization failed: {e}")

    def test_agent_execution_and_stateresponse(self):
        """Executes a support agent turn and validates the state response (stateresponse)."""
        if not self.has_api_key():
            self.skipTest("Skipping because no API Key is configured in .env.")
        from src.agent import execute_agent_turn, verify_state_response, create_agent_graph
        from langchain_core.messages import AIMessage
        
        thread_id = "test_verification_thread_999"
        query = "How do I reset my password?"
        
        try:
            # 1. Execute agent turn
            state_response = execute_agent_turn(thread_id, query)
            
            # 2. Check structure via verify_state_response (raises error on failure)
            verify_state_response(state_response)
            
            # 3. Additional assertions on returned state
            messages = state_response["messages"]
            last_message = messages[-1]
            
            self.assertIsInstance(last_message, AIMessage)
            self.assertTrue(len(last_message.content) > 0, "Assistant response was empty.")
            
            # 4. Verify memory persistence in Redis by fetching state again
            app = create_agent_graph()
            config = {"configurable": {"thread_id": thread_id}}
            fetched_state = app.get_state(config)
            
            self.assertIsNotNone(fetched_state, "Could not fetch state from Redis.")
            self.assertTrue(len(fetched_state.values.get("messages", [])) >= 2, 
                            "Redis did not persist the conversation turns.")
            
        except Exception as e:
            self.fail(f"Agent execution and validation failed: {e}")

if __name__ == "__main__":
    unittest.main()
