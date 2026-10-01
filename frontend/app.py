"""
app.py
------
Streamlit frontend for the SmartSACCO AI Agent.
"""

import sys
import os
import streamlit as st

# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the agent executor initialization function from our backend
from backend.agent import get_agent_executor

# Configure the Streamlit page layout and title
st.set_page_config(page_title="SmartSACCO AI Assistant", layout="centered")

# ==========================================
# 1. INITIALIZE SESSION STATE FIRST (MUST BE HERE)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
# ==========================================

st.title("SmartSACCO AI Assistant")
st.markdown("Ask questions about your account balance or official SACCO policies.")

# --- SUGGESTED PROMPTS FOR EASY TESTING ---
st.markdown("**Suggested questions to test the AI:**")
col1, col2 = st.columns(2)

with col1:
    if st.button("Check M001 Balance"):
        st.session_state.messages.append({"role": "user", "content": "What is the savings balance for member M001?"})
        st.rerun()
        
    if st.button("Check M002 Loan Eligibility"):
        st.session_state.messages.append({"role": "user", "content": "I am member M002. Based on my current savings, am I eligible for a 100,000 KES loan?"})
        st.rerun()

with col2:
    if st.button("Development Loan Interest Rate"):
        st.session_state.messages.append({"role": "user", "content": "What is the interest rate for a development loan, and how is it calculated?"})
        st.rerun()
        
    if st.button("Check Invalid Member M999"):
        st.session_state.messages.append({"role": "user", "content": "What is the savings balance for member M999?"})
        st.rerun()
# ------------------------------------------

# Display all historical chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Ask me about your SACCO account or policies..."):
    # 1. Add the user's message to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Display the user's message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Generate the AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking and retrieving data..."):
            try:
                # Initialize the agent executor
                executor = get_agent_executor()
                
                # Invoke the agent with the user's prompt
                response = executor.invoke({"input": prompt})
                raw_output = response["output"]
                
                # Robustly parse the output to ensure we only display clean text
                if isinstance(raw_output, str):
                    output_text = raw_output
                elif isinstance(raw_output, list):
                    output_text = "\n".join(
                        [item.get("text", str(item)) for item in raw_output if isinstance(item, dict)]
                    )
                else:
                    output_text = str(raw_output)
                    
                if "503" in output_text or "UNAVAILABLE" in output_text or "high demand" in output_text.lower():
                    output_text = "The AI service is currently experiencing high traffic. Please wait a moment and try your question again."
                    
            except Exception as e:
                error_msg = str(e)
                if "503" in error_msg or "UNAVAILABLE" in error_msg:
                    output_text = "The AI service is currently experiencing high traffic. Please wait a moment and try your question again."
                else:
                    output_text = "An unexpected error occurred. Please try again later."
                
        st.markdown(output_text)
    
    # 4. Add the assistant's response to the chat history
    st.session_state.messages.append({"role": "assistant", "content": output_text})