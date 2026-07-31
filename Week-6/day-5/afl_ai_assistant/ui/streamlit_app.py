import streamlit as st
import requests
import uuid

# Configuration
API_URL = "http://localhost:8000/api/v1/chat"

st.set_page_config(page_title="AFL AI Assistant", page_icon="🏉", layout="centered")

st.title("🏉 AFL AI Assistant")
st.markdown("Ask me anything about the Australian Football League (AFL)!")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("metadata"):
            with st.expander("Debug Info"):
                st.json(message["metadata"])

# Chat Input
if prompt := st.chat_input("E.g., Who will win between Collingwood and Brisbane?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # API Request
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "query": prompt,
                    "thread_id": st.session_state.session_id
                }
                response = requests.post(API_URL, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Display response
                message_placeholder.markdown(data["response"])
                
                # Show metadata as sub-text
                meta_str = f"Intent: `{data.get('intent')}` | Latency: `{data.get('latency'):.2f}s`"
                st.caption(meta_str)
                
                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["response"],
                    "metadata": {
                        "intent": data.get("intent"),
                        "latency": data.get("latency"),
                        "tool": data.get("metadata", {}).get("tool_requested")
                    }
                })
                
            except Exception as e:
                message_placeholder.error(f"Error communicating with backend: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
